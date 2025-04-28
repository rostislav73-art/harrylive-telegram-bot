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
GROUP_CHAT_ID = -1001234567890  # <-- смени с реалното ID на групата

wiki_bg = wikipediaapi.Wikipedia(
    user_agent="Harrylive_73Bot/1.0 (https://t.me/Harrylive_73Bot)",
    language='bg'
)
wiki_en = wikipediaapi.Wikipedia(
    user_agent="Harrylive_73Bot/1.0 (https://t.me/Harrylive_73Bot)",
    language='en'
)

@bot.message_handler(commands=['getchatid'])
def get_chat_id(message):
    bot.reply_to(message, f"🆔 Chat ID: `{message.chat.id}`")

def detect_language(text):
    if re.search(r'[а-яА-Я]', text):
        return 'bg'
    else:
        return 'en'

... (останалата част от кода остава същата)


def search_wikipedia(query):
    lang = detect_language(query)
    wiki = wiki_bg if lang == 'bg' else wiki_en
    page = wiki.page(query)

    if page.exists():
        summary = page.summary
        if len(summary) > 500:
            summary = summary[:500] + "..."
        return f"\ud83d\udcda *\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043e\u0442 Wikipedia:*\n\n{summary}"
    else:
        return None

def get_weather(city="Sofia"):
    if not city.strip():
        return "\u26a0\ufe0f *\u041c\u043e\u043b\u044f, \u0432\u044a\u0432\u0435\u0434\u0438 \u0432\u0430\u043b\u0438\u0434\u043d\u043e \u0438\u043c\u0435 \u043d\u0430 \u0433\u0440\u0430\u0434!*"
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&lang=bg&key={OPENWEATHER_API_KEY}&contentType=json"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            print("Weather API error:", res.text)
            return "\u26a0\ufe0f *\u0413\u0440\u0435\u0448\u043a\u0430 \u043f\u0440\u0438 \u0432\u0437\u0435\u043c\u0430\u043d\u0435 \u043d\u0430 \u043f\u0440\u043e\u0433\u043d\u043e\u0437\u0430\u0442\u0430 \u0437\u0430 \u0432\u0440\u0435\u043c\u0435\u0442\u043e.*"
        data = res.json()
        if "days" not in data:
            return "\u26a0\ufe0f *\u041d\u044f\u043c\u0430 \u043f\u0440\u043e\u0433\u043d\u043e\u0437\u0430 \u0437\u0430 \u0442\u043e\u0432\u0430 \u043c\u044f\u0441\u0442\u043e.*"
        day = data["days"][0]
        temp = day.get("temp")
        conditions = day.get("conditions", "").lower()
        humidity = day.get("humidity")

        icons = {
            "rain": "\ud83c\udf27\ufe0f", "overcast": "\u2601\ufe0f", "cloud": "\u2601\ufe0f",
            "clear": "\u2600\ufe0f", "snow": "\u2744\ufe0f", "thunderstorm": "\u26c8\ufe0f"
        }
        weather_icon = "\ud83c\udf21\ufe0f"
        for key, icon in icons.items():
            if key in conditions:
                weather_icon = icon
                break

        return f"{weather_icon} *\u0412 \u043c\u043e\u043c\u0435\u043d\u0442\u0430 \u0432 {city} \u0435 {temp}\u00b0C \u0441 {conditions}.*\n\ud83d\udca7 \u0412\u043b\u0430\u0436\u043d\u043e\u0441\u0442: {humidity}%"
    except Exception as e:
        print("Weather API exception:", e)
        return "\u26a0\ufe0f *\u0412\u044a\u0437\u043d\u0438\u043a\u043d\u0430 \u0433\u0440\u0435\u0448\u043a\u0430 \u043f\u0440\u0438 \u0432\u0440\u044a\u0437\u043a\u0430\u0442\u0430 \u0441 \u043f\u0440\u043e\u0433\u043d\u043e\u0437\u0430\u0442\u0430.*"

def ask_gpt(chat_id, message_text):
    if not message_text.strip():
        return "\u26a0\ufe0f *\u041c\u043e\u043b\u044f, \u0432\u044a\u0432\u0435\u0434\u0438 \u0441\u044a\u043e\u0431\u0449\u0435\u043d\u0438\u0435!*"
    try:
        history = user_context.get(chat_id, [])
        history.append({"role": "user", "content": message_text})
        history = history[-10:]

        response = client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[
                {"role": "system", "content": "\u0422\u0438 \u0441\u0438 Telegram \u0431\u043e\u0442. \u0414\u043d\u0435\u0441 \u0435 \u0430\u043f\u0440\u0438\u043b 2025 \u0433\u043e\u0434\u0438\u043d\u0430. \u041e\u0442\u0433\u043e\u0432\u0430\u0440\u044f\u0439 \u043c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u043d\u043e \u043f\u043e\u043b\u0435\u0437\u043d\u043e \u0438 \u0430\u043a\u0442\u0443\u0430\u043b\u043d\u043e."}
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
        return "\u26a0\ufe0f *\u0412\u044a\u0437\u043d\u0438\u043a\u043d\u0430 \u0433\u0440\u0435\u0448\u043a\u0430 \u043f\u0440\u0438 \u0432\u0440\u044a\u0437\u043a\u0430\u0442\u0430 \u0441 GPT.*"

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("\ud83c\udf26\ufe0f \u041f\u043e\u043f\u0438\u0442\u0430\u0439 \u0437\u0430 \u0432\u0440\u0435\u043c\u0435\u0442\u043e", callback_data="weather"))
    markup.add(InlineKeyboardButton("\ud83d\udcac \u0413\u043e\u0432\u043e\u0440\u0438 \u0441 GPT", callback_data="chatgpt"))
    markup.add(InlineKeyboardButton("\u2139\ufe0f \u041f\u043e\u043c\u043e\u0449", callback_data="help"))
    bot.send_message(message.chat.id, "\ud83c\udf0d *\u0414\u043e\u0431\u0440\u0435 \u0434\u043e\u0448\u044a\u043b! \u0418\u0437\u0431\u0435\u0440\u0438 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u043e\u0442 \u043c\u0435\u043d\u044e\u0442\u043e:*", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "weather":
        user_context[chat_id] = [{"role": "system", "content": "awaiting_city"}]
        bot.send_message(chat_id, "\u270d\ufe0f *\u041d\u0430\u043f\u0438\u0448\u0438 \u0438\u043c\u0435\u0442\u043e \u043d\u0430 \u0433\u0440\u0430\u0434\u0430, \u0437\u0430 \u0434\u0430 \u0442\u0438 \u0434\u0430\u043c \u043f\u0440\u043e\u0433\u043d\u043e\u0437\u0430!*")
    elif call.data == "chatgpt":
        user_context[chat_id] = []
        bot.send_message(chat_id, "\ud83d\udcac *\u041f\u0438\u0448\u0438 \u043c\u0438 \u0432\u044a\u043f\u0440\u043e\u0441 \u0438 \u0449\u0435 \u0442\u0438 \u043e\u0442\u0433\u043e\u0432\u043e\u0440\u044f \u043a\u0430\u0442\u043e GPT-4!* \u2728")
    elif call.data == "help":
        bot.send_message(chat_id, "\u2139\ufe0f *\u0418\u043d\u0441\u0442\u0440\u0443\u043a\u0446\u0438\u0438:*\n\n\ud83c\udf26\ufe0f \u041d\u0430\u0442\u0438\u0441\u043d\u0438 'Попитай за времето', за да получиш прогноза.\n\ud83d\udcac \u041d\u0430\u0442\u0438\u0441\u043d\u0438 'Говори с GPT', за да питаш AI въпроси.\n\ud83d\udcda \u0418\u043b\u0438 \u043f\u0440\u043e\u0441\u0442\u043e \u0438\u0437\u043f\u0440\u0430\u0442\u0438 \u0434\u0443\u043c\u0430 \u0437\u0430 \u0442\u044a\u0440\u0441\u0435\u043d\u0435 \u0432 Wikipedia!")

@bot.message_handler(func=lambda message: True)
def text_handler(message):
    chat_id = message.chat.id
    history = user_context.get(chat_id, [])

    if history and history[0]["content"] == "awaiting_city":
        city = message.text
        weather_info = get_weather(city)
        bot.send_message(chat_id, weather_info)
        user_context[chat_id] = []
    else:
        reply = ask_gpt(chat_id, message.text)
        if reply is None:
            reply = search_wikipedia(message.text) or "\u2753 *\u041d\u0435 \u0443\u0441\u043f\u044f\u0445 \u0434\u0430 \u043d\u0430\u043c\u0435\u0440\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f.*"
        bot.send_message(chat_id, reply)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Invalid content type', 403

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
