# Эмулятор оболочки UNIX (вариант 22)

## Общее описание

Эмулятор командной строки UNIX-подобной ОС с графическим интерфейсом
(tkinter). Реализованы этапы 1–3: REPL, конфигурация и виртуальная
файловая система (VFS).

## Функции и настройки

- Окно с заголовком `Эмулятор - [username@hostname]`; имя пользователя и
  хост берутся из реальной ОС.
- Парсер: строка делится по пробелам на команду и аргументы.
- `ls`, `cd` — заглушки, печатают своё имя и список аргументов.
- `exit` — закрывает эмулятор.
- Неизвестная команда: `<имя>: command not found`.
- Пустой ввод игнорируется.
- Параметры командной строки:
  - `--vfs PATH` — путь к файлу VFS (CSV-формат). Если не задан или файл
    не найден — используется VFS по умолчанию (корень `/` с каталогом
    `home`), в отладке выводится сообщение об ошибке.
  - `--script PATH` — путь к стартовому скрипту.
- При запуске в окно выводится отладочная информация о заданных
  параметрах (`[debug] ...`).
- Стартовый скрипт: набор команд эмулятора, выполняемых по очереди при
  запуске. Поддерживает комментарии — символ `#` и всё до конца строки
  (в начале строки или после пробела). Пустые строки и строки-комментарии
  пропускаются. Ошибочные команды скрипта не прерывают выполнение —
  выводится `<имя>: command not found`, и работа продолжается. Если
  скрипт содержит `exit`, оставшиеся строки не выполняются, и окно
  закрывается.
- При выполнении скрипта в окне отображается как ввод (приглашение и
  команда), так и вывод — имитация диалога с пользователем.
- Если скрипт не найден или его не удалось прочитать, выводится
  сообщение вида `script: не удалось прочитать '<путь>': ...`, работа
  эмулятора продолжается.
- `vfs-info` — показывает имя загруженной VFS и её SHA-256 хеш.
- `vfs-save PATH` — сохраняет текущее состояние VFS на диск в CSV-формат.
  Без аргумента выводится ошибка, работа не прерывается.

## Команды для сборки проекта и запуска тестов

Нужен Python 3.8+ (tkinter входит в стандартную поставку).

Запуск эмулятора:

    run.bat                                   # Windows, без параметров
    ./run.sh                                  # Linux / macOS, без параметров
    python src/main.py --vfs PATH --script PATH   # напрямую, с параметрами

Юнит-тесты:

    python -m unittest discover -s tests

Проверка параметров командной строки (все сочетания `--vfs`/`--script`):

    ./scripts/test_config.sh    # Linux / macOS
    scripts\test_config.bat     # Windows

Проверка стартового скрипта (комментарии, ошибки, `exit`, отсутствующий
файл, неизвестный параметр):

    ./scripts/test_script.sh    # Linux / macOS
    scripts\test_script.bat     # Windows

Проверка VFS (загрузка, сохранение, ошибки формата, разные варианты VFS):

    ./scripts/test_vfs.sh       # Linux / macOS
    scripts\test_vfs.bat        # Windows


## Структура

    src/cmd_parser.py   разбор строки на команду и аргументы
    src/config.py        параметры командной строки (--vfs, --script)
    src/script.py         чтение стартового скрипта, обработка комментариев
    src/shell.py          логика команд, запуск стартового скрипта
    src/vfs.py            виртуальная файловая система (загрузка, сохранение)
    src/gui.py             окно tkinter
    src/main.py            точка входа
    data/                  примеры файлов VFS (*.csv)
    tests/                 юнит-тесты
    examples/              примеры стартовых скриптов эмулятора (*.emu)
    scripts/                скрипты реальной ОС для проверки параметров

## Примеры

### Этап 1. Команды в интерактивном режиме

    user@host:~$ ls -l /tmp
    ls: аргументы: ['-l', '/tmp']
    user@host:~$ cd docs
    cd: аргументы: ['docs']
    user@host:~$ foo
    foo: command not found
    user@host:~$ exit

### Этап 2. Запуск с параметрами и стартовым скриптом

Файл `examples/basic.emu`:

    # Базовый стартовый скрипт: команды-заглушки и ошибка
    ls -l /tmp        # команда с аргументами
    cd docs

    # пустые строки и комментарии пропускаются
    foo               # неизвестная команда -> command not found

Запуск:

    python src/main.py --vfs data/vfs.csv --script examples/basic.emu

Вывод в окне эмулятора:

    [debug] Параметры запуска:
    [debug]   vfs    = data/vfs.csv
    [debug]   script = examples/basic.emu
    user@host:~$ ls -l /tmp
    ls: аргументы: ['-l', '/tmp']
    user@host:~$ cd docs
    cd: аргументы: ['docs']
    user@host:~$ foo
    foo: command not found

Если параметр не задан, в отладке выводится `(не задан)`:

    python src/main.py

    [debug] Параметры запуска:
    [debug]   vfs    = (не задан)
    [debug]   script = (не задан)

Скрипт с командой `exit` (`examples/with_exit.emu`) завершает эмулятор
и закрывает окно, не выполняя строки после `exit`:

    # Скрипт завершает эмулятор командой exit
    ls
    exit
    ls                # эта строка уже не выполнится

### Этап 3. Работа с VFS

Формат файла VFS — CSV с колонками `path`, `type`, `content`. Вложенность
передаётся путём (например, `/docs/2024/report.txt`); промежуточные
каталоги создаются неявно. Содержимое файлов хранится в base64.

Пример (`data/vfs_minimal.csv`):

    path,type,content
    /home,dir,
    /home/hello.txt,file,SGVsbG8=

Запуск с файлом VFS и стартовым скриптом:

    python src/main.py --vfs data/vfs_minimal.csv --script examples/full_check.emu

Вывод в окне эмулятора:

    [debug] Параметры запуска:
    [debug]   vfs    = data/vfs_minimal.csv
    [debug]   script = examples/full_check.emu
    user@host:~$ ls -l /tmp
    ls: аргументы: ['-l', '/tmp']
    user@host:~$ vfs-info
    vfs-info: vfs_minimal.csv
    ab44f3a9391d9200130f35a648b7d13a262f4eefceb20f1efff10e6168e58254
    user@host:~$ vfs-save output.csv
    vfs-save: сохранено в 'output.csv'
    user@host:~$ vfs-save
    vfs-save: требуется один аргумент – путь

Если файл VFS не найден или формат неверный, выводится ошибка и
используется VFS по умолчанию:

    python src/main.py --vfs data/nonexistent.csv

    [debug] Параметры запуска:
    [debug]   vfs    = data/nonexistent.csv
    [debug]   script = (не задан)
    vfs: не удалось открыть 'data/nonexistent.csv': [Errno 2] No such file or directory