from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import random
from datetime import datetime, time
import logging

TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"
NIKITA_CHAT_ID = 123456789  # сюда вставь настоящий chat_id Никиты
YOUR_CHAT_ID = 987654321    # твой chat_id

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Кнопки
btn_add_boy = KeyboardButton(text="Добавить парня")
btn_add_fact = KeyboardButton(text="Добавить факт")
btn_rating = KeyboardButton(text="Посмотреть рейтинг")

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [btn_add_boy],
        [btn_add_fact],
        [btn_rating]
    ],
    resize_keyboard=True
)

# Словари для данных
boys = {}  # {"Имя": {"факты": [], "оценки": []}}
compliments = [
    "Ты отличный человек",
    "Все хуесосы, ты один хороший",
    "Ты очень умный дядька",
    "Ты мой самый лучший друг ❤️",
    "Ты просто невероятный!!"
]

# Старт
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)

# Обработка кнопок
@dp.message()
async def handle_buttons(message: types.Message, state: FSMContext):
    text = message.text

    if text == "Добавить парня":
        await message.answer("Напиши имя парня:")
        await state.set_state("adding_boy")

    elif text == "Добавить факт":
        if not boys:
            await message.answer("Сначала добавьте парня!")
            return
        await message.answer("К какому парню добавляем факт?")
        await state.set_state("choosing_boy_for_fact")

    elif text == "Посмотреть рейтинг":
        if not boys:
            await message.answer("Нет данных для рейтинга.")
            return
        reply = "Рейтинг парней:\n"
        for name, data in boys.items():
            score = sum(data.get("оценки", []))
            reply += f"{name}: {score}\n"
        await message.answer(reply)

    else:
        current_state = await state.get_state()
        if current_state == "adding_boy":
            boys[text] = {"факты": [], "оценки": []}
            await message.answer(f"Парень {text} добавлен!")
            await state.clear()
        elif current_state == "choosing_boy_for_fact":
            if text not in boys:
                await message.answer("Такого парня нет!")
                return
            await state.update_data(current_boy=text)
            await message.answer("Напишите факт:")
            await state.set_state("adding_fact")
        elif current_state == "adding_fact":
            data = await state.get_data()
            boy = data["current_boy"]
            boys[boy]["факты"].append(text)
            await message.answer(f"Факт для {boy} добавлен!")
            await state.clear()
        else:
            await message.answer("Выберите действие с помощью кнопок.")

# Функция отправки комплимента Никите
async def send_compliment():
    while True:
        now = datetime.now().time()
        # Отправляем комплименты дважды в день
        if now >= time(10, 0) and now <= time(10, 5):
            await send_to_nikita()
        if now >= time(18, 0) and now <= time(18, 5):
            await send_to_nikita()
        await asyncio.sleep(60)  # проверяем каждую минуту

async def send_to_nikita():
    compliment = random.choice(compliments)

    # Отправляем Никите
    await bot.send_message(chat_id=NIKITA_CHAT_ID, text=compliment)

    # Тебе уведомление
    await bot.send_message(chat_id=YOUR_CHAT_ID, text=f"✨ Никите отправлен комплимент: {compliment}")

    # Лог для консоли
    logging.info(f"Никите отправлен комплимент: {compliment}")

# Запуск
async def main():
    try:
        logging.info("Бот запущен!")
        asyncio.create_task(send_compliment())
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())





