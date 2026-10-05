#!/bin/sh
# Проверка команд этапа 5 (chown, rmdir) на разных VFS.
# Каждый запуск сам закроет окно командой exit из стартового скрипта.
cd "$(dirname "$0")/.." || exit 1

echo "1. VFS с вложенностью (есть пустой каталог /empty для rmdir)"
./run.sh --vfs data/vfs_nested.csv --script examples/stage5_check.emu

echo "2. VFS по умолчанию (только пустой каталог home)"
./run.sh --script examples/stage5_check.emu

echo "3. Минимальная VFS (нет подходящих каталогов - только ошибки)"
./run.sh --vfs data/vfs_minimal.csv --script examples/stage5_check.emu
