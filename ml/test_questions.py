# This file has to be executed after executing fastapiapp
# Test file with questions -- run at a terminal

import requests,json
import time


# Serve model at localhost first by running in one terminal the following:
# $ export "MKL_SERVICE_FORCE_INTEL=1"
# $ uvicorn haystack_api:app --reload

# Then execute this script to get answers to questions

PREDICT_URL = "http://127.0.0.1:8000/predict"

   
def get_response(question):
    """
    Parameters
    ----------
    question : Dictionnary
        contains the question to be answered.

    Returns
    -------
    json with answer, score, probability and execution time in ms

    """
    time_start = time.time()
    
    payload = json.dumps(question)
    response = requests.put(PREDICT_URL,data = payload)
    response = response.json()
    
    time_end = time.time()
    exec_time = int((time_end - time_start) * 1000)
    response['exec_time_ms']= exec_time
    
    return response
 

question = {
    "question": "Are young children more susceptible to coronavirus?"
 }
response= get_response(question)
print(response)
