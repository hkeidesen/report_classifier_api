import test
import classifier
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class sumNumbers(Resource):
    def get(self):
        return {'data' : classifier.main()}

api.add_resource(sumNumbers, '/classification/')

if __name__ == '__main__':
    app.run(debug=True, port=5050)