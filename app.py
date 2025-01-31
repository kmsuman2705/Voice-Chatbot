from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import requests
import threading

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama API URL

# Global variable to store bot's latest response
bot_response = ""

# ✅ Speech-to-Text (Microphone se input lena)
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🔊 Speak now...")  # Inform user to speak
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio, language="en-US")  # Recognizing speech in English
        print(f"🗣️ You said: {text}")  # Print recognized speech
        return text
    except sr.UnknownValueError:
        return "I couldn't understand that, please speak again..."  # Error if speech not recognized
    except sr.RequestError:
        return "⚠️ Internet error"  # Error in case of API or connection failure

# ✅ Ollama API se Jawab lena
def get_ollama_response(user_input):
    payload = {
        "model": "llama3.1:latest",  # Correct model name
        "prompt": user_input,        # User's speech input as prompt
        "stream": False              # Non-streaming response
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)  # POST request to Ollama API
        
        if response.status_code == 200:  # If request is successful
            data = response.json()
            return data.get("response", "No response found.")  # Get response or a fallback message
        else:
            return f"⚠️ Ollama API ka response nahi aaya. Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"⚠️ API request error: {e}"

# ✅ Text-to-Speech (Bot ka jawab bolna)
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)  # Speed of speech
    engine.setProperty("volume", 1)  # Volume of speech
    engine.say(text)  # Convert text to speech
    engine.runAndWait()  # Wait until speaking finishes

# Continuously listen and respond in the background
def listen_and_respond():
    global bot_response
    while True:
        user_input = listen()  # Listen to user's voice input and convert it to text
        if user_input:
            bot_response = get_ollama_response(user_input)  # Get response from Ollama API
            speak(bot_response)  # Convert the response to speech
            print(f"Bot: {bot_response}")  # Output to console (you can also send it to the browser)

# ✅ Flask Route for Home Page
@app.route("/")
def index():
    return render_template("index.html")  # Return the home page with a microphone button

# ✅ Flask API Route for Speech Chatbot
@app.route("/chat", methods=["POST"])
def chat():
    user_input = listen()  # Listen to user's voice input and convert it to text
    if user_input:
        response = get_ollama_response(user_input)  # Get response from Ollama API
        speak(response)  # Convert the response to speech
        return jsonify({"user": user_input, "bot": response})  # Return both user and bot response as JSON
    return jsonify({"error": "No speech detected"})  # Error if no speech input is detected

# ✅ Flask Route for retrieving the latest bot response
@app.route("/get_response")
def get_response():
    return jsonify({"bot": bot_response})

if __name__ == "__main__":
    # Start the background thread for continuous listening
    threading.Thread(target=listen_and_respond, daemon=True).start()
    app.run(debug=True)  # Start Flask app in debug mode
