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
            messages=[
                {"role": "user", "content": message_text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("OpenAI error:", e)
        return "Възникна грешка при генериране на отговор."

@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        reply = generate_reply(text)

        payload = {
            "chat_id": chat_id,
            "text": reply
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_URL, json=payload, headers=headers)
        print("Telegram response:", response.status_code, response.text)

    except Exception as e:
        print("Webhook error:", e)

    return {"ok": True}

if __name__ == "__main__":
    if os.getenv("RAILWAY_ENVIRONMENT"):
        pass  # в Railway gunicorn стартира приложението
    else:
        app.run(debug=True)
