from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage

from io import StringIO
from io import BytesIO

import re
import requests
import json 
import openpyxl
from urllib.request import urlopen, Request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from time import sleep

#from Installation_Type_Dictionary import Installations

def get_all_pdf_link_on_url():
    url = "https://www.ptil.no/"
    
    url_reports_pages = "https://www.ptil.no/tilsyn/tilsynsrapporter/?p=" 

    url_to_reports = []

    
    url = "https://www.ptil.no/tilsyn/tilsynsrapporter/?p=6"
    response = requests.get(url) #need headers?
    soup = BeautifulSoup(response.content, "html.parser")

    if response.status_code == 200:
        for link in soup.find_all("a", {"class":"pcard"}, href=True):
            try:
                url_to_reports.append(link['href'])
                    
            except KeyError:
                print("An key error occured. Proceeding")
                pass
    else:
        print("An error has occured, and it is most likely because the Internt connection")

    print(url_to_reports)
    return url_to_reports

get_all_pdf_link_on_url()