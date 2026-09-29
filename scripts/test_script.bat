@echo off
chcp 65001 >nul
cd /d "%~dp0.."
rem Проверка стартового скрипта: комментарии, ошибки, exit, нет файла.

echo 1. Скрипт с комментариями и неизвестной командой
call run.bat --script examples\basic.emu

echo 2. Скрипт с exit (окно закроется само)
call run.bat --script examples\with_exit.emu

echo 3. Несуществующий скрипт
call run.bat --script examples\no_such_file.emu

echo 4. Неизвестный параметр
call run.bat --bogus
