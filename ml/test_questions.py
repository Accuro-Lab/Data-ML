# This file has to be executed after executing fastapiapp
# Test file with questions -- run at a terminal

import requests,json


# Serve model at localhost first by running in one terminal the following:
# $ export "MKL_SERVICE_FORCE_INTEL=1"
# $ uvicorn haystack_api:app --reload

# Then execute this script to get answers to questions

payload = json.dumps({
   "question": "Are children more susceptible to coronavirus?"
 })
response = requests.put("http://127.0.0.1:8000/predict",data = payload)
response.json()
