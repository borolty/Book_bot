from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import LEXICON

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

#button_start = KeyboardButton(text=LEXICON["Start read"])
# Инициализируем билдер для клавиатуры с кнопкой Начать чтение
#start_kb_builder = ReplyKeyboardBuilder()

# Добавляем кнопки в билдер с аргументом width=2
#start_kb_builder.row(button_start, width=2)

# Создаём клавиатуру с кнопкой Начать чтение
#start_kb: ReplyKeyboardMarkup = start_kb_builder.as_markup(
#    one_time_keyboard=True, resize_keyboard=True)

# Создаем объекты инлайн-кнопок
button_start_in = InlineKeyboardButton(
    text=LEXICON["Start read"], callback_data="Start read3"
)

# Создаем объект инлайн-клавиатуры
keyboard_in = InlineKeyboardMarkup(inline_keyboard=[[button_start_in]])


# Функция, генерирующая клавиатуру для страницы книги
def create_pagination_keyboard(*buttons: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Добавляем в билдер ряд с кнопками
    kb_builder.row(
        *[
            InlineKeyboardButton(
                text=LEXICON[button] if button in LEXICON else button, #text=LEXICON.get(button, button) - можно так записать
                callback_data=button,
            )
            for button in buttons
        ]
    )
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()