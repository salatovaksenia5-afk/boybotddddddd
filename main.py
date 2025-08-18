from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import asyncio
import storage
import random

BOT_TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"
OWNER_ID = 123456789  # твой Telegram ID
FRIEND_ID = 987654321  # Никита

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ---------- Проверка владельца ----------
def _is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

# ---------- КОМАНДЫ ----------
@dp.message(Command("add_compliment"))
async def add_compliment(message: Message):
    if not _is_owner(message.from_user.id):
        await message.answer("Только владелец может добавлять комплименты.")
        return
    text = message.text.removeprefix("/add_compliment").strip()
    if not text:
        await message.answer("Напиши текст комплимента после команды.")
        return
    storage.add_compliment(text)
    await message.answer(f"Комплимент добавлен:\n{text}")

@dp.message(Command("compliments"))
async def list_compliments(message: Message):
    if not _is_owner(message.from_user.id):
        await message.answer("Только владелец может смотреть комплименты.")
        return
    items = storage.get_compliments()
    if not items:
        await message.answer("Комплиментов пока нет.")
        return
    txt = "\n".join([f"• {c}" for c in items])
    await message.answer("Список комплиментов:\n" + txt)

@dp.message(Command("set_reactions"))
async def set_reactions(message: Message):
    if not _is_owner(message.from_user.id):
        await message.answer("Только владелец может устанавливать реакции.")
        return
    text = message.text.removeprefix("/set_reactions").strip()
    if not text:
        await message.answer("Напиши реакции через запятую, например: 👍,❤️,🔥")
        return
    reactions = [r.strip() for r in text.split(",") if r.strip()]
    storage.set_reactions(reactions)
    await message.answer(f"Реакции установлены:\n{', '.join(reactions)}")

@dp.message(Command("reactions"))
async def show_reactions(message: Message):
    if not _is_owner(message.from_user.id):
        await message.answer("Только владелец может смотреть реакции.")
        return
    reactions = storage.get_reactions()
    if not reactions:
        await message.answer("Реакций пока нет.")
        return
    await message.answer("Текущие реакции:\n" + ", ".join(reactions))

# ---------- ФАКТ С РЕАКЦИЯМИ ----------
async def send_fact_with_reactions(fact: str):
    reactions = storage.get_reactions()
    if not reactions:
        reactions = ["👍", "❤️", "🔥"]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=r, callback_data=f"react:{r}") for r in reactions]
        ]
    )
    await bot.send_message(FRIEND_ID, fact, reply_markup=keyboard)

@dp.callback_query(F.filter(lambda c: c.data.startswith("react:")))
async def handle_reaction(callback: CallbackQuery):
    reaction = callback.data.split(":", 1)[1]
    user_name = callback.from_user.full_name
    await bot.send_message(OWNER_ID, f"Никита ({user_name}) выбрал реакцию: {reaction}")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Спасибо за реакцию!")

# ---------- ЕЖЕДНЕВНЫЙ КОМПЛИМЕНТ ----------
async def daily_compliment():
    while True:
        compliments = storage.get_compliments()
        if compliments:
            text = random.choice(compliments)
            await bot.send_message(FRIEND_ID, f"💌 Никита, {text}")
        await asyncio.sleep(24*60*60)  # раз в сутки

# ---------- ЗАПУСК ----------
async def main():
    asyncio.create_task(daily_compliment())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

