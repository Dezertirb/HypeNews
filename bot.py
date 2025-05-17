import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from datetime import time

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я буду присылать тебе новости дважды в день.")

# Рассылка по расписанию
async def scheduled_news(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.chat_id
    await context.bot.send_message(chat_id=chat_id, text="📰 Вот твоя утренняя подборка новостей!")

def main():
    app = Application.builder().token(TOKEN).job_queue_enabled(True).build()

    app.add_handler(CommandHandler("start", start))

    # Пример: добавим рассылку каждый день в 9:00
    app.job_queue.run_daily(
        scheduled_news,
        time=time(hour=9, minute=0),
        chat_id=123456789  # Замените на ваш Telegram ID
    )

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
