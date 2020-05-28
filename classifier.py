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

from app.src.Installation_Type_Dictionary import Installations

class Report:

    def __init__(self, year, date, activity_number, title, taskleader,
                 participants_in_revision, count_participants, url, installation_name, installation_type, myndighet, number_of_participants, total_number_of_findings, operator):
        #self.authority = "PTIL"'
        self.year = year
        self.date = date
        self.activity_number = activity_number
        self.title = title
        self.taskleader = taskleader
        self.participants_in_revision = participants_in_revision
        self.count_participants = count_participants
        self.url = url
        self.installation_name = installation_name
        self.installation_type = installation_type

        self.deviation_list = []
        self.improvement_list = []

        self.myndighet = myndighet
        self.number_of_participants = number_of_participants
        self.total_number_of_findings = total_number_of_findings
        self.operator = operator

class Deviation:

    def __init__(self, title, description, regulations, dev_cntr):
        self.finding_type = "Avvik"
        self.title = title
        self.description = description
        self.regulations = regulations
        self.dev_cntr = dev_cntr
        #self.cathegory = cathegory

class Improvementpoint:

    def __init__(self, title, description, regulations, imp_cntr):
        self.finding_type = "Forbedringspunkt"
        self.title = title
        self.description = description
        self.regulations = regulations
        self.imp_cntr = imp_cntr
        #self.cathegory = cathegory

## Make soup of webpage
def make_soup(url):

    res = requests.get(url)
    soup = BeautifulSoup(res.text,"lxml")

    return soup

## Function for searching a report-webpage on PTIL (as 'soup') and extracting the url for the pdf





def find_pdf_url_on_webpage(soup):
    report_link = "/"

    ## Find link to the report. In case of two 'similar' tilsynsrapporter, it will always choose the last report
    ## It will distinguish between tilsynrapport and other pdfs, ie. brev
    links = soup.findAll('a', attrs={"class":"d-flex w-100 justify-content-between"})
    #print(links,'\n')
    for link in links:
        pdf_types = link.findAll('h3')
        for pdf_type in pdf_types:
            tmp = pdf_type.get_text()
            # print("the temp is:", tmp, '\n')
            print("Getting the report link...")
            if "Rapport" in tmp or "rapport" in tmp or "tilsynsrapport" in tmp or "Tilsynsrapport" in tmp:
                report_link = link.get('href')
                print("The report link has been obtained. Proceeding")
            else:
                print("There was an error getting the report link. Are you sure that the provided link contains a PDF-file?")
                print(report_link)
            return report_link
    return "https://www.ptil.no/" + report_link
## Function for opening, reading and converting a pdf url to txt format



def get_all_pdf_link_on_url(pages):
    url = "https://www.ptil.no/"
    url_reports_pages = "https://www.ptil.no/tilsyn/tilsynsrapporter/?p="
    url_to_reports = []
    url = pages
    response = requests.get(url) #need headers?
    soup = BeautifulSoup(response.content, "html.parser")

    if response.status_code == 200:
        for link in soup.find_all("a", {"class":"pcard"}, href=True):
            try:
                url_to_reports.append(link['href'])

            except AttributeError:
                print("An AttributeError error occured. Proceeding")
                pass
    else:
            print("An error has occured, and it is most likely because the Internt connection")
    #print(url_to_reports)
    return url_to_reports

def find_url_to_all_reportpages():
    # Needed for the header in request
    headers = {"User-Agent": "Mozilla/5.0"}
    pages = []
    url_reports = []

    # i=0 telles the for-loop to start looking at page 0 in the URL that is being given in the for-loop
    i=0
    end_page = 100
    #this for-loop looks for the pagination in the url, and uses BeautifulSoup to retrieve the page numbers
    # the range(1,10) can be increased to include all pages, or just the pages that are of interest.
    print("Getting the number of pages in the URL. This will take some time based on the Internet connection")
    for i in range(1,end_page):

        #the URL that is being used to retrieve all paginated pages
        url = "https://www.ptil.no/tilsyn/tilsynsrapporter/?p="

        #as can be seen in the URL above, no page number is provided, hence "/?p=". The page number is being assigned in the line below
        url = url + str(i)
        #the URL from the previous step is used to .get all the content on the website
        response = requests.get(url, headers=headers)
        #using the built-in html parser, the content from the response is translated to text?
        soup = BeautifulSoup(response.content,"html.parser")
            #based on the webpage structure, it can be found that the currect pagination page can be found in the class "page-item active" and "li".
            #This is then transformed to .text.

            # Ensuring that if the response code is 200, else it will fail
        if response.status_code == 200:
            #try: except: to catch the error that will be presenting if soup_page_number = soup.find().text fails
            try:
                soup_page_number = soup.find("li", {"class":"page-item active"}).text

                #translated to integer
                soup_page_number = int(soup_page_number) # det er dette som tilsvarer i?

                #print("Appending the current page,", i ,", to the list \"pages\"")
                #pages.append(soup_page_number)

                #increases i
                i+=1
            #in this case, an AttributeError will be caught in soup_page_number. Most likely it is becasue there are no more pages to load.
            # An AttributeError is risen when there are no more pages in the pagination to load
            except AttributeError:
                print("End of page reached. Last page is", pages[-1])
                #breaking out of the for-loop when there are no more pages to load.
                break
        else:
            print("An error with the URL casued the program to crash. It can either be the website or the the connection to the website. The server responded with error code",
                    response.status_code)
            break
        #url_reports.append(find_pdf_url_on_webpage(url))
        print("The URL we are visiting now is", url)

        #callinf the function to retrieve all report-url on each page
        get_all_pdf_link_on_url(url)

    return pages
#find_url_to_all_reportpages()



def convert_pdf_to_txt(pdf_url):

    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    import urllib
    import http
    from datetime import datetime

    try:
        f = urlopen(pdf_url).read()

    except (http.client.IncompleteRead) as e:
        f = e.partial
        print(datetime.now())
    #f = urlopen(pdf_url).read()

    # f = requestObj
    fp = BytesIO(f)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    pdf_as_text = retstr.getvalue()
    #print(pdf_as_text)

    fp.close()
    device.close()
    retstr.close()

    #print(pdf_as_text)
    return pdf_as_text

## Function for finding participants in revision team
def find_participants_in_revision(idx, report_text):

    idx += -1

    while report_text[idx] != " " and report_text[idx] != "":
        participants_in_revision = ""
        participants_in_revision += report_text[idx]
        idx += 1
        # print("report_text[",idx,"]= ", report_text[idx])
    print("The parcticipants were: ", participants_in_revision)
    if "," not in participants_in_revision: # This check is to remedy the case when the there are too many participants to fit all of them in one line, casue that case will only return the last entry.
        print("There are too few participants...")
        participants_in_revision = ""
        participants_in_revision = report_text[20] + report_text[21] # these numbers are identificed by running print("report_text[",idx,"]= ", report_text[idx])
    return participants_in_revision

## Function for finding task leader
def find_taskleader(idx, report_text):

    task_leader = ""
    idx += 1
    task_leader += report_text[idx]

    return task_leader

## Function for finding report title
def find_report_title(idx, report_text):
    
    
    idx += -1 # Trying with idx += -1

    while report_text[idx] != " " and report_text[idx] != "":
        report_title = ""
        report_title += report_text[idx]
        idx += 1
    #print("The report title is: " + report_title)
        if report_title[0].isupper(): # A check to see if the title has been cut-off. See comment below on how this was fixed (a valid title would have an upper-case as first letter)
            continue
        else:
            report_title = ""
            # print("The IDX is", idx)
            # The reason the report_text[9] and [10] are used is because if the title of the report is on two lines of code, the code will only report the last line of the title.
            # These sepcific numbers have been found by printing the idx, identify what idx gives the report title, and then assigning these numbers manually. If the idx changes (where idx is initially assigned above),
            # it is possible that the two values needs changig also.
            report_title = report_text[9] + report_text[10] # If, for some reason, the index 9 and 10 needs to change in the future, execute print("report_text[",idx,"]= ", report_text[idx]) 
    return report_title

#finding myndighet
def find_myndighet(idx, report_text):
    idx += 1
    myndighet = ""
    myndighet += report_text[idx]
    if myndighet == "":    # As of right now, there is no obvious indication in the report that the "myndighet" is PTIL, however, it is a certainty that there can be no other governing agent other than PTILs report that will be classified by this script
        myndighet = "PTIL" # Therefore, the "myndighet" is pragramatically assigned with PTIL
    return myndighet

## Function for finding activity number
def find_activity_number(idx, report_text):

    idx += 1
    activity_number = ""
    activity_number += report_text[idx]

    return activity_number

## Function for finding date of the report
def find_date(idx, report_text):

    idx += 1
    report_date = ""

    report_date += report_text[idx]

    return report_date

## Function for finding the introduction text
def find_introduction(idx, report_text):

    idx += 1
    report_intro = ""

    while not re.compile('2\s+').match(report_text[idx]):

        report_intro += report_text[idx]
        idx +=1

    return report_intro

## Function for finding installation type
def find_installation_and_type(report_intro):

    for key in Installations:
        if key in report_intro:
            installation_type = Installations.get(key)
            installation_name = key

            found = True
            break
    #print("installation_name: ", installation_name, "installation_type: ",installation_type)
    return installation_name, installation_type

## Function for looping through pdf and searching for keywords
def find_relevant_info_in_pdf(report_as_a_list_of_sentences):
   
    for idx, line in enumerate(report_as_a_list_of_sentences):
        #print(idx, line)
        if ("Deltakere i revisjonslaget" in line) or ("Deltakarar i revisjonslaget" in line):
            participants_in_revision = find_participants_in_revision(idx, report_as_a_list_of_sentences)
            # print("trying to find the participants in the team.")
            number_of_participants = participants_in_revision.count(",") + 1 # the number of commas in participants_in_revision + 1 indicates the number of participants 
        if ("Oppgaveleder" in line) or ("Oppgåveleiar" in line):
            taskleader = find_taskleader(idx, report_as_a_list_of_sentences)

        if "Aktivitetsnummer" in line:
            activity_number = find_activity_number(idx, report_as_a_list_of_sentences)

        if "Dato" in line:
            date = find_date(idx, report_as_a_list_of_sentences)
            year = date[-5:] #returns the years from the date (the structre of the date here is very important!!!!)
            print(date)
            print(year)
        if "Rapporttittel" in line:
            title = find_report_title(idx, report_as_a_list_of_sentences)
            if title[0].isupper(): # This code block can be deleted, as it is possible that the title will no longer be cut off
                continue
            else:
                print("The title has been cut off.")

        if bool(re.compile('1\s+').match(line)):
            intro = find_introduction(idx, report_as_a_list_of_sentences)
            installation_name, installation_type = find_installation_and_type(intro)

        if "Myndighet" in line:
            myndighet = find_myndighet(idx, report_as_a_list_of_sentences)
        else:
            myndighet = ""

        # import csv
        # with open("report_as_sentence.csv", 'w', newline='', encoding='utf-8') as csvfile:
        #     csv_writer = csv.writer(csvfile)
        #     csv_writer.writerow(report_as_a_list_of_sentences)

        total_number_of_findings = 0
        operator = ""

    return participants_in_revision, taskleader, activity_number, date, title, installation_name, installation_type, myndighet, number_of_participants, total_number_of_findings, operator

## Function for finding the title of a deviation, "avvik"
def find_deviation_title(deviation):

    dev_title = deviation.h3.get_text()

    return dev_title

def find_deviation_text(deviation):

    dev_text = deviation.p.get_text()

    return dev_text

## Function for finding the regulations related to a deviation
def find_deviation_regulations(deviation):

    dev_regulations = deviation.find_all('a')
    dev_regulation_list = ""

    for dev_regulation in dev_regulations:
        dev_regulation_list += dev_regulation.get_text()
        dev_regulation_list += "\n"

    return dev_regulation_list

## Function for finding the title of an improvement point, "forbedringspunkt"
def find_improvement_title(improvement):

    imp_title = improvement.h3.get_text()

    return imp_title

## Function for finding the 'reason' of an improvement point
def find_improvement_text(improvement):

    imp_text = improvement.p.get_text()

    return imp_text

## Function for finding the regulations related to an improvement points
def find_improvement_regulations(improvement):

    imp_regulations = improvement.find_all('a')
    imp_regulation_list = ""

    for imp_regulation in imp_regulations:
        imp_regulation_list += imp_regulation.get_text()
        imp_regulation_list += "\n"

    return imp_regulation_list

## Function for extracting all the deviations and improvement points from the webpage of a report
def find_relevant_info_on_web(webpage_as_soup, report):

    deviations = webpage_as_soup.find_all('div', attrs={"class":"tab-pane","id":re.compile('deviation.*')})
    dev_cntr = 0

    #print("Here are the deviations:")
    #print("")
    for deviation in deviations:
        dev_title = find_deviation_title(deviation)
        dev_text = find_deviation_text(deviation)
        dev_regulations = find_deviation_regulations(deviation)
        dev_cntr += 1

        if dev_title == "":
            dev_cntr = 0
            return dev_cntr


        new_deviation = Deviation(dev_title, dev_text, dev_regulations, dev_cntr)

        report.deviation_list.append(new_deviation)

        #report.deviation_list.append(dev_cntr)

    #print("Number of deviations found: ", dev_cntr)

    improvements = webpage_as_soup.find_all('div', attrs={"class":"tab-pane","id":re.compile('improvementPoint.*')})
    imp_cntr = 0
    #print("Here are the improvement points:")
    #print("")
    for improvement in improvements:
        imp_title = find_improvement_title(improvement)
        imp_text = find_improvement_text(improvement)
        imp_regulations = find_improvement_regulations(improvement)
        imp_cntr += 1
        new_improvement = Improvementpoint(imp_title, imp_text, imp_regulations, imp_cntr)
        #print("Improvement point title:")
        #print(new_improvement.title)
        #print("")
        #print("Improvement point explanatory text:")
        #print(new_improvement.description)
        #print("")
        #print("All regulations:")
        #print(new_improvement.regulations)
        #print("----")

        report.improvement_list.append(new_improvement)

        #print("Number of improvement points found: ", imp_cntr)
    return
    #print("")



def main(report_url):
    print("Running main()")
    ## INSERT HERE:Function() for going through 'https://www.ptil.no/tilsyn/tilsynsrapporter//GetData?pageindex=0&pagesize=10000'
    ## -webpage, and making a list of all the urls for new reports that are not in the excel database yet

    ## list_of_webpage_urls_for_reports = []

    ## Make list for all the reports
    report_list = []

    ## for-loop through all the reports in the list
        ## Everything here should be in the for-loop

        ## At every iteration, we extract the pdf url, corresponding to the webpage url


    # Kjørere script for å hente alle rapportene
    # find_url_to_all_reportpages()
    #pages = pages.find_url_to_all_reportpages()

    #test_url = "https://www.ptil.no/tilsyn/tilsynsrapporter/2019/conocophillips-ekofisk-stimuleringsoperasjon-fra-fartoy/"
    #url_to_report = test_url


    """
    There has been some kind of restructuring in PTILs website, and the corrent URL reading code
    does not work correctly. This needs to be fixed ASAP!
    ######url = "https://www.ptil.no/tilsyn/tilsynsrapporter/" +  report_url # THIS URL ONLY WORKS ONE SOME REPORTS!!!
    """
    url = report_url
    print("The url is: " + url)

    url_soup = make_soup(url)

    pdf_link = find_pdf_url_on_webpage(url_soup)
    pdf_link = "https://www.ptil.no/" + pdf_link

    print("The report that is being processed now can be found at:", pdf_link)

        ## Get pdf as txt
    pdfText = convert_pdf_to_txt(pdf_link)
    # print(pdfText)

        ## Split on "\n"
    pdf_as_list_of_words = pdfText.split("\n")  
    # pdf_as_list_of_words = pdfText
    # print('pdf_as_list_of_words', pdf_as_list_of_words)
        ## Looping through report and searching for keywords (returned as string)
    participants_in_revision, taskleader, activity_number, report_date, report_title, installation_name, installation_type, myndighet, number_of_participants, total_number_of_findings, operator = find_relevant_info_in_pdf(pdf_as_list_of_words)


        ## Make a report object
    report = Report(report_date.strip(' ')[-4:], report_date, activity_number, report_title, taskleader,
                   participants_in_revision, participants_in_revision.count(",") + participants_in_revision.count(" og ") + 1,
                   pdf_link, installation_name, installation_type, myndighet, number_of_participants, total_number_of_findings, operator)

        ## Find deviations and improvement points, make objects then add them to the report
    find_relevant_info_on_web(url_soup, report)
        ## INSERT HERE: Probably a function that takes in all the deviations, improvement points, as well as a ML model of
        ## choice, then predicts the cathegories. Maybe require human assistance if classification % is less than a threshold

        ## Append new finding to list
    #   report_list.append(report)


    #print("Successfully written database")


    # ## Printing the extracted information from the report ## MAYBE THIS IS NOT NEEDED ANYMORE.
    # print("URL for pdf:")
    # print(report.url)
    # report_list.append("Report URL:")
    # report_list.append(report.url)
    # report_list.append("activity_number:")
    # report_list.append(report.activity_number)
    # report_list.append(report.title)
    # report_list.append(report.date)
    # report_list.append(report.taskleader)
    # report_list.append(report.participants_in_revision)
    # report_list.append(report.installation_name)
    # report_list.append(report.installation_type)

    #Create a dataframe that will store the resutls from the report.deviation_list.
    import pandas as pd

    """
    IMPORTANT!
    Since the results are returned as a pandas dataframe in main(), when adding more entries to the dataframe, changes in run.py are also needed to have a successfull implementation 
    of the new dataframe entries. This is neccessary to perform as there is some post processeing of the resutls in run.py to ensure correct JSON-formatting in run.py. 
    Most likely the only change is to ensure that the column in the dataframes in this file matches the corresponding column in run.py.
    """

    #the columns that will be used in the dataframe. 
    deviation_columns = ['Avviksnummer','Tittel på avvik','Avvikets beskrivende tekst','Alle regelhenvisninger (avvik)']
    
    #construct the dataframe object
    df_deviation_list = pd.DataFrame(columns=deviation_columns)
    
    # The following for-loop will first append the results to a list, before it the same results is appended to the dataframe
    # This is currently slow and unwise, and will be fixed in a future release. 
    # TODO: remove write to list, and only focus on the dataframe.
    for test_dev in report.deviation_list:        
        # report_list.append("Totalt antall avvik:")
        # report_list.append(test_dev.dev_cntr)
        df_deviation_list = df_deviation_list.append({'Avviksnummer' : test_dev.dev_cntr}, ignore_index=True)
        # report_list.append("Tittel på avvik:")
        # report_list.append(test_dev.title)        
        df_deviation_list = df_deviation_list.append({'Tittel på avvik' : test_dev.title}, ignore_index=True)
        # report_list.append("Avvikets beskrivende tekst:")
        # report_list.append(test_dev.description)
        df_deviation_list = df_deviation_list.append({'Avvikets beskrivende tekst' : test_dev.description}, ignore_index=True)
        # report_list.append("Alle regelhenvisninger:")
        # report_list.append(test_dev.regulations)
        df_deviation_list = df_deviation_list.append({'Alle regelhenvisninger (avvik)' : test_dev.regulations}, ignore_index=True)

        if len(df_deviation_list.Avviksnummer.value_counts()) < 0: # a rule that check if there are no deivations. Something needs to be retured in the df, just to make it clearer for the user
            df_deviation_list = df_deviation_list.append({'Avviksnummer' : "N/A"}, ignore_index=True)
            # report_list.append("Tittel på avvik:")
            # report_list.append(test_dev.title)        
            df_deviation_list = df_deviation_list.append({'Tittel på avvik' : "N/A"}, ignore_index=True)
            # report_list.append("Avvikets beskrivende tekst:")
            # report_list.append(test_dev.description)
            df_deviation_list = df_deviation_list.append({'Avvikets beskrivende tekst' : "Ingen avvik funnet"}, ignore_index=True)
            # report_list.append("Alle regelhenvisninger:")
            # report_list.append(test_dev.regulations)
            df_deviation_list = df_deviation_list.append({'Alle regelhenvisninger' : "Ingen avvik funnet"}, ignore_index=True)

        """
        Using pandas to transfrom the list to a dataframe. This is easier to work with when
        reading all deviations to the .JSON results.
        """ 
        #df_deviation_list = pd.DataFra
        # me(columns=['Totalt antall avvik', 'Tittel på avvik', 'Avvikets beskrivende tekst','Alle regelhenvisninger'])
    # Cleans up the dataframe, since ignore_index = True, new entries will be appended to the proceeding index, like so:
    
    #     Avviksnummer                                    Tittel på avvik                         Avvikets beskrivende tekst                             Alle regelhenvisninger
    # 0            1.0                                                NaN                                                NaN                                                NaN
    # 1            NaN   Offshorekranene – kranførers sikt til lasteom...                                                NaN                                                NaN
    # 2            NaN                                                NaN  Lasteområder eller deler av disse er ikke utfo...                                                NaN
    # 3            NaN                                                NaN                                                NaN  Innretningsforskriften § 13 - Materialhåndteri...
    #
    # The following code will clean this, so that the "avviksnummer" matches the title, description and regulation at the same index
    df_deviation_list = pd.concat([df_deviation_list[x].dropna().reset_index(drop=True) for x in df_deviation_list], axis=1)
    #print(df_deviation_list)

        

    improvement_columns = ['Forbedringspunkter','Tittel på forbedringspunkt','Forbedringens beskrivende tekst','Alle regelhenvisninger (forbedring)']
    df_improvement_list = pd.DataFrame(columns=improvement_columns)

    for test_imp in report.improvement_list:
        df_improvement_list = df_improvement_list.append({'Forbedringspunkter' : test_imp.imp_cntr}, ignore_index=True)    
        df_improvement_list = df_improvement_list.append({'Tittel på forbedringspunkt' : test_imp.title}, ignore_index=True)     
        df_improvement_list = df_improvement_list.append({'Forbedringens beskrivende tekst' : test_imp.description}, ignore_index=True)       
        df_improvement_list = df_improvement_list.append({'Alle regelhenvisninger (forbedring)' : test_imp.regulations}, ignore_index=True)

        if len(df_improvement_list.Forbedringspunkter.value_counts()) < 0: # a rule that check if there are no deivations. Something needs to be retured in the df, just to make it clearer for the user
            df_improvement_list = df_improvement_list.append({'Forbedringspunkter' : "N/A"}, ignore_index=True)       
            df_improvement_list = df_improvement_list.append({'Tittel på forbedringspunkt' : "N/A"}, ignore_index=True)   
            df_improvement_list = df_improvement_list.append({'Avvikets beskrivende tekst' : "Ingen forbedringspunkt funnet"}, ignore_index=True)       
            df_improvement_list = df_improvement_list.append({'Alle regelhenvisninger' : "Ingen forbedringspunkt funnet"}, ignore_index=True)

    
    df_improvement_list = pd.concat([df_improvement_list[i].dropna().reset_index(drop=True) for i in df_improvement_list], axis=1)
    df_improvement_list = df_improvement_list.dropna()
    # print(df_improvement_list)
    # transforming to pandas dataframe to then it to convert json
    # import pandas as pd
    # df =  pd.DataFrame(report_list)
    # df = df.to_json()
    
    general_report_columns = ['URL','Aktivitetsnummer','Rapporttittel','Dato','Oppgaveleder','Deltakere_i_revisjon', "Myndighet", "Tilsynslaget størrelse", "År"]
    df_general_report_stuff = pd.DataFrame(columns=general_report_columns)
    #print('the report url is (before the df): ', report.url)
    df_general_report_stuff = df_general_report_stuff.append({'URL' : report.url}, ignore_index=True)
    df_general_report_stuff = df_general_report_stuff.append({'Aktivitetsnummer' : report.activity_number}, ignore_index=True)
    df_general_report_stuff = df_general_report_stuff.append({'Rapporttittel' : report.title}, ignore_index=True)
    df_general_report_stuff = df_general_report_stuff.append({'Dato' : report.date}, ignore_index=True)
    df_general_report_stuff = df_general_report_stuff.append({'Oppgaveleder' : report.taskleader}, ignore_index=True)
    df_general_report_stuff = df_general_report_stuff.append({'Deltakere_i_revisjon' : report.participants_in_revision}, ignore_index=True)
    df_general_report_stuff = df_general_report_stuff.append({'Myndighet' : "PTIL"}, ignore_index=True)
    df_general_report_stuff = df_general_report_stuff.append({"Tilsynslaget størrelse": report.number_of_participants}, ignore_index = True)
    df_general_report_stuff = df_general_report_stuff.append({"År": report.year}, ignore_index = True)
    #df_general_report_stuff = 1

    df_general_report_stuff = pd.concat([df_general_report_stuff[i].dropna().reset_index(drop=True) for i in df_general_report_stuff], axis=1)
    df_general_report_stuff = df_general_report_stuff.dropna() 
       

    #Report stuff
    url = json.dumps(report.url)
    activity_number = json.dumps(report.activity_number)
    title = json.dumps(report.title)
    date = json.dumps(report.date)
    taskleader = json.dumps(report.taskleader)
    participants_in_revision = json.dumps(report.participants_in_revision)

    if not report.installation_name:
        installation_name = json.dumps("Navn på installasjon ikke funnet.")
        installation_type = json.dumps(report.installation_type)
    else:
        installation_name = json.dumps(report.installation_name)
        installation_type = json.dumps(report.installation_type)

    myndighet = json.dumps("PTIL")

    #Avvik-stuff'
    # print(df_deviation_list['Avviksnummer'].iloc[-1])
    if df_deviation_list['Avviksnummer'].iloc[-1] == 1:
        if not report.deviation_list: #If the deviation list is empty, it means that there are not deviations found.
            title_on_deviation = json.dumps("Ingen avvik funnet")
            dev_description = json.dumps("Ingen avvik funnet")
            number_of_deviations = json.dumps("0")
            dev_regulations = json.dumps("N/A")
        else:
            title_on_deviation = json.dumps(test_dev.title)
            dev_description = json.dumps(test_dev.description)
            number_of_deviations = json.dumps(test_dev.dev_cntr)
            dev_regulations = json.dumps(test_dev.regulations)
    else:
        print("Using the constructed dataframe to write to JSON")
        #df_json = df_deviation_list.set_index('Avviksnummer').T.to_dict('list')
        # df_json = json.dumps(df_json)
        # df_josn = {}
        # for key, df_gb in df_deviation_list.groupby('Avviksnummer'):
        #     df_josn[(key)] = df_gb.to_dict('records')
        # df_json = json.dumps(df_josn, indent=1)
        # print(df_json)
        
        if not report.deviation_list: #If the deviation list is empty, it means that there are not deviations found.
            title_on_deviation = json.dumps("Ingen avvik funnet")
            dev_description = json.dumps("Ingen avvik funnet")
            number_of_deviations = json.dumps("0")
            dev_regulations = json.dumps("N/A")
        else:
            title_on_deviation = json.dumps(test_dev.title)
            dev_description = json.dumps(test_dev.description)
            number_of_deviations = json.dumps(test_dev.dev_cntr)
            dev_regulations = json.dumps(test_dev.regulations)
    # print("the title of imp is: ", report.__str__)


    #Improvement-stuff
    #print("the title of dev is: ", title_on_deviation)
    if not report.improvement_list: #if improvement list is empty, the below will be executed
        title_on_improvement = json.dumps("Ingen forbedringspunkter funnet")
        imp_description = json.dumps("Ingen forbedringspunkt funnet")
        total_number_of_improvements = json.dumps("0")
        imp_regulations = json.dumps("N/A")
    else:
        total_number_of_improvements = json.dumps(test_imp.imp_cntr)
        title_on_improvement = json.dumps(test_imp.title)
        imp_description = json.dumps(test_imp.description)
        imp_regulations = json.dumps(test_imp.regulations)
    #print("the title of imp is: ", report.improvement_list)

    #Regulations


    #CATEGORY PREDICTION
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer
    # import csv


    #Trained 23.04.2020
    X_train = pd.Series(pd.read_pickle("X_train.pkl")) #X_trin for "category"
    y_train = pd.Series(pd.read_pickle("y_train.pkl")) #y_train fora "category"

    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(X_train)
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    clf = MultinomialNB().fit(X_train_tfidf, y_train)
    clf = MultinomialNB().fit(X_train_tfidf, y_train)
    dev_category_pred_input = dev_description #test_dev.description
    imp_category_pred_input =  imp_description

    #deviation category classification
    if not report.deviation_list: #Bypasses the classification if there are no deviations to classify
        category_deviation = json.dumps("N/A")
    else:
        category_deviation = clf.predict(count_vect.transform([dev_category_pred_input])) # prediction
        category_deviation = category_deviation.tolist() #to list before to json
        category_deviation = ' '.join(category_deviation).replace('[\'','').split() # trying to remove "[ ]" from the results, but no luck so far
        category_deviation = json.dumps(category_deviation) #to json

    #improvement category classiification
    if not report.improvement_list:
        category_improvement = "N/A"
    else:
        category_improvement = clf.predict(count_vect.transform([imp_category_pred_input])) # prediction
        category_improvement = category_improvement.tolist() #to list before to json
        category_improvement = ' '.join(category_improvement).replace('[\'','').split() # trying to remove "[ ]" from the results, but no luck so far
        category_improvement = json.dumps(category_improvement) #to json

    
    df_all_results = df_deviation_list.join(df_improvement_list)
    df_all_results = df_all_results.join(df_general_report_stuff)
    df_all_results.to_excel('results.xlsx')
    # print(df_general_report_stuff)
    return df_all_results