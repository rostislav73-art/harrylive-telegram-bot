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

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Функция за прогнозата за времето
def get_weather(city="Sofia"):
    api_key = OPENWEATHER_API_KEY
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&lang=bg&key={api_key}&contentType=json"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            print("Weather API error:", res.text)
            return "⚠️ Грешка при вземане на прогнозата за времето."
        data = res.json()
        if "days" not in data:
            return "⚠️ Няма прогноза за това място."
        day = data["days"][0]
        temp = day.get("temp")
        conditions = day.get("conditions", "").lower()
        humidity = day.get("humidity")

        icons = {
            "rain": "🌧️",
            "overcast": "☁️",
            "cloud": "☁️",
            "clear": "☀️",
            "snow": "❄️",
            "thunderstorm": "⛈️"
        }
        weather_icon = "🌡️"
        for key, icon in icons.items():
            if key in conditions:
                weather_icon = icon
                break

        return f"{weather_icon} В момента в {city} е {temp}°C с {conditions}. Влажността е {humidity}%.",
    except Exception as e:
        print("Weather API exception:", e)
        return "⚠️ Възникна грешка при връзката с прогнозата."

# Функция за чат с GPT

def ask_gpt(message_text):
    if "времето" in message_text.lower():
        match = re.search(r'в\s+([А-Яа-яA-Za-z\s]+)', message_text)
        city = match.group(1).strip() if match else "Sofia"
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

# Старт команда с меню
@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🌦️ Попитай за времето", callback_data="weather"))
    markup.add(InlineKeyboardButton("💬 Говори с GPT", callback_data="chatgpt"))
    markup.add(InlineKeyboardButton("ℹ️ Помощ", callback_data="help"))
    bot.send_message(message.chat.id, "Избери какво искаш да направиш:", reply_markup=markup)

# Callback бутони
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "weather":
        bot.send_message(call.message.chat.id, "🌦️ Напиши името на града, за да ти дам прогноза!")
    elif call.data == "chatgpt":
        bot.send_message(call.message.chat.id, "💬 Пиши ми въпрос и ще ти отговоря като GPT-4!")
    elif call.data == "help":
        bot.send_message(call.message.chat.id, 
            "ℹ️ Инструкции:\n\n"
            "🌦️ Натисни 'Попитай за времето' и напиши името на град, за да получиш прогноза.\n"
            "💬 Натисни 'Говори с GPT', за да ми зададеш въпрос и ще ти отговоря като ChatGPT.\n"
            "\nПросто напиши какво те интересува!")

# Обработване на съобщения
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    reply = ask_gpt(message.text)
    bot.send_message(message.chat.id, reply)

# Webhook обработка
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
    return {'ok': True}

# Инфо страница
@app.route("/")
def index():
    return "🤖 Bot is live! Use /webhook for Telegram updates."

# Set webhook
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
