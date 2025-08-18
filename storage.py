import datetime
import random

# Словарь фактов: {парень: [{"текст": ..., "дата": ..., "оценка": None, "reacted_by": []}]}
facts = {}

# Список комплиментов для Никиты
compliments = [compliments = 
    "Ты отличный человек",
    "все хуесосы, ты один хороший",
    "Ты очень умный дядька",
    "Ты мой самый лучший друг ❤️",
    "ты просто невероятный!!"
]

def add_fact(subject, text):
    facts.setdefault(subject, []).append({
        "текст": text,
        "дата": str(datetime.date.today()),
        "оценка": None,
        "reacted_by": []
    })

def rate_fact(subject, index, rating, user):
    fact = facts[subject][index]
    fact["оценка"] = rating
    if user not in fact["reacted_by"]:
        fact["reacted_by"].append(user)

def list_facts(subject=None):
    if subject:
        return facts.get(subject, [])
    return facts

def add_compliment(text):
    compliments.append(text)

def get_random_compliment():
    return random.choice(compliments) if compliments else None

def get_unreacted_facts(user):
    result = []
    for subject, fact_list in facts.items():
        for idx, fact in enumerate(fact_list):
            if user not in fact["reacted_by"]:
                result.append((subject, idx, fact))
    return result
