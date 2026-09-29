#!/bin/sh
# Проверка стартового скрипта: комментарии, ошибки, exit, нет файла.
cd "$(dirname "$0")/.." || exit 1

echo "1. Скрипт с комментариями и неизвестной командой"
./run.sh --script examples/basic.emu

echo "2. Скрипт с exit (окно закроется само)"
./run.sh --script examples/with_exit.emu

echo "3. Несуществующий скрипт (ошибка, диалог продолжается)"
./run.sh --script examples/no_such_file.emu

echo "4. Неизвестный параметр (справка и код возврата 2)"
./run.sh --bogus
