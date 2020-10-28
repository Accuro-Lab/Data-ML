import datetime
import os

import numpy as np
import urllib.request
from bs4 import BeautifulSoup
import urllib.request
from urllib.request import Request, urlopen
import re



TAGS_TO_AVOID = ['last-reviewed', 'page-share', 'None']
TO_IGNORE = ['LanguagesEspañol简体中文Tiếng Việt한국어Other Languages \n\n\nPrint\n\n\n\n\n\n\n\n\n',
    'Facebook\nTwitter\nLinkedIn\nEmail\nSyndicate\n\n\n\n\n\n\n\n\n\n\n\n\nMinus\n\n\n\n\nRelated Pages\n\n\n\n\n',
    'minus icon', 'Top of Page', 'external icon', 'Abstract', 'Top']
CARDBODY_EXCERPTS = ['card-body bg-cyan-q', 'card-body bg-amber-q',
    'card-body bg-amber-s', 'card-body bg-amber-s',
    'card-body bg-tertiary']

def get_soup(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(page, 'html.parser')
    return soup

def clean_text(list_of_text):
    clean_text = '\n'.join(list_of_text)
    for _ in TO_IGNORE:
        clean_text = clean_text.replace(_, '')    
    clean_text = clean_text.strip()
    return clean_text

def get_init_article(link, siteName='Centers for Disease Control and Prevention'):
    article = {}
    article['url'] = link
    article['dir'] = 'null'
    article['siteName'] = siteName
    scrapped_time = datetime.datetime.utcnow()
    article['scrapeDate'] = scrapped_time.strftime("%Y-%m-%dT%H:%M:%S")
    article['scrapeTimestamp'] = int(datetime.datetime.timestamp(scrapped_time))
    article['title'] = 'null'
    article['excerpt'] = 'null'
    article['content'] = 'null'
    article['byline'] = 'null'
    return article