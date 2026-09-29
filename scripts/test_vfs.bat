@echo off
chcp 65001 >nul
cd /d "%~dp0.."
rem Проверка работы с разными вариантами VFS и обработки ошибок загрузки.

echo 1. VFS по умолчанию (путь не задан)
call run.bat --script examples\full_check.emu

echo 2. Минимальная VFS (один файл)
call run.bat --vfs data\vfs_minimal.csv --script examples\full_check.emu

echo 3. VFS с несколькими файлами (включая бинарный)
call run.bat --vfs data\vfs_files.csv --script examples\full_check.emu

echo 4. VFS с вложенностью не менее 3 уровней
call run.bat --vfs data\vfs_nested.csv --script examples\full_check.emu

echo 5. Ошибка: файл VFS не найден
call run.bat --vfs data\no_such_vfs.csv --script examples\full_check.emu

echo 6. Ошибка: неверный формат VFS (неверный type)
call run.bat --vfs data\vfs_bad.csv --script examples\full_check.emu
