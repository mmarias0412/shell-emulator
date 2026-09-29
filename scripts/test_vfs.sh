#!/bin/sh
# Проверка работы с разными вариантами VFS и обработки ошибок загрузки.
# Каждый запуск сам закроет окно командой exit из стартового скрипта.
cd "$(dirname "$0")/.." || exit 1

echo "1. VFS по умолчанию (путь не задан)"
./run.sh --script examples/full_check.emu

echo "2. Минимальная VFS (один файл)"
./run.sh --vfs data/vfs_minimal.csv --script examples/full_check.emu

echo "3. VFS с несколькими файлами (включая бинарный)"
./run.sh --vfs data/vfs_files.csv --script examples/full_check.emu

echo "4. VFS с вложенностью не менее 3 уровней"
./run.sh --vfs data/vfs_nested.csv --script examples/full_check.emu

echo "5. Ошибка: файл VFS не найден"
./run.sh --vfs data/no_such_vfs.csv --script examples/full_check.emu

echo "6. Ошибка: неверный формат VFS (неверный type)"
./run.sh --vfs data/vfs_bad.csv --script examples/full_check.emu
