import string
import re

import nltk as nltk
from nltk.corpus import wordnet as wn
from bs4 import BeautifulSoup
import urllib.request
from urllib.request import Request, urlopen
from constants import IGNORED_WORDS
from constants import COUNTRY_BY_DOMAIN, SPEAKING


def clean_text(text):
    text = text.strip()
    text = re.sub(r'[^a-zA-Z\s+\d]+[.!\?\,:;]+', '', text)
    return text

def get_unique_id(summary, date):
    summary = summary.replace("'", '')
    summary = summary.replace('"', '')
    summary = summary.replace("`", '')
    summary = summary.replace("-", '')
    summary = summary.translate(str.maketrans('', '', string.punctuation))
    #summary = re.sub(r'\W+', '', summary) 
    summary = re.sub(r'[^a-zA-Z\s]+', '', summary) 
    summary = summary.split(' ')
    words_to_keep = []
    capital_words = []
    for word in summary:
        if len(word) <= 3:
            continue
        if word.lower() in IGNORED_WORDS:
            continue
        if word.endswith('ing'):
            continue
        tmp = wn.synsets(word)
        try:
            type_word = tmp[0].pos()
            if type_word == 'v':
                continue
        except:
            pass
        if word[0].isupper():
            capital_words.append(word.upper())
        elif not word.endswith('ed'):
            words_to_keep.append(word.upper())
    if len(words_to_keep) >= 2:
        words_id = '{}-{}'.format(words_to_keep[0],words_to_keep[-1])
    elif len(words_to_keep) >= 1:
        words_id = '{}'.format(words_to_keep[0])
    elif len(summary) > 0:
        words_id = '{}'.format(summary[0].upper())
    else:
        words_id = 'null'
    if len(capital_words) > 0:
        words_id = '{}-{}'.format(capital_words[0], words_id)
    unique_id = '{}_{}'.format(date.replace('/',''), words_id)
    return unique_id

def get_language(url_source_article):
    country_domain = url_source_article
    prefixes = ['http://', 'https://', 'www.']
    for prefix in prefixes:
        country_domain = country_domain.replace(prefix, '')
    country_domain = country_domain.split('/')[0]
    country_domain = '.{}'.format(country_domain.split('.')[-1])
    if country_domain == '.com':
        return None
    country = COUNTRY_BY_DOMAIN.get(country_domain, None)
    language = None
    if country is not None:
        for l,c in SPEAKING.items():
            if country in c:
                language = l
                break
    return language

    """if country_domain == 'es':
        language = 'spanish'
    elif country_domain == 'fr':
        language = 'french'
    elif country_domain in ['us', 'com', 'uk']:
        language = 'english'
    return language"""

def get_soup(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(page, 'html.parser')
    return soup