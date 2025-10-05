import os
import platform
import shlex
import subprocess
import sys


def in_pty() -> bool:
    """
    Возвращает True, если текущий процесс запущен в «настоящем» терминале
    (есть псевдотерминал / интерактивный stdin). Если запускаем из IDE
    (встроенная консоль), часто возвращается False.

    Зачем:
    - Если уже в терминале, можем сразу запускать curses-интерфейс.
    - Если не в терминале (напр., запуск из IDE), создадим внешнее окно.
    """
    try:
        return sys.stdin.isatty()
    except Exception:
        # На всякий случай: в некоторых окружениях stdin может отсутствовать.
        return False


def run_external():
    """
    Открывает новое окно терминала и запускает модуль с вашим curses-меню:
    `python -m ui.main_windows`.

    Платформенная логика:
    - Windows: стартуем новый процесс с флагом CREATE_NEW_CONSOLE.
    - Linux/*nix: пробуем популярные эмуляторы (x-terminal-emulator, gnome-terminal, konsole, xfce4-terminal).
    - macOS: используем AppleScript (osascript), чтобы дернуть Terminal.app.
    - Фоллбек: если ничего не удалось — запускаем в текущем окне.
    """
    # Команда запуска вашего UI-модуля (точка входа curses-меню)
    cmd = [sys.executable, "-m", "ui.main_windows"]

    if os.name == "nt":
        # Windows: новое окно консоли
        CREATE_NEW_CONSOLE = 0x00000010
        # cwd=os.getcwd() — важен, чтобы относительные пути в приложении
        # (например, data/hr.db) резолвились относительно корня проекта.
        subprocess.Popen(cmd, creationflags=CREATE_NEW_CONSOLE, cwd=os.getcwd())
    else:
        # *nix/macOS: пробуем открыть новый терминал различными способами
        term_cmds = [
            ["x-terminal-emulator", "-e"] + cmd,
            ["gnome-terminal", "--"] + cmd,
            ["konsole", "-e"] + cmd,
            # xfce4-terminal любит одну строку команды — поэтому склеиваем
            ["xfce4-terminal", "-e", " ".join(shlex.quote(c) for c in cmd)],
        ]
        for tcmd in term_cmds:
            try:
                subprocess.Popen(tcmd, cwd=os.getcwd())
                break  # первый удачный — выходим из цикла
            except FileNotFoundError:
                # Если эмулятор не установлен, пробуем следующий
                continue
        else:
            # Если ни один терминал не стартовал — branch `for-else`
            if platform.system() == "Darwin":
                # macOS: открываем Terminal.app и выполняем команду в новой вкладке/окне
                quoted = " ".join(shlex.quote(c) for c in cmd)
                osa = f'tell application "Terminal" to do script "cd {shlex.quote(os.getcwd())}; {quoted}"'
                subprocess.Popen(["osascript", "-e", osa])
            else:
                # Фоллбек для прочих случаев — запускаем в текущем окне
                subprocess.Popen(cmd, cwd=os.getcwd())


if __name__ == "__main__":
    """
    Поведение при прямом запуске лаунчера:
    1) Если уже запущены в реальном терминале — запускаем curses-приложение сразу:
       - импортируем curses
       - импортируем вашу функцию main(stdscr) из ui.main_windows
       - передаём управление через curses.wrapper(main)
    2) Иначе — открываем внешнее окно терминала (run_external()).
    """
    if in_pty():
        try:
            import curses
            from ui.main_windows import main  # Ваша точка входа: def main(stdscr):
            # рекомендую не менять, а писать уже в созданной структуре, так будет быстрее и проще для вас

            # wrapper:
            # - инициализирует curses (режим терминала, цвета, буферы),
            # - создаёт стандартное окно stdscr,
            # - передаёт его в main(stdscr),
            # - корректно восстанавливает терминал при выходе/исключении.
            curses.wrapper(main)
        except Exception as e:
            # В случае ошибки — выводим понятное сообщение (без падения стека на экран)
            print("Ошибка запуска интерфейса:", e)
    else:
        # Не в интерактивной консоли — открываем внешнее окно, как задумано.
        run_external()
