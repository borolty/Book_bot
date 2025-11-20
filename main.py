import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode # форматирование текста (пр: <b>жирный текст</b>)
from config.config import Config, load_config
from handlers.other import other_router
from handlers.user import user_router
from keyboards.menu_commands import set_main_menu
from services.file_handling import prepare_book
#from database.database import init_db
from database.database import db

# Инициализируем логгер
logger = logging.getLogger(__name__)

# Функция конфигурирования и запуска бота
async def main():
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Задаём базовую конфигурацию логирования
    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
    )
    # Выводим в консоль информацию о начале запуска бота
    logger.info("Starting bot")

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()


# Подготавливаем книгу
    logger.info("Preparing book")
    book = prepare_book("book/book.txt")
    logger.info("The book is uploaded. Total pages: %d", len(book))

# Инициализируем "базу данных"
#    db: dict = init_db()


# Сохраняем готовую книгу и "базу данных" в `workflow_data`
    dp.workflow_data.update(book=book, db=db)

# асинхронный вызов функции для настройки главное меню команд
    await set_main_menu(bot)

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_router)
    dp.include_router(other_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


# из шаблона
# Импортируем роутеры
# ...
# Импортируем миддлвари
# ...
# Импортируем вспомогательные функции для создания нужных объектов
# ...
#from keyboards.main_menu import set_main_menu

# Инициализируем логгер
#logger = logging.getLogger(__name__)

# Инициализируем объект хранилища
#storage = ...

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота, полученный у @BotFather
#BOT_TOKEN = '8368878470:AAHodapW6XrrDhfr9clYMawpTtIQ0-W9RhM'

#config: Config = load_config('.env')

# Инициализируем другие объекты (пул соединений с БД, кэш и т.п.)
# ...

# Помещаем нужные объекты в workflow_data диспетчера
#dp.workflow_data.update(...)

# Настраиваем главное меню бота
#await set_main_menu(bot)

# Регистриуем роутеры
#logger.info('Подключаем роутеры')
# ...

# Регистрируем миддлвари
#logger.info('Подключаем миддлвари')
# ...

# Список с ID администраторов бота (в квадратных скобках через запятую)
#admin_ids: list[int] = [9...]
