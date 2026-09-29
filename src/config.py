"""Параметры командной строки эмулятора."""
import argparse
from dataclasses import dataclass
from typing import Optional

NOT_SET = "(не задан)"


@dataclass
class Config:
    """Параметры, с которыми запущен эмулятор."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None

    def debug_lines(self):
        """Отладочный вывод всех заданных параметров."""
        return [
            "[debug] Параметры запуска:",
            f"[debug]   vfs    = {self.vfs_path or NOT_SET}",
            f"[debug]   script = {self.script_path or NOT_SET}",
        ]


def parse_args(argv=None):
    """Разбирает аргументы командной строки и возвращает Config."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор оболочки UNIX (вариант 22)",
    )
    parser.add_argument(
        "--vfs", metavar="PATH",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--script", metavar="PATH",
        help="путь к стартовому скрипту",
    )
    args = parser.parse_args(argv)
    return Config(vfs_path=args.vfs, script_path=args.script)
