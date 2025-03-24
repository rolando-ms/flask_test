from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
users = db["Users"]
admins = db["Admins"]

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
            return_json = {
                "status": 301,
                "message": "User already registered"
            }
            return jsonify(return_json)
        
        hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert_one(
            {
                "Username": username,
                "Password": hashed_password,
                "Tokens": 10
            }
        )

        return_json = {
            "status": 200,
            "message": "Username succesfully added."
        }

        return jsonify(return_json)
    
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
    
class DetectSimilarity(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        text1 = posted_data["text1"]
        text2 = posted_data["text2"]

        if not user_exist(username):
            return_json = {
                "status": 301,
                "message": "Invalid username"
            }
            return jsonify(return_json)
        
        correct_password = verify_password(username, password)

        if not correct_password:
            return_json = {
                "status": 302,
                "message": "Invalid password"
            }
            return jsonify(return_json)
        
        tokens = count_tokens(username)
        
        if tokens <= 0:
            return_json = {
                "status": 303,
                "message": "Not enough tokens available for this operation "
                "(%s tokens left)." % (str(tokens))
            }
            return jsonify(return_json)
        
        nlp = spacy.load('en_core_web_sm')

        text1 = nlp(text1)
        text2 = nlp(text2)

        ratio = text1.similarity(text2)

        return_json = {
            "status": 200,
            "message": "Similarity calculated succesfully.",
            "similarity": ratio
        }

        users.update_one(
            {
                "Username": username
            },
            {
                "$set":
                {
                    "Tokens": tokens - 1
                }
            }
        )

        return jsonify(return_json)
    
def admin_exist(admin):
    if admins.count_documents({"Admin": admin}) == 0:
        return False
    return True

class RegisterAdmin(Resource):
    def post(self):
        posted_data = request.get_json()

        admin = posted_data["admin"]
        password = posted_data["password"]

        if admin_exist(admin):
            return_json = {
                "status": 301,
                "message": "Admin already registered"
            }
            return jsonify(return_json)
        
        hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        admins.insert_one(
            {
                "Admin": admin,
                "Password": hashed_password
            }
        )

        return_json = {
            "status": 200,
            "message": "Admin succesfully added."
        }

        return jsonify(return_json)

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
        password = posted_data["password"]
        username = posted_data["username"]
        refill_tokens = posted_data["tokens"]

        if not admin_exist(admin):
            return_json = {
                "status": 301,
                "message": "Invalid admin"
            }
            return jsonify(return_json)
        
        correct_password = verify_admin_password(admin, password)

        if not correct_password:
            return_json = {
                "status": 302,
                "message": "Invalid admin password"
            }
            return jsonify(return_json)
        
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

        return_json = {
            "status": 200,
            "message": "Refill succesful. Tokens available for User: %s = %s tokens" % 
            (username, str(tokens + refill_tokens))
        }
        return jsonify(return_json)

class GetTokens(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        if not user_exist(username):
            return_json = {
                "status": 301,
                "message": "Invalid username"
            }
            return jsonify(return_json)
        
        correct_password = verify_password(username, password)

        if not correct_password:
            return_json = {
                "status": 302,
                "message": "Invalid password"
            }
            return jsonify(return_json)
        
        tokens = users.find(
        {
            "Username": username
        }
        )[0]["Tokens"]

        return_json = {
            "status": 200,
            "Number of tokens available": tokens
        }

        return jsonify(return_json)


api.add_resource(RegisterUser, "/registerUser")
api.add_resource(DetectSimilarity, "/detectSimilarity")
api.add_resource(RegisterAdmin, "/registerAdmin")
api.add_resource(RefillTokens, "/refillTokens")
api.add_resource(GetTokens, "/getTokens")

if __name__ == "__main__":
    app.run(host='0.0.0.0')