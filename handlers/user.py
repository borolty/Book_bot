from copy import deepcopy

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command, CommandStart
from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from keyboards.bookmarks_kb import create_bookmarks_keyboard, create_edit_keyboard
from keyboards.pagination_kb import create_pagination_keyboard, keyboard_in
from lexicon.lexicon import LEXICON

#from keyboards.keyboards import game_kb, yes_no_kb
#from lexicon.lexicon import LEXICON_RU
#from services.services import get_bot_choice, get_winner

#from aiogram.filters import ChatMemberUpdatedFilter, KICKED, BaseFilter
#from aiogram.types import Message, ChatMemberUpdated

# Инициализируем роутер уровня модуля
user_router = Router()


# Этот хэндлер будет срабатывать на команду "/start" -
# добавлять пользователя в базу данных, если его там еще не было
# и отправлять ему приветственное сообщение
@user_router.message(CommandStart())
async def process_start_command(message: Message, db: dict):
    await message.answer(LEXICON[message.text], reply_markup=keyboard_in)
    if message.from_user.id not in db["users"]:
        db["users"][message.from_user.id] = deepcopy(db.get("user_template"))



# Этот хэндлер будет срабатывать на команду "/help"
# и отправлять пользователю сообщение со списком доступных команд в боте
@user_router.message(Command(commands="help"))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])


# Этот хэндлер будет срабатывать на команду "/beginning"
# и отправлять пользователю первую страницу книги с кнопками пагинации
@user_router.message(Command(commands="beginning"))
async def process_beginning_command(message: Message, book: dict, db: dict):
    db["users"][message.from_user.id]["page"] = 1
    text = book[1]
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"1/{len(book)-1}",
            "forward",
        ),
    )

# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data `button_in_start_click`
@user_router.callback_query(F.data == "Start read3")
async def process_button_start_in_click(callback: CallbackQuery, book: dict, db: dict):
        current_page = db["users"][callback.from_user.id]["page"]
        if current_page < len(book):
            db["users"][callback.from_user.id]["page"] = 1 #+=1
            text = book[1]                  #[current_page + 1]
            await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                "backward",
                f"{current_page}/{len(book)-1}",  #f"{current_page + 1}/{len(book)}",
                "forward",
            ),
        )
        await callback.answer()
    #    await callback.answer()
   # ):
   # await callback.message.edit_text(
   #     text='Была нажата КНОПКА 1',
    #    reply_markup=callback.message.reply_markup)

# Этот хэндлер будет срабатывать на команду "/continue"
# и отправлять пользователю страницу книги, на которой пользователь
# остановился в процессе взаимодействия с ботом
@user_router.message(Command(commands="continue"))
async def process_continue_command(message: Message, book: dict, db: dict):
    text = book[db["users"][message.from_user.id]["page"]]
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"{db['users'][message.from_user.id]['page']}/{len(book)-1}",
            "forward",
        ),
    )


# Этот хэндлер будет срабатывать на команду "/bookmarks"
# и отправлять пользователю список сохраненных закладок,
# если они есть или сообщение о том, что закладок нет
@user_router.message(Command(commands="bookmarks"))
async def process_bookmarks_command(message: Message, book: dict, db: dict):
    if db["users"][message.from_user.id]["bookmarks"]:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(
                *db["users"][message.from_user.id]["bookmarks"], book=book
            ),
        )
    else:
        await message.answer(text=LEXICON["no_bookmarks"])


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперёд"
# во время взаимодействия пользователя с сообщением-книгой
@user_router.callback_query(F.data == "forward")
async def process_forward_press(callback: CallbackQuery, book: dict, db: dict):
    current_page = db["users"][callback.from_user.id]["page"]
    if current_page < len(book):
        db["users"][callback.from_user.id]["page"] += 1
        text = book[current_page + 1]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                "backward",
                f"{current_page + 1}/{len(book)-1}",
                "forward",
            ),
        )
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
# во время взаимодействия пользователя с сообщением-книгой
@user_router.callback_query(F.data == "backward")
async def process_backward_press(callback: CallbackQuery, book: dict, db: dict):
    current_page = db["users"][callback.from_user.id]["page"]
    if current_page > 1:
        db["users"][callback.from_user.id]["page"] -= 1
        text = book[current_page - 1]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                "backward",
                f"{current_page - 1}/{len(book)-1}",
                "forward",
            ),
        )
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с номером текущей страницы и добавлять текущую страницу в закладки
@user_router.callback_query(
    lambda x: "/" in x.data and x.data.replace("/", "").isdigit()
)
async def process_page_press(callback: CallbackQuery, db: dict):
    db["users"][callback.from_user.id]["bookmarks"].add(
        db["users"][callback.from_user.id]["page"]
    )
    await callback.answer("Страница добавлена в закладки!")


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок
@user_router.callback_query(IsDigitCallbackData())
async def process_bookmark_press(callback: CallbackQuery, book: dict, db: dict):
    text = book[int(callback.data)]
    db["users"][callback.from_user.id]["page"] = int(callback.data)
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard(
            "backward",
            f"{db['users'][callback.from_user.id]['page']}/{len(book)-1}",
            "forward",
        ),
    )


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "редактировать" под списком закладок
@user_router.callback_query(F.data == "edit_bookmarks")
async def process_edit_press(callback: CallbackQuery, book: dict, db: dict):
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_keyboard(
            *db["users"][callback.from_user.id]["bookmarks"], book=book
        ),
    )


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# "отменить" во время работы со списком закладок (просмотр и редактирование)
@user_router.callback_query(F.data == "cancel")
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON["cancel_text"])


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки
# с закладкой из списка закладок к удалению
@user_router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery, book: dict, db: dict):
    db["users"][callback.from_user.id]["bookmarks"].remove(int(callback.data[:-3]))
    if db["users"][callback.from_user.id]["bookmarks"]:
        await callback.message.edit_text(
            text=LEXICON["/bookmarks"],
            reply_markup=create_edit_keyboard(
                *db["users"][callback.from_user.id]["bookmarks"], book=book
            ),
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