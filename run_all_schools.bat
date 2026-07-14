@echo off
REM Double-click this file to fetch data for all schools (all tables, no arguments).
cd /d "%~dp0"
python -m data_fetchers.school_data.fetch_script
if errorlevel 1 (
    echo.
    echo Script exited with an error.
)
pause
