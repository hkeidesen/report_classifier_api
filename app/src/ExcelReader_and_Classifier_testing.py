import xlrd
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import cross_val_score

from sklearn.svm import LinearSVC
from sklearn.naive_bayes import ComplementNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import GridSearchCV

loc = (r'C:\Users\HANNORU\Downloads\Tilsynsdatabase.xlsx')

# open Excel sheet, indexing it. Upon reviewing the code it is revealed that xlrd is rather slow. 
# Might want to try sxl (https://pypi.org/project/sxl/), which only reads stuff into memory as needed, as opposed to xlrd, that throws the entire workbook into memory.
# Poor memory never deserved such a beating. 
wb = xlrd.open_workbook(loc) 
sheet = wb.sheet_by_index(0) 

## Extract columns that we would like to work with. It is advised to open the "loc-file" (see line 25) to understand the what is being done here.
# This creates a list of the neccessary values
MyList = [sheet.col_values(sheet.row_values(16).index('Myndighet'))[17:],
          sheet.col_values(sheet.row_values(16).index('Begrunnet tekst'))[17:],
          sheet.col_values(sheet.row_values(16).index('Kategori'))[17:],
          sheet.col_values(sheet.row_values(16).index('Avvik / Forb.pnkt'))[17:],
          sheet.col_values(sheet.row_values(16).index('Regelhenvisning'))[17:]]

## Make a dataframe out of these said columns
df = pd.DataFrame(list(zip(MyList[0],MyList[1],MyList[2],MyList[3],MyList[4])),
                  columns = ['Myndighet','Begrunnet tekst','Kategori','Avvik / Forb.pnkt','Regelhenvisning'])


#All df-modifications are to tranpose the df to a common structure

## Make lowercase, to avoid A/a differences, and remove eventual white spaces 
df.loc[:,'Kategori'] = df['Kategori'].str.lower()
df.loc[:,'Kategori'] = df['Kategori'].str.replace(" ", "")

## Remove entries with no avvik/forbedringer, as we are not training nor testing on those
df = df.loc[(df['Kategori'] != 'ingenavvik/forbedring/anmerkning')]
df = df.loc[df['Begrunnet tekst'] != ""]
df = df.loc[df['Kategori'] != ""]

## Clean up the data frames, df2 combining Begrunnet tekst with Regelhenvisning
df2 = df.assign(Combo = df['Regelhenvisning'] + " " + df['Begrunnet tekst'])
df2 = df2.drop(['Myndighet'], axis=1)
df2 = df2.drop(['Avvik / Forb.pnkt'], axis=1)
df2 = df2.drop(['Begrunnet tekst'], axis=1)
df2 = df2.drop(['Regelhenvisning'], axis=1)
df = df.drop(['Regelhenvisning'], axis=1)
df = df.drop(['Myndighet'], axis=1)
df = df.drop(['Avvik / Forb.pnkt'], axis=1)

## Define set of norwegian stopwords
stopwordSet = set(stopwords.words('norwegian'))
## if you get a nltk and stopwords fail error (https://stackoverflow.com/questions/26693736/nltk-and-stopwords-fail-lookuperror):
## type in a Python console:
## import nltk
## nltk.download()
## press download

## Try a Norwegian stemmer.
from nltk import stem
stemmer = stem.snowball.NorwegianStemmer(ignore_stopwords = True)

## Function for cleaning up the text string
def clean_text(text):
    
    ## Remove eventual characters [\], ['] and ["]
    text = re.sub(r"\\", "", text)    
    text = re.sub(r"\'", "", text)    
    text = re.sub(r"\"", "", text)    
    
    ## Convert text to lowercase
    text = text.strip().lower()
    
    ## Replace punctuation characters with spaces
    filters='!"\'#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n»«°º˚–…•”“'
    translate_dict = dict((c, " ") for c in filters)
    translate_map = str.maketrans(translate_dict)
    text = text.translate(translate_map)
    
    ## Remove whitespace between § and the following number 
    text = text.replace("§ ","§")
    
    ## Stem the words in the text
    text = text.split()
    text = " ".join([stemmer.stem(word) for word in text])
    
    return text
#print(df)