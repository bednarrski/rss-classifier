# !/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
print(sys.version)

import os
os.system('which python')

from time import gmtime, strftime
print(strftime("%Y%m%d_%H%M%S", gmtime()))

import git
import requests
import re
import os
import pandas as pd
from time import gmtime, strftime
from models.RSS_classifier import *
import numpy as np

def get_articles_and_xml(url):
    page = requests.get(url)

    pattern = '<item rdf:about=.*?</item>'
    article_list = re.findall(pattern, page.text, flags=(re.MULTILINE | re.DOTALL))
    return article_list, page.text

def extract_item_info(xml_string):
    item_dict = {}
    item_dict['url'] = re.findall('http://arxiv.org/abs/\d{1,8}\.\d{1,8}', xml_string, flags=(re.MULTILINE | re.DOTALL))[0]
    item_dict['title'] = (re.findall('<title>(.*?)[(]arXiv:', xml_string, flags=(re.MULTILINE | re.DOTALL))[0]).strip()
    item_dict['abstract'] = re.findall('<description rdf:.*?>(.*?)</description>', xml_string, flags=(re.MULTILINE | re.DOTALL))[0]
    item_dict['authors'] = re.findall('<dc:creator>(.*?)</dc:creator>', xml_string, flags=(re.MULTILINE | re.DOTALL))[0]
    item_dict['authors'] = re.findall('\&quot;\&gt;(.*?)\&lt;/a\&gt;', item_dict['authors'], flags=(re.MULTILINE | re.DOTALL))
    item_dict['authors'] = ', '.join(item_dict['authors'])
    item_dict['full_text'] = xml_string
    return item_dict

def get_feed_parts(xml_string):
    beginning = re.findall('.*?<rdf:Seq>\n', xml_string, flags=(re.MULTILINE | re.DOTALL))[0]
    middle = re.findall('</rdf:Seq>.*?</image>', xml_string, flags=(re.MULTILINE | re.DOTALL))[0]
    end = '</rdf:RDF>'
    
    beginning_good = re.sub('<title>(.*?)</title>', '<title>Good papers from arXiv</title>', beginning, flags=(re.MULTILINE | re.DOTALL))
    beginning_bad = re.sub('<title>(.*?)</title>', '<title>Boring papers from arXiv</title>', beginning, flags=(re.MULTILINE | re.DOTALL))
    
    beginning_good = re.sub('<description(.*?)>(.*?)</description>', '<description\g<1>>The Good Papers on ML, AI and Statistics</description>', beginning_good, flags=(re.MULTILINE | re.DOTALL))
    beginning_bad = re.sub('<description(.*?)>(.*?)</description>', '<description\g<1>>The Bad Papers on ML, AI and Statistics</description>', beginning_bad, flags=(re.MULTILINE | re.DOTALL))
    
    return beginning_good, beginning_bad, middle, end

def build_feeds(xml_string, articles_info_classified_pd):
    beginning_good, beginning_bad, middle, end = get_feed_parts(xml_string)
    
    
    items_good = []
    items_bad = []
    for i in range(len(articles_info_classified_pd)):
        item = '<rdf:li rdf:resource="' + articles_info_classified_pd['url'].iloc[i] + '"/>'
        if articles_info_classified_pd['class'].iloc[i] == True:
            items_good.append(item)
        else:
            items_bad.append(item)
            
    items_good = '\n'.join(items_good)
    items_bad = '\n'.join(items_bad)
    
    abstracts_good = []
    abstracts_bad = []
    for i in range(len(articles_info_classified_pd)):
        item = articles_info_classified_pd['full_text'].iloc[i]
        if articles_info_classified_pd['class'].iloc[i] == True:
            abstracts_good.append(item)
        else:
            abstracts_bad.append(item)
            
    abstracts_good = '\n'.join(abstracts_good)
    abstracts_bad = '\n'.join(abstracts_bad)
    
    good_text = beginning_good + items_good + middle + abstracts_good + end
    bad_text = beginning_bad + items_bad + middle + abstracts_bad + end
    
    return good_text, bad_text

urls = [
    'http://arxiv.org/rss/cs.NE',
    'http://arxiv.org/rss/cs.AI',
    'http://arxiv.org/rss/stat.ML'
]
good_feed_name = '/home/piotr.bednarski/Repositories/rss-classifier/papers_good.xml'
bad_feed_name = '/home/piotr.bednarski/Repositories/rss-classifier/papers_bad.xml'

articles_info_classified_list = []
for url in urls:
    article_list, xml_string = get_articles_and_xml(url)

    articles_info_list = []
    for article in article_list:
        info = extract_item_info(article)
        articles_info_list.append(info)

    articles_info_pd = pd.DataFrame(articles_info_list)
    articles_info_classified_list.append(classify(articles_info_pd))
    #articles_info_classified_pd = classify(articles_info_pd)

articles_info_classified_pd = pd.concat([articles_info_classified_list[0], 
                                              articles_info_classified_list[1],
                                              articles_info_classified_list[2]])

articles_info_classified_pd = articles_info_classified_pd.drop_duplicates(subset=['url'])

good_text, bad_text = build_feeds(xml_string, articles_info_classified_pd)

with open(good_feed_name, 'w') as good:
    good.write(good_text)
    
with open(bad_feed_name, 'w') as bad:
    bad.write(bad_text)

repo = git.Repo( '/home/piotr.bednarski/Repositories/rss-classifier' )
print(repo.git.add( '.' ))

timestring = strftime("%Y%m%d_%H%M%S", gmtime())
message = '"Update at ' + timestring + '"'

print(repo.git.commit( m=message ))
print(repo.git.push())
print(repo.git.status())

