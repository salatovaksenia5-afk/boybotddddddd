import logging
import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"
CHAT_ID_NIKITA = 123456789  # Никита
CHAT_ID_YOU = 987654321     # Ты

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Хранилище ---
boys = []  # список имён парней
facts = {}  # {имя_парня: [факт1, факт2, ...]}
reactions = ["пиздец", "сразу замуж", "норм", "ниче", "непонятно", "промолчу"]
compliments = [
    "Ты отличный человек",
    "все хуесосы, ты один хороший",
    "Ты очень умный дядька",
    "Ты мой самый лучший друг ❤️",
    "ты просто невероятный!!"
]
nickita_reactions = {}  # реакции Никиты

# --- Временное хранилище выбора имени ---
user_selected_boy = {}

# --- Утилиты ---
def get_boys_keyboard():
    kb = InlineKeyboardMarkup()
    for name in boys:
        kb.add(InlineKeyboardButton(name, callback_data=f"choose_boy:{name}"))
    return kb

def get_facts_keyboard(name):
    kb = InlineKeyboardMarkup()
    for idx, fact in enumerate(facts.get(name, [])):
        kb.add(InlineKeyboardButton(f"{fact}", callback_data=f"react:{name}:{idx}"))
    return kb

async def send_compliment():
    while True:
        await asyncio.sleep(12*60*60)  # каждые 12 часов
        compliment = random.choice(compliments)
        await bot.send_message(chat_id=CHAT_ID_NIKITA, text=f"Комплимент: {compliment}")

# --- Хэндлеры ---
@dp.message()
async def handle_message(message: types.Message):
    text = message.text.lower()
    if text.startswith("добавить парня:"):
        name = message.text.split(":", 1)[1].strip()
        if name and name not in boys:
            boys.append(name)
            await message.reply(f"Парень '{name}' добавлен ✅")
        else:
            await message.reply("Неправильное имя или оно уже есть.")

    elif text == "добавить факт":
        if not boys:
            await message.reply("Сначала добавь хотя бы одного парня командой 'добавить парня:имя'")
            return
        kb = get_boys_keyboard()
        await message.reply("Выбери парня, про которого хочешь добавить факт:", reply_markup=kb)

    elif text == "рейтинг":
        text_out = "Рейтинг парней:\n"
        for name, reacts in nickita_reactions.items():
            positive = sum(1 for _, r in reacts if r in ["сразу замуж", "норм", "ниче"])
            negative = sum(1 for _, r in reacts if r in ["пиздец", "непонятно", "промолчу"])
            text_out += f"{name}: +{positive}, -{negative}\n"
        await message.reply(text_out)

    elif text.startswith("факт:"):
        if message.from_user.id not in user_selected_boy:
            await message.reply("Сначала выбери парня через кнопки!")
            return
        name = user_selected_boy.pop(message.from_user.id)
        fact_text = message.text.split(":", 1)[1].strip()
        facts.setdefault(name, []).append(fact_text)
        await message.reply(f"Факт добавлен про {name} ✅")
        kb = get_facts_keyboard(name)
        await bot.send_message(chat_id=CHAT_ID_NIKITA, text=f"Новый факт про {name}:", reply_markup=kb)

@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    data = callback.data
    if data.startswith("choose_boy:"):
        name = data.split(":", 1)[1]
        user_selected_boy[callback.from_user.id] = name
        await callback.message.reply(f"Теперь напиши факт про {name} в формате: факт:текст")
        await callback.answer()

    elif data.startswith("react:"):
        _, name, idx = data.split(":")
        idx = int(idx)
        fact_text = facts[name][idx]
        reaction = random.choice(reactions)
        nickita_reactions.setdefault(name, []).append((fact_text, reaction))
        await bot.send_message(chat_id=CHAT_ID_YOU, text=f"Никита отреагировал на факт про {name}: {reaction}")
        await callback.answer("Реакция учтена!")

# --- Запуск ---
async def main():
    asyncio.create_task(send_compliment())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


