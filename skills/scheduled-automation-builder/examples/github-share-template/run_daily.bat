@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist logs mkdir logs

py -3.11 update_report.py >> logs\update.log 2>&1
if errorlevel 1 exit /b 1

py -3.11 analyze_and_update.py >> logs\analyze.log 2>&1
if errorlevel 1 exit /b 1
