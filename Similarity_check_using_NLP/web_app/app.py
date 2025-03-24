from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
users = db["Users"]

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
                "message": "Invalid username"
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

api.add_resource(RegisterUser, "/registerUser")

if __name__ == "__main__":
    app.run(host='0.0.0.0')