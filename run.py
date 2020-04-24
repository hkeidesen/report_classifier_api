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
    data = flask.request.get_json()

    #accessing the part after ?id= in the URL
    report_url = flask.request.args.get('id')
    print("The POST request is: ",flask.request.args.get('id'))

    return jsonify(classifier.main(report_url)), status_code, 


@app.route('/testDB')
def testdb():
    #configure db
    import pyodbc
    from params import conn_string
    cnxn = pyodbc.connect(conn_string)
    cursor = cnxn.cursor()
    result = cursor.execute("SELECT TOP 0.01 percent * FROM dbo.Avvik_og_forbedringspunkt;")
    items =[]
    for row in result:
        items.append({'id':row[1]})
    import json
    return jsonify({'items':items})


if __name__ == '__main__':
    app.run(debug=True, port=5000)