import os
import time
import wave
import pyaudio
import speech_recognition as sr
import openai
import requests
from flask import Flask, render_template, request, jsonify, send_file
import openai
import requests
import json
from gtts import gTTS
import os
import tempfile

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('indextest.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    user_text = request.form.get('user_text', None)
    transcribed_text = transcribe_audio(user_text)
    answer = process_query(transcribed_text)

    return jsonify(answer=answer)


def text_to_speech(text):
    speech = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as speech_file:
        speech.save(speech_file.name)
        return speech_file.name

def intro_audio():
    intro_text = "Searching Ohio Penal Code for Your Answer"
    intro_audio_file = text_to_speech(intro_text)
    return intro_audio_file

def process_query(query):
    # Your existing code for processing the query and generating the answer
    openai.api_key = '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'

    response = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002"
    )

    result = response['data']
    embeddings = result[0]['embedding']

    # ... continue with the rest of the code ...
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

    return answer

@app.route('/search_audio', methods=['POST'])
def search_audio():
    query = request.form['query']
    answer = process_query(query)

    audio_file = text_to_speech(answer)

    response = send_file(audio_file, mimetype='audio/mpeg', as_attachment=False)
    os.remove(audio_file)  # Delete the temporary file
    return response




def transcribe_audio(user_text=None):
    if user_text is None:
        openai.api_key = os.getenv("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")

        r = sr.Recognizer()
        p = pyaudio.PyAudio()

        frames = []

        def callback(in_data, frame_count, time_info, status):
            frames.append(in_data)
            return (in_data, pyaudio.paContinue)

        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        stream_callback=callback)

        print("Listening for 'gavel copy'...")

        while True:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, phrase_time_limit=2)
                try:
                    text = r.recognize_google(audio)
                    if "gavel copy" in text.lower():
                        print("Recording started...")
                        break
                except sr.UnknownValueError:
                    continue

        frames.clear()
        stream.start_stream()

        print("Listening for 'gavel over'...")

        while True:
            time.sleep(0.5)
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, phrase_time_limit=2)
                try:
                    text = r.recognize_google(audio)
                    if "gavel over" in text.lower():
                        print("Recording stopped...")
                        break
                except sr.UnknownValueError:
                    continue

        stream.stop_stream()
        stream.close()
        p.terminate()

        with open("temp_recording.wav", "wb") as f:
            wf = wave.open(f, "wb")
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b"".join(frames))
            wf.close()

        with sr.AudioFile("temp_recording.wav") as source:
            audio_data = r.record(source)

        headers = {"Authorization": f"Bearer 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"}
        url = "https://api.openai.com/v1/audio/transcriptions"

        with open("temp_recording.wav", "rb") as f:
            response = requests.post(
                url,
                headers=headers,
                data={"model": "whisper-1"},
                files={"file": ("temp_recording.wav", f, "audio/wav")},
            )

            if response.status_code == 200:
                json_response = response.json()
                transcript = json_response["text"]
                clean_transcript = transcript.replace("gavel over", "").strip()
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                return None
    else:
        clean_transcript = user_text

    return clean_transcript


if __name__ == '__main__':
    result = transcribe_audio()