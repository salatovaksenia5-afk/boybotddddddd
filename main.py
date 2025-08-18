import os
import re
import random
from datetime import datetime, date
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, Update, InlineKeyboardButton, InlineKeyboardMarkup

import storage

# === ENV ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))     # ты
FRIEND_ID = int(os.getenv("FRIEND_ID", "0"))   # Никита
WEBHOOK_URL = os.getenv("WEBHOOK_URL")         # https://<your-service>/webhook
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")  # необязательно, но желательно
CRON_TOKEN = os.getenv("CRON_TOKEN", "")       # защищает /cron/compliment

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is required")

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()
app = FastAPI()

WARSAW = ZoneInfo("Europe/Warsaw")


COMPLIMENTS = [
    "Никита, ты самый крутой. 🚀",
    "Никита, ты лучший. Не забывай об этом. 💪",
    "Никита, ты вдохновляешь. ✨",
    "Никита, ты делаешь мир лучше. 🙌",
    "Никита, у тебя всё получится. 🔥",
]

# === HELPERS ===
def _is_owner(user_id: int) -> bool:
    return OWNER_ID and user_id == OWNER_ID

def _is_friend(user_id: int) -> bool:
    return FRIEND_ID and user_id == FRIEND_ID

def _parse_fact(text: str) -> tuple[str, str] | None:
    # Формат: "Имя: текст факта"
    m = re.match(r"^\s*([^:]{1,50})\s*:\s*(.+)$", text.strip())
    if not m:
        return None
    subject, fact = m.group(1), m.group(2)
    return subject.strip(), fact.strip()

def _reaction_keyboard(fact_id: int) -> InlineKeyboardMarkup:
    buttons = []
    for r in storage.get_reactions():
        buttons.append(InlineKeyboardButton(text=r, callback_data=f"react:{fact_id}:{r}"))
    # В один ряд по 3 кнопки (примерно)
    # aiogram сам перенесёт строку при необходимости
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

async def _send_fact_to_friend(subject: str, text: str, fact_id: int):
    msg = await bot.send_message(
        FRIEND_ID,
        f"<b>Новый факт про {subject}</b>\n{text}\n\nВыбери реакцию:",
        reply_markup=_reaction_keyboard(fact_id)
    )
    storage.set_fact_sent(fact_id, FRIEND_ID, msg.message_id)

async def _notify_owner(text: str):
    if OWNER_ID:
        await bot.send_message(OWNER_ID, text)

# === HANDLERS ===
@dp.message(F.text == "/start")
async def start(message: Message):
    who = "владелица" if _is_owner(message.from_user.id) else ("друг" if _is_friend(message.from_user.id) else "пользователь")
    await message.answer(
        "Привет! Я бот с фактами и комплиментами.\n\n"
        "Команды:\n"
        "/myid — показать ваш Telegram ID\n"
        "/reactions — показать текущие реакции\n"
        "/set_reactions 🔥,😍,👍 — (только владелица) задать реакции\n"
        "/facts [Имя] — показать сохранённые факты\n\n"
        "Чтобы добавить факт, просто напиши:\n"
        "<code>Имя: сам факт...</code>\n\n"
        f"Вы распознаны как: {who}."
    )
@dp.message(F.text == "/compliments")
async def list_compliments(message: Message):
    if not _is_owner(message.from_user.id):
        await message.answer("Эта команда доступна только владелице.")
        return
    items = storage.get_compliments()
    if not items:
        await message.answer("Комплиментов пока нет.")
        return
    txt = "\n".join([f"• {c}" for c in items])
    await message.answer("Список комплиментов (только для тебя):\n" + txt)
   

@dp.message(F.text == "/myid")
async def myid(message: Message):
    await message.answer(f"Ваш ID: <code>{message.from_user.id}</code>")

@dp.message(F.text.startswith("/reactions"))
async def reactions_show(message: Message):
    rs = storage.get_reactions()
    await message.answer("Текущие реакции: " + " ".join(rs))

@dp.message(F.text.startswith("/set_reactions"))
async def reactions_set(message: Message):
    if not _is_owner(message.from_user.id):
        await message.answer("Эта команда только для владелицы.")
        return
    payload = message.text.removeprefix("/set_reactions").strip()
    if not payload:
        await message.answer("Формат: /set_reactions 🔥,😍,👍,🤔")
        return
    # разделяем по запятой
    parts = [p.strip() for p in payload.split(",") if p.strip()]
    # ограничим длину callback_data (телега <=64 байт), но эмодзи ок
    if not parts:
        await message.answer("Не удалось разобрать реакции.")
        return
    storage.set_reactions(parts[:8])  # максимум 8 кнопок
    await message.answer("Готово. Новые реакции: " + " ".join(storage.get_reactions()))

@dp.message(F.text.startswith("/facts"))
async def facts_list(message: Message):
    parts = message.text.split(maxsplit=1)
    subject = parts[1].strip() if len(parts) > 1 else None
    facts = storage.list_facts(subject)
    if not facts:
        await message.answer("Фактов пока нет.")
        return
    lines = []
    for f in facts[-30:]:  # последние 30, чтобы не спамить
        tag = "✅" if f["status"] == "rated" else "🕘"
        react = f['reaction'] or "—"
        lines.append(f"{tag} #{f['id']} «{f['subject']}»: {f['text']}  [реакция: {react}]")
    await message.answer("\n\n".join(lines))

@dp.message()
async def any_text(message: Message):
    # Только владелица добавляет факты
    if not _is_owner(message.from_user.id):
        await message.answer("Я собираю факты от владелицы и шлю их другу с кнопками.")
        return
    parsed = _parse_fact(message.text or "")
    if not parsed:
        await message.answer("Формат факта: <code>Имя: сам факт...</code>")
        return
    subject, fact_text = parsed
    item = storage.add_fact(subject, fact_text)
    await message.answer(f"Факт сохранён (#{item['id']}) и отправлен другу.")
    await _send_fact_to_friend(subject, fact_text, item["id"])

@dp.callback_query(F.data.startswith("react:"))
async def on_react(call: CallbackQuery):
    if not _is_friend(call.from_user.id):
        await call.answer("Эти реакции предназначены другу.", show_alert=True)
        return
    try:
        _, sid, reaction = call.data.split(":", 2)
        fact_id = int(sid)
    except Exception:
        await call.answer("Некорректные данные.")
        return

    item = storage.set_fact_reaction(fact_id, reaction)
    if not item:
        await call.answer("Факт не найден.")
        return

    # Обновим сообщение у друга: уберём кнопки
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await call.answer(f"Оценка принята: {reaction}")
    await _notify_owner(
        f"Никита оценил факт #{item['id']} про {item['subject']} — <b>{reaction}</b>.\n"
        f"Текст: {item['text']}"
    )

# === WEB ===
@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    # Проверим секрет, если задан
    if TELEGRAM_WEBHOOK_SECRET:
        hdr = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if hdr != TELEGRAM_WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Bad secret")

    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return JSONResponse({"ok": True})

@app.get("/cron/compliment")
async def cron_compliment(token: str | None = None):
    if CRON_TOKEN and token != CRON_TOKEN:
        raise HTTPException(status_code=401, detail="Bad token")

    # Отправим 1 раз в день, когда локальное время ~12:00
    now = datetime.now(WARSAW)
    last = storage.get_last_compliment_date()
    today = date.today()

    if last == today.isoformat():
        return {"ok": True, "skipped": "already_sent_today"}

    if now.hour == 12:
        txt = random.choice(COMPLIMENTS)
        await bot.send_message(FRIEND_ID, txt)
        storage.set_last_compliment_date(today)
        return {"ok": True, "sent": True, "at": now.isoformat()}

    return {"ok": True, "skipped": f"hour_is_{now.hour}_not_12"}

# === STARTUP: ставим webhook ===
@app.on_event("startup")
async def on_startup():
    if not WEBHOOK_URL:
        print("WARNING: WEBHOOK_URL is not set. Set it in env for production.")
        return
    await bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=TELEGRAM_WEBHOOK_SECRET or None,
        allowed_updates=["message", "callback_query"]
    )
    print("Webhook set to", WEBHOOK_URL)
