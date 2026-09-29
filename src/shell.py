"""Логика эмулятора оболочки. Не зависит от GUI, поэтому легко тестируется."""
import getpass
import socket

from cmd_parser import parse
from config import Config
from script import ScriptError, read_script
from vfs import Vfs, VfsError


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
        self.vfs_error=None
        self.vfs=self._load_vfs()
        self.commands = {
            "ls": self._stub,
            "cd": self._stub,
            "exit": self._exit,
            "vfs-info": self._vfs_info,
            "vfs-save": self._vfs_save,
        }
    def _load_vfs(self):
        """Загружает VFS по пути из конфигурации, иначе — VFS по умолчанию."""
        if not self.config.vfs_path:
            return Vfs.default()
        try:
            return Vfs.load(self.config.vfs_path)
        except VfsError as err:
            self.vfs_error = str(err)
            return Vfs.default()

    def title(self):
        """Заголовок окна на основе реальных данных ОС."""
        return f"Эмулятор - [{self.user}@{self.host}]"

    def prompt(self):
        """Приглашение к вводу, как в UNIX-оболочке."""
        return f"{self.user}@{self.host}:~$ "
    def startup_output(self):
        """Строки для вывода при запуске: отладка, статус VFS, скрипт."""
        lines = self.config.debug_lines()
        if self.vfs_error:
            lines.append(f"vfs: {self.vfs_error}")
            lines.append("vfs: используется VFS по умолчанию")
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
    def _vfs_info(self, name, args):
        """Служебная команда: имя загруженной VFS и хеш SHA-256 её данных."""
        return f"vfs-info: {self.vfs.name} {self.vfs.sha256}"

    def _vfs_save(self, name, args):
        """Сохраняет текущее состояние VFS на диск в исходном формате."""
        if len(args) != 1:
            return "vfs-save: требуется один аргумент - путь"
        try:
            self.vfs.save(args[0])
        except VfsError as err:
            return f"vfs-save: {err}"
        return f"vfs-save: сохранено в '{args[0]}'"

