'''
RESTful API with Database as a Service
Storage of sentences

- Registration of new user costs 0 tokens
- Each user gets initially 10 tokens
- Store a sentence on DB costs 1 token
- Retrieve teh stored sentence costs 1 token
'''

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import bcrypt

from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDB
users = db["Users"]

def verify_password(username, password):
    hashed_password = users.find(
        {
            "Username": username
        }
    )[0]["Password"]
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

class RegisterUser(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        # Encrypting password for security
        hashed_password = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        # Storing encrypted password and user into DB
        users.insert_one(
            {
                "Username": username,
                "Password": hashed_password,
                "Sentence": "",
                "Tokens": 10
            }
        )

        return_json = {
            "status": 200,
            "message": "You signed up for the API"
        }

        return jsonify(return_json)
    
class StoreSentence(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        sentence = posted_data["sentence"]

        correct_password = verify_password(username, password)

        if not correct_password:
            return_json = {
                "status": 302,
                "message": "Password is not correct"
            }
            return jsonify(return_json)
        
        num_tokens = count_tokens(username)
        if num_tokens <= 0:
            return_json = {
                "status": 301,
                "message": "Not enough tokens for this service (%s tokens left)" % (str(num_tokens))
            }
            return jsonify(return_json)
        
        users.update_one(
            {
                "Username": username
            },
            {
                "$set":
                {
                    "Sentence": sentence,
                    "Tokens": num_tokens - 1
                }
            }
        )

        return_json = {
            "status": 200,
            "message": "Sentence saved succesfully"
        }

        return jsonify(return_json)
    
class GetSentence(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        correct_password = verify_password(username, password)

        if not correct_password:
            return_json = {
                "status": 302,
                "message": "Password is not correct"
            }
            return jsonify(return_json)
        
        num_tokens = count_tokens(username)
        if num_tokens <= 0:
            return_json = {
                "status": 301,
                "message": "Not enough tokens for this service (%s tokens left)" % (str(num_tokens))
            }
            return jsonify(return_json)
        
        users.update_one(
            {
                "Username": username
            },
            {
                "$set":
                {
                    "Tokens": num_tokens - 1
                }
            }
        )
        
        sentence = users.find(
        {
            "Username": username
        }
        )[0]["Sentence"]

        return_json = {
            "status": 200,
            "sentence": sentence
        }

        return jsonify(return_json)
    
class GetTokens(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        correct_password = verify_password(username, password)

        if not correct_password:
            return_json = {
                "status": 302,
                "message": "Password is not correct"
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
    
class SetTokens(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        tokens = posted_data["tokens"]

        correct_password = verify_password(username, password)

        if not correct_password:
            return_json = {
                "status": 302,
                "message": "Password is not correct"
            }
            return jsonify(return_json)
        
        users.update_one(
            {
                "Username": username
            },
            {
                "$set":
                {
                    "Tokens": tokens
                }
            }
        )

        return_json = {
            "status": 200,
            "Tokens updated. Number of tokens available": tokens 
        }

        return jsonify(return_json)
    
api.add_resource(RegisterUser, "/registerUser")
api.add_resource(StoreSentence, "/storeSentence")
api.add_resource(GetSentence, "/getSentence")
api.add_resource(GetTokens, "/getTokens")
api.add_resource(SetTokens, "/setTokens")

if __name__ == "__main__":
    app.run(host='0.0.0.0')