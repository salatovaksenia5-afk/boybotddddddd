import json
import os
from datetime import date
from typing import List, Dict, Any

DB_FILE = os.getenv("DB_FILE", "db.json")

def _empty_db() -> Dict[str, Any]:
    return {
        "next_id": 1,
        "reactions": ["пиздец", "сразу замуж", "норм", "ниче непонятно", "промолчу"],
        "facts": [],
        "last_compliment_date": None
    }

def _load() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        return _empty_db()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return _empty_db()

def _save(db: Dict[str, Any]) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_reactions() -> List[str]:
    return _load()["reactions"]

def set_reactions(reactions: List[str]) -> None:
    db = _load()
    db["reactions"] = reactions
    _save(db)

def add_fact(subject: str, text: str) -> Dict[str, Any]:
    db = _load()
    fact_id = db["next_id"]
    db["next_id"] += 1
    item = {
        "id": fact_id,
        "subject": subject.strip(),
        "text": text.strip(),
        "status": "pending",
        "reaction": None,
        "friend_message_id": None,
        "friend_chat_id": None
    }
    db["facts"].append(item)
    _save(db)
    return item

def set_fact_sent(fact_id: int, friend_chat_id: int, msg_id: int) -> None:
    db = _load()
    for it in db["facts"]:
        if it["id"] == fact_id:
            it["friend_chat_id"] = friend_chat_id
            it["friend_message_id"] = msg_id
            break
    _save(db)

def set_fact_reaction(fact_id: int, reaction: str) -> Dict[str, Any] | None:
    db = _load()
    for it in db["facts"]:
        if it["id"] == fact_id:
            it["reaction"] = reaction
            it["status"] = "rated"
            _save(db)
            return it
    return None

def list_facts(subject: str | None = None) -> List[Dict[str, Any]]:
    db = _load()
    facts = db["facts"]
    if subject:
        facts = [f for f in facts if f["subject"].lower() == subject.lower()]
    return facts

def get_last_compliment_date() -> str | None:
    return _load().get("last_compliment_date")

def set_last_compliment_date(d: date) -> None:
    db = _load()
    db["last_compliment_date"] = d.isoformat()
    _save(db)
