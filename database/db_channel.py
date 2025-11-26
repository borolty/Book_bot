import json
import os

BASE = os.path.dirname(__file__)
DB_FILE = os.path.join(BASE, "channel_read_db.json")


def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


db = load_db()


def get_user_state(user_id: int):
    uid = str(user_id)
    if uid not in db:
        db[uid] = {
            "current_post": 1,
            "history": []
        }
        save_db(db)
    return db[uid]


# def set_user_post(user_id: int, post_id: int):
#     uid = str(user_id)
#     db.setdefault(uid, {})
#     db[uid]["current_post"] = post_id
#     save_db(db)


def set_current_post(user_id: int, post_id: int):
    uid = str(user_id)
    db.setdefault(uid, {})
    db[uid]["current_post"] = post_id
    save_db(db)


def push_history(user_id: int, post_id: int):
    uid = str(user_id)
    db.setdefault(uid, {}).setdefault("history", [])
    db[uid]["history"].append(post_id)
    save_db(db)


def pop_history(user_id: int):
    uid = str(user_id)
    hist = db.get(uid, {}).get("history", [])
    if not hist:
        return None
    last = hist.pop()
    save_db(db)
    return last
