from flask import Flask, request
import os
from dotenv import load_dotenv
import telebot
from telebot import types
from thefuzz import process

# Загружаем переменные из .env файла (для локального запуска)
load_dotenv()

# Берем токен из переменной окружения (для Render)
TOKEN = os.getenv('TOKEN')

if not TOKEN:
    raise Exception("Токен не найден! Проверь настройки.")

bot = telebot.TeleBot(TOKEN)

# База данных растений/овощей/фруктов
PLANTS_DB = {
    "морковь": {
        "category": "🥬 Овощи",
        "status": "✅ Можно, но с осторожностью",
        "info": "Содержит много сахара и витамина А. Избыток сахара вреден.",
        "norm": "1-2 раза в неделю, небольшой кусочек.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Carrots_of_different_colors.jpg/640px-Carrots_of_different_colors.jpg"
    },
    "огурец": {
        "category": "🥬 Овощи",
        "status": "✅ Можно",
        "info": "Состоит из воды. Неочищенный огурец давать нельзя!",
        "norm": "Можно ежедневно, но в меру.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Cucumber_cross_section.jpg/640px-Cucumber_cross_section.jpg"
    },
    "болгарский перец": {
        "category": "🥬 Овощи",
        "status": "🌟 Суперфуд (Обязательно)",
        "info": "Богат витамином С. Обязательно включайте в рацион!",
        "norm": "Можно ежедневно, семена убрать.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Bell_peppers_-_variety_of_colours.jpg/640px-Bell_peppers_-_variety_of_colours.jpg"
    },
    "капуста": {
        "category": "🥬 Овощи",
        "status": "❌ Опасно / Нельзя",
        "info": "Вызывает сильное газообразование и вздутие живота.",
        "norm": "Полностью исключить из рациона.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Cabbage_and_cross_section_on_white.jpg/640px-Cabbage_and_cross_section_on_white.jpg"
    },
    "петрушка": {
        "category": "🌿 Травы",
        "status": "⚠️ Ограниченно",
        "info": "Содержит много кальция. Риск камней в мочевом пузыре.",
        "norm": "Не чаще 1-2 раз в неделю, маленькая веточка.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Petroselinum_crispum_002.JPG/640px-Petroselinum_crispum_002.JPG"
    },
    "укроп": {
        "category": "🌿 Травы",
        "status": "✅ Отлично",
        "info": "Полезная зелень, улучшает пищеварение.",
        "norm": "Можно ежедневно, небольшой пучок.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Dill_leaf.jpg/640px-Dill_leaf.jpg"
    },
    "яблоко": {
        "category": "🍎 Фрукты",
        "status": "✅ Можно, но с осторожностью",
        "info": "Содержит много сахара. Косточки давать НЕЛЬЗЯ.",
        "norm": "1-2 раза в неделю, ломтик без косточек.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Red_Apple.jpg/640px-Red_Apple.jpg"
    },
    "банан": {
        "category": "🍎 Фрукты",
        "status": "⚠️ Редко",
        "info": "Очень сладкий. Может вызвать проблемы с ЖКТ.",
        "norm": "1 раз в месяц, маленький кружок.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/640px-Banana-Single.jpg"
    }
}

# Список категорий для меню
CATEGORIES = ["🥬 Овощи", "🌿 Травы", "🍎 Фрукты"]

@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    # Создаем клавиатуру с категориями
    markup = types.InlineKeyboardMarkup(row_width=2)
    for cat in CATEGORIES:
        btn = types.InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}")
    markup.add(*[types.InlineKeyboardButton(text=c, callback_data=f"cat_{c}") for c in CATEGORIES])
    
    text = (
        "🐹 <b>Привет! Я умный бот по питанию морских свинок.</b>\n\n"
        "Выбери категорию ниже, чтобы увидеть список продуктов, "
        "или просто напиши название растения текстом (я пойму даже с опечатками!)."
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data.startswith("cat_"):
        category = call.data.replace("cat_", "")
        
        # Фильтруем продукты по выбранной категории
        items_in_cat = [name for name, data in PLANTS_DB.items() if data["category"] == category]
        
        if items_in_cat:
            markup = types.InlineKeyboardMarkup(row_width=2)
            for item in items_in_cat:
                # callback_data для продукта
                markup.add(types.InlineKeyboardButton(text=item.capitalize(), callback_data=f"item_{item}"))
            
            # Кнопка "Назад"
            back_btn = types.InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")
            markup.add(back_btn)
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  text=f"Выбери продукт из категории <b>{category}</b>:", 
                                  reply_markup=markup, parse_mode='HTML')
    
    elif call.data.startswith("item_"):
        plant_name = call.data.replace("item_", "")
        show_plant_info(call.message.chat.id, plant_name, call.message.message_id)
    
    elif call.data == "back_to_menu":
        start_message(call.message)

# Функция для показа информации о растении
def show_plant_info(chat_id, plant_name, msg_id=None):
    plant = PLANTS_DB.get(plant_name)
    if not plant:
        return
        
    response_text = (
        f"🌿 <b>{plant_name.capitalize()}</b>\n\n"
        f"📊 <b>Статус:</b> {plant['status']}\n"
        f"ℹ️ <b>Информация:</b> {plant['info']}\n"
        f"⚖️ <b>Норма потребления:</b> {plant['norm']}"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🔙 Выбрать другой", callback_data="back_to_menu"))

    try:
        bot.send_photo(
            chat_id=chat_id, 
            photo=plant['image_url'], 
            caption=response_text, 
            reply_markup=markup, 
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"Ошибка фото: {e}")
        bot.send_message(chat_id, response_text, reply_markup=markup, parse_mode='HTML')

# Обработчик текстовых сообщений (Умный поиск)
@bot.message_handler(content_types=['text'])
def handle_text(message):
    query = message.text.strip().lower()
    
    # Получаем список всех названий растений из базы
    all_plants = list(PLANTS_DB.keys())
    
    # Ищем лучшее совпадение
    match, score = process.extractOne(query, all_plants)
    
    # Если совпадение достаточно хорошее (больше 60%)
    if score > 60:
        show_plant_info(message.chat.id, match)
    else:
        bot.send_message(message.chat.id, f"🤔 Я не нашел '{message.text}'. Попробуй написать точнее или выбери категорию кнопкой.")

if __name__ == '__main__':
    print("Умный бот запущен...")

# === НАСТРОЙКА WEBHOOK ДЛЯ RENDER ===
app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    """Этот адрес будет принимать сообщения от Telegram"""
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def home():
    """Простая заглушка для проверки работы сервиса"""
    return "🐹 Бот для морских свинок работает!"

if __name__ == '__main__':
    # Устанавливаем вебхук при запуске
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    if WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)
        print(f"Webhook установлен на: {WEBHOOK_URL}")
    
    # Запускаем сервер на порту, который дает Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)



