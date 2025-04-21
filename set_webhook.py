import os
import requests
from dotenv import load_dotenv

# Зареждане на .env файла
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAILWAY_URL = os.getenv("RAILWAY_URL")

# Генериране URL за webhook
webhook_url = f"{RAILWAY_URL}/webhook"
telegram_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

# Изпращане заявка към Telegram
response = requests.post(telegram_api_url, json={"url": webhook_url})

# Отговор
print("==> Отговор от Telegram:")
print("Статус код:", response.status_code)
print("Съобщение:", response.text)
