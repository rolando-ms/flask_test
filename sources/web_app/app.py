from flask import Flask, jsonify, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

def check_posted_data(posted_data, function_name):
    if function_name == "add" or function_name == "subtract" or \
    function_name == "multiply":
        if "x" not in posted_data or "y" not in posted_data:
            return 301
        else:
            return 200
    elif function_name == "divide":
        if "x" not in posted_data or "y" not in posted_data:
            return 301
        elif int(posted_data["y"]) == 0:
            return 302
        else:
            return 200


class Add(Resource):
    def post(self):
        # Resource requested as post
        
        posted_data = request.get_json()
        
        status_code = check_posted_data(posted_data, "add")

        if status_code != 200:
            return_map = \
            {
                'Message' : "An Error Occurred",
                'Status Code' : status_code
            }
            return jsonify(return_map)
        x = posted_data["x"]
        y = posted_data["y"]
        x = int(x)
        y = int(y)
        ret = x + y
        return_map = \
        {
            'Sum' : ret,
            'Status Code' : 200
        }
        return jsonify(return_map)

class Subtract(Resource):
    def post(self):
        # Resource requested as post
        
        posted_data = request.get_json()
        
        status_code = check_posted_data(posted_data, "subtract")

        if status_code != 200:
            return_map = \
            {
                'Message' : "An Error Occurred",
                'Status Code' : status_code
            }
            return jsonify(return_map)
        x = posted_data["x"]
        y = posted_data["y"]
        x = int(x)
        y = int(y)
        ret = x - y
        return_map = \
        {
            'Sum' : ret,
            'Status Code' : 200
        }
        return jsonify(return_map)

class Multiply(Resource):
    def post(self):
        # Resource requested as post
        
        posted_data = request.get_json()
        
        status_code = check_posted_data(posted_data, "multiply")

        if status_code != 200:
            return_map = \
            {
                'Message' : "An Error Occurred",
                'Status Code' : status_code
            }
            return jsonify(return_map)
        x = posted_data["x"]
        y = posted_data["y"]
        x = int(x)
        y = int(y)
        ret = x * y
        return_map = \
        {
            'Sum' : ret,
            'Status Code' : 200
        }
        return jsonify(return_map)

class Divide(Resource):
    def post(self):
        # Resource requested as post
        
        posted_data = request.get_json()
        
        status_code = check_posted_data(posted_data, "divide")

        if status_code != 200:
            return_map = \
            {
                'Message' : "An Error Occurred",
                'Status Code' : status_code
            }
            return jsonify(return_map)
        x = posted_data["x"]
        y = posted_data["y"]
        x = int(x)
        y = int(y)
        ret = (x * 1.0) / (y * 1.0)
        return_map = \
        {
            'Sum' : ret,
            'Status Code' : 200
        }
        return jsonify(return_map)

api.add_resource(Add, "/add")
api.add_resource(Subtract, "/subtract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/divide")

@app.route('/')
def hello_world():
    return "Hello World"

if __name__ == "__main__":
    app.run(host='0.0.0.0')