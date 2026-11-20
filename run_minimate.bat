@echo off
chcp 65001 > nul
set PYTHONUTF8=1
cd /d "%~dp0"

echo Dang khoi dong MINIMATE...
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" src\main.py %*
) else if exist ".venv_hf_test\Scripts\python.exe" (
    ".venv_hf_test\Scripts\python.exe" src\main.py %*
) else (
    python src\main.py %*
)

if errorlevel 1 (
    echo.
    echo Chuong trinh gap loi. Nhan phim bat ky de dong.
    pause > nul
)
