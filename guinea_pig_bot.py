import json
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from flask import Flask, request
import threading

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask приложение для health check на Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Бот работает! 🐹"

@flask_app.route('/health')
def health():
    return "OK", 200

# Загрузка базы данных растений
def load_plants_database():
    with open('plants_database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

PLANTS_DB = load_plants_database()

# Категории на русском
CATEGORY_NAMES = {
    'herbs': '🌿 Травы',
    'vegetables': '🥕 Овощи',
    'fruits': '🍎 Фрукты',
    'berries': '🫐 Ягоды'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = (
        "🐹 Добро пожаловать в бота о питании морских свинок!\n\n"
        "Здесь вы найдете информацию о том, какие растения можно давать вашим питомцам.\n\n"
        "Выберите категорию:"
    )
    
    keyboard = [
        [InlineKeyboardButton(CATEGORY_NAMES['herbs'], callback_data='category_herbs')],
        [InlineKeyboardButton(CATEGORY_NAMES['vegetables'], callback_data='category_vegetables')],
        [InlineKeyboardButton(CATEGORY_NAMES['fruits'], callback_data='category_fruits')],
        [InlineKeyboardButton(CATEGORY_NAMES['berries'], callback_data='category_berries')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список растений в категории"""
    query = update.callback_query
    await query.answer()
    
    category_key = query.data.replace('category_', '')
    plants = PLANTS_DB.get(category_key, [])
    
    if not plants:
        await query.edit_message_text("В этой категории пока нет растений.")
        return
    
    keyboard = []
    for i, plant in enumerate(plants):
        button_text = plant['name']
        callback_data = f"plant_{category_key}_{i}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад в меню", callback_data='back_to_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{CATEGORY_NAMES[category_key]}:\n\nВыберите растение:",
        reply_markup=reply_markup
    )

async def show_plant_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает детальную информацию о растении"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split('_')
    category_key = parts[1]
    plant_index = int(parts[2])
    
    plants = PLANTS_DB.get(category_key, [])
    if plant_index >= len(plants):
        await query.edit_message_text("Растение не найдено.")
        return
    
    plant = plants[plant_index]
    
    details_text = (
        f"🌱 *{plant['name']}*\n\n"
        f"✅ *Польза:*\n{plant['benefits']}\n\n"
        f"⚠️ *Вред/Предостережения:*\n{plant['harm']}\n\n"
        f"📏 *Разрешенное количество:*\n{plant['amount']}"
    )
    
    if plant.get('photo_url'):
        try:
            await query.edit_message_media(
                media={'type': 'photo', 'media': plant['photo_url']},
                reply_markup=None
            )
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=details_text,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка отправки фото: {e}")
            await query.edit_message_text(details_text, parse_mode='Markdown')
    else:
        await query.edit_message_text(details_text, parse_mode='Markdown')
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад к списку", callback_data=f'category_{category_key}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Вернуться к списку:",
        reply_markup=reply_markup
    )

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    await start(update, context)

def run_bot():
    """Запуск бота"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_category, pattern='^category_'))
    application.add_handler(CallbackQueryHandler(show_plant_details, pattern='^plant_'))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern='^back_to_menu$'))
    
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

def start_flask():
    """Запуск Flask для health checks"""
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Запускаем Flask в отдельном потоке для health checks
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запускаем бота
    run_bot()
