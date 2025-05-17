import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from openai import OpenAI

# Настройка
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация OpenAI
client = OpenAI(api_key=OPENAI_KEY)

# Категории
CATEGORIES = ["🎮 Игры", "🏀 Спорт", "🎬 Кино", "📺 Сериалы"]
user_preferences = {}

# Логгирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Генерация новости
def generate_news(categories):
    prompt = f"Составь краткую новость на русском языке по следующим категориям: {', '.join(categories)}."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_preferences[update.effective_user.id] = []
    await update.message.reply_text("Привет! Выбери интересующие категории:", reply_markup=category_menu())

# Меню категорий
def category_menu():
    buttons = [
        [InlineKeyboardButton(cat, callback_data=f"toggle_{cat}")]
        for cat in CATEGORIES
    ]
    buttons.append([InlineKeyboardButton("✅ Готово", callback_data="done")])
    return InlineKeyboardMarkup(buttons)

# Обработка выбора категорий
async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "done":
        selected = user_preferences.get(user_id, [])
        if not selected:
            await query.edit_message_text("Вы не выбрали категории. Попробуйте ещё раз.")
            return
        news = generate_news(selected)
        await query.edit_message_text(f"Ваши категории: {', '.join(selected)}\n\n🗞 {news}")
    else:
        category = data.replace("toggle_", "")
        prefs = user_preferences.setdefault(user_id, [])
        if category in prefs:
            prefs.remove(category)
        else:
            prefs.append(category)
        await query.edit_message_reply_markup(reply_markup=category_menu())

# Команда /news
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    prefs = user_preferences.get(user_id)
    if not prefs:
        await update.message.reply_text("Сначала выберите категории командой /start.")
        return
    news = generate_news(prefs)
    await update.message.reply_text(f"🗞 {news}")

# Основной запуск
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CallbackQueryHandler(category_handler))

    logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling()

if __name__ == "__main__":
    main()
