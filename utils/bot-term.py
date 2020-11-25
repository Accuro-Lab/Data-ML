# bot-term.py
# A simple interactive terminal to test the model
# Usage: python3 bot-term.py
# ITL 2020-11-15

import requests

# api_url = "http://3.139.62.97:4000/predict"
api_url = "http://ec2-3-139-62-97.us-east-2.compute.amazonaws.com:4000/predict"

print("\nWelcome to the Accurolab Covid-19 test bot.")
print("Please ask a question, or hit return to exit.\n")

continue_loop = True
while continue_loop:
  q = input("> ")
  if q == "":
    continue_loop = False
  else:
    payload = {"question" : q }
    r = requests.put(api_url, json=payload).json()
    for x in r:
        if x != 'question':
            print(x,": ",r[x])
    print("\n")
