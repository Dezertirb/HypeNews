import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import httpx

load_dotenv()

# Настройки
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

user_categories = {}

# Варианты интересов
ALL_CATEGORIES = ["Игры", "Спорт", "Кино", "Сериалы"]

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_categories[user_id] = []
    await update.message.reply_text("Привет! Выбери категории новостей:", reply_markup=category_keyboard(user_id))

def category_keyboard(user_id):
    keyboard = [
        [InlineKeyboardButton(f"{'✅' if c in user_categories.get(user_id, []) else '☐'} {c}", callback_data=c)]
        for c in ALL_CATEGORIES
    ]
    keyboard.append([InlineKeyboardButton("Готово", callback_data="done")])
    return InlineKeyboardMarkup(keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    category = query.data
    if category == "done":
        await query.edit_message_text("Категории сохранены. Используйте /news для получения новостей.")
        return

    user_cats = user_categories.setdefault(user_id, [])
    if category in user_cats:
        user_cats.remove(category)
    else:
        user_cats.append(category)

    await query.edit_message_reply_markup(reply_markup=category_keyboard(user_id))

async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    categories = user_categories.get(user_id, [])
    if not categories:
        await update.message.reply_text("Вы не выбрали категории. Введите /start.")
        return

    prompt = f"Подбери свежие и интересные новости в категориях: {', '.join(categories)}. Представь их как для глянцевого журнала."
    
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            news = result["choices"][0]["message"]["content"]
            await update.message.reply_text(news)
    except Exception as e:
        logger.error(f"Ошибка при получении новостей: {e}")
        await update.message.reply_text("Произошла ошибка при получении новостей.")

def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", get_news))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
