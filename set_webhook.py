import os
import requests
from dotenv import load_dotenv

# Зареждаме .env файла
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAILWAY_URL = os.getenv("RAILWAY_URL")

# Сглобяваме webhook URL-то
webhook_url = f"{RAILWAY_URL}/webhook"
telegram_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

# Изпращаме заявка към Telegram API
response = requests.post(telegram_api_url, json={"url": webhook_url})

# Отпечатваме резултата
print("==> Отговор от Telegram:")
print("Статус код:", response.status_code)
print("Съобщение:", response.text)
