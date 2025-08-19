import asyncio
import random
from datetime import datetime, time, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

BOT_TOKEN = "8413897465:AAHOLQB_uKo0YVdOfqGtEq0jdjzHjj8C1-U"
NIKITA_ID = 123456789  # твой Никита Telegram ID
MY_ID = 987654321      # твой ID

# Данные системы
boys = []  # список парней
facts = {}  # {boy_name: [факт1, факт2, ...]}
reactions_list = ["пиздец", "сразу замуж", "норм", "ниче", "непонятно", "промолчу"]
compliments = [
    "Ты отличный человек",
    "все хуесосы, ты один хороший",
    "Ты очень умный дядька",
    "Ты мой самый лучший друг ❤️",
    "ты просто невероятный!!"
]

# Удаляем webhook
async def remove_webhook():
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook()
    await bot.close()
    print("Webhook удалён")

# Основной бот
async def main():
    await remove_webhook()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Функция для авто-комплиментов дважды в день
    async def send_daily_compliments():
        while True:
            now = datetime.now()
            for target_time in [time(9,0), time(21,0)]:  # 9:00 и 21:00
                target_datetime = datetime.combine(now.date(), target_time)
                if now > target_datetime:
                    target_datetime += timedelta(days=1)
                wait_seconds = (target_datetime - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                compliment = random.choice(compliments)
                await bot.send_message(NIKITA_ID, f"Комплимент для тебя: {compliment}")

    # Команда /start
    @dp.message()
    async def start_handler(message: types.Message):
        keyboard = InlineKeyboardBuilder()
        keyboard.row(InlineKeyboardButton(text="Добавить парня", callback_data="add_boy"))
        keyboard.row(InlineKeyboardButton(text="Добавить факт", callback_data="add_fact"))
        keyboard.row(InlineKeyboardButton(text="Посмотреть рейтинг", callback_data="rating"))
        await message.answer("Привет! Выбирай действие:", reply_markup=keyboard.as_markup())

    # Обработка кнопок
    @dp.callback_query()
    async def callback_handler(callback: types.CallbackQuery):
        data = callback.data

        if data == "add_boy":
            await callback.message.answer("Отправь имя парня:")
            @dp.message(F.chat.id == callback.from_user.id)
            async def add_boy_name(message: types.Message):
                boy_name = message.text.strip()
                if boy_name not in boys:
                    boys.append(boy_name)
                    facts[boy_name] = []
                    await message.answer(f"Парень {boy_name} добавлен.")
                else:
                    await message.answer(f"{boy_name} уже есть.")
                dp.message.handlers.pop()  # убираем временный хэндлер

        elif data == "add_fact":
            if not boys:
                await callback.message.answer("Сначала добавь парней!")
                return
            keyboard = InlineKeyboardBuilder()
            for boy in boys:
                keyboard.button(text=boy, callback_data=f"fact_{boy}")
            await callback.message.answer("Выбери парня:", reply_markup=keyboard.as_markup())

        elif data.startswith("fact_"):
            boy_name = data[5:]
            await callback.message.answer(f"Напиши факт для {boy_name}:")
            @dp.message(F.chat.id == callback.from_user.id)
            async def add_fact_message(message: types.Message):
                fact = message.text.strip()
                facts[boy_name].append(fact)
                # отправляем Никите уведомление с выбором реакции
                keyboard = InlineKeyboardMarkup(row_width=3)
                for r in reactions_list:
                    keyboard.add(InlineKeyboardButton(r, callback_data=f"react_{boy_name}_{len(facts[boy_name])-1}_{r}"))
                await bot.send_message(NIKITA_ID, f"Новая информация про {boy_name}: {fact}", reply_markup=keyboard)
                await message.answer(f"Факт добавлен для {boy_name}.")
                dp.message.handlers.pop()

        elif data.startswith("react_"):
            parts = data.split("_")
            boy_name = parts[1]
            fact_index = int(parts[2])
            reaction = parts[3]
            fact = facts[boy_name][fact_index]
            await bot.send_message(MY_ID, f"Никита отреагировал на факт про {boy_name}: '{fact}' → {reaction}")
            await bot.answer_callback_query(callback.id, text="Реакция сохранена!")

        elif data == "rating":
            text = ""
            for boy, facts_list in facts.items():
                text += f"{boy}: {len(facts_list)} фактов\n"
            if text == "":
                text = "Фактов пока нет."
            await callback.message.answer(text)

    # Запуск авто-комплиментов параллельно с polling
    await asyncio.gather(
        dp.start_polling(bot, skip_updates=True),
        send_daily_compliments()
    )

asyncio.run(main())

