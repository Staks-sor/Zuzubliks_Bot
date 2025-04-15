# Zuzubliks Bot

Telegram-бот для вычесления средней цены.
Цену в боте получаю из xpath далее обрабатываю ее. 

## Требования
- Python 3.11+
- Poetry для управления зависимостями
- Telegram-бот токен (получите через @BotFather)

## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/zuzubliks-bot.git
   ```
   ```bash
   cd zuzubliks-bot
   ```
## Запуск
Создайте .env c содержимым TELEGRAM_BOT_TOKEN= тут ваш апи бот 123445567:буквы
```bash
pip install poetry
```
```bash
poetry install
```
```bash
poetry run python bot.py
```
