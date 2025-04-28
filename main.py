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
        bot.send_message(chat_id, "ℹ️ *Инструкции:*\n\n🌦️ Натисни 'Попитай за времето', за да получиш прогноза.\n💬 Натисни 'Говори с GPT', за да питаш AI въпроси.\n📚 Или просто изпрати дума за търсене в Wikipedia!")

@bot.message_handler(commands=['post'])
def gpt_direct_post(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "❌ Използвай тази команда само в личен чат.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Моля, напиши тема! Пример: `/post здраве`")
        return

    topic = parts[1].strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[
                {"role": "system", "content": "Ти си креативен писател на постове за социални мрежи. Пиши позитивен, вдъхновяващ пост на български за зададена тема. Постът трябва да е кратък, мотивиращ и с емотикони."},
                {"role": "user", "content": f"Напиши пост на тема: {topic}"}
            ],
            temperature=0.8,
            max_tokens=300,
        )

        post_text = response.choices[0].message.content.strip()

        bot.send_message(GROUP_CHAT_ID, post_text, parse_mode='Markdown')
        bot.reply_to(message, "✅ Постът е генериран и публикуван директно в групата!")

    except Exception as e:
        print("GPT Post Error:", e)
        bot.reply_to(message, "⚠️ Възникна грешка при публикуване.")

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
            reply = search_wikipedia(message.text) or "❓ *Не успях да намеря информация.*"
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
