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
    import pandas as pd
    # working URL¨
    # all_results = classifier.main('https://www.ptil.no/tilsyn/tilsynsrapporter/2020/sut-tilsyn-seadrill-west-bollsta-logistikk/') #link ok
    # all_results = classifier.main('https://www.ptil.no/tilsyn/tilsynsrapporter/2020/neptune--gjoa--palegg-etter-tilsyn-med-vedlikeholdsstyring/')
    all_results = classifier.main('https://www.ptil.no/tilsyn/tilsynsrapporter/2020/okea-draugen-materialhandtering-kran-og-loft-arbeid-i-hoyden-og-arbeidsmiljo/')
    # print('the dataframe looks like this: ', all_results)
    #deviations:
    deviation_columns = ['Avviksnummer','Tittel på avvik','Avvikets beskrivende tekst','Alle regelhenvisninger (avvik)'] # this is identical to the columns constructed for the deviations list in classifier.py
    df_deviations = all_results[deviation_columns]
    
    # this is done to remove NaN potential NaN entries
    df_json_deviations = {} # empty dict that will contain the resutls from 'result'
    # print(df_deviations)
    if df_deviations['Avviksnummer'].isnull().values.any():
        print(df_deviations['Avviksnummer'].isnull().values.any())
        print("no entries in dataframe (avvik, run.py)")
    else:
        number_of_deviation_points = int(df_deviations['Avviksnummer'].max())
        df_deviations = df_deviations[0:number_of_deviation_points]

        for index, row in df_deviations.iterrows():
            df_json_deviations[index+1] = dict(row)

    
    # improvements
    improvement_columns = ['Forbedringspunkter','Tittel på forbedringspunkt','Forbedringens beskrivende tekst','Alle regelhenvisninger (forbedring)','Kategori (forbedringer)'] # this is identical to the columns constructed for the improvement list in classifier.py
    df_improvements = all_results[improvement_columns]
    # in order to not carry over all the "NaN"-values that are created during the joining of the returned
    # dataframes in classifier.py, these lines of code is needed.

    # this line finds the number of improvement points, returned as an integer.
    df_json_improvements = {}
    if df_improvements.empty:#df_improvements['Forbedringspunkter'].isnull().values.any():
        print(df_improvements['Forbedringspunkter'].isnull().values.any())
        print("no entries in dataframe (forbedringspunkter, run.py)")
    else:
        number_of_improvements_points = int(df_improvements['Forbedringspunkter'].max())

        # print("the number of imp points are:", number_of_improvements_points)
        # and the result is used to slice the dataframe df_improvements based on the total number of 
        # improvement points
        df_improvements = df_improvements[0:number_of_improvements_points]
        # print(df_improvements)
        # df_improvements = df_improvements.drop_duplicates(keep=False,inplace=True)
        # print(df_improvements) 
         #empty dict that will contain the resutls from 'result'
        for index_improvements, row_improvements in df_improvements.iterrows():
            df_json_improvements[index_improvements+1] = dict(row_improvements)

    # general report stuff
    general_report_columns = ['URL','Aktivitetsnummer','Rapporttittel','Dato','Oppgaveleder','Deltakere_i_revisjon', "Myndighet", "Tilsynslaget størrelse", "År", "Antall funn"]
    df_general = all_results[general_report_columns]
    df_json_general = {}
    for index_general, row_general in df_general.iteritems():
        df_json_general[index_general] = dict(row_general)
    
    # print(cleanNullTerms(df_json_improvements))
    return jsonify(avvik = df_json_deviations,
                forbedringer = df_json_improvements,
                generelt = df_json_general)

if __name__ == '__main__':
    app.run(debug=True, port=5000)