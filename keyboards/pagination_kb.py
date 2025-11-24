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
    text=LEXICON["Start_reading"], callback_data="start_reading"
)

# Создаем объект инлайн-клавиатуры
keyboard_in = InlineKeyboardMarkup(inline_keyboard=[[button_start_in]])

# Матрешка - создание кнопок и создание клавиатуры
continue_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=LEXICON["Сontinue_reading"], callback_data="continue_reading")]
            ]
        )

# Функция, генерирующая содержание на нескольких страницах
def paginate(text: str, page_size: int = 1250) -> list[str]:
    pages = []
    while len(text) > page_size:
        split_pos = text.rfind("\n", 0, page_size)
        if split_pos == -1:
            split_pos = page_size
        pages.append(text[:split_pos])
        text = text[split_pos:].lstrip()
    pages.append(text)
    return pages

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
