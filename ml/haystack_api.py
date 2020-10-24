from haystack import Finder
from haystack.preprocessor.cleaning import clean_wiki_text
from haystack.preprocessor.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.reader.farm import FARMReader
from haystack.reader.transformers import TransformersReader
from haystack.utils import print_answers
from haystack.document_store.memory import InMemoryDocumentStore


import pandas as pd
import io
import re
import numpy

import os


##### HAYSTACK (same as our Colab Proof of concept)
PROJECT_DIRECTORY = os.getcwd()
ARTICLES_FOLDER = PROJECT_DIRECTORY+"/data/CKB-articles-scrape/"

# In the bash we have to set export MKL_SERVICE_FORCE_INTEL=1

import pathlib
from haystack.retriever.sparse import TfidfRetriever

def load_documents_for_reader():
    
    # define the path
    path_folder = pathlib.Path(ARTICLES_FOLDER)

    # # define the pattern
    json_files = "*.json"

    articles = [ json_file.absolute().as_posix() for json_file in path_folder.glob(json_files)]
   
    return articles

def process_documents(articles):
    dicts_textContent = []

    for article in articles:
        try:
            df_article = pd.read_json(article)
        except:
            print(article)
            continue
        complete_text = df_article['textContent'] + df_article['excerpt'] + df_article['title']
        list_textContent = complete_text.tolist() 

        for i in range(len(list_textContent)):
            dicts_textContent.append({'text': df_article['textContent'][i], 'meta': {'name': df_article['title'][i], 'url': df_article['url'][i]}})
    
    return dicts_textContent

def feed_documents_to_model():
    document_store = InMemoryDocumentStore()
    articles = load_documents_for_reader()
    dicts_textContent = process_documents(articles)
    document_store.write_documents(dicts_textContent)
    retriever = TfidfRetriever(document_store=document_store)
    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2-covid", use_gpu=False)
    finder = Finder(reader, retriever)
    
    return finder



### FASTAPI


from fastapi import FastAPI
from pydantic import BaseModel


class Input(BaseModel):
    question : str
        
app = FastAPI()

# Should only execute at moment of load
finder = feed_documents_to_model()


@app.put("/predict")
def answer_question(d:Input):
    '''Given a question at input, provide answer using the finder model
     d: d.question str
     returns question provided by user
             answer text as answer
             score of answer
             probability of answer
     '''
    prediction = finder.get_answers(question=d.question, top_k_retriever=3, top_k_reader=1)
    answer = prediction['answers'][0]['answer']
    probability = prediction['answers'][0]['probability']
    score = prediction['answers'][0]['score']
    return {'question': d.question, 'answer': answer, 'score': score,'probability': probability}


