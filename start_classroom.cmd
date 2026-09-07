@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please follow INTERACTIVE.md to create .venv and install dependencies.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" tools\start_classroom.py
if errorlevel 1 pause
