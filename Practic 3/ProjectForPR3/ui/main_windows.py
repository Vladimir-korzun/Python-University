import curses

# Пункты меню. Здесь — демо :) ; в реальном проекте заполните по ТЗ
MENU_ITEMS = [
    "Настроить базу данных",
    "Добавить сотрудника",
    "и т.д. пункты согласно ТЗ"  # <-- замените на полный список
]

# ФИО авторизованного администратора (подтягивайте из БД при старте)
FIO_ADMIN = "Загружается из БД"

# Название в целом можно поменять (не строго)
APP_TITLE = "HR Manager — Главное меню"
SUBTITLE = f"Авторизован: {FIO_ADMIN}"


def draw_menu(stdscr, idx: int) -> None:
    """
    Рисует главный экран: заголовок, список пунктов и «нижнюю шапку» подсказок,
    ее по-хорошему дополнить, так же можно придумать всплывающее окно с ошибкой,
    а не просто писать его строкой.

    Параметры:
    - stdscr: главное окно curses (standard screen), предоставленное wrapper-ом.
    - idx: индекс текущего выделенного пункта (для подсветки).
    """
    stdscr.clear()  # очистить экран перед перерисовкой
    h, w = stdscr.getmaxyx()  # текущие размеры окна (строки, столбцы)

    # Заголовок по центру
    stdscr.addstr(1, max(0, (w - len(APP_TITLE)) // 2), APP_TITLE, curses.A_BOLD)
    stdscr.addstr(2, max(0, (w - len(SUBTITLE)) // 2), SUBTITLE)

    # Рисуем пункты меню столбиком, выделяя активный
    start_y = 5
    for i, text in enumerate(MENU_ITEMS):
        y = start_y + i
        x = 4
        if i == idx:
            # Включаем цветовую пару для выделения строки (инитим в main)
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, f"> {text}")
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, f"  {text}")

    # «Нижняя шапка» — строка подсказок по клавишам, рисуем другим фоном
    helpbar = " ↑/↓ — перемещение   Enter — выбрать   Esc — выход "
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(h - 1, 0, " " * (w - 1))  # заполняем последнюю строку фоном
    stdscr.addstr(h - 1, max(0, (w - len(helpbar)) // 2), helpbar)
    stdscr.attroff(curses.color_pair(2))

    stdscr.refresh()  # показать все изменения


def handle_choice(stdscr, choice: str) -> None:
    """
    Демонстрационная обработка выбора пункта меню.
    Здесь вы вызываете соответствующий функционал (подменю, функции и обработчики (перенести с первой ЛР))

    Как пример choice == "Добавить сотрудника" -> add_worker_flow(stdscr, services)
    """
    stdscr.clear()
    stdscr.addstr(2, 2, f"Вы выбрали: {choice}")
    stdscr.addstr(4, 2, "Здесь вызови соответствующую функцию/подменю…")
    stdscr.addstr(6, 2, "Нажмите любую клавишу, чтобы вернуться.")
    stdscr.refresh()
    stdscr.getch()  # ждём любую клавишу и возвращаемся в главное меню


def main(stdscr) -> None:
    """
    Точка входа curses-интерфейса. Её вызывает curses.wrapper(main) из лаунчера.

    Что делает:
    - настраивает режимы curses (скрывает курсор, включает цвета),
    - инициализирует цветовые пары (для подсветки строки меню и helpbar),
    - запускает главный цикл обработки клавиш (↑/↓/Enter/Esc),
    - перерисовывает экран при каждом шаге.

    Можете погуглить и индивидуализировать интерфейс как хотите, но прошу
    соблюдать читаемость не стоит делать красный фон и черные буквы, или красный фон и желтые,
    Лучше использовать нейтральные цветовые пары (зеленый/черный, синий/белый, оранджевый/черный)

    """
    curses.curs_set(0)  # прячем «аппаратный» курсор терминала
    curses.start_color()  # включаем поддержку цветов
    curses.use_default_colors()

    # Определяем 2 пары цветов:
    # 1) подсветка активного пункта меню (текст на CYAN фоне)
    # 2) нижняя шапка helpbar (текст на WHITE фоне)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

    current_idx = 0  # текущий выделенный пункт

    while True:
        draw_menu(stdscr, current_idx)
        key = stdscr.getch()  # ждём нажатие клавиши

        # Управление: стрелки ↑/↓ или vi-стиль k/j
        if key in (curses.KEY_UP, ord('k')):
            current_idx = (current_idx - 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_DOWN, ord('j')):
            current_idx = (current_idx + 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_ENTER, 10, 13):
            # Enter может приходить как KEY_ENTER или код 10/13 в разных терминалах
            choice = MENU_ITEMS[current_idx]
            if choice == "Выход":
                break  # выходим из главного цикла
            handle_choice(stdscr, choice)
        elif key == 27:  # Esc
            break  # тоже выходим


# Позволяет запустить модуль напрямую: python -m ui.main_windows
if __name__ == "__main__":
    curses.wrapper(main)
