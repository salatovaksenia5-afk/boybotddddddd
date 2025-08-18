import logging
import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# Вставь свой токен сюда
BOT_TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --- Хранилище ---
facts = {}  # {имя_парня: [факт1, факт2, ...]}
reactions = ["пиздец", "сразу замуж", "норм", "ниче", "непонятно", "промолчу"]
compliments = [
    "Ты отличный человек",
    "все хуесосы, ты один хороший",
    "Ты очень умный дядька",
    "Ты мой самый лучший друг ❤️",
    "ты просто невероятный!!"
]

# Для хранения реакций Никиты
nickita_reactions = {}

# --- Утилиты ---
def get_facts_keyboard(name):
    kb = InlineKeyboardMarkup()
    for idx, fact in enumerate(facts.get(name, [])):
        kb.add(InlineKeyboardButton(f"{fact}", callback_data=f"react:{name}:{idx}"))
    return kb

async def send_compliment():
    while True:
        await asyncio.sleep(12*60*60)  # каждые 12 часов
        compliment = random.choice(compliments)
        await bot.send_message(chat_id="YOUR_CHAT_ID_NIKITA", text=f"Комплимент: {compliment}")

# --- Команды ---
@dp.message_handler(commands=["start"])
async def cmd_start(message):
    await message.reply("Привет! Добавляй факты про парней командой: факт:имя:текст")

@dp.message_handler(lambda message: message.text.lower().startswith("факт:"))
async def add_fact(message):
    try:
        _, name, text = message.text.split(":", 2)
    except ValueError:
        await message.reply("Неправильный формат. Используй факт:имя:текст")
        return

    facts.setdefault(name, []).append(text)
    await message.reply(f"Факт добавлен про {name} ✅")

    # Отправляем Никите кнопки для реакции
    kb = get_facts_keyboard(name)
    await bot.send_message(chat_id="1304999368", text=f"Новый факт про {name}:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("react:"))
async def handle_reaction(callback):
    _, name, idx = callback.data.split(":")
    idx = int(idx)
    fact_text = facts[name][idx]
    reaction = random.choice(reactions)
    nickita_reactions.setdefault(name, []).append((fact_text, reaction))
    await bot.send_message(chat_id="1026494049", text=f"Никита отреагировал на факт про {name}: {reaction}")
    await callback.answer("Реакция учтена!")

@dp.message_handler(lambda message: message.text.lower() == "рейтинг")
async def show_ranking(message):
    text = "Рейтинг парней:\n"
    for name, reacts in nickita_reactions.items():
        positive = sum(1 for _, r in reacts if r in ["сразу замуж", "норм", "ниче"])
        negative = sum(1 for _, r in reacts if r in ["пиздец", "непонятно", "промолчу"])
        text += f"{name}: +{positive}, -{negative}\n"
    await message.reply(text)

# --- Запуск комплиментов ---
loop = asyncio.get_event_loop()
loop.create_task(send_compliment())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

