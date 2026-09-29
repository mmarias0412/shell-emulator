@echo off
chcp 65001 >nul
cd /d "%~dp0.."
rem Проверка параметров --vfs и --script (все сочетания).

echo 1. Без параметров
call run.bat

echo 2. Только --vfs
call run.bat --vfs data\vfs.csv

echo 3. Только --script
call run.bat --script examples\basic.emu

echo 4. Оба параметра
call run.bat --vfs data\vfs.csv --script examples\basic.emu
