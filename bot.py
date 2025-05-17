import logging
import openai
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)
from datetime import time

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Установка ключа OpenAI
openai.api_key = OPENAI_API_KEY

# Получение новостей от OpenAI
async def get_news():
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Provide me with the latest news in the technology sector",
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Ошибка при получении новостей: {str(e)}"

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой новостной бот. Напиши /news, чтобы получить последние новости.")

# Команда /news
async def send_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = await get_news()
    await update.message.reply_text(news)

# Плановая рассылка новостей
async def scheduled_news(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    news = await get_news()
    await context.bot.send_message(chat_id=chat_id, text=news)

# Основная функция запуска бота
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", send_news))

    # Планируем рассылку дважды в день
    app.job_queue.run_daily(scheduled_news, time=time(9, 0), chat_id=YOUR_CHAT_ID)
    app.job_queue.run_daily(scheduled_news, time=time(18, 0), chat_id=YOUR_CHAT_ID)

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
