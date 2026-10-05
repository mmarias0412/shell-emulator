@echo off
chcp 65001 >nul
cd /d "%~dp0.."
rem Проверка команд этапа 5 (chown, rmdir) на разных VFS.

echo 1. VFS с вложенностью (есть пустой каталог /empty для rmdir)
call run.bat --vfs data\vfs_nested.csv --script examples\stage5_check.emu

echo 2. VFS по умолчанию (только пустой каталог home)
call run.bat --script examples\stage5_check.emu

echo 3. Минимальная VFS (нет подходящих каталогов - только ошибки)
call run.bat --vfs data\vfs_minimal.csv --script examples\stage5_check.emu
