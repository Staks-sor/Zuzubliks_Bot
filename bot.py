import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
import pandas as pd
from pathlib import Path
from database import Database
from parser import calculate_average_prices
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = ('.xlsx', '.xls')
REQUIRED_FIELDS = ['title', 'url', 'xpath']
ROWS_PER_MESSAGE = 5

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    upload_button = InlineKeyboardButton("Загрузить файл", callback_data="upload")
    keyboard = [[upload_button]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Нажмите кнопку для загрузки Excel-файла:", reply_markup=reply_markup
    )

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "upload":
        await query.message.reply_text(
            "Пожалуйста, загрузите Excel-файл (.xlsx или .xls) с полями: title, url, xpath (цена должна быть в xpath)."
        )

async def is_excel_file(file_name: str) -> bool:
    return file_name.lower().endswith(ALLOWED_EXTENSIONS)

async def validate_excel_columns(df: pd.DataFrame) -> bool:
    return all(column in df.columns for column in REQUIRED_FIELDS)

async def send_chunked_message(update: Update, df: pd.DataFrame) -> None:
    for chunk_start in range(0, len(df), ROWS_PER_MESSAGE):
        chunk = df[chunk_start:chunk_start + ROWS_PER_MESSAGE]
        chunk_lines = [
            f"{idx + 1}. {row['title']} ({row['url']}) - Цена: {row['xpath']}"
            for idx, (_, row) in enumerate(chunk.iterrows(), start=chunk_start)
        ]
        chunk_text = "\n".join(chunk_lines)
        await update.message.reply_text(f"Содержимое файла:\n{chunk_text}")

async def save_to_database(df: pd.DataFrame) -> None:
    database = Database()
    for _, row in df.iterrows():
        database.save_site(row['title'], row['url'], row['xpath'])

async def format_average_prices(avg_prices: list) -> str:
    message = "Средние цены по сайтам:\n"
    for idx, site in enumerate(avg_prices, start=1):
        avg_price = site['average_price']
        price_display = f"{avg_price:.2f}" if avg_price else "Нет данных"
        message += f"{idx}. {site['title']} ({site['url']}): {price_display}\n"
    return message

async def handle_uploaded_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message.document:
        await update.message.reply_text("Пожалуйста, загрузите файл!")
        return

    file_name = update.message.document.file_name

    if not await is_excel_file(file_name):
        await update.message.reply_text(
            "Я такое не читаю. Пожалуйста, загрузите Excel-файл (.xlsx или .xls) с полями: title, url, xpath (цена должна быть в xpath)."
        )
        return

    file = await update.message.document.get_file()
    file_path = UPLOAD_DIRECTORY / file_name
    await file.download_to_drive(file_path)

    try:
        df = pd.read_excel(file_path, engine='openpyxl')

        if not await validate_excel_columns(df):
            await update.message.reply_text(
                "Ошибка: Файл должен содержать столбцы title, url, xpath (цена должна быть в xpath)."
            )
            return

        await send_chunked_message(update, df)

        await update.message.reply_text("Рассчитываю среднюю цену, подождите")

        await save_to_database(df)

        average_prices = calculate_average_prices(df)

        prices_message = await format_average_prices(average_prices)
        await update.message.reply_text(prices_message)

    except Exception as error:
        await update.message.reply_text(f"Ошибка обработки файла: {str(error)}")

async def handle_non_document_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Я такое не читаю. Пожалуйста, загрузите Excel-файл (.xlsx или .xls) с полями: title, url, xpath (цена должна быть в xpath)."
    )

def setup_bot() -> Application:

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("Не найден TELEGRAM_BOT_TOKEN в файле .env. Пожалуйста, добавьте его.")

    bot = Application.builder().token(bot_token).build()

    bot.add_handler(CommandHandler("start", start_command))
    bot.add_handler(CallbackQueryHandler(handle_button_click))
    bot.add_handler(MessageHandler(filters.Document.ALL, handle_uploaded_file))
    bot.add_handler(MessageHandler(~filters.Document.ALL & ~filters.COMMAND, handle_non_document_message))

    return bot

def main() -> None:
    bot = setup_bot()
    bot.run_polling()

if __name__ == "__main__":
    main()