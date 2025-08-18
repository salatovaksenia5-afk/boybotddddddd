import random
import asyncio

# Хранилища
facts = {}  # {имя_парня: [{"текст": факт, "оценка": None}]}
compliments = [compliments = 
    "Ты отличный человек",
    "все хуесосы, ты один хороший",
    "Ты очень умный дядька",
    "Ты мой самый лучший друг ❤️",
    "ты просто невероятный!!"
]  # список комплиментов для Никиты

# Добавление факта про парня
def add_fact(subject, text):
    if subject not in facts:
        facts[subject] = []
    facts[subject].append({"текст": text, "оценка": None})

# Получение фактов
def list_facts(subject=None):
    if subject:
        return facts.get(subject, [])
    return facts

# Никита оценивает факт
def react_to_fact(subject, index, reaction):
    try:
        facts[subject][index]["оценка"] = reaction
        return True
    except (IndexError, KeyError):
        return False

# Добавление комплимента
def add_compliment(text):
    compliments.append(text)

# Получение случайного комплимента
def get_random_compliment():
    if compliments:
        return random.choice(compliments)
    return None

# Подсчет рейтинга парней по реакциям
def rating():
    score_map = {
        "пиздец": 1,
        "сразу замуж": 5,
        "норм": 3,
        "ниче": 2,
        "непонятно": 0,
        "промолчу": 0
    }
    result = {}
    for subject, lst in facts.items():
        total = 0
        count = 0
        for f in lst:
            if f["оценка"]:
                total += score_map.get(f["оценка"], 0)
                count += 1
        result[subject] = total if count > 0 else 0
    return result
