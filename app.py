from flask import Flask, render_template, request
import openai
import requests
import json
import time
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from flask import Flask, render_template, request, jsonify

import pinecone
import os

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form['query']

    # Your existing code for processing the query and generating the answer
    openai.api_key = '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'

    response = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002"
    )

    result = response['data']
    embeddings = result[0]['embedding']

    import pinecone

    PINECONE_API_KEY = 'bce58a20-b111-4380-90d4-2b20126f889a'
    PINECONE_API_ENV = 'us-east-1-aws'

    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_API_ENV
    )

    index_name = "police2"

    index = pinecone.Index(index_name)

    results = index.query(
        vector=embeddings,
        top_k=5,
        include_values=False,
        include_metadata=True
    )

    def remove_special_characters(text):
        text = text.replace("[", "")
        text = text.replace("]", "")
        text = text.replace("{", "")
        text = text.replace("}", "")
        text = text.replace("'", "")
        text = text.replace('"', "")
        return text

    metadata = results.matches

    cleaned_metadata = []
    for meta in metadata:
        cleaned_meta = remove_special_characters(str(meta.metadata))
        cleaned_metadata.append(cleaned_meta)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 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'
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": ""
            },
            {
                "role": "user",
                "content": "Pretend you are an expert in Ohio Penal Code. Only use data from the PROMPT for your answer and summarize your answer. If you cannot get an answer from the PROMPT say 'I don't know'. In your answer, do not ever say the word prompt. PROMPT: " + " ".join(cleaned_metadata) + query
            }
        ]
    }

    response = requests.post(
        'https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        chat = response.json()
        answer = chat['choices'][0]['message']['content']
    else:
        answer = 'Request failed with status code: ' + \
            str(response.status_code)

        ##############################################################
    text = answer
    speech = text_to_speech(text)
    print(speech)


    ##############################################################

    return jsonify(answer=answer)

import requests

def text_to_speech(text):
    # url = "https://large-text-to-speech.p.rapidapi.com/tts"

    # payload = {"text": text}
    # headers = {
    #     "content-type": "application/json",
    #     "X-RapidAPI-Key": "6d5e247b6amsh047d78a3ee76b6dp1b3927jsn61671dc60097",
    #     "X-RapidAPI-Host": "large-text-to-speech.p.rapidapi.com"
    # }

    # response = requests.post(url, json=payload, headers=headers)
    # print(response)

    import pyttsx3

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 150)

        
    engine.say(text)
    engine.runAndWait()
    

    return text



if __name__ == '__main__':
    app.run()


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     answer = ""
#     if request.method == 'POST':
#         query = request.form['query']

#         # Your existing code for processing the query and generating the answer
#         openai.api_key = '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'

#         response = openai.Embedding.create(
#             input=query,
#             model="text-embedding-ada-002"
#         )

#         result = response['data']
#         embeddings = result[0]['embedding']

#         import pinecone

#         PINECONE_API_KEY = 'bce58a20-b111-4380-90d4-2b20126f889a'
#         PINECONE_API_ENV = 'us-east-1-aws'

#         pinecone.init(
#             api_key=PINECONE_API_KEY,
#             environment=PINECONE_API_ENV
#         )

#         index_name = "police2"

#         index = pinecone.Index(index_name)

#         results = index.query(
#             vector=embeddings,
#             top_k=5,
#             include_values=False,
#             include_metadata=True
#         )

#         def remove_special_characters(text):
#             text = text.replace("[", "")
#             text = text.replace("]", "")
#             text = text.replace("{", "")
#             text = text.replace("}", "")
#             text = text.replace("'", "")
#             text = text.replace('"', "")
#             return text

#         metadata = results.matches

#         cleaned_metadata = []
#         for meta in metadata:
#             cleaned_meta = remove_special_characters(str(meta.metadata))
#             cleaned_metadata.append(cleaned_meta)

#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': 'Bearer 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'
#         }

#         data = {
#             "model": "gpt-3.5-turbo",
#             "messages": [
#                 {
#                     "role": "system",
#                     "content": ""
#                 },
#                 {
#                     "role": "user",
#                     "content": "Pretend you are an expert in Ohio Penal Code. Only use data from the PROMPT for your answer and summarize your answer. If you cannot get an answer from the PROMPT say 'I don't know'. In your answer, do not ever say the word prompt. PROMPT: " + " ".join(cleaned_metadata) + query
#                 }
#             ]
#         }

#         response = requests.post(
#             'https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(data))

#         if response.status_code == 200:
#             chat = response.json()
#             answer = chat['choices'][0]['message']['content']
#         else:
#             answer = 'Request failed with status code: ' + \
#                 str(response.status_code)

#     return render_template('index.html', answer=answer)
