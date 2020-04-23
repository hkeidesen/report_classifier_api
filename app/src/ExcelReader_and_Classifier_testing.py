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

# Split into train and test set
#X_train, X_test, y_train, y_test = train_test_split(df['Begrunnet tekst'], df['Kategori'], test_size = 0.2, random_state = 42)

## Split into train and test set, Regelhenvisning included
X_train2, X_test2, y_train2, y_test2 = train_test_split(df2['Combo'], df2['Kategori'], test_size = 0.2, random_state = 42)
df2.head(54)

## Define two Count vectorizers, one with ngram, one without
Cvectorizer_with_ngram = CountVectorizer(preprocessor=clean_text, stop_words = stopwordSet, ngram_range=(1, 2))
Cvectorizer_without_ngram = CountVectorizer(preprocessor=clean_text, stop_words = stopwordSet)

X_train_Cv_ngram = Cvectorizer_with_ngram.fit_transform(X_train2)
X_test_Cv_ngram = Cvectorizer_with_ngram.transform(X_test2)

X_train_Cv_no_ngram = Cvectorizer_without_ngram.fit_transform(X_train2)
X_test_Cv_no_ngram = Cvectorizer_without_ngram.transform(X_test2)

test_model = LinearSVC()
#test_model = ComplementNB()
#test_model = LogisticRegression()
#test_model = RandomForestClassifier(n_estimators=200, random_state=42)

#testX = TFIDF_vectorizer_without_ngram.fit_transform(df['Begrunnet tekst'])
testX = TFIDF_vectorizer_with_ngram.fit_transform(df['Begrunnet tekst'])
#testX = Cvectorizer_with_ngram.fit_transform(df['Begrunnet tekst'])
#testX = Cvectorizer_without_ngram.fit_transform(df['Begrunnet tekst'])

#smt = SMOTE(random_state=42)
#smt = RandomOverSampler(random_state=42)
#X_SMOTE_ngram, y_SMOTE_ngram = smt.fit_sample(testX, df['Kategori'])
#X_SMOTE_no_ngram, y_SMOTE_no_ngram = smt.fit_sample(testX, df['Kategori'])

#accuracy = cross_val_score(test_model, X = testX, y = df['Kategori'], scoring='accuracy', cv = 10)
accuracy = cross_val_score(test_model, X = testX, y = df['Kategori'], scoring='f1_weighted', cv = 10)
#accuracy = cross_val_score(test_model, X = X_SMOTE_ngram, y = y_SMOTE_ngram, scoring='accuracy', cv = 10)
print(accuracy)

print("F1 of Model with Cross Validation is:",accuracy.mean() * 100)

## TFIDF vectorizer proves to be much better than Count vectorizer
X_train3, X_test3, y_train3, y_test3 = train_test_split(df2['Combo'], df2['Kategori'], test_size = 0.2, random_state = 7331)

param_grid = {"C" : [1e-5,1e-4,5e-4,1e-3,5e-3,1e-2,5e-2,1e-1,5e-1,1,5,1e1,5e1,1e2,5e2,1e3,5e3,1e4,5e4,1e5],
              "solver" : ["newton-cg", "lbfgs", "liblinear", "sag"],  
             }

model = LogisticRegression(max_iter = 400)
GSCV = GridSearchCV(model, param_grid=param_grid, scoring = 'accuracy', cv=5)

Count_vectorizer_without_ngram = CountVectorizer(preprocessor=clean_text, stop_words = stopwordSet)
X_train_Count_no_ngram = Count_vectorizer_without_ngram.fit_transform(X_train3)
X_test_Count_no_ngram = Count_vectorizer_without_ngram.transform(X_train3)
'''
TFIDF_vectorizer_with_ngram = TfidfVectorizer(preprocessor=clean_text, analyzer = 'char_wb', stop_words = stopwordSet, ngram_range=(4, 4))
X_train_TFIDF_ngram = TFIDF_vectorizer_with_ngram.fit_transform(X_train3)
X_test_TFIDF_ngram = TFIDF_vectorizer_with_ngram.transform(X_train3)

GSCV.fit(X_train_TFIDF_ngram,y_train3)
'''
GSCV.fit(X_train_Count_no_ngram, y_train3)
print(GSCV.best_params_)

## Best area to search for hyperpar, when using TFIDF with ngram(4,4)
## Result: liblinear-solver with C = 6 provides the best model, with 0.718
means = GSCV.cv_results_['mean_test_score']
stds = GSCV.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, GSCV.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))

means = GSCV.cv_results_['mean_test_score']
stds = GSCV.cv_results_['std_test_score']
for mean, std, params in zip(means, stds, GSCV.cv_results_['params']):
    print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))

X_train, X_test, y_train, y_test = train_test_split(df2['Combo'], df2['Kategori'], test_size = 0.2, random_state = 42)
TFIDF_vectorizer_with_ngram = TfidfVectorizer(preprocessor=clean_text, analyzer = 'char_wb', stop_words = stopwordSet, ngram_range=(4, 4))
X_train_TFIDF_ngram = TFIDF_vectorizer_with_ngram.fit_transform(X_train)
X_test_TFIDF_ngram = TFIDF_vectorizer_with_ngram.transform(X_test)

model = LogisticRegression(max_iter = 400, solver = 'liblinear', C = 6)

model.fit(X_train_TFIDF_ngram, y_train)
y_pred = model.predict(X_test_TFIDF_ngram)

acc = accuracy_score(y_test, y_pred)

print("Accuracy on classification, with ngram: {:.2f}".format(acc*100))

a = np.where(y_test != y_pred)
cntr = 0
pred_prob = model.predict_proba(X_test_TFIDF_ngram)[a]
true_cat = y_test.reset_index().iloc[a]['Kategori']
true_cat = true_cat.reset_index(drop = True)
for i in np.linspace(0,len(true_cat)-1,len(true_cat), dtype = int):
    cat_index = np.argpartition(pred_prob[i], -3)[-3:]
    #print(cat_index)
    cat_list = model.classes_[cat_index]
    #print(cat_list)
    if true_cat[i] in cat_list:
        cntr += 1

right_preds = len(model.predict(X_test_TFIDF_ngram)[np.where(y_test == y_pred)])
print("Top 3 accuracy: ", (cntr + right_preds)/len(y_test))