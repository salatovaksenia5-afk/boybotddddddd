from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import storage
from datetime import datetime, timedelta

BOT_TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===================== Команды =====================

@dp.message(Command(commands=["addfact"]))
async def add_fact_cmd(message: types.Message):
    try:
        _, subject, *text = message.text.split()
        fact_text = " ".join(text)
        storage.add_fact(subject, fact_text)

        # Создаем инлайн-кнопки с реакциями
        keyboard = InlineKeyboardMarkup(row_width=3)
        buttons = [InlineKeyboardButton(text=r, callback_data=f"{fact_text}|{r}") for r in storage.available_reactions]
        keyboard.add(*buttons)

        await message.answer(f"Факт про {subject} добавлен:\n{fact_text}\nВыберите реакцию:", reply_markup=keyboard)
    except Exception:
        await message.answer("Используй: /addfact <Имя> <факт>")

@dp.callback_query()
async def handle_reaction(callback: types.CallbackQuery):
    fact, reaction = callback.data.split("|")
    storage.add_reaction(fact, reaction)
    await callback.message.edit_text(f"{callback.message.text}\nВыбрана реакция: {reaction}")
    await callback.answer("Реакция сохранена!")

# ===================== Автокомплименты =====================

async def daily_compliments():
    await bot.wait_until_ready()
    while True:
        now = datetime.now()
        next_run = datetime.combine(now.date(), datetime.min.time()) + timedelta(hours=12)
        if now > next_run:
            next_run += timedelta(days=1)
        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        compliment = storage.get_random_compliment()
        await bot.send_message(chat_id="ID_НИКИТЫ", text=compliment)

# ===================== Запуск =====================

async def main():
    asyncio.create_task(daily_compliments())
    from aiogram import webhook
    await dp.start_webhook(
        dispatcher=dp,
        webhook_path="/webhook",
        on_startup=None,
        on_shutdown=None,
        skip_updates=True,
        bot=bot,
        host="0.0.0.0",
        port=10000
    )

if __name__ == "__main__":
    asyncio.run(main())
