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
NIKITA_ID = 123456789  # ID Никиты
YOUR_CHAT_ID = 987654321  # Для логов

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

# Кнопки
btn_add_boy = KeyboardButton(text="Добавить парня")
btn_add_fact = KeyboardButton(text="Добавить факт")
btn_rating = KeyboardButton(text="Посмотреть рейтинг")
btn_send_compliment = KeyboardButton(text="Отправить комплимент Никите")

keyboard = ReplyKeyboardMarkup(
    keyboard=[[btn_add_boy], [btn_add_fact], [btn_rating], [btn_send_compliment]],
    resize_keyboard=True
)

# Данные
boys = {}  # {"Имя": {"факты": [], "оценки": []}}
compliments = [
    "Никита, ты крутой!",
    "Никита, ты лучший!",
    "Никита, у тебя всё получится!",
    "Никита, я тебя обожаю!",
    "Никита, ты мой герой!",
    "Никита, ты умный и талантливый!",
    "Никита, у тебя невероятное обаяние!",
    "Никита, ты настоящий мужчина!",
    "Никита, ты делаешь мир лучше!",
    "Никита, я горжусь тобой!"
]

nikita_reactions = [
    "Уважаемый",
    "Пиздец, беги от него",
    "Слабоватый",
    "Пойдёт",
    "Он самый лучший, выбирай его",
    "Ничего себе"
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

    elif text == "Отправить комплимент Никите":
        compliment = random.choice(compliments)
        await bot.send_message(chat_id=NIKITA_ID, text=compliment)
        logging.info(f"Комплимент отправлен Никите вручную: {compliment}")
        await message.answer(f"Комплимент отправлен Никите: {compliment}")

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
            # Отправляем Никите факт + случайная реакция
            reaction = random.choice(nikita_reactions)
            await bot.send_message(chat_id=NIKITA_ID, text=f"Факт о {boy}: {text}\nРеакция: {reaction}")
            logging.info(f"Факт о {boy} отправлен Никите: {text} / Реакция: {reaction}")
            await message.answer(f"Факт для {boy} добавлен и отправлен Никите!")
            await state.clear()
        else:
            await message.answer("Выберите действие с помощью кнопок.")

# Функция отправки комплиментов по времени
async def send_compliment():
    while True:
        now = datetime.now().time()
        if time(10, 0) <= now <= time(10, 5) or time(18, 0) <= now <= time(18, 5):
            compliment = random.choice(compliments)
            await bot.send_message(chat_id=NIKITA_ID, text=compliment)
            logging.info(f"Комплимент отправлен Никите: {compliment}")
        await asyncio.sleep(60)

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






