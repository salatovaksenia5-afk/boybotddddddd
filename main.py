from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
import asyncio
import random
import logging
from datetime import datetime, time

TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://YOUR-RENDER-URL.com" + WEBHOOK_PATH  # замени на свой URL
YOUR_CHAT_ID = "ID_НИКИТЫ"  # сюда будут отправляться комплименты Никите

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

# Кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить парня")],
        [KeyboardButton(text="Добавить факт")],
        [KeyboardButton(text="Посмотреть рейтинг")]
    ],
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

# Хэндлеры
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)

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
            # Отправляем факт Никите
            await bot.send_message(chat_id=YOUR_CHAT_ID, text=f"Факт о {boy}: {text}")
            await message.answer(f"Факт для {boy} добавлен!")
            await state.clear()
        else:
            await message.answer("Выберите действие с помощью кнопок.")

# Комплименты Никите
async def send_compliments():
    while True:
        now = datetime.now().time()
        if (time(10, 0) <= now <= time(10, 5)) or (time(18, 0) <= now <= time(18, 5)):
            compliment = random.choice(compliments)
            await bot.send_message(chat_id=YOUR_CHAT_ID, text=compliment)
            logging.info(f"Комплимент отправлен: {compliment}")
        await asyncio.sleep(60)

# Webhook
async def handle(request):
    update = types.Update(**await request.json())
    await dp.process_update(update)
    return web.Response()

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    asyncio.create_task(send_compliments())
    logging.info("Webhook установлен и задача комплиментов запущена")

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()
    logging.info("Webhook удалён")

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)





