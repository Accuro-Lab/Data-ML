import os

import numpy as np
import re

from utils import get_init_article


TAGS_TO_AVOID = ['last-reviewed', 'page-share', 'None']
TO_IGNORE = ['LanguagesEspañol简体中文Tiếng Việt한국어Other Languages \n\n\nPrint\n\n\n\n\n\n\n\n\n',
    'Facebook\nTwitter\nLinkedIn\nEmail\nSyndicate\n\n\n\n\n\n\n\n\n\n\n\n\nMinus\n\n\n\n\nRelated Pages\n\n\n\n\n',
    'minus icon', 'Top of Page', 'external icon', 'Abstract', 'Top']
CARDBODY_EXCERPTS = ['card-body bg-cyan-q', 'card-body bg-amber-q',
    'card-body bg-amber-s', 'card-body bg-amber-s',
    'card-body bg-tertiary']

def clean_text(list_of_text):
    clean_text = '\n'.join(list_of_text)
    for _ in TO_IGNORE:
        clean_text = clean_text.replace(_, '')    
    clean_text = clean_text.strip()
    return clean_text

def get_init_article_cdc(link, idSource):
    article = get_init_article(link, idSource)
    article['extraMeta'] = {}
    article['extraMeta']['excerpt'] = 'null'
    article['extraMeta']['byline'] = 'null'
    return article