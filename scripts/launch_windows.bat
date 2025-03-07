@echo off
echo ======================================
echo CreepyAI - Windows Launcher
echo ======================================

:: Get script directory
set "SCRIPT_DIR=%~dp0"
cd "%SCRIPT_DIR%"

:: Check for virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    set PYTHON_PATH=venv\Scripts\python.exe
) else (
    set PYTHON_PATH=python
    echo No virtual environment detected, using system Python
)

:: Clear any conflicting Qt plugin paths
set QT_PLUGIN_PATH=
set QT_QPA_PLATFORM_PLUGIN_PATH=

:: Get PyQt5 path and set plugin path
for /f "tokens=*" %%a in ('%PYTHON_PATH% -c "import PyQt5; import os; print(os.path.dirname(PyQt5.__file__))"') do set QT_BASE=%%a

if not "%QT_BASE%"=="" (
    echo Found PyQt5 at: %QT_BASE%
    set "QT_PLUGIN_PATH=%QT_BASE%\Qt5\plugins"
    echo Set QT_PLUGIN_PATH to: %QT_PLUGIN_PATH%
) else (
    echo Error: Could not find PyQt5 installation
    exit /b 1
)

:: Launch CreepyAI
echo Launching CreepyAI...
%PYTHON_PATH% launch_creepyai.py %*
