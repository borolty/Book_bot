from copy import deepcopy
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command, CommandStart

from keyboards.bookmarks_kb import create_bookmarks_keyboard, create_edit_keyboard
from keyboards.pagination_kb import create_pagination_keyboard, paginate, keyboard_in, continue_kb
from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from lexicon.lexicon import LEXICON

# ← Вот тут подключаем JSON-базу
from database.database import db, save_all_users


user_router = Router()


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


# ---------- кнопка "Start read3" ----------
@user_router.callback_query(F.data == "Start read3")
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
    current_page = db["users"][user_id]["page"]

    if current_page < len(book):
        new_page = current_page + 1
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
    current_page = db["users"][user_id]["page"]

    if current_page > 1:
        new_page = current_page - 1
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
    page = int(callback.data)

    db["users"][user_id]["page"] = page
    save_all_users(db["users"])

    await callback.message.edit_text(
        text=book[page],
        reply_markup=create_pagination_keyboard(
            "backward",
            f"{page}/{len(book)-1}",
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



# Этот хэндлер срабатывает на команду /start
#@user_router.message(CommandStart())
#async def process_start_command(message: Message):
#    await message.answer(text=LEXICON_RU["/start"], reply_markup=yes_no_kb)


# Этот хэндлер срабатывает на команду /help
#@user_router.message(Command(commands="help"))
#async def process_help_command(message: Message):
#    await message.answer(text=LEXICON_RU["/help"], reply_markup=yes_no_kb)


# Этот хэндлер срабатывает на согласие пользователя играть в игру
#@user_router.message(F.text == LEXICON_RU["yes_button"])
#async def process_yes_answer(message: Message):
#    await message.answer(text=LEXICON_RU["yes"], reply_markup=game_kb)


# Этот хэндлер срабатывает на отказ пользователя играть в игру
#@user_router.message(F.text == LEXICON_RU["no_button"])
#async def process_no_answer(message: Message):
#    await message.answer(text=LEXICON_RU["no"])


# Этот хэндлер срабатывает на любую из игровых кнопок
#@user_router.message(
#    F.text.in_([LEXICON_RU["rock"], LEXICON_RU["paper"], LEXICON_RU["scissors"]]))
#async def process_game_button(message: Message):
#    bot_choice = get_bot_choice()
#    await message.answer(text=f"{LEXICON_RU['bot_choice']} - {LEXICON_RU[bot_choice]}")
#    winner = get_winner(message.text, bot_choice)

#    if winner == "user_won":
#        message_effect_id = "5046509860389126442"
#    else:
#        message_effect_id = None

#    await message.answer(
#        text=LEXICON_RU[winner],
#        message_effect_id=message_effect_id,
#        reply_markup=yes_no_kb,)

# Количество вопросов, доступных пользователю в игре
#ATTEMPTS = 135

# Словарь, в котором будут храниться данные пользователя
#users = {}



# Собственный фильтр, проверяющий юзера на админа
#class IsAdmin(BaseFilter):
#    def __init__(self, admin_ids: list[int]) -> None:
#        # В качестве параметра фильтр принимает список с целыми числами
#        self.admin_ids = admin_ids

#    async def __call__(self, message: Message) -> bool:
#       return message.from_user.id in self.admin_ids

# Этот хэндлер будет срабатывать, если апдейт от админа
#@router.message(IsAdmin(admin_ids))
#async def answer_if_admins_update(message: Message):
#    await message.answer(text='Вы админ')


# Этот хэндлер будет срабатывать, если апдейт не от админа
#@router.message()
#async def answer_if_not_admins_update(message: Message):
#    await message.answer(text='Вы не админ')



# Этот хэндлер будет срабатывать на блокировку бота пользователем
#@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
#async def process_user_blocked_bot(event: ChatMemberUpdated):
#   print(f'Пользователь {event.from_user.id} заблокировал бота')


    # Если пользователь только запустил бота и его нет в словаре '
    # 'users - добавляем его в словарь (добавляем после хандлера Старт)
    #if message.from_user.id not in users:
     #   users[message.from_user.id] = {
     #       'in_game': False,
     #       'value_number': None,
     #       'attempts': None,
     #       'total_values': 0,
     #       'wins': 0   }



# Этот хэндлер будет срабатывать на команду "/continue"
#@router.message(Command(commands="continue"))
#async def process_continue_command(message: Message):
#    await message.answer(
#        f'Вы остановились на вопросе: '
#        f'{users[message.from_user.id]["total_values"]}\n'
        #f'Игр выиграно: {users[message.from_user.id]["wins"]}'
#         f'\nПродолжим?'   )


# Этот хэндлер будет срабатывать на команду "/subscribe"
#@router.message(Command(commands="subscribe"))
#async def process_subscribe_command(message: Message):
 #   await message.answer(
 #       'Подпишись чтобы не забыть о проекте познания своего мира' )


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме приведенных команд
#@router.message()
#async def send_echo(message: Message):
 #   await message.reply(text=message.text)


#if __name__ == '__main__':
 #   dp.run_polling(bot)