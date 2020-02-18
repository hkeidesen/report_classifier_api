import test
import classifier
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

@app.route("/health", methods=["GET"])
def health():
    content = ""
    status_code = 200
    return content, status_code

@app.route("/classification", methods=["POST"])    
def classification():
    status_code = 200
    report_url = "2019/conocophillips-ekofisk-stimuleringsoperasjon-fra-fartoy/"
    return classifier.main(report_url), status_code
#api.add_resource(classification, '/classification/<report_url>')

if __name__ == '__main__':
    app.run(debug=True, port=5000)