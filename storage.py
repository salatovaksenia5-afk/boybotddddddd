import random

# ======== ФАКТЫ ========
# словарь вида: {имя: [факт1, факт2, ...]}
facts = {}

def add_fact(name, fact):
    if name not in facts:
        facts[name] = []
    facts[name].append(fact)

def list_facts(name):
    return facts.get(name, [])

# ======== РЕАКЦИИ ========
# список всех реакций
reactions = [
    "пиздец", "сразу замуж", "норм", "ниче", "непонятно", "промолчу"
]

def add_reaction(name, reaction):
    reactions.append(reaction)

def list_reactions():
    return reactions

# ======== КОМПЛИМЕНТЫ НИКИТЕ ========
nikita_compliments = [
    "Ты отличный человек",
    "все хуесосы, ты один хороший",
    "Ты очень умный дядька",
    "Ты мой самый лучший друг ❤️",
    "ты просто невероятный!!"
]

def get_nikita_compliments():
    return nikita_compliments

def get_random_nikita_compliment():
    return random.choice(nikita_compliments)
