from gtts import gTTS
import pygame

pygame.init()
pygame.mixer.init()

text = input("What do you want me to say? ")
speech = gTTS(text)
speech_file = "output.mp3"
speech.save(speech_file)
pygame.mixer.music.load(speech_file)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)
pygame.mixer.music.stop()
pygame.mixer.music.unload()
pygame.time.delay(500)
pygame.quit()

choice = input("Do you want me to say something else? (y/n) ")
if choice.lower() == 'y':
    text = input("What do you want me to say? ")
    speech = gTTS(text)
    speech_file = "output.mp3"
    speech.save(speech_file)
    pygame.mixer.music.load(speech_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    pygame.time.delay(500)
    pygame.quit()



# import pyttsx3

# engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[1].id)
# engine.setProperty('rate', 150)

# while True:
#     text = input("What do you want me to say? ")
#     engine.say(text)
#     engine.runAndWait()
#     choice = input("Do you want me to say something else? (y/n) ")
#     if choice.lower() == 'n':
#         break



# import requests
# import json
# import time

# text = """Text to speech technology allows you to convert text of unlimited sizes to humanlike voice audio files!"""
# apikey = "6d5e247b6amsh047d78a3ee76b6dp1b3927jsn61671dc60097"  # get your free API key from https://rapidapi.com/k_1/api/large-text-to-speech/
# filename = "test-file.wav"

# headers = {'content-type': "application/json",
#            'x-rapidapi-host': "large-text-to-speech.p.rapidapi.com", 'x-rapidapi-key': apikey}
# response = requests.request("POST", "https://large-text-to-speech.p.rapidapi.com/tts",
#                             data=json.dumps({"text": text}), headers=headers)
# id = json.loads(response.text)['id']
# eta = json.loads(response.text)['eta']
# print(f'Waiting {eta} seconds for the job to finish...')
# time.sleep(eta)
# response = requests.request(
#     "GET", "https://large-text-to-speech.p.rapidapi.com/tts", headers=headers, params={'id': id})
# while "url" not in json.loads(response.text):
#     response = requests.request(
#         "GET", "https://large-text-to-speech.p.rapidapi.com/tts", headers=headers, params={'id': id})
#     print(f'Waiting some more...')
#     time.sleep(3)
# url = json.loads(response.text)['url']
# response = requests.request("GET", url)
# with open(filename, 'wb') as f:
#     f.write(response.content)
# print(f'File saved to {filename} ! \nOr download here: {url}')
