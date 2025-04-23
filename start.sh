#!/bin/bash

echo "🚀 Starting bot..."

# Задаваме webhook-а всеки път
python set_webhook.py

# Стартираме Flask приложението
python main.py
