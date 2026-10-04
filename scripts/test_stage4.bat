@echo off
chcp 65001 >nul
cd /d "%~dp0.."
rem Проверка команд этапа 4 (ls, cd, clear, echo, history) на разных VFS.

echo 1. VFS по умолчанию (только каталог home)
call run.bat --script examples\stage4_check.emu

echo 2. Минимальная VFS (один файл в корне)
call run.bat --vfs data\vfs_minimal.csv --script examples\stage4_check.emu

echo 3. VFS с несколькими файлами
call run.bat --vfs data\vfs_files.csv --script examples\stage4_check.emu

echo 4. VFS с вложенностью не менее 3 уровней
call run.bat --vfs data\vfs_nested.csv --script examples\stage4_check.emu
