# Функция для инициализации "базы данных"
def init_db():
    return {
        "user_template": {"page": 1, "bookmarks": set()},
        "users": {}
    }