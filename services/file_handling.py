import logging
import os

logger = logging.getLogger(__name__)


# Функция, возвращающая строку с текстом страницы и её размер
def _get_part_text(text: str, start: int, page_size: int) -> tuple[str, int]:
    end_signs = ".!?"
    forbidden = [" т.", "т.е.", "т. е.", "и т.д.", "и т.п.", "т.к.", "т. к.", ". М. В.",
                "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "0."]  # ← список расширяемый
    max_end = min(len(text), start + page_size)
    chunk = text[start:max_end]

    last_good = -1
    i = 0
    while i < len(chunk):
        if chunk[i] in end_signs:
             # --- ПРОВЕРКА НА ЗАПРЕЩЁННЫЕ АББРЕВИАТУРЫ ---
            if chunk[i] == '.':
                for abbr in forbidden:
                    L = len(abbr)

                    # Проверяем, попадает ли найденная точка внутрь аббревиатуры
                    start_pos = i - (L - 1)
                    if start_pos >= 0 and chunk[start_pos:i+1] == abbr:
                        i += 1
                        break
                else:
                    pass  # если не нашли аббревиатуру — продолжаем обычную логику
                # если нашли — цикл for выполнил break и мы должны continue
                if chunk[i-1] == '.':
                    continue
            # --- КОНЕЦ ПРОВЕРКИ ---

            # Обработка последовательности . ! ?
            while i + 1 < len(chunk) and chunk[i + 1] in end_signs:
                i += 1
            seq_end = i

            after_seq = start + seq_end + 1
            if (
                after_seq == len(text)
                or text[after_seq].isspace()
                or text[after_seq].isalpha()
            ):
                last_good = seq_end
        i += 1

    if last_good != -1:
        page_text = chunk[: last_good + 1]
    else:
        page_text = chunk


    return page_text, len(page_text)


# Функция, формирующая словарь книги
def prepare_book(path: str, page_size: int = 1050) -> dict[int, str]:
    try:
        with open(file=os.path.normpath(path), mode="r", encoding="utf-8") as file:
            text = file.read()
    except Exception as e:
        logger.error("Error reading a book: %s", e)
        raise e

    book = {}
    start = 0
    page_number = 1

    while start < len(text):
        page_text, actual_page_size = _get_part_text(text, start, page_size)
        start += actual_page_size
        book[page_number] = page_text.strip()
        page_number += 1
    # ...

    return book