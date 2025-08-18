# Список доступных реакций
available_reactions = ["пиздец", "сразу замуж", "норм", "ниче", "непонятно", "промолчу"]

# Список комплиментов
compliments = [
    "Ты отличный человек",
    "все хуесосы, ты один хороший",
    "Ты очень умный дядька",
    "Ты мой самый лучший друг ❤️",
    "ты просто невероятный!!"
]

# Словарь фактов: {subject: [факт1, факт2, ...]}
facts = {}

# Словарь реакций к фактам: {факт: [реакция1, реакция2, ...]}
fact_reactions = {}

# ===== Функции для работы =====
def add_fact(subject: str, fact_text: str):
    if subject not in facts:
        facts[subject] = []
    facts[subject].append(fact_text)
    fact_reactions[fact_text] = []

def list_facts(subject: str):
    return facts.get(subject, [])

def add_reaction(fact_text: str, reaction: str):
    if fact_text in fact_reactions:
        fact_reactions[fact_text].append(reaction)

def get_compliments():
    return compliments
