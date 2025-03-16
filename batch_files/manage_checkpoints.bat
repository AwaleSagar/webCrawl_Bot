@echo off
echo Checkpoint Manager
echo =================
echo.

:: Change to parent directory
cd ..

:: Check if checkpoints directory exists
if not exist checkpoints (
    echo No checkpoints directory found.
    echo Run the crawler first to create checkpoints.
    pause
    cd batch_files
    exit /b 1
)

:menu
cls
echo Checkpoint Manager
echo =================
echo.
echo Select an option:
echo.
echo 1. List available checkpoints
echo 2. Resume from a checkpoint
echo 3. Delete a checkpoint
echo 4. Delete all checkpoints
echo 5. Clean sensitive information from checkpoints
echo 6. Return to main menu
echo.
set choice=
set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" (
    call :list_checkpoints
    pause
    goto menu
)

if "%choice%"=="2" (
    call :resume_checkpoint
    cd batch_files
    exit /b 0
)

if "%choice%"=="3" (
    call :delete_checkpoint
    pause
    goto menu
)

if "%choice%"=="4" (
    call :delete_all_checkpoints
    pause
    goto menu
)

if "%choice%"=="5" (
    call :clean_sensitive_info
    pause
    goto menu
)

if "%choice%"=="6" (
    cd batch_files
    exit /b 0
)

echo Invalid choice. Please try again.
pause
goto menu

:list_checkpoints
echo.
echo Available checkpoints:
echo ---------------------
dir /b checkpoints\*.json 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo No checkpoint files found.
)
echo.
goto :eof

:resume_checkpoint
call :list_checkpoints
echo.
echo Enter the name of the checkpoint file to resume from:
set /p checkpoint_file=
if "%checkpoint_file%"=="" (
    echo No checkpoint selected.
    pause
    goto menu
)

if not exist "checkpoints\%checkpoint_file%" (
    echo Error: Checkpoint file not found.
    pause
    goto menu
)

echo.
echo Select how to resume:
echo 1. Run with run_crawler.py
echo 2. Run directly with main.py
echo.
set resume_choice=
set /p resume_choice=Enter your choice (1-2): 

if "%resume_choice%"=="1" (
    echo Resuming from checkpoint using run_crawler.py...
    "C:\Users\sagar\miniconda3\envs\test_env\python.exe" run_crawler.py --resume-from "checkpoints\%checkpoint_file%"
) else if "%resume_choice%"=="2" (
    echo Resuming from checkpoint using main.py directly...
    cd src
    "C:\Users\sagar\miniconda3\envs\test_env\python.exe" main.py --resume-from "..\checkpoints\%checkpoint_file%"
    cd ..
) else (
    echo Invalid choice.
    pause
    goto menu
)
goto :eof

:delete_checkpoint
call :list_checkpoints
echo.
echo Enter the name of the checkpoint file to delete:
set /p checkpoint_file=
if "%checkpoint_file%"=="" (
    echo No checkpoint selected.
    goto :eof
)

if not exist "checkpoints\%checkpoint_file%" (
    echo Error: Checkpoint file not found.
    goto :eof
)

echo.
echo Are you sure you want to delete this checkpoint? (Y/N)
set confirm=
set /p confirm=
if /i "%confirm%"=="Y" (
    del "checkpoints\%checkpoint_file%"
    echo Checkpoint deleted.
) else (
    echo Deletion cancelled.
)
goto :eof

:delete_all_checkpoints
echo.
echo Are you sure you want to delete ALL checkpoints? (Y/N)
set confirm=
set /p confirm=
if /i "%confirm%"=="Y" (
    del /q checkpoints\*.json 2>nul
    echo All checkpoints deleted.
) else (
    echo Deletion cancelled.
)
goto :eof

:clean_sensitive_info
echo.
echo Cleaning sensitive information from checkpoint files...
echo This will remove API keys and other sensitive data from all checkpoint files.
echo.
echo Are you sure you want to proceed? (Y/N)
set confirm=
set /p confirm=
if /i not "%confirm%"=="Y" (
    echo Operation cancelled.
    goto :eof
)

set found_files=0
for %%f in (checkpoints\*.json) do (
    set /a found_files+=1
    echo Processing: %%f
    
    :: Create a temporary file
    "C:\Users\sagar\miniconda3\envs\test_env\python.exe" -c "import json; import sys; import os; fname='%%f'; data=json.load(open(fname)); api_key_removed=False; if 'gemini_api_key' in data: del data['gemini_api_key']; api_key_removed=True; json.dump(data, open(fname+'.tmp', 'w')); print('API key ' + ('removed' if api_key_removed else 'not found') + ' in ' + fname)"
    
    :: Replace the original file with the cleaned version
    if exist "%%f.tmp" (
        del "%%f"
        rename "%%f.tmp" "%%~nxf"
    )
)

if %found_files%==0 (
    echo No checkpoint files found.
) else (
    echo.
    echo Cleaned %found_files% checkpoint files.
)
goto :eof 