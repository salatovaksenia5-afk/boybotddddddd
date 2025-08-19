import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import datetime, time
import random

BOT_TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# ================== Хранилище ==================
boys = {}  # {"Петя": [{"fact": "...", "reaction": None, "date": "..."}], ...}
compliments = [
    "Ты отличный человек",
    "Все хуесосы, ты один хороший",
    "Ты очень умный дядька",
    "Ты мой самый лучший друг ❤️",
    "Ты просто невероятный!!"
]
reactions = ["пиздец", "сразу замуж", "норм", "ниче", "непонятно", "промолчу"]

# ================== Кнопки ==================
kb = ReplyKeyboardBuilder()
kb.add(KeyboardButton(text="Добавить парня"))
kb.add(KeyboardButton(text="Добавить факт"))
kb.add(KeyboardButton(text="Посмотреть рейтинг"))

# ================== Хендлеры ==================
@router.message(Command(commands=["start"]))
async def start(message: types.Message):
    await message.answer("Привет! Выбирай действие:", reply_markup=keyboard)

@router.message(lambda m: m.text == "Добавить парня")
async def add_boy(message: types.Message):
    await message.answer("Напиши имя парня:")

    @router.message()
    async def get_boy_name(msg: types.Message):
        boys[msg.text] = []
        await msg.answer(f"Парень {msg.text} добавлен!")
        router.message.unregister(get_boy_name)

@router.message(lambda m: m.text == "Добавить факт")
async def add_fact(message: types.Message):
    if not boys:
        await message.answer("Сначала добавь парня!")
        return
    await message.answer(f"Выбери парня из списка: {', '.join(boys.keys())}")

    @router.message()
    async def choose_boy(msg: types.Message):
        if msg.text not in boys:
            await msg.answer("Такого парня нет.")
            return
        await msg.answer("Напиши факт о нём:")
        
        @router.message()
        async def get_fact(fact_msg: types.Message):
            boys[msg.text].append({"fact": fact_msg.text, "reaction": None, "date": datetime.now()})
            await fact_msg.answer(f"Факт добавлен для {msg.text}!")
            router.message.unregister(get_fact)
            router.message.unregister(choose_boy)
        
    router.message.unregister(choose_boy)

@router.message(lambda m: m.text == "Посмотреть рейтинг")
async def show_rating(message: types.Message):
    if not boys:
        await message.answer("Нет данных.")
        return
    rating = []
    for boy, facts in boys.items():
        score = sum(1 for f in facts if f["reaction"] in ["пиздец", "норм", "сразу замуж"])  # пример оценки
        rating.append((boy, score))
    rating.sort(key=lambda x: x[1], reverse=True)
    text = "\n".join([f"{b}: {s}" for b, s in rating])
    await message.answer(f"Рейтинг:\n{text}")

# ================== Комплименты Никите ==================
async def send_compliments():
    while True:
        now = datetime.now().time()
        if now >= time(9, 0) and now < time(9, 1) or now >= time(21, 0) and now < time(21, 1):
            compl = random.choice(compliments)
            try:
                await bot.send_message(chat_id="ID_НИКИТЫ", text=compl)
            except:
                pass
        await asyncio.sleep(60)

# ================== Реакции на факты ==================
async def simulate_reactions():
    while True:
        for boy, facts in boys.items():
            for f in facts:
                if f["reaction"] is None:
                    f["reaction"] = random.choice(reactions)
                    await bot.send_message(chat_id="ТВОЙ_ID", text=f"Никита отреагировал на факт про {boy}: {f['reaction']}")
        await asyncio.sleep(300)

# ================== Старт ==================
async def main():
    dp.include_router(router)
    await asyncio.gather(
        dp.start_polling(bot),
        send_compliments(),
        simulate_reactions()
    )

if __name__ == "__main__":
    asyncio.run(main())



