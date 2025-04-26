
import os
import re
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEBHOOK_URL = "https://web-production-f7800.up.railway.app/webhook"

client = OpenAI(api_key=OPENAI_API_KEY)

def get_weather(city="Sofia"):
    api_key = OPENWEATHER_API_KEY
    city = city.strip().replace(" ", "%20")
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&lang=bg&key={api_key}&contentType=json"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        if "days" not in data:
            return "Не мога да намеря прогнозата за това място."
        day = data["days"][0]
        temp = day["temp"]
        conditions = day["conditions"]
        humidity = day["humidity"]
        return f"В момента в {city} е {temp} °C с {conditions}. Влажността е {humidity}%."
    except Exception as e:
        print("Weather API error:", e)
        return "⚠️ Възникна грешка при вземане на прогнозата."

def ask_gpt(message_text):
    if "времето" in message_text.lower():
        match = re.search(r'в\s+([А-Яа-яA-Za-z]+)', message_text)
        city = match.group(1) if match else "Sofia"
        return get_weather(city)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ти си полезен Telegram бот, който помага на потребителя."},
                {"role": "user", "content": message_text}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print("OpenAI error:", e)
        return "⚠️ Възникна грешка при връзката с GPT."

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram error:", e)

@app.route("/")
def index():
    return "🧙‍♂️ Bot is live! Use /webhook for Telegram updates."

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        reply = ask_gpt(text)
        send_message(chat_id, reply)
    return {"ok": True}

def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    try:
        res = requests.get(url)
        print("Webhook set:", res.json())
    except Exception as e:
        print("Failed to set webhook:", e)

set_webhook()

if __name__ == "__main__":
    app.run(debug=True)
