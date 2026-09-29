"""Логика эмулятора оболочки. Не зависит от GUI, поэтому легко тестируется."""
import getpass
import socket

from cmd_parser import parse
from config import Config
from script import ScriptError, read_script


def _get_user():
    try:
        return getpass.getuser()
    except Exception:
        return "user"


class Shell:
    """Выполняет введённые команды и хранит состояние сессии."""

    def __init__(self,config=None):
        self.config=config or Config()
        self.user = _get_user()
        self.host = socket.gethostname()
        self.running = True
        self.commands = {
            "ls": self._stub,
            "cd": self._stub,
            "exit": self._exit,
        }

    def title(self):
        """Заголовок окна на основе реальных данных ОС."""
        return f"Эмулятор - [{self.user}@{self.host}]"

    def prompt(self):
        """Приглашение к вводу, как в UNIX-оболочке."""
        return f"{self.user}@{self.host}:~$ "
    def startup_output(self):
        """Строки для вывода при запуске: отладка параметров и скрипт."""
        lines = self.config.debug_lines()
        if self.config.script_path:
            lines += self.run_script(self.config.script_path)
        return lines

    def run_script(self, path):
        """Выполняет скрипт и возвращает диалог: ввод и вывод строк."""
        try:
            commands = read_script(path)
        except ScriptError as err:
            return [f"script: {err}"]
        dialog = []
        for command in commands:
            dialog.append(self.prompt() + command)
            result = self.execute(command)
            if result:
                dialog.append(result)
            if not self.running:
                break
        return dialog


    def execute(self, line):
        """Выполняет строку и возвращает текст вывода (может быть пустым)."""
        name, args = parse(line)
        if name is None:
            return ""
        handler = self.commands.get(name)
        if handler is None:
            return f"{name}: command not found"
        return handler(name, args)

    def _stub(self, name, args):
        """Заглушка: печатает имя команды и её аргументы."""
        return f"{name}: аргументы: {args}"

    def _exit(self, name, args):
        self.running = False
        return ""
