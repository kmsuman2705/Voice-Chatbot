from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import requests
import threading
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama API URL

# Global variable to store bot's latest response
bot_response = ""

# ✅ Text-to-Speech (Female Voice - Zira)
def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    for voice in voices:
        if "zira" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break
    engine.setProperty("rate", 120)
    engine.setProperty("volume", 1)
    engine.say(text)
    engine.runAndWait()

# ✅ Speech-to-Text (Microphone input)
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🔊 Speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"🗣️ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return "I couldn't understand that, please speak again..."
    except sr.RequestError:
        print("❌ API request error")
        return "⚠️ Internet error"

# ✅ Ollama API Response
def get_deepseek_response(user_input):
    payload = {
        "model": "english-helper",
        "prompt": f"Reply concisely: {user_input}",
        "stream": False,
        "max_tokens": 10,  # Try keeping it minimal
        "temperature": 0.7
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            full_response = data.get("response", "No response found.")
            
            # Trim response to first sentence
            short_response = full_response.split(".")[0]  
            
            print("Bot Response:", short_response)
            return short_response
        else:
            print("API Error:", response.status_code)
            return f"⚠️ DeepSeek API error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
        return f"⚠️ API request error: {e}"


# ✅ One-by-One Conversation Bot
def listen_and_respond():
    global bot_response
    first_time = True
    
    while True:
        if first_time:
            bot_response = "Good morning!"  # Respond with Good morning
            speak(bot_response)
            first_time = False
        else:
            user_input = listen()
            if user_input.strip():
                bot_response = get_deepseek_response(user_input)
                speak(bot_response)
                print(f"[{get_timestamp()}] Bot: {bot_response}")
            time.sleep(1)

# Function to get timestamp
def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# ✅ Flask Route for Home Page
@app.route("/")
def index():
    return render_template("index.html")  

# ✅ Flask API Route for Speech Chatbot
@app.route("/chat", methods=["POST"])
def chat():
    global bot_response
    user_input = listen()
    if user_input.strip():
        # Handle "Good morning" with a simple response
        if user_input.lower() == "good morning":
            response = "Good morning!"  # Respond with just "Good morning"
        else:
            response = get_deepseek_response(user_input)
        
        # Clean up response text
        response = response.replace("<think>", "").replace("</think>", "")
        speak(response)
        bot_response = response
        print(f"User: {user_input}")
        print(f"Bot: {response}")
        return jsonify({"user": user_input, "bot": response})
    else:
        return jsonify({"error": "No speech detected"})

if __name__ == "__main__":
    thread = threading.Thread(target=listen_and_respond, daemon=True)
    thread.start()
    app.run(debug=True)
