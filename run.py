import test
import classifier
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class classification(Resource):
    def get(self):
        return classifier.main()
api.add_resource(classification, '/classification/')

if __name__ == '__main__':
    app.run(debug=True, port=5050)