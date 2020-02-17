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
from setup import config

#from sklearn.svm import SVC
#from sklearn.naive_bayes import ComplementNB
#from sklearn.linear_model import LogisticRegression
#from sklearn.ensemble import RandomForestClassifier

#from sklearn.model_selection import GridSearchCV

# Access key to data container:
# https://ne1dnvglpstgcus0032ypop9.blob.core.windows.net/tilsynsdatabaseea805581-661f-47a4-9526-31cf9c22d5ce?sv=2018-03-28&sr=c&sig=R1PUNotr51ee%2BVwq21zBQP69SXRJ7dsAQciYEUSLbO8%3D&st=2020-01-27T14%3A31%3A52Z&se=2020-07-25T15%3A30%3A29Z&sp=rwdl

#currently just running it locally. Need to figure out how to access the container from the web
#loc = (r'C:\Users\HANNORU\Downloads\Tilsynsdatabase.xlsx')
loc = (r'C:\Users\HANNORU\Downloads\Merget med linker_v18.xlsx')
"""
What is below here is really all you need to train a model for categorization. You could either save the model as a pickle,
then bring it up in the other script when predicting new category, or the whole model could be trained in the overall script file.
"""
## Open excel sheet, index it
wb = xlrd.open_workbook(loc) 
sheet = wb.sheet_by_index(0)

## Extract columns that we would like to work with
MyList = [sheet.col_values(sheet.row_values(16).index('Myndighet'))[17:],
          sheet.col_values(sheet.row_values(16).index('Begrunnet tekst'))[17:],
          sheet.col_values(sheet.row_values(16).index('Kategori'))[17:],
          sheet.col_values(sheet.row_values(16).index('Avvik / Forb.pnkt'))[17:],
          sheet.col_values(sheet.row_values(16).index('Regelhenvisning'))[17:]]

## Make a dataframe out of these said columns
df = pd.DataFrame(list(zip(MyList[0],MyList[1],MyList[2],MyList[3],MyList[4])),
                  columns = ['Myndighet','Begrunnet tekst','Kategori','Avvik / Forb.pnkt','Regelhenvisning'])


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

## Split into train and test set, Regelhenvisning included
X_train, X_test, y_train, y_test = train_test_split(df2['Combo'], 
                                                    df2['Kategori'],
                                                    test_size = 0.2,
                                                    random_state = 42)

#TFIDF_vectorizer_with_ngram = TfidfVectorizer(preprocessor=clean_text, analyzer = 'char_wb', stop_words = stopwordSet, ngram_range=(1, 3))
TFIDF_vectorizer_with_ngram = TfidfVectorizer(preprocessor=clean_text, analyzer = 'char_wb', stop_words = stopwordSet, ngram_range=(4, 4))
X_train_TFIDF_ngram = TFIDF_vectorizer_with_ngram.fit_transform(X_train)
X_test_TFIDF_ngram = TFIDF_vectorizer_with_ngram.transform(X_test)

model = LinearSVC()

model.fit(X_train_TFIDF_ngram, y_train)
y_pred = model.predict(X_test_TFIDF_ngram)


###Saving the trained model to pickle, so that it is possible to utilize the resutlts elsewere

import pickle
filename = "model.pickle"
trained_model = pickle.dumps(model)
pickle.loads(trained_model)
pickle.dump(model, open("prediction.pickle", 'wb'))

acc = accuracy_score(y_test, y_pred)

print("Accuracy on classification, with ngram: {:.2f}".format(acc))

from sklearn.metrics import precision_recall_fscore_support
precision_recall_fscore_support(y_test, y_pred, average='weighted')


conf_mat = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(9,7))
sns.heatmap(conf_mat, annot=True, fmt='d', xticklabels=np.unique(df['Kategori']), yticklabels=np.unique(df['Kategori']))
plt.ylabel('Truth')
plt.xlabel('Predicted')

#plt.show()

