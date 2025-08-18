import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.filters import Command
import storage

BOT_TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"
CHAT_ID_NIKITA = 123456789  # Никита
CHAT_ID_YOU = 987654321     # Ты

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

REACTIONS = ["пиздец", "сразу замуж", "норм", "ниче", "непонятно", "промолчу"]

# --- Команды для фактов ---
@dp.message(Command("add_fact"))
async def add_fact_cmd(msg: types.Message):
    try:
        _, subject, *text = msg.text.split()
        text = " ".join(text)
        storage.add_fact(subject, text)
        await msg.answer(f"Факт для {subject} добавлен!")
        # уведомление Никите
        await bot.send_message(CHAT_ID_NIKITA, f"Новый факт про {subject}: {text}")
    except:
        await msg.answer("Ошибка. Формат: /add_fact имя_парня текст_факта")

@dp.message(Command("react"))
async def react_cmd(msg: types.Message):
    try:
        _, subject, index, reaction = msg.text.split()
        index = int(index)
        if reaction not in REACTIONS:
            await msg.answer(f"Неверная реакция. Выбери: {', '.join(REACTIONS)}")
            return
        ok = storage.react_to_fact(subject, index, reaction)
        if ok:
            await msg.answer(f"Оценка принята: {reaction}")
            # уведомление тебе
            await bot.send_message(CHAT_ID_YOU, f"Никита оценил факт про {subject}: {reaction}")
        else:
            await msg.answer("Не найден факт")
    except:
        await msg.answer("Ошибка. Формат: /react имя_парня индекс реакция")

@dp.message(Command("rating"))
async def rating_cmd(msg: types.Message):
    rat = storage.rating()
    text = "\n".join([f"{k}: {v}" for k,v in rat.items()])
    await msg.answer(f"Рейтинг парней:\n{text}")

# --- Команды для комплиментов ---
@dp.message(Command("add_compliment"))
async def add_compliment_cmd(msg: types.Message):
    try:
        _, *text = msg.text.split()
        text = " ".join(text)
        storage.add_compliment(text)
        await msg.answer("Комплимент добавлен!")
    except:
        await msg.answer("Ошибка. Формат: /add_compliment текст")

# --- Автокомплименты Никите ---
async def auto_compliments():
    while True:
        await asyncio.sleep(random.randint(60, 300))  # каждые 1-5 минут
        compliment = storage.get_random_compliment()
        if compliment:
            await bot.send_message(CHAT_ID_NIKITA, f"Комплимент: {compliment}")

# --- Запуск бота ---
async def main():
    asyncio.create_task(auto_compliments())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
