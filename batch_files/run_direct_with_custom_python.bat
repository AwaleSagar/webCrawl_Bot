@echo off
setlocal enabledelayedexpansion

REM Check if src directory exists
if not exist "%~dp0..\src" (
    echo Error: src directory not found.
    echo Please make sure you are running this script from the correct directory.
    exit /b 1
)

REM Check if main.py exists
if not exist "%~dp0..\src\main.py" (
    echo Error: src\main.py not found.
    echo Please make sure you are running this script from the correct directory.
    exit /b 1
)

REM Create checkpoints directory if it doesn't exist
if not exist "%~dp0..\checkpoints" (
    mkdir "%~dp0..\checkpoints"
    echo Created checkpoints directory.
)

REM Create gemini_logs directory if it doesn't exist
if not exist "%~dp0..\gemini_logs" (
    mkdir "%~dp0..\gemini_logs"
    echo Created gemini_logs directory.
)

REM Ask if user wants to resume from a checkpoint
set /p resume_choice="Do you want to resume from a checkpoint? (Y/N): "
if not defined resume_choice set resume_choice=N

REM Convert to uppercase for easier comparison
set resume_choice=!resume_choice:y=Y!
set resume_choice=!resume_choice:n=N!

if /i "!resume_choice!"=="Y" (
    REM List available checkpoints
    echo.
    echo Available checkpoints:
    dir /b "%~dp0..\checkpoints\*.pkl" 2>nul
    echo.
    
    REM Ask for checkpoint file
    set /p checkpoint_file="Enter checkpoint filename (or press Enter to cancel): "
    
    if not defined checkpoint_file (
        echo Resuming from checkpoint cancelled. Starting fresh crawl...
        goto start_fresh
    )
    
    REM Check if the checkpoint file exists
    if exist "%~dp0..\checkpoints\!checkpoint_file!" (
        echo Resuming from checkpoint: !checkpoint_file!
        echo Running: python "%~dp0..\src\main.py" --resume "!checkpoint_file!"
        python "%~dp0..\src\main.py" --resume "!checkpoint_file!"
    ) else (
        echo Error: Checkpoint file not found: !checkpoint_file!
        echo Available checkpoints:
        dir /b "%~dp0..\checkpoints\*.pkl" 2>nul
        echo.
        echo Starting fresh crawl instead...
        goto start_fresh
    )
) else (
    :start_fresh
    echo Starting fresh crawl...
    echo Running: python "%~dp0..\src\main.py"
    python "%~dp0..\src\main.py"
)

echo.
echo Crawler execution completed.
pause 