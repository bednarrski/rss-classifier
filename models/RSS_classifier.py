import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
import numpy as np

from collections import defaultdict

class MeanEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.dim = len(next(iter(word2vec.items())))
        
    
    def fit(self, X, y):
        return self 

    def transform(self, X):
        return np.array([
            np.mean([self.word2vec[w] for w in words if w in self.word2vec] 
                    or [np.zeros(self.dim)], axis=0)
            for words in X
        ])

class TfidfEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.word2weight = None
        self.dim = len(next(iter(word2vec.items())))
        
    def max_idf_func():
        return self.max_idf
        
    def fit(self, X, y):
        #tfidf = TfidfVectorizer(analyzer=lambda x: x)
        tfidf = TfidfVectorizer(analyzer=rewrite)
        tfidf.fit(X)
        # if a word was never seen - it must be at least as infrequent
        # as any of the known words - so the default idf is the max of 
        # known idf's
        self.max_idf = max(tfidf.idf_)
        self.word2weight = defaultdict(
            #lambda: max_idf, 
            self.max_idf_func, 
            [(w, tfidf.idf_[i]) for w, i in tfidf.vocabulary_.items()])
    
        return self
    
    def transform(self, X):
        return np.array([
                np.mean([self.word2vec[w] * self.word2weight[w]
                         for w in words if w in self.word2vec] or
                        [np.zeros(self.dim)], axis=0)
                for words in X
            ])

def rewrite(x):
    return x
   
def text_to_word_sequence(text,
                          filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n',
                          lower=True, split=" "):
    if lower: text = text.lower()
    if type(text) == str:
        translate_table = {ord(c): ord(t) for c,t in zip(filters, split*len(filters)) }
    else:
        translate_table = maketrans(filters, split * len(filters))
    text = text.translate(translate_table)
    seq = text.split(split)
    return [i for i in seq if i]

def classify(articles_info_pd):
    with open('/home/piotr.bednarski/Repositories/rss-classifier/models/20180202_1025_ensemble_models_with_manager.pickle', 'rb') as f:
        contents_dict = pickle.load(f)

    model_svc = contents_dict['model_svc_sklearn']
    model_svc_tfidf = contents_dict['model_svc_tfidf_sklearn']

    model_nb = contents_dict['model_nb_sklearn']
    model_nb_tfidf = contents_dict['model_nb_tfidf_sklearn']

    etree_w2v = contents_dict['etree_w2v_sklearn']
    etree_w2v_tfidf = contents_dict['etree_w2v_tfidf_sklearn']

    svc_w2v = contents_dict['svc_w2v_sklearn']
    svc_w2v_tfidf = contents_dict['svc_w2v_tfidf_sklearn']

    etree_w2v_custom = contents_dict['etree_w2v_custom_sklearn']
    etree_w2v_tfidf_custom = contents_dict['etree_w2v_tfidf_custom_sklearn']

    svc_w2v_custom = contents_dict['svc_w2v_custom_sklearn']
    svc_w2v_tfidf_custom = contents_dict['svc_w2v_tfidf_custom_sklearn']

    logistic_w2v = contents_dict['logistic_w2v_sklearn']
    logistic_w2v_tfidf = contents_dict['logistic_w2v_tfidf_sklearn']

    sgd_w2v = contents_dict['sgd_w2v_sklearn']
    sgd_w2v_tfidf = contents_dict['sgd_w2v_tfidf_sklearn']
        
    best_mask = contents_dict['best_mask']
    percentile = contents_dict['percentile']
    best_threshold = contents_dict['best_threshold']
    logi = contents_dict['ensembler']
    
    print(contents_dict)
   
    mask_bool = []
    for x in best_mask:
        mask_bool.append(x == 1)
    
    articles_info_pd['class'] = True

    with open('/home/piotr.bednarski/Repositories/rss-classifier/stopwords/english') as f:
        stopwords = [line.strip() for line in f]

    for i in range(len(articles_info_pd['class'])):
        input_text = articles_info_pd.iloc[i]['title']+' '\
                +articles_info_pd.iloc[i]['authors']+' '\
                +articles_info_pd.iloc[i]['abstract']
                
        seq = text_to_word_sequence(input_text)
        clean_seq = [word for word in seq if word not in stopwords]
        input_text = ' '.join(clean_seq)
        
        intermediate_results = np.column_stack((
                model_svc.predict_proba([input_text])[:,1],
                model_svc_tfidf.predict_proba([input_text])[:,1],

                model_nb.predict_proba([input_text])[:,1],
                model_nb_tfidf.predict_proba([input_text])[:,1],

                etree_w2v.predict_proba([input_text])[:,1],
                etree_w2v_tfidf.predict_proba([input_text])[:,1],

                svc_w2v.predict_proba([input_text])[:,1],
                svc_w2v_tfidf.predict_proba([input_text])[:,1],

                etree_w2v_custom.predict_proba([input_text])[:,1],
                etree_w2v_tfidf_custom.predict_proba([input_text])[:,1],

                svc_w2v_custom.predict_proba([input_text])[:,1],
                svc_w2v_tfidf_custom.predict_proba([input_text])[:,1],

                logistic_w2v.predict_proba([input_text])[:,1],
                logistic_w2v_tfidf.predict_proba([input_text])[:,1],

                sgd_w2v.predict_proba([input_text])[:,1],
                sgd_w2v_tfidf.predict_proba([input_text])[:,1]
            ))
        
        intermediate_results_filtered = intermediate_results[:,mask_bool]
        
        
        y_predicted_proba = logi.predict_proba(intermediate_results_filtered)
        manager_result = (y_predicted_proba[:,1] > best_threshold)

        articles_info_pd.set_value(i, 'class', manager_result)
    
    return articles_info_pd

def classify2(articles_info_pd):
    models = pickle.load(open( '/home/piotr.bednarski/Repositories/rss-classifier/rss_models_171215.pickle', "rb" ))
    print(models)
    
    articles_info_pd['class'] = True
    svc = models['svc']
    
    for i in range(len(articles_info_pd['class'])):
        temp = articles_info_pd.iloc[i]['title']+' '\
                +articles_info_pd.iloc[i]['authors']+' '\
                +articles_info_pd.iloc[i]['abstract']
        #articles_info_pd.at[i]['class'] = temp
        #print(svc.predict_proba([temp])[0])
        temp = ((svc.predict_proba([temp])[0])[1] > 0.14)
        articles_info_pd.set_value(i, 'class', temp)
    
    return articles_info_pd
