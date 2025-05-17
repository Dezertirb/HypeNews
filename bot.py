import logging
import openai
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    PicklePersistence,
)
from datetime import time

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Установка ключа OpenAI
openai.api_key = OPENAI_API_KEY

# Получение новостей от OpenAI
async def get_news():
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Give me the latest tech news",
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Ошибка при получении новостей: {str(e)}"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if user_id not in context.bot_data.get("subscribers", []):
        context.bot_data.setdefault("subscribers", []).append(user_id)
        await update.message.reply_text("Вы подписаны на рассылку новостей!")
    else:
        await update.message.reply_text("Вы уже подписаны.")
    await update.message.reply_text("Напиши /news, чтобы получить свежие новости.")

# /news
async def send_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = await get_news()
    await update.message.reply_text(news)

# Рассылка по расписанию
async def scheduled_news(context: ContextTypes.DEFAULT_TYPE):
    subscribers = context.bot_data.get("subscribers", [])
    news = await get_news()
    for user_id in subscribers:
        try:
            await context.bot.send_message(chat_id=user_id, text=news)
        except Exception as e:
            logging.warning(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

# Основной запуск
def main():
    persistence = PicklePersistence(filepath="bot_data.pkl")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).persistence(persistence).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", send_news))

    # Ежедневные рассылки
    app.job_queue.run_daily(scheduled_news, time=time(9, 0))
    app.job_queue.run_daily(scheduled_news, time=time(18, 0))

    # Запуск
    app.run_polling()

if __name__ == "__main__":
    main()
