@echo off
setlocal

:: Set venv folder name
set VENV_DIR=venv

:: Check if venv exists, if not, create it
if not exist %VENV_DIR%\Scripts\activate.bat (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
)

:: Activate the venv
call %VENV_DIR%\Scripts\activate.bat

:: Install required packages
call setup.bat

:: Run the script
python working.py

endlocal
