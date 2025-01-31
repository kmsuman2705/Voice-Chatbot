from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import requests
import threading
import time

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama API URL

# Global variable to store bot's latest response
bot_response = ""

# ✅ Text-to-Speech (Sirf Female Voice - Zira)
def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    
    for voice in voices:
        if "zira" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break
    
    engine.setProperty("rate", 120)  # Slow speech speed
    engine.setProperty("volume", 1)
    engine.say(text)
    engine.runAndWait()
  # 🔹 Wait until speaking finishes

# ✅ Speech-to-Text (Microphone se input lena)
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🔊 Speak now...")  
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio, language="en-US")  # Recognizing speech in English
        print(f"🗣️ You said: {text}")  
        return text
    except sr.UnknownValueError:
        return "I couldn't understand that, please speak again..."  
    except sr.RequestError:
        return "⚠️ Internet error"

# ✅ Ollama API se Jawab lena
# ✅ DeepSeek API se Jawab lena
def get_deepseek_response(user_input):
    payload = {
        "model": "deepseek-r1:1.5b",  # Use the DeepSeek model for faster response
        "prompt": user_input,
        "stream": False,
        "max_tokens": 50,  # Short responses
        "temperature": 0.7  # Balanced randomness
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response found.")
        else:
            return f"⚠️ DeepSeek API ka response nahi aaya. Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"⚠️ API request error: {e}"

# ✅ One by One Conversation Bot
# ✅ One by One Conversation Bot
def listen_and_respond():
    global bot_response
    first_time = True  # Track if it's the first response
    
    while True:
        if first_time:
            bot_response = "Welcome! I am your English Assistant. How can I help you?"
            speak(bot_response)
            first_time = False  # Next time, direct conversation hoga
        else:
            user_input = listen()
            if user_input:
                bot_response = get_deepseek_response(user_input)  # Changed to get_deepseek_response
                speak(bot_response)
                print(f"Bot: {bot_response}")

            time.sleep(1)  # 🔹 Short pause for natural conversation

# ✅ Flask Route for Home Page
@app.route("/")
def index():
    return render_template("index.html")  

# ✅ Flask API Route for Speech Chatbot
@app.route("/chat", methods=["POST"])
def chat():
    user_input = listen()  
    if user_input:
        response = get_ollama_response(user_input)  
        speak(response)  
        return jsonify({"user": user_input, "bot": response})  
    return jsonify({"error": "No speech detected"})  

# ✅ Flask Route for retrieving the latest bot response
@app.route("/get_response")
def get_response():
    return jsonify({"bot": bot_response})

if __name__ == "__main__":
    # ✅ Background thread me bot start ho jayega
    threading.Thread(target=listen_and_respond, daemon=True).start()
    app.run(debug=True)  
