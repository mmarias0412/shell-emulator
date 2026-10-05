# Эмулятор оболочки UNIX (вариант 22)

## Общее описание

Эмулятор командной строки UNIX-подобной ОС с графическим интерфейсом
(tkinter). Реализованы этапы 1–5: REPL, конфигурация, виртуальная
файловая система (VFS), навигация по ней и команды управления файлами.

## Функции и настройки

- Окно с заголовком `Эмулятор - [username@hostname]`; имя пользователя и
  хост берутся из реальной ОС.
- Парсер: строка делится по пробелам на команду и аргументы.
- `ls [путь]` — список содержимого каталога; каталоги помечаются `/`;
  если путь — файл, выводится только его имя; без аргумента — текущий
  каталог.
- `cd [путь]` — переход по VFS; поддерживает `.`, `..`, абсолютные и
  относительные пути; без аргумента переходит в `/home` (если есть)
  или в корень.
- `echo текст` — печатает аргументы через пробел.
- `history` — нумерованный список всех введённых команд.
- `clear` — очищает окно вывода.
- `chown <владелец> <путь>` — меняет владельца файла или каталога.
  Поддерживает относительные и абсолютные пути, включая `.`.
- `rmdir <путь>` — удаляет пустой каталог. Нельзя удалить непустой
  каталог, файл или корень `/`. Если удаляется текущий каталог,
  `cwd` автоматически поднимается на уровень вверх.
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
- Приглашение к вводу показывает текущий каталог VFS:
  `user@host:/docs/2024$`.
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

Проверка команд этапа 4 (навигация, echo, history, clear) на разных VFS:

    ./scripts/test_stage4.sh    # Linux / macOS
    scripts\test_stage4.bat     # Windows

Проверка команд этапа 5 (chown, rmdir) на разных VFS:

    ./scripts/test_stage5.sh    # Linux / macOS
    scripts\test_stage5.bat     # Windows

Каждый вызов эмулятора в этих скриптах открывает окно; чтобы перейти к
следующему запуску, закройте текущее окно (или дождитесь `exit`, если
он есть в тестовом стартовом скрипте).

## Структура

    src/cmd_parser.py   разбор строки на команду и аргументы
    src/config.py        параметры командной строки (--vfs, --script)
    src/script.py         чтение стартового скрипта, обработка комментариев
    src/shell.py          логика команд, запуск стартового скрипта
    src/vfs.py            виртуальная файловая система (загрузка, сохранение, навигация)
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

Формат файла VFS — CSV с колонками `path`, `type`, `content`, `owner`.
Вложенность передаётся путём (например, `/docs/2024/report.txt`);
промежуточные каталоги создаются неявно. Содержимое файлов хранится в
base64. Колонка `owner` необязательна: старые файлы с тремя колонками
по-прежнему читаются, владелец для них по умолчанию `root`.

Пример (`data/vfs_minimal.csv`):

    path,type,content,owner
    /home,dir,,root
    /home/hello.txt,file,SGVsbG8=,root

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
    vfs-save: требуется один аргумент - путь

Если файл VFS не найден или формат неверный, выводится ошибка и
используется VFS по умолчанию:

    python src/main.py --vfs data/nonexistent.csv

    [debug] Параметры запуска:
    [debug]   vfs    = data/nonexistent.csv
    [debug]   script = (не задан)
    vfs: не удалось открыть 'data/nonexistent.csv': [Errno 2] No such file or directory

### Этап 4. Навигация по VFS и дополнительные команды

Реализованы настоящие команды навигации и дополнительные утилиты.
Приглашение к вводу показывает текущий каталог VFS.

Запуск с вложенной VFS:

    python src/main.py --vfs data/vfs_nested.csv

Вывод в окне эмулятора:

    [debug] Параметры запуска:
    [debug]   vfs    = data/vfs_nested.csv
    [debug]   script = (не задан)
    user@host:/$ ls
    docs/  images/
    user@host:/$ cd docs
    user@host:/docs$ cd 2024
    user@host:/docs/2024$ ls
    notes/  report.txt
    user@host:/docs/2024$ cd ..
    user@host:/docs$ cd ..
    user@host:/$ ls /docs/2024/notes
    todo.txt
    user@host:/$ ls /images/logo.png
    logo.png
    user@host:/$ cd /nope
    cd: нет такого файла или каталога: '/nope'
    user@host:/$ cd /images/logo.png
    cd: не каталог: '/images/logo.png'
    user@host:/$ cd a b
    cd: слишком много аргументов
    user@host:/$ echo Привет, виртуальная файловая система!
    Привет, виртуальная файловая система!
    user@host:/$ history
     1  ls
     2  cd docs
     ...
    13  history

### Этап 5. Права доступа и управление каталогами

Добавлены команды управления владельцами файлов и каталогами. Все
изменения производятся только в памяти; для сохранения на диск
используется команда `vfs-save`.

Запуск с вложенной VFS:

    python src/main.py --vfs data/vfs_nested.csv

Вывод в окне эмулятора:

    [debug] Параметры запуска:
    [debug]   vfs    = data/vfs_nested.csv
    [debug]   script = (не задан)
    user@host:/$ ls
    docs/  empty/  images/
    user@host:/$ chown mary /images/logo.png
    chown: '/images/logo.png' теперь принадлежит 'mary'
    user@host:/$ chown root /docs
    chown: '/docs' теперь принадлежит 'root'
    user@host:/$ cd docs
    user@host:/docs$ chown mary .
    chown: '.' теперь принадлежит 'mary'
    user@host:/docs$ cd ..
    user@host:/$ chown alice
    chown: требуется два аргумента — владелец и путь
    user@host:/$ chown mary /nope
    chown: нет такого файла или каталога: '/nope'
    user@host:/$ rmdir /empty
    rmdir: каталог '/empty' удалён
    user@host:/$ ls
    docs/  images/
    user@host:/$ rmdir /docs
    rmdir: каталог не пуст: '/docs'
    user@host:/$ rmdir /images/logo.png
    rmdir: не каталог: '/images/logo.png'
    user@host:/$ rmdir /
    rmdir: нельзя удалить корневой каталог
    user@host:/$ rmdir
    rmdir: требуется один аргумент — путь
    user@host:/$ rmdir a b
    rmdir: требуется один аргумент — путь
    user@host:/$ vfs-save stage5_out.csv
    vfs-save: сохранено в 'stage5_out.csv'

В сохранённом файле `stage5_out.csv` будут видны изменения: папка
`/empty` отсутствует, а владельцы `/images/logo.png` и `/docs`
обновились.

Запуск тестов этапа 5:

    python -m unittest discover -s tests -v
    ./scripts/test_stage5.sh    # Linux / macOS
    scripts\test_stage5.bat     # Windows