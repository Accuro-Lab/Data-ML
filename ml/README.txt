The haystack_api allows to expose an API for the model using the scraped articles

How to use it :
Serve model at localhost first by running in one terminal the following:

$ export "MKL_SERVICE_FORCE_INTEL=1"
$ uvicorn haystack_api:app --reload

This will serve the model at: http://127.0.0.1:8000/

You may interact to provide questions via:
1. Opening http://127.0.0.1:8000/docs and then filling the parameters
2. Using the test_questions.py

What it does:

It will execute the complete ML pipeline at startup (so only once) and then the model is ready to accept questions provided through a PUT request

The PUT request receives a string (the question)

The API returns a json with the following structure:

{'question': question, 'answer': answer, 'score': score,'probability': probability}

There are still many things to do:
- Clean the question that is being input
- Filter answers by score
- Calculate the execution time

