import asyncio
import datetime
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

BOT_TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ====== Данные ======
facts = {}  # {имя_парня: [{"text": факт, "reaction": None}]}
compliments = [ 
    "Ты отличный человек",
    "все хуесосы, ты один хороший",
    "Ты очень умный дядька",
    "Ты мой самый лучший друг ❤️",
    "ты просто невероятный!!"
]
reactions_list = ["пиздец", "сразу замуж", "норм", "ниче", "непонятно", "промолчу"]

# ====== Добавление факта ======
async def add_fact(subject: str, fact: str):
    if subject not in facts:
        facts[subject] = []
    facts[subject].append({"text": fact, "reaction": None})
    # кнопки для реакции Никиты
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(text=r, callback_data=f"{subject}|{len(facts[subject])-1}|{r}") for r in reactions_list]
    keyboard.add(*buttons)
    # отправляем Никите (нужен его chat_id)
    nikita_chat_id = "тут_chat_id_Никиты"
    await bot.send_message(chat_id=nikita_chat_id, text=f"Новый факт про {subject}: {fact}", reply_markup=keyboard)

# ====== Обработка реакции Никиты ======
@dp.callback_query()
async def reaction_handler(callback: types.CallbackQuery):
    data = callback.data.split("|")
    subject, index, reaction = data[0], int(data[1]), data[2]
    facts[subject][index]["reaction"] = reaction
    # уведомление тебе
    your_chat_id = "тут_твой_chat_id"
    await bot.send_message(chat_id=your_chat_id, text=f"Никита отреагировал на {subject}: {reaction}")
    await callback.answer("Реакция принята!")

# ====== Подсчёт рейтинга ======
@dp.message(commands=["rating"])
async def rating_handler(message: types.Message):
    rating = {}
    for subject, items in facts.items():
        positive = 0
        negative = 0
        for item in items:
            if item["reaction"] in ["пиздец", "сразу замуж", "норм"]:
                positive += 1
            elif item["reaction"] in ["ниче", "непонятно", "промолчу"]:
                negative += 1
        rating[subject] = {"positive": positive, "negative": negative}
    text = "\n".join([f"{s}: 👍 {v['positive']} | 👎 {v['negative']}" for s,v in rating.items()])
    await message.answer(f"Рейтинг парней:\n{text}")

# ====== Добавление факта через команду ======
@dp.message(commands=["addfact"])
async def addfact_command(message: types.Message):
    try:
        parts = message.text.split(maxsplit=2)
        subject, fact = parts[1], parts[2]
        await add_fact(subject, fact)
        await message.answer(f"Факт про {subject} добавлен!")
    except IndexError:
        await message.answer("Использование: /addfact <имя_парня> <факт>")

# ====== Отправка комплиментов ======
async def send_compliment():
    comp = random.choice(compliments)
    nikita_chat_id = "тут_chat_id_Никиты"
    await bot.send_message(chat_id=nikita_chat_id, text=comp)

# ====== Планировщик комплиментов два раза в день ======
async def schedule_compliments():
    while True:
        now = datetime.datetime.now()
        if now.hour in [10, 18] and now.minute == 0:
            await send_compliment()
            await asyncio.sleep(60)
        await asyncio.sleep(10)

# ====== Основной запуск ======
async def main():
    await bot.delete_webhook()
    print("Webhook удалён, стартуем polling...")
    asyncio.create_task(schedule_compliments())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

  
