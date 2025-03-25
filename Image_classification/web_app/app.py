from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import numpy as np
import requests

from keras.applications import InceptionV3
from keras.applications.inception_v3 import preprocess_input
from keras.applications import imagenet_utils
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
from io import BytesIO

app = Flask(__name__)
api = Api(app)

# Database
client = MongoClient("mongodb://db:27017")
db = client.ImageClassificationDB
users = db["Users"]
admins = db["Admins"]

# Loading pretrained model
pretrained_model = InceptionV3(weights="imagenet")

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
        
        tokens = count_tokens(username)

        return build_json_response(200, "%s Tokens available"%(str(tokens)))
    
class ClassifyImg(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        img_url = posted_data["img_url"]

        if not user_exist(username):
            return build_json_response(301, "Invalid username")
        
        correct_password = verify_password(username, password)

        if not correct_password:
            return build_json_response(302, "Invalid password")
        
        tokens = count_tokens(username)

        if tokens <= 0:
            return build_json_response(303, "Not enough tokens")
        
        if not img_url:
            return build_json_response(400, "no URL provided")
        
        # Load Image from URL
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content))

        # Preprocess image for model prediction
        img = img.resize((299,299))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Model prediction
        predictions = pretrained_model.predict(img_array)
        decoded_predictions = imagenet_utils.decode_predictions(predictions, top=5)

        return_json = {}
        for prediction in decoded_predictions[0]:
            return_json[prediction[1]] = float(prediction[2]*100)
        
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


api.add_resource(RegisterUser, "/registerUser")
api.add_resource(RegisterAdmin, "/registerAdmin")
api.add_resource(RefillTokens, "/refillTokens")
api.add_resource(GetTokens, "/getTokens")
api.add_resource(ClassifyImg, "/classifyImg")

if __name__ == "__main__":
    app.run(host='0.0.0.0')