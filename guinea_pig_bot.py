import os
import telebot
from telebot import types
from thefuzz import process
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    raise Exception("Токен не найден!")

bot = telebot.TeleBot(TOKEN)

# ПОЛНАЯ БАЗА ДАННЫХ С ЧАСТЯМИ РАСТЕНИЙ
PLANTS_DB = {
    # --- ОВОЩИ ---
    "морковь": {
        "cat": "🥬 Овощи",
        "parts": {
            "корнеплод": {"status": "✅ Можно, но с осторожностью", "info": "Много сахара и витамина А.", "norm": "1-2 раза в неделю."},
            "ботва": {"status": "✅ Отлично", "info": "Полезная зелень, богата калием.", "norm": "Ежедневно, небольшой пучок."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1598170845058-32b9d6a5da37&w=500"
    },
    "огурец": {
        "cat": "🥬 Овощи",
        "parts": {
            "плод": {"status": "✅ Можно", "info": "Мало пользы, много воды. Кожуру лучше чистить.", "norm": "Ежедневно, но немного."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1449300079323-02e209d9d3a6&w=500"
    },
    "болгарский перец": {
        "cat": "🥬 Овощи",
        "parts": {
            "плод": {"status": "🌟 Суперфуд", "info": "Главный источник витамина С. Семена убрать.", "norm": "Ежедневно."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1563565375-f3fdf5efa26f&w=500"
    },
    "кабачок": {
        "cat": "🥬 Овощи",
        "parts": {
            "плод": {"status": "✅ Отлично", "info": "Гипоаллергенный и легкий.", "norm": "Можно ежедневно."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1565257965415-5c62641eb6c9&w=500"
    },
    "тыква": {
        "cat": "🥬 Овощи",
        "parts": {
            "мякоть": {"status": "✅ Можно", "info": "Полезна для шерсти.", "norm": "1-2 раза в неделю."},
            "семечки": {"status": "⚠️ Редко", "info": "Очищенные, как лакомство.", "norm": "1-2 штучки."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1506917728037-b6af011dc3d3&w=500"
    },
    "помидор": {
        "cat": "🥬 Овощи",
        "parts": {
            "мякоть": {"status": "✅ Можно", "info": "Только спелые красные плоды.", "norm": "Редко."},
            "ботва/листья": {"status": "❌ НЕЛЬЗЯ", "info": "Содержат соланин.", "norm": "Никогда."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1592924357228-91a4daadcfea&w=500"
    },
    "картофель": {
        "cat": "🆘 SOS",
        "parts": {
            "клубень": {"status": "❌ НЕЛЬЗЯ", "info": "Токсичен в сыром виде.", "norm": "Никогда."},
            "ботва": {"status": "☠️ ЯД", "info": "Смертельно опасна.", "norm": "КАТЕГОРИЧЕСКИ НЕЛЬЗЯ."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1518977676601-b53f82aba655&w=500"
    },
    "салат айсберг": {
        "cat": "🥬 Овощи",
        "parts": {
            "листья": {"status": "⚠️ Мало пользы", "info": "Почти одна вода, может вызвать диарею.", "norm": "Очень редко."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1&w=500"
    },
    "капуста": {
        "cat": "🥬 Овощи",
        "parts": {
            "листья": {"status": "❌ Опасно", "info": "Вызывает сильное газообразование.", "norm": "Исключить."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1550170560-14e4f775c218&w=500"
    },

    # --- ТРАВЫ И ЗЕЛЕНЬ ---
    "петрушка": {
        "cat": "🌿 Травы",
        "parts": {
            "листья": {"status": "⚠️ Ограниченно", "info": "Много кальция (риск камней).", "norm": "1-2 раза в неделю."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1626078292069-3001c7d180f6&w=500"
    },
    "укроп": {
        "cat": "🌿 Травы",
        "parts": {
            "зелень": {"status": "✅ Отлично", "info": "Улучшает пищеварение.", "norm": "Ежедневно."}
        },
        "img": "https://wsrv.nl/?url=https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Dill_leaf.jpg/640px-Dill_leaf.jpg"
    },
    "базилик": {
        "cat": "🌿 Травы",
        "parts": {
            "листья": {"status": "✅ Можно", "info": "Ароматная приправа, полезна для иммунитета.", "norm": "Небольшой листочек."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1618164436240-44736640d540&w=500"
    },
    "мята": {
        "cat": "🌿 Травы",
        "parts": {
            "листья": {"status": "✅ Можно", "info": "Освежает дыхание, успокаивает.", "norm": "1-2 веточки."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1626462132938-1f44459245c3&w=500"
    },
    "шпинат": {
        "cat": "🌿 Травы",
        "parts": {
            "листья": {"status": "⚠️ Осторожно", "info": "Много щавелевой кислоты.", "norm": "Не чаще 1 раза в неделю."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1576045057995-568f588f82fb&w=500"
    },
    "люцерна": {
        "cat": "🌿 Травы",
        "parts": {
            "свежая трава": {"status": "⚠️ Только малышам", "info": "Слишком много кальция для взрослых.", "norm": "Только до 6 месяцев."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1591189863430-ab87e120f312&w=500"
    },
    "одуванчик": {
        "cat": "🌿 Травы",
        "parts": {
            "цветы": {"status": "✅ Можно всё", "info": "Сладкие и любимые.", "norm": "Ежедневно."},
            "листья": {"status": "✅ Можно всё", "info": "Горчат, но очень полезны.", "norm": "Ежедневно."},
            "стебли": {"status": "✅ Можно всё", "info": "Содержат молочко.", "norm": "Ежедневно."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd&w=500"
    },
    "ромашка": {
        "cat": "🌿 Травы",
        "parts": {
            "цветы": {"status": "✅ Полезно", "info": "Успокаивает животик.", "norm": "Как лакомство."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1606041008023-472dfb5e530f&w=500"
    },
    
    # --- ФРУКТЫ ---
    "яблоко": {
        "cat": "🍎 Фрукты",
        "parts": {
            "мякоть": {"status": "✅ Можно", "info": "Без косточек!", "norm": "1-2 раза в неделю."},
            "косточки": {"status": "❌ НЕЛЬЗЯ", "info": "Содержат цианид.", "norm": "Никогда."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6&w=500"
    },
    "груша": {
        "cat": "🍎 Фрукты",
        "parts": {
            "мякоть": {"status": "✅ Можно", "info": "Мягкая и сладкая.", "norm": "1 раз в неделю."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1615484477778-ca3b77940c25&w=500"
    },
    "киви": {
        "cat": "🍎 Фрукты",
        "parts": {
            "мякоть": {"status": "🌟 Витамин С", "info": "Очень полезен, но кислый.", "norm": "Кружочек раз в неделю."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1585059895524-72359e06133a&w=500"
    },
    "ананас": {
        "cat": "🍎 Фрукты",
        "parts": {
            "мякоть": {"status": "✅ Редко", "info": "Содержит ферменты для ЖКТ.", "norm": "Маленький кусочек."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1550258987-190a2d41a8ba&w=500"
    },
    "дыня": {
        "cat": "🍎 Фрукты",
        "parts": {
            "мякоть": {"status": "✅ Летнее лакомство", "info": "Много воды и сахара.", "norm": "Небольшой ломтик."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=500" 
    },
    "апельсин": {
        "cat": "🍎 Фрукты",
        "parts": {
            "мякоть": {"status": "⚠️ Цитрус", "info": "Может раздражать желудок.", "norm": "Долька раз в 2 недели."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1547514701-42782101795e&w=500"
    },
    "банан": {
        "cat": "🍎 Фрукты",
        "parts": {
            "мякоть": {"status": "⚠️ Редко", "info": "Очень сладкий, вызывает запоры.", "norm": "Раз в месяц."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1571771896612-424bafef6551&w=500"
    },

    # --- ЯГОДЫ ---
    "клубника": {
        "cat": "🍓 Ягоды",
        "parts": {
            "ягода": {"status": "✅ Любимое", "info": "Свинки обожают запах.", "norm": "1 ягодка в неделю."},
            "листья": {"status": "✅ Полезно", "info": "Можно сушить для чая.", "norm": "Небольшой пучок."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1464965911861-746a04b4bca6&w=500"
    },
    "черника": {
        "cat": "🍓 Ягоды",
        "parts": {
            "ягода": {"status": "✅ Суперфуд", "info": "Полезна для зрения и сердца.", "norm": "3-5 ягодок."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1498557850523-fd3d118b962e&w=500"
    },
    "малина": {
        "cat": "🍓 Ягоды",
        "parts": {
            "ягода": {"status": "✅ Можно", "info": "Сладкая и ароматная.", "norm": "2-3 ягодки."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1577069861033-55d04cec4ef5&w=500"
    },
    "голубика": {
        "cat": "🍓 Ягоды",
        "parts": {
            "ягода": {"status": "✅ Безопасно", "info": "Меньше сахара, чем в других ягодах.", "norm": "Небольшая горсть."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1498557850523-fd3d118b962e&w=500"
    },
    "ежевика": {
        "cat": "🍓 Ягоды",
        "parts": {
            "ягода": {"status": "✅ Можно", "info": "Богата антиоксидантами.", "norm": "2-3 ягодки."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1615485925763-867862f8021a&w=500"
    },
    "смородина": {
        "cat": "🍓 Ягоды",
        "parts": {
            "ягода": {"status": "⚠️ Кисло", "info": "Черная или красная.", "norm": "Веточка с ягодами."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1596363505729-4190a9506133&w=500"
    },

    # --- ЗАПРЕЩЕНО (SOS) ---
    "авокадо": {
        "cat": "🆘 SOS",
        "parts": {
            "мякоть": {"status": "☠️ СМЕРТЕЛЬНО", "info": "Токсичен для сердца.", "norm": "НИКОГДА."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1523049673857-eb18f1d7b578&w=500"
    },
    "лук": {
        "cat": "🆘 SOS",
        "parts": {
            "луковица": {"status": "☠️ ЯД", "info": "Разрушает эритроциты.", "norm": "НИКОГДА."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb&w=500"
    },
    "шоколад": {
        "cat": "🆘 SOS",
        "parts": {
            "продукт": {"status": "☠️ ОПАСНО", "info": "Нарушает работу сердца.", "norm": "НИКОГДА."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1511381939415-e44015466834&w=500"
    },
    "хлеб": {
        "cat": "🆘 SOS",
        "parts": {
            "продукт": {"status": "❌ Нельзя", "info": "Вызывает вздутие.", "norm": "НИКОГДА."}
        },
        "img": "https://wsrv.nl/?url=https://images.unsplash.com/photo-1509440159596-0249088772ff&w=500"
    }
}

CATEGORIES = ["🥬 Овощи", "🌿 Травы", "🍎 Фрукты", "🍓 Ягоды", "🆘 SOS"]

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for cat in CATEGORIES:
        markup.add(types.InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}"))
   text =(
       "🐹 <b>Привет! Я бот-помощник по питанию морских свинок.</b>/n/n"
       "Я помогу тебе понять, можно ли твоему питомцу то или иное растение, овощ, фрукт или ягоду, и в каком количестве."
       "🔍 Как пользоваться:"
       "Просто напиши мне название продукта (например: огурец, петрушка, перец), и я выдам подробную информацию о пользе, вреде и норме потребления!" 
       "Ты так же можешь выбрать интересующую тебя категорию:"
   )
    bot.send_message(message.chat.id, text, reply_markup=markup)

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
        show_plant_options(call.message.chat.id, plant_name)

    elif call.data.startswith("part_"):
        data_parts = call.data.replace("part_", "").split("_", 1)
        plant_name = data_parts[0]
        part_name = data_parts[1].replace("_", " ")
        show_part_info(call.message.chat.id, plant_name, part_name)

    elif call.data == "back":
        start(call.message)
    
    elif call.data.startswith("all_info_"):
        plant_name = call.data.replace("all_info_", "")
        show_all_parts_info(call.message.chat.id, plant_name)

def show_plant_options(chat_id, plant_name):
    plant = PLANTS_DB.get(plant_name)
    if not plant: return

    markup = types.InlineKeyboardMarkup(row_width=1)
    parts = plant['parts']
    
    for part_name in parts.keys():
        btn_text = part_name.capitalize()
        safe_part = part_name.replace(" ", "_")
        markup.add(types.InlineKeyboardButton(text=btn_text, callback_data=f"part_{plant_name}_{safe_part}"))
    
    markup.add(types.InlineKeyboardButton(text="📋 Вся информация сразу", callback_data=f"all_info_{plant_name}"))
    markup.add(types.InlineKeyboardButton(text="🔙 Назад к категории", callback_data="back"))

    bot.send_photo(chat_id, plant['img'], caption=f"🌿 <b>{plant_name.capitalize()}</b>\nВыбери часть растения:", reply_markup=markup, parse_mode='HTML')

def show_part_info(chat_id, plant_name, part_name):
    plant = PLANTS_DB.get(plant_name)
    part_data = plant['parts'].get(part_name)
    
    if part_data:
        text = f"🌿 <b>{plant_name.capitalize()} ({part_name})</b>\n\n{part_data['status']}\n{part_data['info']}\n⚖️ {part_data['norm']}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"item_{plant_name}"))
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')

def show_all_parts_info(chat_id, plant_name):
    plant = PLANTS_DB.get(plant_name)
    text = f"🌿 <b>{plant_name.capitalize()} — Полный гид</b>\n\n"
    
    for part, data in plant['parts'].items():
        text += f"🔸 <b>{part.capitalize()}:</b> {data['status']}\n   {data['info']}\n   ⚖️ {data['norm']}\n\n"
        
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"item_{plant_name}"))
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')

# Умный поиск
@bot.message_handler(content_types=['text'])
def handle_text_search(message):
    query = message.text.strip().lower()
    if query.startswith('/'): return
    all_plants = list(PLANTS_DB.keys())
    match, score = process.extractOne(query, all_plants)
    if score > 60:
        show_plant_options(message.chat.id, match)
    else:
        bot.send_message(message.chat.id, f"🤔 Я не нашел '{message.text}'.")

# Webhook логика
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
