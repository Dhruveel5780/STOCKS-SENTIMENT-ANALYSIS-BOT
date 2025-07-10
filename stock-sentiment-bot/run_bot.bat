@echo off
echo 🚀 Starting Stock Sentiment Analysis Bot...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please make sure you're in the correct directory and the venv folder exists.
    pause
    exit /b 1
)

REM Activate virtual environment and run the bot
call venv\Scripts\activate.bat
python sentiment_bot.py

echo.
echo 👋 Bot finished. Press any key to exit...
pause > nul
