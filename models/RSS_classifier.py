import pandas as pd
#import numpy as np

def classify(articles_info_pd):
    articles_info_pd['class'] = True
    
    articles_info_pd.loc[articles_info_pd['abstract'].str.contains('voice'),['class']] = False
    
    return articles_info_pd