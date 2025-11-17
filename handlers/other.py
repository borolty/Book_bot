from aiogram import Router
from aiogram.types import Message
from lexicon.lexicon import LEXICON

# Инициализируем роутер уровня модуля
other_router = Router()


# Хэндлер для сообщений, которые не попали в другие хэндлеры
@other_router.message()
async def send_answer(message: Message):
    await message.answer(text=LEXICON["other_answer"]) # (f"Это эхо! {message.text}") - в скобках можно записать так и не вызывать LEXICON_RU

# Повторюша
#async def send_echo(message: Message):
#    try:
#        await message.send_copy(chat_id=message.chat.id)
#    except TypeError:
#        await message.reply(text=LEXICON_RU['no_echo'])
