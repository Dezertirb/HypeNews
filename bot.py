import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Инициализируем OpenAI клиента
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот, который генерирует текст с помощью OpenAI. Напиши /news чтобы получить новость.")

# Команда /news
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Генерирую новость...")

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты пишешь короткие интересные новости в стиле глянцевого журнала."},
                {"role": "user", "content": "Напиши короткую новость на любую тему, актуальную на сегодня."}
            ],
            max_tokens=300,
            temperature=0.9
        )

        news_text = response.choices[0].message.content
        await update.message.reply_text(news_text)

    except Exception as e:
        logging.error(f"Ошибка при запросе к OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при генерации текста.")

# Главная функция
if __name__ == '__main__':
    TOKEN = os.getenv("TELEGRAM_TOKEN")

    if not TOKEN:
        print("Ошибка: TELEGRAM_TOKEN не найден в .env файле.")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))

    print("Бот запущен...")
    app.run_polling()
