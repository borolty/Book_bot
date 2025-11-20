# # Функция для инициализации "базы данных"
# def init_db():
#     return {
#         "user_template": {"page": 1, "bookmarks": set()},
#         "users": {}
#     }

import json
import os

USERS_FILE = "users.json"


# ---------- загрузка всех пользователей ----------
def load_all_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


# ---------- сохранение всех пользователей ----------
def save_all_users(data: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------- шаблон данных одного пользователя ----------
USER_TEMPLATE = {
    "page": 1,
    "bookmarks": []     # важно! JSON поддерживает только список
}


# ---------- глобальная структура базы данных ----------
db = {
    "users": load_all_users(),
    "user_template": USER_TEMPLATE
}

# создаём файл если пустой
save_all_users(db["users"])