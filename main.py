import os
import openai
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

app = Flask(__name__)

def generate_reply(message_text):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message_text}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("OpenAI error:", e)
        return "⚠️ Грешка при генериране на отговор."

@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received data:", data)  # <== логваме заявката в Railway логовете

    try:
        message = data.get("message")
        if not message:
            return {"ok": True}

        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        reply = generate_reply(text)

        payload = {
            "chat_id": chat_id,
            "text": reply
        }
        headers = {'Content-Type': 'application/json'}
        requests.post(API_URL, json=payload, headers=headers)

    except Exception as e:
        print("Webhook error:", e)

    return {"ok": True}

if __name__ == "__main__":
    if os.getenv("RAILWAY_ENVIRONMENT"):
        pass
    else:
        app.run(debug=True)
