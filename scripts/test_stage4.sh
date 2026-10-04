#!/bin/sh
# Проверка команд этапа 4 (ls, cd, clear, echo, history) на разных VFS.
# Каждый запуск сам закроет окно командой exit из стартового скрипта.
cd "$(dirname "$0")/.." || exit 1

echo "1. VFS по умолчанию (только каталог home)"
./run.sh --script examples/stage4_check.emu

echo "2. Минимальная VFS (один файл в корне)"
./run.sh --vfs data/vfs_minimal.csv --script examples/stage4_check.emu

echo "3. VFS с несколькими файлами"
./run.sh --vfs data/vfs_files.csv --script examples/stage4_check.emu

echo "4. VFS с вложенностью не менее 3 уровней"
./run.sh --vfs data/vfs_nested.csv --script examples/stage4_check.emu
