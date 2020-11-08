import os
import json
from collections import defaultdict

import numpy as np
from bs4 import NavigableString
import argparse

from Poynter_utils import get_soup, get_unique_id, clean_text

    
def scrap_one_article(article_data):
    url_poynter_article = article_data['url_poynter']
    soup_poynter_article = get_soup(url_poynter_article)
    for p in soup_poynter_article.main.article.find_all('p'):
        t = p.get_text()
        if 'Explanation: ' in t:  
            explanation = t.replace('Explanation: ', '')
        elif 'originated from:' in t:
            origin = t.split('originated from: ')[-1]
        elif 'Fact-checked by' in t:
            checker = t.replace('Fact-checked by: ', '')
        elif '--topinfo' in p.get('class')[-1]:
            date, country = t.split(' | ')
    for a in soup_poynter_article.main.article.find_all('a'):
        if isinstance(a, NavigableString):
            continue
        elif 'Read the Full Article' in a.get_text():
            url_source_article = a.get('href')
    
    article_data['explanation'] = clean_text(explanation)
    article_data['origin'] = clean_text(origin)
    article_data['checker'] = clean_text(checker)
    article_data['date'] = date
    article_data['country'] = clean_text(country)
    article_data['url_source'] = url_source_article
    proposed_id = get_unique_id(article_data['summary'], article_data['date'])
    """
    language = get_language(url_source_article)
    article_data['language'] = language
    if language == 'english':
        soup = get_soup(url_source_article)
        content = soup.main.find(id='content')
        for p in content:
            if isinstance(p, NavigableString):
                pass
            else:
                body_text = p.get_text()
    else:
        body_text = 'NONE-{}'.format(language)"""
    return article_data, proposed_id

class PoynterCrawler():
    def __init__(self, base_url, base_site, query_mark, name):
        self.base_url = base_url
        self.base_site = base_site
        self.query_mark = query_mark
        self.name = name
        
        print('Querying page {} from {}...'.format(self.base_url, self.base_site))
        soup = get_soup(base_url)
        # Get the number of pages
        pages = []
        for link_element in soup.find_all('a'):
            link = link_element.get('href', '')
            if 'ifcn-covid-19-misinformation/page/' in link:
                page = link.split('/')[-2]
                pages.append(int(page))
        self.n_pages = np.max(pages)
        print('Found {} pages of content!'.format(self.n_pages))

    def scrap_selected_pages(self, verbose=False, page_min=None, page_max=None, output_dir=None):
        if page_min is None:
            page_min = 1
        if page_max is None:
            page_max = self.n_pages
        for n in range(page_min, page_max+1):
            if n == page_min:
                page_facts = None
            page_facts = self.scrap_page(n, verbose=verbose, page_facts=page_facts)
        if output_dir is not None:
            with open(os.path.join(output_dir, 'all.json'), 'w') as fp:
                json.dump(page_facts, fp, indent=1)
            print('Wrote at {}!'.format(os.path.join(output_dir, 'all.json')))
        else:
            return page_facts
        
    def scrap_all(self, verbose=False, output_dir=None):
        return self.scrap_selected_pages(verbose=verbose, output_dir=output_dir)
    
    def scrap_page(self, page_number, verbose, page_facts=None, output_dir=None):
        print('-Page {}...'.format(page_number))
        if page_facts is None:
            page_facts = defaultdict(dict)
        else:
            assert isinstance(page_facts, defaultdict)
        page_url = '{}page/{}/'.format(self.base_url, page_number)
        soup = get_soup(page_url)
        for link_element in soup.find_all('a'):
            url_poynter_article = link_element.get('href', '')
            is_button = not (link_element.get('class', None) is None)
            if url_poynter_article.replace(self.base_site, '').startswith(self.query_mark):
                if is_button:
                    continue
                veracity = link_element.span.string
                summary = link_element.text.replace(veracity, '')
                fact = [url_poynter_article, summary]
                article_data = {
                    'summary': clean_text(summary),
                    'veracity': clean_text(veracity.replace(':','')),
                    'explanation': None,
                    'origin': None,
                    'checker': None,
                    'date': None,
                    'country': None,
                    'url_source': None,
                    'url_poynter': url_poynter_article}    
                article_data, proposed_id = scrap_one_article(article_data)
                count = 0
                while True:
                    if page_facts.get(proposed_id, None) is None:
                        page_facts[proposed_id] = article_data
                        if verbose:
                            print(verbose)
                            print('\n')
                            print(proposed_id)
                            print(article_data)
                        break
                    else:
                        proposed_id = '{}_{}'.format(proposed_id.split('_')[0], count)
                        count += 1
                if output_dir is not None:
                    assert os.path.isdir(output_dir)
                    with open(os.path.join(output_dir, '{}.json'.format(proposed_id)), 'w') as fp:
                        json.dump(article_data, fp, indent=0)
                    print('Wrote at {}!'.format(os.path.join(output_dir, proposed_id)))
        if output_dir is not None:
            # Write json
            with open(os.path.join(output_dir, 'page{}.json'.format(page_number)), 'w') as fp:
                json.dump(page_facts, fp, indent=1)
            print('Wrote at {}!'.format(os.path.join(output_dir, 'page{}.json'.format(page_number))))
            return None
        else:
            return page_facts

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawl poynter and write all the summaries.')
    parser.add_argument('--verbose', type=bool, required=False, default=False)
    parser.add_argument('--page_min', type=int, required=False, default=None)
    parser.add_argument('--page_max', type=int, required=False, default=None)
    parser.add_argument('--page', type=int, required=False, default=1)
    parser.add_argument('--all', type=bool, required=False, default=False)
    parser.add_argument('--output_dir', type=str, required=False, 
        default='/mnt/Documents/accurolab/data/poynter/summaries')
    args = parser.parse_args()
    poynter_crawler = PoynterCrawler(base_url='https://www.poynter.org/ifcn-covid-19-misinformation/', 
                base_site='https://www.poynter.org/', 
                query_mark='?ifcn_misinformation',
                name='Poynter')
    if args.all:
        print('Scrapping all pages!')
        all_facts = poynter_crawler.scrap_all(args.verbose, output_dir=args.output_dir)
    elif args.page_min is not None or args.page_max is not None:
        print('Scrapping pages from {} to {}:'.format(args.page_min, args.page_max))
        all_facts = poynter_crawler.scrap_selected_pages(args.verbose, 
            page_min=args.page_min, page_max=args.page_max, output_dir=args.output_dir)
    else:
        print('Scrapping page {}'.format(args.page))
        all_facts = poynter_crawler.scrap_page(args.page, args.verbose, 
            output_dir=args.output_dir)
    