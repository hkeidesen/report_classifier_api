import test
import classifier
import flask
from flask_restful import Resource, Api
import json
from flask import jsonify

import urllib.parse

app = flask.Flask(__name__)
api = Api(app)


@app.route("/health", methods=["GET"])
def health():
    return ("200 OK")

@app.route("/classification", methods=["POST"])    
def classification():
    status_code = 200
    #data = flask.request.get_json()
    
    #accessing the part after ?id= in the URL
    report_url = flask.request.args.get('id')
    print("The POST request is: ", flask.request.args.get('id'))

    return jsonify(classifier.main(report_url)), status_code, 


@app.route('/testDB', methods=["POST"])
def testdb():
    #configure db
    return jsonify(classifier.main("/2019/conocophillips-ekofisk-stimuleringsoperasjon-fra-fartoy/")) 


if __name__ == '__main__':
    app.run(debug=True, port=5000)