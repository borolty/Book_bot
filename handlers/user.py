from copy import deepcopy
from aiogram import F, Router, types
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command, CommandStart

from keyboards.bookmarks_kb import create_bookmarks_keyboard, create_edit_keyboard
from keyboards.pagination_kb import create_pagination_keyboard, paginate, keyboard_in, continue_kb, post_keyboard
from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from lexicon.lexicon import LEXICON

# подключаем JSON-базу
from database.database import db, save_all_users
from database.db_channel import get_user_state, set_current_post, push_history, pop_history

CHANNEL = "@rechelove"
FIRST_POST = 29
MAX_POST_ID = 3000

user_router = Router()


# Используйте Command() с аргументом commands (в виде списка)
@user_router.message(Command(commands=["start_posts"]))
async def process_start_posts(message: types.Message, bot):
    # Ваш код обработчика здесь
    #await message.reply("Обработка команды start_posts")
    user = get_user_state(message.from_user.id)
    user["current_post"] = FIRST_POST
    user["history"] = []
    set_current_post(message.from_user.id, FIRST_POST)

    await bot.forward_message(
        chat_id=message.from_user.id,
        from_chat_id=CHANNEL,
        message_id=FIRST_POST
        )

    set_current_post(message.from_user.id, FIRST_POST + 1)

    await message.answer(
        "Приятного чтения!",
        reply_markup=post_keyboard()
    )

    # ------------------- NEXT POST ------------------------
@user_router.callback_query(F.data == "next_post")
async def next_post(callback: CallbackQuery, bot):

    #user = get_user_state(callback.from_user.id) - одной строкой две следущ строки
    user_id = callback.from_user.id
    user = get_user_state(user_id)

    post_id = user["current_post"]

    # На случай, если вышли за пределы канала
    if post_id > MAX_POST_ID:
        await callback.answer("Поздравляем, вы дочитали книгу!")
        return

    try:
        # Пробуем отправить пост
        await bot.forward_message(
            chat_id=user_id, #callback.from_user.id,
            from_chat_id=CHANNEL,
            message_id=post_id
        )

        # Сохраняем историю
        push_history(user_id, post_id)

        # Увеличиваем номер поста
        set_current_post(user_id, post_id + 1)
    #set_current_post(callback.from_user.id, post_id + 1)

        # Обновляем кнопки
        await callback.message.answer(
            f"Страница_{post_id}",
            reply_markup=post_keyboard()
        )

        await callback.answer()

    except: #Exception as e:
        # Пост может быть удалён → просто прыгаем к следующему
        set_current_post(user_id, post_id + 1)
        await callback.answer(f"Пост {post_id} недоступен, пропускаю...")

    # ------------------- PREVIOUS POST ------------------------
@user_router.callback_query(F.data == "previous_post")
async def previous_post(callback: CallbackQuery, bot):

    #user = get_user_state(callback.from_user.id)
    user_id = callback.from_user.id
    user = get_user_state(user_id)

    prev_id = pop_history(user_id)
    #post_id = user["current_post"]

    # На случай, если вышли за пределы канала
    if prev_id is None:
        await callback.answer("Вы на первой странице.")
        return

    try:
        # Пробуем отправить пост
        await bot.forward_message(
            chat_id=user_id, #callback.from_user.id,
            from_chat_id=CHANNEL,
            message_id=prev_id
        )

        # Обновляем текущий
        current = user["current_post"]
        set_current_post(user_id, prev_id)

        # текущий пост (который мы сейчас покинули) должен уйти в историю
        # но ТОЛЬКО если он не совпадает с prev_id (чтобы не было дублей)
        if current != prev_id:
            push_history(user_id, current)

        # Обновляем кнопки
        await callback.message.answer(
            f"Страница_{prev_id}",
            reply_markup=post_keyboard()
        )

        await callback.answer()

    except:

        await callback.answer("Этот пост недоступен.")

# ---------- /start ----------
@user_router.message(CommandStart())
async def process_start_command(message: Message):
    user_id = str(message.from_user.id)

    # если пользователя ещё нет — создаём по шаблону
    if user_id not in db["users"]:
        db["users"][user_id] = deepcopy(db["user_template"])
        save_all_users(db["users"])

        await message.answer(LEXICON[message.text], reply_markup=keyboard_in)

    else:
        # пользователь уже есть — смотрим, на какой странице он остановился
        page = db["users"][user_id]["page"]

        await message.answer(
            LEXICON[message.text],
            reply_markup=continue_kb
        )

# ---------- /book_selection ----------
@user_router.message(Command(commands="book_selection"))
async def process_book_selection_command(message: Message):
    await message.answer(LEXICON[message.text])

# ---------- /help ----------
@user_router.message(Command(commands="help"))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])


# ---------- /contents ----------
@user_router.message(Command(commands="contents"))
async def process_contents_command(message: Message):
    text = LEXICON["/contents"]

    pages = paginate(text)

    for page in pages:
        await message.answer(page)


# ---------- /beginning ----------
@user_router.message(Command(commands="beginning"))
async def process_beginning_command(message: Message, book: dict):
    user_id = str(message.from_user.id)

    db["users"][user_id]["page"] = 1
    save_all_users(db["users"])

    text = book[1]
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"1/{len(book) - 1}",
            "forward",
        ),
    )

# ---------- кнопка "Book_selection" ----------
@user_router.callback_query(F.data == "Book_selection")
async def process_button_start_in_click(callback: CallbackQuery):

    await callback.message.edit_text(
        text=LEXICON["/book_selection"],
        #reply_markup=create_pagination_keyboard(),
    )
    await callback.answer()

# ---------- кнопка "start reading" ----------
@user_router.callback_query(F.data == "start_reading")
async def process_button_start_in_click(callback: CallbackQuery, book: dict):
    user_id = str(callback.from_user.id)

    db["users"][user_id]["page"] = 1
    save_all_users(db["users"])

    text = book[1]
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"1/{len(book)-1}",
            "forward",
        ),
    )
    await callback.answer()

# ---------- кнопка "continue_reading" ----------
@user_router.callback_query(F.data == "continue_reading")
async def continue_reading(callback: CallbackQuery, book: dict):
    user_id = str(callback.from_user.id)
    page = db["users"][user_id]["page"]

    await callback.message.edit_text(
        text=book[page],
        reply_markup=create_pagination_keyboard(
            "backward",
            f"{page}/{len(book)-1}",
            "forward",
        ),
    )
    await callback.answer()

# ---------- /continue ----------
@user_router.message(Command(commands="continue"))
async def process_continue_command(message: Message, book: dict):
    user_id = str(message.from_user.id)

    page = db["users"][user_id]["page"]
    text = book[page]

    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"{page}/{len(book)-1}",
            "forward",
        ),
    )


# ---------- /bookmarks ----------
@user_router.message(Command(commands="bookmarks"))
async def process_bookmarks_command(message: Message, book: dict):
    user_id = str(message.from_user.id)
    bookmarks = db["users"][user_id]["bookmarks"]

    if bookmarks:
        await message.answer(
            text=LEXICON["/bookmarks"],
            reply_markup=create_bookmarks_keyboard(*bookmarks, book=book),
        )
    else:
        await message.answer(text=LEXICON["no_bookmarks"])


# ---------- кнопка ВПЕРЁД ----------
@user_router.callback_query(F.data == "forward")
async def process_forward_press(callback: CallbackQuery, book: dict):
    user_id = str(callback.from_user.id)
    page = db["users"][user_id]["page"]

    if page < len(book):
        new_page = page + 1
        db["users"][user_id]["page"] = new_page
        save_all_users(db["users"])

        await callback.message.edit_text(
            text=book[new_page],
            reply_markup=create_pagination_keyboard(
                "backward",
                f"{new_page}/{len(book)-1}",
                "forward",
            ),
        )
    await callback.answer()


# ---------- кнопка НАЗАД ----------
@user_router.callback_query(F.data == "backward")
async def process_backward_press(callback: CallbackQuery, book: dict):
    user_id = str(callback.from_user.id)
    page = db["users"][user_id]["page"]

    if page > 1:
        new_page = page - 1
        db["users"][user_id]["page"] = new_page
        save_all_users(db["users"])

        await callback.message.edit_text(
            text=book[new_page],
            reply_markup=create_pagination_keyboard(
                "backward",
                f"{new_page}/{len(book)-1}",
                "forward",
            ),
        )
    await callback.answer()


# ---------- добавление закладки ----------
@user_router.callback_query(lambda c: "/" in c.data and c.data.replace("/", "").isdigit())
async def process_page_press(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    page = db["users"][user_id]["page"]

    if page not in db["users"][user_id]["bookmarks"]:
        db["users"][user_id]["bookmarks"].append(page)
        save_all_users(db["users"])

    await callback.answer("Страница добавлена в закладки!")


# ---------- переход по закладке ----------
@user_router.callback_query(IsDigitCallbackData())
async def process_bookmark_press(callback: CallbackQuery, book: dict):
    user_id = str(callback.from_user.id)
    bookmarks = int(callback.data)

    db["users"][user_id]["page"] = bookmarks
    save_all_users(db["users"])

    await callback.message.edit_text(
        text=book[bookmarks],
        reply_markup=create_pagination_keyboard(
            "backward",
            f"{bookmarks}/{len(book)-1}",
            "forward",
        ),
    )


# ---------- режим редактирования закладок ----------
@user_router.callback_query(F.data == "edit_bookmarks")
async def process_edit_press(callback: CallbackQuery, book: dict):
    user_id = str(callback.from_user.id)

    await callback.message.edit_text(
        text=LEXICON["edit_bookmarks"],
        reply_markup=create_edit_keyboard(
            *db["users"][user_id]["bookmarks"], book=book
        ),
    )


# ---------- отмена редактирования ----------
@user_router.callback_query(F.data == "cancel")
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON["cancel_text"])


# ---------- удаление закладки ----------
@user_router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery, book: dict):
    user_id = str(callback.from_user.id)
    page = int(callback.data[:-3])

    db["users"][user_id]["bookmarks"].remove(page)
    save_all_users(db["users"])

    bookmarks = db["users"][user_id]["bookmarks"]
    if bookmarks:
        await callback.message.edit_text(
            text=LEXICON["/bookmarks"],
            reply_markup=create_edit_keyboard(*bookmarks, book=book),
        )
    else:
        await callback.message.edit_text(text=LEXICON["no_bookmarks"])
