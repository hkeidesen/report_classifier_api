from flask import Flask, jsonify
from flask_restful import Resource, Api
from app.src import ExcelReader_and_Classifier_testing


app = Flask(__name__)
api = Api(app)

class Classifier(Resource):
    def get(self):
        return jsonify(ExcelReader_and_Classifier_testing)
api.add_resource(Classifier, '/')

if __name__ == '__main__':
    app.run(debug=True)
   