import os
import json
import datetime
import argparse
import re

import numpy as np
from bs4 import NavigableString

from CDC_utils import get_soup, clean_text, get_init_article
from CDC_utils import TAGS_TO_AVOID, CARDBODY_EXCERPTS

    
def scrap_cdc_article(link, verbose=False):
    soup = get_soup(link)
    article = get_init_article(link)
    if 'eid/article' in link:
        for p in soup.main.find_all(class_='header article-title'):
            title = p.get_text().replace('| CDC', '').strip()
            article['title'] = title
        for p in soup.main.find_all(id='authors'):
            byline = p.get_text().strip()
            article['byline'] = byline
        excerpt = []
        for p in soup.main.find_all(id='abstract'):
            excerpt.append(p.get_text().strip())
        article['excerpt'] = clean_text(excerpt)
        content = []
        for p in soup.main.find_all(id='mainbody'):
            content.append(p.get_text().strip())  
        article['content'] = clean_text(content)
    else:
        soup_title = soup.title
        if soup_title is not None:
            if isinstance(soup_title, NavigableString):
                title = soup_title
            else:
                title = soup_title.get_text()
            article['title'] = title.replace('| CDC', '').strip()
        if soup.main is not None:
            # Find excerpt
            excerpt = []
            for c in CARDBODY_EXCERPTS:
                for p in soup.main.find_all(class_=c):
                    excerpt.append(p.get_text())
            for p in soup.main.find_all(class_="card-body"):
                if p.get_text().startswith('What you need to know'):
                    excerpt.append(p.get_text())
            article['excerpt'] = clean_text(excerpt)
             # Find content
            content = []
            h3 = soup.main.find_all('h3')
            if len(h3) > 1:
                for p in soup.main.find_all('h3'):
                    if ' ytd-video-primary-info-renderer' in p.parent.find('h3').get('class', ''):
                        continue
                    else:
                        content.append(p.parent.get_text().strip())
            else:
                for p in soup.main:
                    if isinstance(p, NavigableString):
                        continue
                    if not bool(re.match('^\s+$', p.get_text())):
                        if p.div is not None:
                            keep_text = True
                            for tag in p.div.get('class', ['None']):
                                if tag in TAGS_TO_AVOID:
                                    keep_text = False
                            if keep_text:
                                content.append(p.get_text().strip())
                if len(content) == 0:
                    # No text was found
                    for p in soup.main.find_all('p'):
                        content.append(p.get_text())
    article['content'] = clean_text(content)
    article['length'] = len(article['content'])
    if verbose:
        for k in ['title', 'url', 'excerpt', 'byline', 'length']:
            print('-{}: {}'.format(k, article[k]))
    return article

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawl CDC and write all the summaries.')
    parser.add_argument('--verbose', type=bool, required=False, default=False)
    parser.add_argument('--input_list_path', type=str, required=False, 
        default='/mnt/Documents/accurolab/data/cdc/cdc_list1.json')
    parser.add_argument('--output_dir', type=str, required=False, 
        default='/mnt/Documents/accurolab/data/cdc/articles')
    parser.add_argument('--output_filename', type=str, required=False, 
        default='articles-cdc-DATE.json')
    args = parser.parse_args()

    # Sanity Check
    assert os.path.isfile(args.input_list_path)
    assert os.path.isdir(args.output_dir)
    assert args.input_list_path.endswith('.json')
    assert args.output_filename.endswith('.json')

    if 'DATE' in args.output_filename:
        date =  datetime.datetime.now().strftime("%Y%m%d")
        args.output_filename = args.output_filename.replace('DATE', date)
    output_file_path = os.path.join(args.output_dir, args.output_filename)
    if os.path.isfile(output_file_path):
        with open(output_file_path, 'rb') as fp:
            articles = json.load(fp) 
    else:
        articles = []

    print('Loading the input list {}'.format(args.input_list_path))
    with open(args.input_list_path, 'rb') as fp:
        input_list = json.load(fp) 
    print('Begin the scrapping:')
    for link in input_list['url']:
        article = scrap_cdc_article(link, verbose=args.verbose)
        articles.append(article)
    print('Saving results in {}'.format(output_file_path))
    with open(output_file_path, 'w') as fp:
        json.dump(articles, fp, indent=1)


    