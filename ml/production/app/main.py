from haystack import Finder
from haystack.preprocessor.cleaning import clean_wiki_text
from haystack.preprocessor.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.reader.farm import FARMReader
from haystack.reader.transformers import TransformersReader
from haystack.utils import print_answers
from haystack.document_store.memory import InMemoryDocumentStore
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.retriever.sparse import TfidfRetriever, ElasticsearchRetriever


import pathlib
import pandas as pd
import io
import re
import numpy

import os

from fastapi import FastAPI
from pydantic import BaseModel

import sys
# append Retrieval modules' folder path here
sys.path.append('/retrieval')

import get_data as ret
import utils

# HAYSTACK (same as our Colab Proof of concept)
PROJECT_DIRECTORY = os.getcwd()
ARTICLES_FOLDER = PROJECT_DIRECTORY + "/data"

# In the bash we have to set export MKL_SERVICE_FORCE_INTEL=1
# MANIFEST of data to be loaded
# TODO: Read from a file
MANIFEST = {
    'include' : {
        'pathnames': [
            './new_format/articles*.json',
        ]
    } ,
    'exclude' : {
        'pathnames': [

        ]
    }
}

def load_documents():
    """Retrieves scraped articles filepaths from ARTICLES_FOLDER
    DEPRECATED
    Returns
    -------
    articles: List of str
      List of filepaths for each article from ARTICLES_FOLDER
    """

    # define the path
    path_folder = pathlib.Path(ARTICLES_FOLDER)

    # define the pattern
    json_files = "*.json"

    # extract absolute filepath for each of the articles
    articles = [
        json_file.absolute().as_posix() for json_file in path_folder.glob(json_files)
    ]

    return articles


def process_documents(articles):
    """Process articles  and returns it in dictionary format

    Parameters
    ----------
    articles : list of str
        List of articles dictionaries

    Returns
    -------
    dicts_textContent : dict
        Dictionary containing the required structure used by the models:
        {"text": article text content
         "meta": {"name": article title, "uri": article url, 
                "pubDate":publication date (optional)}}
    """

    dicts_textContent = []

    for article in articles:
        # Join text and title as they all provide
        # interesting information
        complete_text = (
            article["text"] + article["title"]
        )

        # For each of the texts format in form of dictionary
        dicts_textContent.append(
            {
                "text": complete_text,
                "meta": {
                    "name": article["title"],
                    "uri": article["uri"],
                    "pubDate": article["pubDate"]
                },
            }
        )

    return dicts_textContent


def feed_documents_to_model(model_name="deepset/roberta-base-squad2-covid",
                            dev = True):
    """Feeds documents to model and returns a model ready to make predictions

    Parameters
    ----------
    model_name : str
        The path of the model to be selected from HuggingFace
        By default uses the pretrained version of roBERTa in squad2
        and covid articles

    Returns
    -------
    finder
        the model to use for predictions
    """

    # Initialize in memory Document Store
    if dev == True:
        document_store = InMemoryDocumentStore()
    else:
        document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", index="document")

    # Load articles and format it as dictionary
    articles = ret.get_data(MANIFEST, ARTICLES_FOLDER,[])
    dicts_textContent = process_documents(articles)
    # Store the dictionary with articles content in the Document Store
    document_store.write_documents(dicts_textContent)
    # Retriever chooses what is the subset of documents that are relevant
    # many techniques are possible: for dev purposes TfidfRetriever is faster
    if dev == True:
        retriever = TfidfRetriever(document_store=document_store)
    else:
        retriever = ElasticsearchRetriever(document_store=document_store)
        document_store.update_embeddings(retriever)
    # Reader provides interface to use the pre trained transformers
    # by default we're using the roberta
    reader = FARMReader(model_name_or_path=model_name, use_gpu=False)
    # The finder retrieves predictions
    finder = Finder(reader, retriever)

    return finder


# FASTAPI
class Input(BaseModel):
    question: str


app = FastAPI()

# Start ElasticSearch docker first

#  Should only execute at moment of load
finder_in_memory = feed_documents_to_model(dev=True)
finder_elastic = feed_documents_to_model(dev=False)


@app.put("/predict")
def answer_question(d: Input):
    """ For InMemory document Store and TFIDF
    Given a question at input, provide answer using the finder model

    Parameters
    ----------
    d: d.question str

    Returns
    -------
    a dict: {question: provided by user,
            answer: text as answer,
            score: of answer,
            probability: of answer,
            url: article url,
            pubDate: article published date,
            articleName: article name}
    """

    # Get predictions for the input question
    # TODO: Clean question text before passing
    # it to the model
    prediction = finder_in_memory.get_answers(
        question=d.question, top_k_retriever=3, top_k_reader=1
    )
    # TODO: Filter out the answer if it is not reliable
    answer = prediction["answers"][0]["answer"]
    probability = prediction["answers"][0]["probability"]
    score = prediction["answers"][0]["score"]
    url = prediction["answers"][0]["meta"]["uri"]
    pub_date = prediction["answers"][0]["meta"]["pubDate"]
    article_name = prediction["answers"][0]["meta"]["name"]

    return {
        "question": d.question,
        "answer": answer,
        "score": score,
        "probability": probability,
        "url": url,
        "pubDate": pub_date,
        "articleName": article_name,
    }

@app.put("/predict2")
def answer_question_dense(d: Input):
    """For DenseRetriever using ElasticSearch
    Given a question at input, provide answer using the finder model

    Parameters
    ----------
    d: d.question str

    Returns
    -------
    a dict: {question: provided by user,
            answer: text as answer,
            score: of answer,
            probability: of answer,
            url: article url,
            pubDate: article published date,
            articleName: article name}
    """

    # Get predictions for the input question
    # TODO: Clean question text before passing
    # it to the model
    prediction = finder_elastic.get_answers(
        question=d.question, top_k_retriever=3, top_k_reader=1
    )
    # TODO: Filter out the answer if it is not reliable
    answer = prediction["answers"][0]["answer"]
    probability = prediction["answers"][0]["probability"]
    score = prediction["answers"][0]["score"]
    url = prediction["answers"][0]["meta"]["uri"]
    pub_date = prediction["answers"][0]["meta"]["pubDate"]
    article_name = prediction["answers"][0]["meta"]["name"]

    return {
        "question": d.question,
        "answer": answer,
        "score": score,
        "probability": probability,
        "url": url,
        "pubDate": pub_date,
        "articleName": article_name,
    }