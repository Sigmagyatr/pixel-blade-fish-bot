@echo off
title Pixel Blade Fishing Bot
echo Starting Pixel Blade Fishing Bot (No Console Window)...
echo.
echo Using .pyw extension - Python will run without console window!
echo.
echo Checking if .pyw files exist...
if exist main.pyw (
    echo Found main.pyw - launching now...
    python main.pyw
) else (
    echo .pyw files not found, creating them...
    echo.
    echo Renaming .py files to .pyw...
    rename main.py main.pyw 2>nul
    rename bot_core.py bot_core.pyw 2>nul
    rename status_window.py status_window.pyw 2>nul
    echo.
    echo Files renamed successfully! Launching bot...
    python main.pyw
)
if errorlevel 1 (
    echo.
    echo Error: Could not start the bot.
    echo.
    echo Make sure Python is installed and try running as administrator.
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
    echo Please run START.bat again after installation.
)
pause
