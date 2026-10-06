"""Логика эмулятора оболочки. Не зависит от GUI, поэтому легко тестируется."""
import getpass
import socket

from cmd_parser import parse
from config import Config
from script import ScriptError, read_script
from vfs import Vfs, VfsError, path_str

CLEAR_SENTINEL = "\x00CLEAR\x00"
<<<<<<< HEAD
MAX_PATH_ARGS = 1
CHOWN_ARGS = 2
=======
MAX_PATH_ARGS = 1      
CHOWN_ARGS = 2 
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
        self.cwd=[]
        self.history=[]
        self.commands = {
            "ls": self._ls,
            "cd": self._cd,
            "exit": self._exit,
            "vfs-info": self._vfs_info,
            "vfs-save": self._vfs_save,
            "clear": self._clear,
            "echo": self._echo,
            "history": self._history,
            "chown": self._chown,
            "rmdir": self._rmdir,
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
        """Приглашение к вводу: пользователь, хост и текущий каталог VFS."""
        return f"{self.user}@{self.host}:{path_str(self.cwd)}$ "
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
        self.history.append(line)
        handler = self.commands.get(name)
        if handler is None:
            return f"{name}: command not found"
        return handler(name, args)


    def _exit(self, name, args):
        self.running = False
        return ""
    def _vfs_info(self, name, args):
        """Служебная команда: имя загруженной VFS и хеш SHA-256 её данных."""
        return f"vfs-info: {self.vfs.name} {self.vfs.sha256}"

    def _vfs_save(self, name, args):
        """Сохраняет текущее состояние VFS на диск в исходном формате."""
        if len(args) != MAX_PATH_ARGS:
            return "vfs-save: требуется один аргумент - путь"
        try:
            self.vfs.save(args[0])
        except VfsError as err:
            return f"vfs-save: {err}"
        return f"vfs-save: сохранено в '{args[0]}'"
    def _ls(self, name, args):
        """Выводит содержимое каталога (текущего или указанного)."""
        if len(args) > MAX_PATH_ARGS:
            return f"{name}: слишком много аргументов"
        path = args[0] if args else "."
        try:
            _, node = self.vfs.resolve(self.cwd, path)
        except VfsError as err:
            return f"{name}: {err}"
        if not node.is_dir:
            return node.name
        entries = sorted(node.children)
        names = [
            child_name + ("/" if node.children[child_name].is_dir else "")
            for child_name in entries
        ]
        return "  ".join(names)

    def _cd(self, name, args):
        """Переходит в указанный каталог (или домашний, если нет аргумента)."""
        if len(args) > MAX_PATH_ARGS:
            return f"{name}: слишком много аргументов"
        if not args:
            path = "/home" if "home" in self.vfs.root.children else "/"
        else:
            path = args[0]
        try:
            segments, node = self.vfs.resolve(self.cwd, path)
        except VfsError as err:
            return f"{name}: {err}"
        if not node.is_dir:
            return f"{name}: не каталог: '{path}'"
        self.cwd = segments
        return ""

    def _clear(self, name, args):
        """Запрашивает очистку окна вывода у GUI."""
        return CLEAR_SENTINEL

    def _echo(self, name, args):
        """Выводит переданные аргументы, разделённые пробелом."""
        return " ".join(args)

    def _history(self, name, args):
        """Выводит список всех выполненных ранее команд с номерами."""
        if not self.history:
            return ""
        width = len(str(len(self.history)))
        lines = [
            f"{i:>{width}}  {cmd}"
            for i, cmd in enumerate(self.history, start=1)
        ]
        return "\n".join(lines)
    def _chown(self, name, args):
        """Меняет владельца файла или каталога."""
        if len(args) != CHOWN_ARGS:
            return f"{name}: требуется два аргумента — владелец и путь"
        owner, path = args
        try:
            self.vfs.chown(self.cwd, path, owner)
        except VfsError as err:
            return f"{name}: {err}"
        return f"{name}: владелец '{path}' изменён на '{owner}'"

    def _rmdir(self, name, args):
        """Удаляет пустой каталог."""
        if len(args) != MAX_PATH_ARGS:
            return f"{name}: требуется один аргумент — путь"
        path = args[0]
        try:
            target_segments, _ = self.vfs.resolve(self.cwd, path)
            self.vfs.rmdir(self.cwd, path)
        except VfsError as err:
            return f"{name}: {err}"
        
        if target_segments == self.cwd:
            self.cwd = self.cwd[:-1] if self.cwd else []
        
        return f"{name}: каталог '{path}' удалён"

