import test
import classifier
import flask
from flask_restful import Resource, Api
import json
from flask import jsonify

import urllib.parse

app = flask.Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
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


# @app.route('/testDB', methods=["POST"])
# def testdb():
#     #configure db
    
#     import pyodbc
#     from params import conn_string
#     cnxn = pyodbc.connect(conn_string)
#     cursor = cnxn.cursor()
#     result = cursor.execute("SELECT TOP 0.01 percent * FROM dbo.Avvik_og_forbedringspunkt;")
#     items =[]
#     for row in result:
#         items.append({'id':row[1]})
#     import json
#     return jsonify({'items':items})

@app.route('/testing', methods=["POST"])
def testing():
    # working URL¨
    # all_results = classifier.main('https://www.ptil.no/tilsyn/tilsynsrapporter/2020/sut-tilsyn-seadrill-west-bollsta-logistikk/') #link ok
    all_results = classifier.main('https://www.ptil.no/tilsyn/tilsynsrapporter/2020/neptune--gjoa--palegg-etter-tilsyn-med-vedlikeholdsstyring/')
    # print('the dataframe looks like this: ', all_results)
    #deviations:
    # deviation_columns = ['Avviksnummer','Tittel på avvik','Avvikets beskrivende tekst','Alle regelhenvisninger (avvik)'] # this is identical to the columns constructed for the deviations list in classifier.py
    # df_deviations = all_results[deviation_columns]
    # df_json_deviations = {}    
    # for index, row in df_deviations.iterrows():
    #     df_json_deviations[index+1] = dict(row)

    
    #improvements
    improvement_columns = ['Forbedringspunkter','Tittel på forbedringspunkt','Forbedringens beskrivende tekst','Alle regelhenvisninger (forbedring)'] # this is identical to the columns constructed for the improvement list in classifier.py
    df_improvements = all_results[improvement_columns]
    # print(df_improvements)
    # df_improvements = df_improvements.drop_duplicates(keep=False,inplace=True)
    # print(df_improvements) 
    df_json_improvements = {}
    for index_improvements, row_improvements in df_improvements.iterrows():
        df_json_improvements[index_improvements+1] = dict(row_improvements)

    df_json_improvements_dropna = {}    
    for key, value in df_json_improvements.items():
        if value not in df_json_improvements_dropna.values():
            df_json_improvements_dropna[key] = value

    # return jsonify(flere_avvik=df_json_deviations,  
    #                forbedringer = df_json_improvements)
    return jsonify(forbedringer = df_json_improvements)

if __name__ == '__main__':
    app.run(debug=True, port=5000)