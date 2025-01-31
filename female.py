import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

for voice in voices:
    print(f"Voice Name: {voice.name}, ID: {voice.id}")
