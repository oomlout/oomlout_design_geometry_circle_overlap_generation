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

set /p WORD=Word to preview in 3D: 
if "%WORD%"=="" goto :error

echo.
echo Opening cinematic 3D preview...
%PYTHON% preview_3d.py --word "%WORD%" --material topo_clay
if errorlevel 1 goto :error

goto :eof

:error
echo.
echo 3D preview failed.
exit /b 1