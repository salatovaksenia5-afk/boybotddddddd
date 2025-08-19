import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# ------------------ Настройки ------------------
BOT_TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"  # Вставь сюда токен
NIKITA_ID = 123456789  # ID Никиты
USER_ID = 987654321  # Твой ID для уведомлений

# ------------------ Данные ------------------
boys = []  # Список парней
facts = {}  # Факты о парнях: { "Имя": [{"fact": "факт", "reaction": None}] }

compliments = [
    "Ты отличный человек",
    "все хуесосы, ты один хороший",
    "Ты очень умный дядька",
    "Ты мой самый лучший друг ❤️",
    "ты просто невероятный!!"
]

reactions_list = ["пиздец", "сразу замуж", "норм", "ниче", "непонятно", "промолчу"]

# ------------------ Инициализация ------------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ------------------ Клавиатура ------------------
kb = ReplyKeyboardBuilder()
kb.add(KeyboardButton(text="Добавить парня"))
kb.add(KeyboardButton(text="Добавить факт"))
kb.add(KeyboardButton(text="Посмотреть рейтинг"))


# ------------------ Хелперы ------------------
async def send_compliment():
    while True:
        for hour in [10, 18]:  # Два раза в день: 10:00 и 18:00
            now_hour = int(asyncio.get_event_loop().time()) % 24
            if now_hour == hour:
                compliment = random.choice(compliments)
                await bot.send_message(NIKITA_ID, compliment)
                await bot.send_message(USER_ID, f"Комплимент отправлен: {compliment}")
            await asyncio.sleep(3600)  # Проверка каждый час

def calculate_rating():
    rating = {}
    for boy, boy_facts in facts.items():
        pos = sum(1 for f in boy_facts if f["reaction"] in ["сразу замуж", "норм", "ниче"])
        neg = sum(1 for f in boy_facts if f["reaction"] in ["пиздец", "непонятно"])
        rating[boy] = {"Позитив": pos, "Негатив": neg}
    return rating

# ------------------ Хэндлеры ------------------
@dp.message()
async def handle_all_messages(message: types.Message):
    if message.text == "Добавить парня":
        await message.answer("Введите имя парня:")
        dp.register_message_handler(add_boy)
    elif message.text == "Добавить факт":
        if not boys:
            await message.answer("Сначала добавьте парня!")
            return
        buttons = [KeyboardButton(name) for name in boys]
        markup = ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True)
        await message.answer("Выберите парня для факта:", reply_markup=markup)
        dp.register_message_handler(select_boy_for_fact)
    elif message.text == "Посмотреть рейтинг":
        rating = calculate_rating()
        if not rating:
            await message.answer("Нет данных для рейтинга.")
        else:
            msg = ""
            for boy, r in rating.items():
                msg += f"{boy}: +{r['Позитив']} / -{r['Негатив']}\n"
            await message.answer(msg)
    else:
        await message.answer("Выберите действие с помощью кнопок.", reply_markup=kb.as_markup(resize_keyboard=True))

async def add_boy(message: types.Message):
    name = message.text.strip()
    if name in boys:
        await message.answer("Такой парень уже есть.")
    else:
        boys.append(name)
        facts[name] = []
        await message.answer(f"Парень {name} добавлен.", reply_markup=kb.as_markup(resize_keyboard=True))

async def select_boy_for_fact(message: types.Message):
    boy = message.text.strip()
    if boy not in boys:
        await message.answer("Парень не найден.")
        return
    await message.answer(f"Введите факт о {boy}:")
    dp.register_message_handler(lambda msg: add_fact(msg, boy))

async def add_fact(message: types.Message, boy: str):
    fact_text = message.text.strip()
    fact_entry = {"fact": fact_text, "reaction": None}
    facts[boy].append(fact_entry)
    # Отправка Никите для реакции
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for r in reactions_list:
        keyboard.add(KeyboardButton(r))
    sent = await bot.send_message(NIKITA_ID, f"Факт о {boy}: {fact_text}", reply_markup=keyboard)
    # Логируем, что факт отправлен
    await bot.send_message(USER_ID, f"Факт про {boy} отправлен Никите.")
    
    # Регистрируем хэндлер на реакцию Никиты
    dp.register_message_handler(lambda msg: add_reaction(msg, boy, fact_entry), lambda msg: msg.from_user.id == NIKITA_ID and msg.text in reactions_list)

async def add_reaction(message: types.Message, boy: str, fact_entry: dict):
    reaction = message.text.strip()
    fact_entry["reaction"] = reaction
    await bot.send_message(USER_ID, f"Никита отреагировал на факт про {boy}: {reaction}")

# ------------------ Запуск ------------------
async def main():
    asyncio.create_task(send_compliment())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


