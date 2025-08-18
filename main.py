# main.py
from fastapi import FastAPI
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import storage

BOT_TOKEN = "ВАШ_ТОКЕН_ТЕЛЕГРАМ"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ====== Команды ======
@dp.message(commands=["compliments"])
async def send_compliments(message: types.Message):
    comp_list = storage.get_compliments()
    text = "Текущие комплименты:\n" + "\n".join(comp_list)
    await message.answer(text)

@dp.message(commands=["addfact"])
async def add_fact_cmd(message: types.Message):
    try:
        _, subject, *text = message.text.split()
        fact_text = " ".join(text)
        storage.add_fact(subject, fact_text)

        keyboard = InlineKeyboardMarkup(row_width=3)
        buttons = [
            InlineKeyboardButton(text=r, callback_data=f"{fact_text}|{r}") 
            for r in storage.available_reactions
        ]
        keyboard.add(*buttons)

        await message.answer(
            f"Факт про {subject} добавлен:\n{fact_text}\nВыберите реакцию:", 
            reply_markup=keyboard
        )
    except Exception:
        await message.answer("Используй: /addfact <Имя> <факт>")

@dp.callback_query()
async def handle_reaction(callback: types.CallbackQuery):
    fact, reaction = callback.data.split("|")
    storage.add_reaction(fact, reaction)
    await callback.message.edit_text(f"{callback.message.text}\nВыбрана реакция: {reaction}")
    await callback.answer("Реакция сохранена!")

# ====== FastAPI приложение ======
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # Запуск polling
    asyncio.create_task(dp.start_polling())

@app.get("/")
async def root():
    return {"status": "ok"}
