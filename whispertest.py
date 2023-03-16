import os
import time
import wave
import pyaudio
import speech_recognition as sr
import openai
import requests

def transcribe_audio():
    openai.api_key = os.getenv("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")

    r = sr.Recognizer()
    p = pyaudio.PyAudio()

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

    # openai_api_key = os.getenv("OPENAI_API_KEY")
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
            print(json_response)  # Add this line to print the JSON response
            transcript = json_response["text"]
            clean_transcript = transcript.replace("gavel over", "").strip()
            return clean_transcript
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None



frames = []

# Call the function to start listening and transcribing
result = transcribe_audio()
print("Transcribed text:", result)
