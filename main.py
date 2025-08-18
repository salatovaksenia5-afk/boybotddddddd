import asyncio
import random
from datetime import datetime, time, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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
        # уведомление Никите с кнопками
        keyboard = InlineKeyboardMarkup(row_width=3)
        buttons = [InlineKeyboardButton(text=r, callback_data=f"react|{subject}|{len(storage.facts[subject])-1}|{r}") for r in REACTIONS]
        keyboard.add(*buttons)
        await bot.send_message(CHAT_ID_NIKITA, f"Новый факт про {subject}: {text}", reply_markup=keyboard)
    except Exception as e:
        await msg.answer(f"Ошибка. Формат: /add_fact имя_парня текст_факта\n{e}")

# --- Обработка нажатий кнопок ---
@dp.callback_query(lambda c: c.data and c.data.startswith("react|"))
async def process_react_callback(callback: types.CallbackQuery):
    try:
        _, subject, index, reaction = callback.data.split("|")
        index = int(index)
        ok = storage.react_to_fact(subject, index, reaction)
        if ok:
            await callback.answer(f"Вы оценили факт: {reaction}")
            # уведомление тебе
            await bot.send_message(CHAT_ID_YOU, f"Никита оценил факт про {subject}: {reaction}")
        else:
            await callback.answer("Факт не найден", show_alert=True)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)

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

# --- Команда рейтинга ---
@dp.message(Command("rating"))
async def rating_cmd(msg: types.Message):
    rat = storage.rating()
    text = "\n".join([f"{k}: {v}" for k,v in rat.items()])
    await msg.answer(f"Рейтинг парней:\n{text}")

# --- Автокомплименты дважды в день ---
async def daily_compliments():
    while True:
        now = datetime.now()
        # Время отправки: 10:00 и 20:00
        targets = [time(10,0), time(20,0)]
        for t in targets:
            send_time = datetime.combine(now.date(), t)
            if send_time < now:
                send_time += timedelta(days=1)
            wait_seconds = (send_time - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            compliment = storage.get_random_compliment()
            if compliment:
                await bot.send_message(CHAT_ID_NIKITA, f"Комплимент: {compliment}")
        # Ждем до следующего дня
        await asyncio.sleep(1)

# --- Запуск бота ---
async def main():
    asyncio.create_task(daily_compliments())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

  
