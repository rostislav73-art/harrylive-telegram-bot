import os
import re
import requests
from flask import Flask, request
from openai import OpenAI
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEBHOOK_URL = "https://web-production-f7800.up.railway.app/webhook"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='Markdown')
client = OpenAI(api_key=OPENAI_API_KEY)

user_context = {}  # нов речник за контекста на потребителите

def get_weather(city="Sofia"):
    if not city.strip():
        return "⚠️ *Моля, въведи валидно име на град!*"
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&lang=bg&key={OPENWEATHER_API_KEY}&contentType=json"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            print("Weather API error:", res.text)
            return "⚠️ *Грешка при вземане на прогнозата за времето.*"
        data = res.json()
        if "days" not in data:
            return "⚠️ *Няма прогноза за това място.*"
        day = data["days"][0]
        temp = day.get("temp")
        conditions = day.get("conditions", "").lower()
        humidity = day.get("humidity")

        icons = {
            "rain": "🌧️", "overcast": "☁️", "cloud": "☁️",
            "clear": "☀️", "snow": "❄️", "thunderstorm": "⛈️"
        }
        weather_icon = "🌡️"
        for key, icon in icons.items():
            if key in conditions:
                weather_icon = icon
                break

        return f"{weather_icon} *В момента в {city} е {temp}°C с {conditions}.*\n💧 Влажност: {humidity}%"
    except Exception as e:
        print("Weather API exception:", e)
        return "⚠️ *Възникна грешка при връзката с прогнозата.*"

def ask_gpt(message_text):
    if not message_text.strip():
        return "⚠️ *Моля, въведи съобщение!*"
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
        return "⚠️ *Възникна грешка при връзката с GPT.*"

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("\ud83c\udf26️ Попитай за времето", callback_data="weather"))
    markup.add(InlineKeyboardButton("\ud83d\udcac Говори с GPT", callback_data="chatgpt"))
    markup.add(InlineKeyboardButton("\u2139\ufe0f Помощ", callback_data="help"))
    bot.send_message(message.chat.id, "\ud83c\udf10 *Добре дошъл! Избери действие от менюто:*", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "weather":
        user_context[chat_id] = "awaiting_city"
        bot.send_message(chat_id, "✍️ *Напиши името на града, за да ти дам прогноза!*")
    elif call.data == "chatgpt":
        user_context[chat_id] = "chatgpt"
        bot.send_message(chat_id, "\ud83d\udcac *Пиши ми въпрос и ще ти отговоря като GPT-4!* ✨")
    elif call.data == "help":
        bot.send_message(chat_id, "\u2139\ufe0f *Инструкции:*\n\n\ud83c\udf26️ Натисни 'Попитай за времето' и напиши град за прогноза.\n\ud83d\udcac Натисни 'Говори с GPT', за да ми зададеш въпрос.\n\n✨ *Просто напиши какво те интересува!* ✍️")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text.startswith("/"):
        bot.send_message(chat_id, "❓ *Неразпозната команда. Използвай менюто /start ✨")
        return

    state = user_context.get(chat_id)

    if state == "awaiting_city":
        reply = get_weather(text)
        bot.send_message(chat_id, reply)
        user_context[chat_id] = None
    else:
        reply = ask_gpt(text)
        bot.send_message(chat_id, reply)

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
    return {'ok': True}

@app.route("/")
def index():
    return "🤖 Bot is live! Use /webhook for Telegram updates."

import requests as rq

def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    try:
        res = rq.get(url)
        print("Webhook set:", res.json())
    except Exception as e:
        print("Failed to set webhook:", e)

set_webhook()

if __name__ == "__main__":
    app.run(debug=True)
