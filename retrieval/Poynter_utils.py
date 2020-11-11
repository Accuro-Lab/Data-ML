import string
import re

import nltk as nltk
from nltk.corpus import wordnet as wn

#from constants import COUNTRY_BY_DOMAIN, SPEAKING
from utils import get_init_article



def get_init_article_poynter(link, idSource):
    article = get_init_article(link, idSource)
    article['extraMeta'] = {}
    article['extraMeta']['summary'] = 'null'
    article['extraMeta']['veracity'] = 'null'
    article['extraMeta']['explanation'] = 'null'
    article['extraMeta']['origin'] = 'null'
    article['extraMeta']['checker'] = 'null'
    article['extraMeta']['date'] = 'null'
    article['extraMeta']['country'] = 'null'
    article['extraMeta']['url_source'] = 'null'
    #article['extraMeta']['url_poynter'] = None this is in link
    return article  


def clean_text(text):
    text = text.strip()
    text = re.sub(r'[^a-zA-Z\s+\d]+[.!\?\,:;]+', '', text)
    return text

"""def get_language(url_source_article):
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
    return language"""
