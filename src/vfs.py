"""Виртуальная файловая система (VFS).

Источник данных — CSV-файл. Каждая строка описывает один элемент VFS:
путь от корня, тип ('file' или 'dir') и содержимое файла в base64
(для каталогов поле содержимого пустое). Вложенность передаётся самим
путём (например, '/docs/2024/report.txt'); промежуточные каталоги,
не перечисленные отдельной строкой, создаются неявно. Все операции
производятся только в памяти: чтение CSV строит дерево объектов,
запись VFS на диск (vfs-save) сериализует текущее дерево обратно
в тот же CSV-формат.
"""
import base64
import csv
import hashlib
import io

DEFAULT_NAME = "(в памяти)"


class VfsError(Exception):
    """Ошибка загрузки, разбора или сохранения VFS."""


class VfsNode:
    """Узел VFS: файл или каталог."""

    def __init__(self, name, is_dir, content=b""):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children = {} if is_dir else None

    def ensure_dir(self, name):
        """Возвращает дочерний каталог, создавая его при необходимости."""
        child = self.children.get(name)
        if child is None:
            child = VfsNode(name, is_dir=True)
            self.children[name] = child
        elif not child.is_dir:
            raise VfsError(f"'{name}' уже существует как файл")
        return child

    def add_file(self, name, content):
        """Добавляет файл; ошибка, если путь уже занят."""
        if name in self.children:
            raise VfsError(f"путь с именем '{name}' уже существует")
        self.children[name] = VfsNode(name, is_dir=False, content=content)


def _split_path(path):
    """Возвращает сегменты пути без пустых элементов."""
    return [part for part in path.strip("/").split("/") if part]


class Vfs:
    """Дерево VFS в памяти с загрузкой из CSV и сохранением обратно."""

    COLUMNS = ["path", "type", "content"]

    def __init__(self, name, root, source_bytes):
        self.name = name
        self.root = root
        self.source_bytes = source_bytes

    @property
    def sha256(self):
        """Хеш SHA-256 данных, из которых построена текущая VFS."""
        return hashlib.sha256(self.source_bytes).hexdigest()

    @classmethod
    def default(cls):
        """VFS по умолчанию, когда путь к ней не задан при запуске."""
        root = VfsNode("/", is_dir=True)
        root.ensure_dir("home")
        return cls(DEFAULT_NAME, root, cls._serialize(root))

    @classmethod
    def load(cls, path):
        """Загружает VFS из CSV-файла на диске."""
        try:
            with open(path, "rb") as file:
                raw = file.read()
        except OSError as err:
            raise VfsError(f"не удалось открыть '{path}': {err}") from err
        root = cls._parse(raw, path)
        name = path.replace("\\", "/").rsplit("/", 1)[-1]
        return cls(name, root, raw)

    @classmethod
    def _parse(cls, raw, path):
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as err:
            raise VfsError(f"'{path}': неверная кодировка ({err})") from err
        reader = csv.DictReader(io.StringIO(text))
        if reader.fieldnames != cls.COLUMNS:
            raise VfsError(
                f"'{path}': ожидались колонки {cls.COLUMNS}, "
                f"получено {reader.fieldnames}"
            )
        root = VfsNode("/", is_dir=True)
        for row_num, row in enumerate(reader, start=2):
            cls._add_row(root, row, path, row_num)
        return root

    @classmethod
    def _add_row(cls, root, row, path, row_num):
        raw_path = (row.get("path") or "").strip()
        kind = (row.get("type") or "").strip()
        content_field = row.get("content") or ""
        if not raw_path or raw_path == "/":
            return
        if kind not in ("file", "dir"):
            raise VfsError(
                f"'{path}': строка {row_num}: неверный type '{kind}'"
            )
        segments = _split_path(raw_path)
        try:
            node = root
            for part in segments[:-1]:
                node = node.ensure_dir(part)
            leaf = segments[-1]
            if kind == "dir":
                node.ensure_dir(leaf)
            else:
                content = base64.b64decode(content_field, validate=True)
                node.add_file(leaf, content)
        except (VfsError, ValueError) as err:
            raise VfsError(
                f"'{path}': строка {row_num}: {err}"
            ) from err

    @classmethod
    def _serialize(cls, root):
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow(cls.COLUMNS)
        for path, node in cls._walk(root, ""):
            kind = "dir" if node.is_dir else "file"
            content = "" if node.is_dir else base64.b64encode(
                node.content
            ).decode("ascii")
            writer.writerow([path, kind, content])
        return buf.getvalue().encode("utf-8")

    @classmethod
    def _walk(cls, node, prefix):
        for name in sorted(node.children):
            child = node.children[name]
            path = f"{prefix}/{name}"
            yield path, child
            if child.is_dir:
                yield from cls._walk(child, path)

    def save(self, path):
        """Сохраняет текущее (только в памяти изменённое) состояние
        VFS на диск в исходном CSV-формате."""
        data = self._serialize(self.root)
        try:
            with open(path, "wb") as file:
                file.write(data)
        except OSError as err:
            raise VfsError(f"не удалось сохранить '{path}': {err}") from err
        self.source_bytes = data
