import json
from pathlib import Path

FILE_PATH = Path("storage.json")

# Загружаем или создаём файл
if FILE_PATH.exists():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "compliments": [],
        "reactions": ["пиздец", "сразу замуж", "норм", "ниче", "непонятно", "промолчу"]
    }
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- Комплименты ----------
def add_compliment(text: str):
    data["compliments"].append(text)
    _save()

def get_compliments():
    return data["compliments"].copy()

# ---------- Реакции ----------
def set_reactions(reactions: list[str]):
    data["reactions"] = reactions.copy()
    _save()

def get_reactions():
    return data["reactions"].copy()

# ---------- Сохранение ----------
def _save():
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

