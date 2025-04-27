import os
import re
import requests
import wikipediaapi
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

user_context = {}

wiki_bg = wikipediaapi.Wikipedia(
    user_agent="Harrylive_73Bot/1.0 (https://t.me/Harrylive_73Bot)",
    language='bg'
)
wiki_en = wikipediaapi.Wikipedia(
    user_agent="Harrylive_73Bot/1.0 (https://t.me/Harrylive_73Bot)",
    language='en'
)

def detect_language(text):
    if re.search(r'[а-яА-Я]', text):
        return 'bg'
    else:
        return 'en'

def search_wikipedia(query):
    lang = detect_language(query)
    wiki = wiki_bg if lang == 'bg' else wiki_en
    page = wiki.page(query)

    if page.exists():
        summary = page.summary
        if len(summary) > 500:
            summary = summary[:500] + "..."
        return f"📚 *Информация от Wikipedia:*\n\n{summary}"
    else:
        return None

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

def ask_gpt(chat_id, message_text):
    if not message_text.strip():
        return "⚠️ *Моля, въведи съобщение!*"
    try:
        bot.send_chat_action(chat_id, 'typing')  # 🔥 Показва typing

        history = user_context.get(chat_id, [])
        history.append({"role": "user", "content": message_text})
        history = history[-10:]

        response = client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[
                {"role": "system", "content": "Ти си Telegram бот. Днес е април 2025 година. Отговаряй максимално полезно и актуално."}
            ] + history,
            temperature=0.7,
            max_tokens=1500,
        )

        reply_text = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply_text})
        user_context[chat_id] = history
        return reply_text
    except Exception as e:
        print("OpenAI error:", e)
        return "⚠️ *Възникна грешка при връзката с GPT.*"

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🌦️ Попитай за времето", callback_data="weather"))
    markup.add(InlineKeyboardButton("💬 Говори с GPT", callback_data="chatgpt"))
    markup.add(InlineKeyboardButton("ℹ️ Помощ", callback_data="help"))
    bot.send_message(message.chat.id, "🌍 *Добре дошъл! Избери действие от менюто:*", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "weather":
        user_context[chat_id] = [{"role": "system", "content": "awaiting_city"}]
        bot.send_message(chat_id, "✍️ *Напиши името на града, за да ти дам прогноза!*")
    elif call.data == "chatgpt":
        user_context[chat_id] = []
        bot.send_message(chat_id, "💬 *Пиши ми въпрос и ще ти отговоря като GPT-4!* ✨")
    elif call.data == "help":
        bot.send_message(chat_id, "ℹ️ *Инструкции:*\n\n🌦️ Натисни 'Попитай за времето' и напиши град за прогноза.\n💬 Натисни 'Говори с GPT', за да ми зададеш въпрос.\n\n✨ *Просто напиши какво те интересува!* ✍️")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text.startswith("/"):
        bot.send_message(chat_id, "❓ *Неразпозната команда. Използвай менюто /start ✨")
        return

    context = user_context.get(chat_id, [])

    if context and context[0]["content"] == "awaiting_city":
        bot.send_chat_action(chat_id, 'typing')  # 🔥
        reply = get_weather(text)
        bot.send_message(chat_id, reply)
        user_context[chat_id] = []
        return

    lowered = text.lower()

    if "времето в" in lowered:
        try:
            bot.send_chat_action(chat_id, 'typing')  # 🔥
            city = lowered.split("времето в", 1)[1].strip().rstrip("?.,!")
            reply = get_weather(city)
            bot.send_message(chat_id, reply)
        except Exception as e:
            print("City parse error:", e)
            bot.send_message(chat_id, "⚠️ *Моля, задай въпроса отново по правилен начин!*")
        return

    if lowered.startswith(("кой е", "какво е", "кога е", "къде е", "who is", "what is", "when is", "where is")):
        bot.send_chat_action(chat_id, 'typing')  # 🔥
        wiki_info = search_wikipedia(text)
        if wiki_info:
            bot.send_message(chat_id, wiki_info)
            return

    if "хари" in lowered:
        bot.send_chat_action(chat_id, 'typing')  # 🔥
        if "какво правиш" in lowered:
            bot.send_message(chat_id, "🤖 Работя неуморно, за да ти помагам! Какво ще пожелаеш?")
        elif "къде си" in lowered:
            bot.send_message(chat_id, "📍 В дигиталния свят съм, винаги до теб! Какво мога да направя?")
        elif "кой си" in lowered:
            bot.send_message(chat_id, "👋 Аз съм Хари — твоят Telegram помощник, свързан с GPT-4! 🚀")
        else:
            bot.send_message(chat_id, "👋 Здравей! Какво мога да направя за теб?")
        return

    bot.send_chat_action(chat_id, 'typing')  # 🔥
    reply = ask_gpt(chat_id, text)
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

@app.route("/setwebhook", methods=["GET"])
def setwebhook_route():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    try:
        res = rq.get(url)
        if res.status_code == 200 and res.json().get('ok'):
            return "✅ Webhook успешно е настроен!", 200
        else:
            print("Webhook error:", res.text)
            return "❌ Неуспех при настройка на webhook.", 500
    except Exception as e:
        print("Webhook exception:", e)
        return "❌ Грешка при настройка на webhook.", 500

if __name__ == "__main__":
    app.run()
