import os
import openai
from flask import Flask, request
import requests
from dotenv import load_dotenv

# Зареждане на .env файл
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

app = Flask(__name__)

# Основна функция за генериране на отговор от OpenAI
def generate_reply(message_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message_text}
        ]
    )
    return response.choices[0].message.content

# Обработка на Telegram POST заявките – това е правилният URL!
@app.route("/webhook", methods=["POST"])
def handle_message():
    data = request.get_json()
    try:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        reply = generate_reply(text)
        payload = {"chat_id": chat_id, "text": reply}
        requests.post(API_URL, json=payload)
    except Exception as e:
        print("Error:", e)
    return {"ok": True}

# За да не връща 405 при отваряне през браузъра
@app.route("/", methods=["GET"])
def home():
    return "✅ Telegram bot is running!"

# Само за локален тест
if __name__ == "__main__":
    app.run(debug=True)
