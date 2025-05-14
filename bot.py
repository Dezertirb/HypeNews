import logging
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токены для доступа к Telegram API и OpenAI API
TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Логирование ошибок
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Устанавливаем OpenAI API ключ
openai.api_key = OPENAI_API_KEY

# Функция для получения новостей через OpenAI
def get_news():
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Provide me with the latest news in the technology sector",
            temperature=0.5,
            max_tokens=500
        )
        news = response.choices[0].text.strip()
        return news
    except Exception as e:
        return f"Ошибка при получении новостей: {str(e)}"

# Функция для старта бота
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я твой новостной бот. Напиши /news, чтобы получить последние новости.")

# Функция для получения новостей
def send_news(update: Update, context: CallbackContext):
    news = get_news()
    update.message.reply_text(news)

# Функция для обновления новостей дважды в день
def schedule_news(context: CallbackContext):
    job_queue = context.job_queue
    job_queue.run_daily(send_news, time='09:00', context=context.job.context)
    job_queue.run_daily(send_news, time='18:00', context=context.job.context)

# Основная функция для запуска бота
def main():
    # Создание объекта Updater
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    # Команды бота
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("news", send_news))

    # Планирование новостей дважды в день
    job_queue.run_daily(schedule_news, time='09:00')

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
