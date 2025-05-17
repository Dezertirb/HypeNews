import logging
import os
from dotenv import load_dotenv
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Загружаем переменные окружения
load_dotenv()

# Устанавливаем ключ OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот, который генерирует новости. Напиши /news.")

# Команда /news
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Генерирую новость...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты пишешь короткие глянцевые новости."},
                {"role": "user", "content": "Напиши короткую новость, актуальную сегодня."}
            ],
            max_tokens=300,
            temperature=0.9
        )
        news_text = response['choices'][0]['message']['content']
        await update.message.reply_text(news_text)

    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при генерации новости.")

# Запуск бота
if __name__ == '__main__':
    TOKEN = os.getenv("TELEGRAM_TOKEN")

    if not TOKEN:
        print("Ошибка: TELEGRAM_TOKEN не найден в .env")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))

    print("Бот запущен...")
    app.run_polling()
