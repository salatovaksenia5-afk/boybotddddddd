import asyncio
import random
from datetime import datetime, time, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Text

from storage import boys, facts, reactions, compliments, nikita_reactions

BOT_TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"
NIKITA_ID = 123456789
YOUR_ID = 987654321

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ----------------- Хэндлеры -----------------

# Добавление факта о парне
@dp.message(Text(startswith="факт:"))
async def add_fact(message: types.Message):
    try:
        _, boy_name, fact_text = message.text.split(":", 2)
    except ValueError:
        await message.answer("Неверный формат. Используй: факт:ИмяПарня:Описание")
        return

    facts.setdefault(boy_name, []).append(fact_text)
    await message.answer(f"Факт про {boy_name} добавлен!")

    # Кнопки для Никиты
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(text=r, callback_data=f"react:{boy_name}:{fact_text}:{r}") for r in reactions]
    keyboard.add(*buttons)

    await bot.send_message(NIKITA_ID, f"Новый факт про {boy_name}: {fact_text}\nВыбери реакцию:", reply_markup=keyboard)

# Обработка кнопок с реакциями
@dp.callback_query(Text(startswith="react:"))
async def handle_reaction(callback: types.CallbackQuery):
    _, boy_name, fact_text, reaction = callback.data.split(":", 3)
    nikita_reactions.setdefault(boy_name, []).append((fact_text, reaction))
    
    await callback.answer(f"Ты выбрал реакцию: {reaction}")
    
    # Уведомление тебе
    await bot.send_message(YOUR_ID, f"Никита отреагировал на факт про {boy_name}: {reaction}")

# Показ рейтинга
@dp.message(Text("рейтинг"))
async def show_ranking(message: types.Message):
    ranking = []
    for boy_name in boys:
        score = len(nikita_reactions.get(boy_name, []))
        ranking.append((boy_name, score))
    ranking.sort(key=lambda x: x[1], reverse=True)

    text = "Рейтинг парней по реакции Никиты:\n"
    for name, score in ranking:
        text += f"{name}: {score} реакций\n"

    await message.answer(text)

# ----------------- Авто-комплименты -----------------
async def send_daily_compliment():
    while True:
        now = datetime.now()
        for send_time in [time(10, 0), time(20, 0)]:
            target_datetime = datetime.combine(now.date(), send_time)
            if now > target_datetime:
                target_datetime += timedelta(days=1)
            wait_seconds = (target_datetime - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            compliment = random.choice(compliments)
            await bot.send_message(NIKITA_ID, f"Комплимент для Никиты: {compliment}")

# ----------------- Запуск -----------------
async def main():
    asyncio.create_task(send_daily_compliment())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


  
