#!/bin/sh
# Проверка параметров --vfs и --script (все сочетания).
# Каждый запуск открывает окно; закройте его, чтобы пойти дальше.
cd "$(dirname "$0")/.." || exit 1

echo "1. Без параметров"
./run.sh

echo "2. Только --vfs"
./run.sh --vfs data/vfs.csv

echo "3. Только --script"
./run.sh --script examples/basic.emu

echo "4. Оба параметра"
./run.sh --vfs data/vfs.csv --script examples/basic.emu
