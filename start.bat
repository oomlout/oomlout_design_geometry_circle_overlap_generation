@echo off
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else (
    where py >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON=py -3"
    ) else (
        set "PYTHON=python"
    )
)

%PYTHON% main.py
if errorlevel 1 goto :error

%PYTHON% generate_navigation.py
if errorlevel 1 goto :error

echo.
echo Output gallery refreshed at output\README.md
goto :eof

:error
echo.
echo Start failed.
exit /b 1