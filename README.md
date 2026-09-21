# Эмулятор оболочки UNIX (вариант 22)

## Общее описание

Эмулятор командной строки UNIX-подобной ОС с графическим интерфейсом
(tkinter). Реализован этап 1 — REPL: диалог с пользователем и
команды-заглушки.

## Функции

- Окно с заголовком `Эмулятор - [username@hostname]`; имя пользователя и
  хост берутся из реальной ОС.
- Парсер: строка делится по пробелам на команду и аргументы.
- `ls`, `cd` — заглушки, печатают своё имя и список аргументов.
- `exit` — закрывает эмулятор.
- Неизвестная команда: `<имя>: command not found`.
- Пустой ввод игнорируется.

## Запуск и тесты

Нужен Python 3.8+ (tkinter входит в стандартную поставку).

    run.bat            # Windows
    ./run.sh           # Linux / macOS
    python src/main.py # напрямую

Тесты:

    python -m unittest discover -s tests

## Структура

    src/cmd_parser.py  разбор строки
    src/shell.py       логика команд
    src/gui.py         окно tkinter
    src/main.py        точка входа
    tests/             юнит-тесты

## Примеры

    user@host:~$ ls -l /tmp
    ls: аргументы: ['-l', '/tmp']
    user@host:~$ cd docs
    cd: аргументы: ['docs']
    user@host:~$ foo
    foo: command not found
    user@host:~$ exit
