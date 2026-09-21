"""Логика эмулятора оболочки. Не зависит от GUI, поэтому легко тестируется."""
import getpass
import socket

from cmd_parser import parse


def _get_user():
    try:
        return getpass.getuser()
    except Exception:
        return "user"


class Shell:
    """Выполняет введённые команды и хранит состояние сессии."""

    def __init__(self):
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
