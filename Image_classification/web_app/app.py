from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.ImageClassificationDB
users = db["Users"]
admins = db["Admins"]

def build_json_response(status_code: int, message: str):
    return_json = {
        "status": status_code,
        "message": message
    }
    return jsonify(return_json)

def user_exist(username):
    if users.count_documents({"Username": username}) == 0:
        return False
    return True

class RegisterUser(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        if user_exist(username):
            return build_json_response(301, "User already registered")
        
        hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert_one(
            {
                "Username": username,
                "Password": hashed_password,
                "Tokens": 10
            }
        )

        return build_json_response(200, "Username succesfully added.")
    
def verify_password(username, password):
    if not user_exist(username):
        return False
    
    hashed_password = users.find(
        {
            "Username": username
        }
    )[0]['Password']

    if bcrypt.hashpw(password.encode('utf8'), hashed_password) == hashed_password:
        return True
    return False


def count_tokens(username):
    tokens = users.find(
        {
            "Username": username
        }
    )[0]["Tokens"]
    return tokens
    
def admin_exist(admin):
    if admins.count_documents({"Admin": admin}) == 0:
        return False
    return True

class RegisterAdmin(Resource):
    def post(self):
        posted_data = request.get_json()

        admin = posted_data["admin"]
        password = posted_data["admin_password"]

        if admin_exist(admin):
            return build_json_response(301, "Admin already registered")
        
        hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        admins.insert_one(
            {
                "Admin": admin,
                "Password": hashed_password
            }
        )

        return build_json_response(200, "Admin succesfully added.")

def verify_admin_password(admin, password):
    if not admin_exist(admin):
        return False
    
    hashed_password = admins.find(
        {
            "Admin": admin
        }
    )[0]['Password']

    if bcrypt.hashpw(password.encode('utf8'), hashed_password) == hashed_password:
        return True
    return False
    
class RefillTokens(Resource):
    def post(self):
        posted_data = request.get_json()

        admin = posted_data["admin"]
        password = posted_data["admin_password"]
        username = posted_data["username"]
        refill_tokens = posted_data["tokens"]

        if not admin_exist(admin):
            return build_json_response(301, "Invalid admin")
        
        correct_password = verify_admin_password(admin, password)

        if not correct_password:
            return build_json_response(302, "Invalid admin password")
        
        tokens = count_tokens(username)

        users.update_one(
            {
                "Username": username
            },
            {
                "$set":
                {
                    "Tokens": tokens + refill_tokens
                }
            }
        )

        return build_json_response(200, "Refill succesful. Tokens available for User: %s = %s tokens" % 
            (username, str(tokens + refill_tokens)))

class GetTokens(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        if not user_exist(username):
            return build_json_response(301, "Invalid username")
        
        correct_password = verify_password(username, password)

        if not correct_password:
            return build_json_response(302, "Invalid password")
        
        tokens = users.find(
        {
            "Username": username
        }
        )[0]["Tokens"]

        return build_json_response(200, "%s Tokens available"%(str(tokens)))


api.add_resource(RegisterUser, "/registerUser")
api.add_resource(RegisterAdmin, "/registerAdmin")
api.add_resource(RefillTokens, "/refillTokens")
api.add_resource(GetTokens, "/getTokens")

if __name__ == "__main__":
    app.run(host='0.0.0.0')