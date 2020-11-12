import hashlib
import datetime

from bs4 import BeautifulSoup
import urllib.request
from urllib.request import Request, urlopen

MANDATORY_KEYS = ['title', 'text', 'uri', 'scrapeTimestamp', 'scrapeDate', 'id']
# Remove idSource

def get_soup(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(page, 'html.parser')
    return soup

def get_init_article(link, idSource):
    article = {}
    # Mandatory
    article['title'] = 'null'
    article['uri'] = link
    scrape_time = datetime.datetime.utcnow()
    article['scrapeTimestamp'] = int(datetime.datetime.timestamp(scrape_time))
    article['scrapeDate'] = scrape_time.strftime("%Y-%m-%dT%H:%M:%S")
    hashableId = (link+str(article['scrapeTimestamp'])).encode()
    article['id'] = hashlib.sha224(hashableId).hexdigest()
    article['idSource'] = idSource
    # Optional
    article['html'] = 'null'
    article['pubDate'] = 'null'
    # Additional Metadata
    article['extraMeta'] = 'null'
    return article

def check_data_format(data, additional_keys=[]):
    for key in MANDATORY_KEYS:
        if data.get(key, None) is None:
            return False
    for key in additional_keys:
        if data['extraMeta'].get(key, None) is None:
            return False
    return True