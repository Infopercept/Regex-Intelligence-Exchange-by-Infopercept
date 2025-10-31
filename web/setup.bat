@echo off
REM Setup script for Regex Intelligence Exchange Web Application

echo Setting up Regex Intelligence Exchange Web Application...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Install development dependencies if requested
if "%1"=="--dev" (
    echo Installing development dependencies...
    pip install -r requirements-dev.txt
)

echo Setup complete!
echo.
echo To run the application:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run the application: python run.py
echo.
echo For development:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run with debug mode: python run.py --debug