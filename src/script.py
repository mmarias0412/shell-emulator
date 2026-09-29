"""Чтение стартового скрипта: комментарии и пустые строки пропускаются."""
import re


COMMENT_RE = re.compile(r"(^|\s)#.*$")


class ScriptError(Exception):
    """Ошибка чтения стартового скрипта."""


def strip_comment(line):
    """Удаляет комментарий и пробелы по краям строки."""
    return COMMENT_RE.sub("", line).strip()


def read_script(path):
    """Возвращает список команд скрипта без комментариев и пустых строк."""
    try:
        with open(path, encoding="utf-8-sig") as file:
            lines = file.read().splitlines()
    except (OSError, UnicodeDecodeError) as err:
        raise ScriptError(f"не удалось прочитать '{path}': {err}") from err
    commands = (strip_comment(line) for line in lines)
    return [command for command in commands if command]
