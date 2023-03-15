from flask import Flask, render_template, request
import openai
import requests
import json
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
import os

# print("Current working directory:", os.getcwd())
# print("Templates folder path:", os.path.abspath('templates'))


# app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    answer = ""
    if request.method == 'POST':
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

        PINECONE_API_KEY = '20017f4f-c621-4e18-a94c-f8b68905d035'
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

    return render_template('index.html', answer=answer)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)
