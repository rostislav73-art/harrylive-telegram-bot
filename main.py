import os
import json
import requests
import openai
from functools import lru_cache
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

# --- Инициализация ---
load_dotenv()

# 🔒 Зареждане на конфигурации със защитени проверки
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALLOWED_USERS = list(map(int, os.getenv("ALLOWED_USERS", "6255661181").split(",")))  # Default: твоят chat_id

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ Липсват BOT_TOKEN или OPENAI_API_KEY в .env!")

openai.api_key = OPENAI_API_KEY
app = Flask(__name__)
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# --- Помощни функции ---
@lru_cache(maxsize=100)  # 🚀 Кеширане на повторящи се заявки
def get_ai_response(prompt: str) -> str:
    """Изпраща заявка към OpenAI и връща отговор."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except openai.RateLimitError:
        return "⚠️ Превишен лимит на заявки. Опитай след 1 минута."
    except Exception as e:
        print(f"❌ OpenAI грешка: {e}")
        return "⚠️ Вътрешна грешка при обработка на заявката."

def log_to_file(chat_id: int, request_text: str, response_text: str) -> None:
    """Записва логове във файл в JSON формат."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "chat_id": chat_id,
        "request": request_text,
        "response": response_text
    }
    with open("logs.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

# --- Flask рути ---
@app.route("/")
def home():
    return "🤖 Bot is live! Use /webhook for Telegram updates."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Получен update:", json.dumps(data, indent=2))

    if "message" not in data:
        return jsonify({"ok": True})

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # 🔒 Проверка за разрешен потребител
    if chat_id not in ALLOWED_USERS:
        print(f"🚫 Неразрешен достъп от: {chat_id}")
        return jsonify({"ok": True})

    # 🤖 Обработка на заявката
    reply = get_ai_response(text)
    log_to_file(chat_id, text, reply)

    # 📤 Изпращане на отговор към Telegram (с 3 опита)
    for attempt in range(3):
        try:
            r = requests.post(
                API_URL,
                json={"chat_id": chat_id, "text": reply},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if r.status_code == 200:
                break
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Грешка при опит {attempt + 1}: {e}")

    return jsonify({"ok": True})

# --- Стартиране на сървъра ---
if __name__ == "__main__":
    # 🔄 Задаване на уебхук автоматично (ако се изпълнява локално)
    if os.getenv("SET_WEBHOOK", "False").lower() == "true":
        webhook_url = os.getenv("WEBHOOK_URL")
        if webhook_url:
            requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}/webhook")
    
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("DEBUG", "False") == "True")