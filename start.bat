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

set /p WORD=Word to generate: 
if "%WORD%"=="" goto :error

echo.
echo Generating 2D artwork and scene data...
%PYTHON% main.py --word "%WORD%"
if errorlevel 1 goto :error

echo.
echo Generating 3D previews and orbit renders...
%PYTHON% preview_3d.py --word "%WORD%" --all-materials
if errorlevel 1 goto :error

echo.
echo Refreshing gallery navigation...
%PYTHON% generate_navigation.py
if errorlevel 1 goto :error

echo.
echo Output gallery refreshed at output\README.md
goto :eof

:error
echo.
echo Start failed.
exit /b 1