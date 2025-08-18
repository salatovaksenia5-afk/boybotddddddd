import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram import Router
import storage

BOT_TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"  # вставь сюда свой токен

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Добавление факта ---
@dp.message(Command("addfact"))
async def add_fact_handler(message: Message, state: FSMContext):
    # Формат: /addfact <имя> <факт>
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Используй: /addfact Имя Факт")
        return
    subject, fact = parts[1], parts[2]
    storage.add_fact(subject, fact)
    await message.answer(f"Факт добавлен для {subject}: {fact}")

# --- Просмотр фактов ---
@dp.message(Command("facts"))
async def list_facts_handler(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Используй: /facts Имя")
        return
    subject = parts[1]
    facts = storage.list_facts(subject)
    if not facts:
        await message.answer(f"Фактов для {subject} нет.")
        return
    # Создаем инлайн-кнопки для реакций друга
    for fact in facts:
        kb = InlineKeyboardBuilder()
        for reaction in ["норм", "пиздец", "сразу замуж", "ниче", "непонятно", "промолчу"]:
            kb.add(InlineKeyboardButton(text=reaction, callback_data=f"{subject}|{fact}|{reaction}"))
        kb.adjust(3)
        await message.answer(f"Факт про {subject}: {fact}", reply_markup=kb.as_markup())

# --- Обработка реакции друга ---
@dp.callback_query()
async def reaction_callback(callback):
    data = callback.data.split("|")
    subject, fact, reaction = data
    storage.add_reaction(reaction)
    await callback.message.edit_reply_markup(None)
    await callback.message.answer(f"Друг оценил факт про {subject}: {reaction}")
    # Уведомление тебе
    await bot.send_message(chat_id="ТВОЙ_CHAT_ID", text=f"{subject} факт оценен: {reaction}")
    await callback.answer()

# --- Ежедневные комплименты Никите ---
async def daily_nikita_compliment():
    while True:
        now = asyncio.get_event_loop().time()
        # Ждем до 12:00 по серверу
        import datetime
        target = datetime.datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        delta = (target - datetime.datetime.now()).total_seconds()
        if delta < 0:
            delta += 86400  # если уже после 12:00, ждем до следующего дня
        await asyncio.sleep(delta)
        await bot.send_message(chat_id="CHAT_ID_НИКИТЫ", text=storage.get_random_nikita_compliment())
        await asyncio.sleep(60)  # чтобы не зациклить

# --- Запуск ---
async def main():
    asyncio.create_task(daily_nikita_compliment())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
