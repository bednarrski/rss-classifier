import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

#import numpy as np

def classify(articles_info_pd):
    
    articles_info_pd['class'] = True
    
    articles_info_pd.loc[articles_info_pd['abstract'].str.contains('voice'),['class']] = False
    
    return articles_info_pd

def classify2(articles_info_pd):
    models = pickle.load(open( 'rss_models_171215.pickle', "rb" ))
    print(models)
    
    articles_info_pd['class'] = True
    
    articles_info_pd.loc[articles_info_pd['abstract'].str.contains('voice'),['class']] = False
    
    return articles_info_pd