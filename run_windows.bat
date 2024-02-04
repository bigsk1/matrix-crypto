@echo off

REM Define the virtual environment directory
SET VENV_DIR=venv
REM Check for Python 3.6+ installation
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 6) else 1);" 2> NUL
if errorlevel 1 (
    echo Python 3.6 or newer is not installed. Please install Python 3.6+ before running this script.
	pause
    exit /b 1
)

REM Create a Python virtual environment if it doesn't exist
IF NOT EXIST "%VENV_DIR%" (
    echo Creating a Python virtual environment...
    python -m venv %VENV_DIR%
    echo Installing requirements...
    call %VENV_DIR%\Scripts\activate.bat
    pip install -r requirements.txt
) ELSE (
    echo Activating the virtual environment...
    call %VENV_DIR%\Scripts\activate.bat
)

REM Start the application
echo Starting the application...Use crt+c to exit
python matrix_crypto.py

REM Keep the window open and virtual environment activated after script execution
echo Script execution completed. You are still in the virtual environment.
echo Feel free to run more commands.
cmd /k