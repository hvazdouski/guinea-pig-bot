import os
import telebot
from telebot import types
from thefuzz import process
from flask import Flask, request
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    raise Exception("Токен не найден!")

bot = telebot.TeleBot(TOKEN)

# Расширенная база данных
PLANTS_DB = {
    # --- ОВОЩИ ---
    "морковь": {"cat": "🥬 Овощи", "status": "✅ Можно, но с осторожностью", "info": "Много сахара и витамина А.", "norm": "1-2 раза в неделю.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1598170845058-32b9d6a5da37&w=500"},
    "огурец": {"cat": "🥬 Овощи", "status": "✅ Можно", "info": "Мало пользы, много воды.", "norm": "Ежедневно, но немного.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1449300079323-02e209d9d3a6&w=500"},
    "болгарский перец": {"cat": "🥬 Овощи", "status": "🌟 Суперфуд", "info": "Главный источник витамина С.", "norm": "Ежедневно.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1563565375-f3fdf5efa26f&w=500"},
    "кабачок": {"cat": "🥬 Овощи", "status": "✅ Отлично", "info": "Гипоаллергенный и легкий.", "norm": "Можно ежедневно.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1565257965415-5c62641eb6c9&w=500"},
    "тыква": {"cat": "🥬 Овощи", "status": "✅ Можно", "info": "Полезна для шерсти.", "norm": "1-2 раза в неделю.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1506917728037-b6af011dc3d3&w=500"},
    "помидор": {"cat": "🥬 Овощи", "status": "✅ Можно (мякоть)", "info": "Ботву и зеленые части давать нельзя!", "norm": "Редко, без зелени.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1592924357228-91a4daadcfea&w=500"},
    "картофель": {"cat": "🥬 Овощи", "status": "❌ НЕЛЬЗЯ", "info": "Токсичен для свинок.", "norm": "Никогда.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1518977676601-b53f82aba655&w=500"},
    "салат айсберг": {"cat": "🥬 Овощи", "status": "⚠️ Мало пользы", "info": "Почти одна вода, может вызвать диарею.", "norm": "Очень редко.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1&w=500"},

    # --- ТРАВЫ И ЗЕЛЕНЬ ---
    "петрушка": {"cat": "🌿 Травы", "status": "⚠️ Ограниченно", "info": "Много кальция (риск камней).", "norm": "1-2 раза в неделю.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1626078292069-3001c7d180f6&w=500"},
    "укроп": {"cat": "🌿 Травы", "status": "✅ Отлично", "info": "Улучшает пищеварение.", "norm": "Ежедневно.", "img": "https://wsrv.nl/?url=https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Dill_leaf.jpg/640px-Dill_leaf.jpg"},
    "базилик": {"cat": "🌿 Травы", "status": "✅ Можно", "info": "Ароматная приправа, полезна для иммунитета.", "norm": "Небольшой листочек.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1618164436240-44736640d540&w=500"},
    "мята": {"cat": "🌿 Травы", "status": "✅ Можно", "info": "Освежает дыхание, успокаивает.", "norm": "1-2 веточки.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1626462132938-1f44459245c3&w=500"},
    "шпинат": {"cat": "🌿 Травы", "status": "⚠️ Осторожно", "info": "Много щавелевой кислоты.", "norm": "Не чаще 1 раза в неделю.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1576045057995-568f588f82fb&w=500"},
    "люцерна": {"cat": "🌿 Травы", "status": "⚠️ Только малышам", "info": "Слишком много кальция для взрослых.", "norm": "Только до 6 месяцев.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1591189863430-ab87e120f312&w=500"},
    "одуванчик": {"cat": "🌿 Травы", "status": "✅ Можно всё", "info": "Любимое лакомство.", "norm": "Ежедневно (без химии).", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd&w=500"},
    "ромашка": {"cat": "🌿 Травы", "status": "✅ Полезно", "info": "Успокаивает животик.", "norm": "Как лакомство.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1606041008023-472dfb5e530f&w=500"},
    
    # --- ФРУКТЫ ---
    "яблоко": {"cat": "🍎 Фрукты", "status": "✅ Можно", "info": "Без косточек!", "norm": "1-2 раза в неделю.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6&w=500"},
    "груша": {"cat": "🍎 Фрукты", "status": "✅ Можно", "info": "Мягкая и сладкая.", "norm": "1 раз в неделю.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1615484477778-ca3b77940c25&w=500"},
    "киви": {"cat": "🍎 Фрукты", "status": "🌟 Витамин С", "info": "Очень полезен, но кислый.", "norm": "Кружочек раз в неделю.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1585059895524-72359e06133a&w=500"},
    "ананас": {"cat": "🍎 Фрукты", "status": "✅ Редко", "info": "Содержит ферменты для ЖКТ.", "norm": "Маленький кусочек.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1550258987-190a2d41a8ba&w=500"},
    "дыня": {"cat": "🍎 Фрукты", "status": "✅ Летнее лакомство", "info": "Много воды и сахара.", "norm": "Небольшой ломтик.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=500"}, # Заглушка, лучше найти фото дыни
    "апельсин": {"cat": "🍎 Фрукты", "status": "⚠️ Цитрус", "info": "Может раздражать желудок.", "norm": "Долька раз в 2 недели.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1547514701-42782101795e&w=500"},
    "банан": {"cat": "🍎 Фрукты", "status": "⚠️ Редко", "info": "Очень сладкий, вызывает запоры.", "norm": "Раз в месяц.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1571771896612-424bafef6551&w=500"},

    # --- ЯГОДЫ ---
    "клубника": {"cat": "🍓 Ягоды", "status": "✅ Любимое", "info": "Свинки обожают запах.", "norm": "1 ягодка в неделю.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1464965911861-746a04b4bca6&w=500"},
    "черника": {"cat": "🍓 Ягоды", "status": "✅ Суперфуд", "info": "Полезна для зрения и сердца.", "norm": "3-5 ягодок.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1498557850523-fd3d118b962e&w=500"},
    "малина": {"cat": "🍓 Ягоды", "status": "✅ Можно", "info": "Сладкая и ароматная.", "norm": "2-3 ягодки.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1577069861033-55d04cec4ef5&w=500"},
    "голубика": {"cat": "🍓 Ягоды", "status": "✅ Безопасно", "info": "Меньше сахара, чем в других ягодах.", "norm": "Небольшая горсть.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1498557850523-fd3d118b962e&w=500"}, # Похожа на чернику
    "ежевика": {"cat": "🍓 Ягоды", "status": "✅ Можно", "info": "Богата антиоксидантами.", "norm": "2-3 ягодки.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1615485925763-867862f8021a&w=500"},
    "смородина": {"cat": "🍓 Ягоды", "status": "⚠️ Кисло", "info": "Черная или красная.", "norm": "Веточка с ягодами.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1596363505729-4190a9506133&w=500"},

    # --- ЗАПРЕЩЕНО (SOS) ---
    "авокадо": {"cat": "🆘 SOS", "status": "☠️ СМЕРТЕЛЬНО", "info": "Токсичен для сердца.", "norm": "НИКОГДА.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1523049673857-eb18f1d7b578&w=500"},
    "лук": {"cat": "🆘 SOS", "status": "☠️ ЯД", "info": "Разрушает эритроциты.", "norm": "НИКОГДА.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb&w=500"},
    "шоколад": {"cat": "🆘 SOS", "status": "☠️ ОПАСНО", "info": "Нарушает работу сердца.", "norm": "НИКОГДА.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1511381939415-e44015466834&w=500"},
    "хлеб": {"cat": "🆘 SOS", "status": "❌ Нельзя", "info": "Вызывает вздутие.", "norm": "НИКОГДА.", "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1509440159596-0249088772ff&w=500"}
}

CATEGORIES = ["🥬 Овощи", "🌿 Травы", "🍎 Фрукты", "🍓 Ягоды", "🆘 SOS"]

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for cat in CATEGORIES:
        markup.add(types.InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}"))
    bot.send_message(message.chat.id, "🐹 Привет! Выбери категорию:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data.startswith("cat_"):
        category = call.data.replace("cat_", "")
        items = [name for name, data in PLANTS_DB.items() if data["cat"] == category]
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        for item in items:
            markup.add(types.InlineKeyboardButton(text=item.capitalize(), callback_data=f"item_{item}"))
        markup.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="back"))
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=f"Продукты в категории <b>{category}</b>:", reply_markup=markup, parse_mode='HTML')

    elif call.data.startswith("item_"):
        plant_name = call.data.replace("item_", "")
        show_plant_info(call.message.chat.id, plant_name)

    elif call.data == "back":
        start(call.message)

def show_plant_info(chat_id, plant_name):
    plant = PLANTS_DB.get(plant_name)
    if plant:
        text = f"🌿 <b>{plant_name.capitalize()}</b>\n\n{plant['status']}\n{plant['info']}\n⚖️ {plant['norm']}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="back"))
        try:
            bot.send_photo(chat_id, plant['img'], caption=text, reply_markup=markup, parse_mode='HTML')
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')

# === ОБРАБОТЧИК ТЕКСТОВОГО ПОИСКА (УМНЫЙ ПОИСК) ===
@bot.message_handler(content_types=['text'])
def handle_text_search(message):
    query = message.text.strip().lower()
    
    # Игнорируем команды, чтобы не искать их как растения
    if query.startswith('/'):
        return

    # Получаем список всех названий растений из базы
    all_plants = list(PLANTS_DB.keys())
    
    # Ищем лучшее совпадение с помощью thefuzz
    match, score = process.extractOne(query, all_plants)
    
    # Если совпадение достаточно хорошее (больше 60%)
    if score > 60:
        show_plant_info(message.chat.id, match)
    else:
        bot.send_message(message.chat.id, f"🤔 Я не нашел '{message.text}'. Попробуй написать точнее или выбери категорию кнопкой.")

# Webhook логика для Render
app = Flask(__name__)
@app.route('/', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def home():
    return "🐹 Бот работает!"

if __name__ == '__main__':
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    if WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
