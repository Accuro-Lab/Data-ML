For the haystack-api.py: The haystack_api allows to expose an API for the model using the scraped articles.

!IMPORTANT - needed packages
-> If you're using Linux (not MACOS) you can directly install all the packages that are used by Haystack using the requirements.txt in this folder
--> Else, use --> pip install farm-haystack
   Note: this will also install fastapi and ucivorn that are used forward

- How to use it :

  1. Create data folder and unzip the CKB-articles-scrape from Google Drive
       --ml/
         |-data/
             |- CKB-articles-scrape/

  2. Serve model at localhost first by running in a terminal the following:

  $ export "MKL_SERVICE_FORCE_INTEL=1"
  $ uvicorn haystack_api:app --reload

  This will serve the model at: http://127.0.0.1:8000/

  3. You may interact to provide questions via:
     - Opening http://127.0.0.1:8000/docs and then filling the parameters
     - Using the test_questions.py

- What it does:

  It will execute the complete ML pipeline at startup (so only once) and then the model is ready to accept questions provided through a PUT request

  The PUT request receives a string (the question)

  The API returns a json with the following structure:

 {'question': question, 'answer': answer, 'score': score,'probability': probability}

- There are still many things to do:
  - Clean the question that is being input
  - Filter answers by score
  - Calculate the execution time

