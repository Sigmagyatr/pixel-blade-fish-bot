@echo off
title Pixel Blade Fishing Bot - Admin Mode
echo Requesting administrator privileges...
powershell -Command "Start-Process python -ArgumentList 'bot_gui.py' -Verb RunAs"
