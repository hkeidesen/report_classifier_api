import pyodbc
from params import conn_string
from flask import jsonify

def upload_to_db(data):
    cnxn = pyodbc.connect(conn_string)
    cursor = cnxn.cursor()
    result = cursor.execute("SELECT TOP 0.01 percent * FROM dbo.Avvik_og_forbedringspunkt;")
    items =[]
    for row in result:
        items.append({'id':row[1]})
    return("Data writte succesfully")

