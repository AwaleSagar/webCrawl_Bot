@echo off
title Web Crawler Launcher
color 0A

:menu
cls
echo Web Crawler Launcher
echo ====================
echo.
echo Select an option:
echo.
echo 1. Run Web Crawler
echo 2. Run Web Crawler Directly
echo 3. Install Dependencies
echo 4. Download NLTK Data
echo 5. Test Web Crawler
echo 6. Manage Checkpoints
echo 7. View Logs
echo 8. View Gemini API Logs
echo 9. Exit
echo.
set choice=
set /p choice=Enter your choice (1-9): 

if "%choice%"=="" goto invalid_choice

if "%choice%"=="1" (
    echo.
    echo Running Web Crawler...
    cd batch_files
    call run_with_custom_python.bat
    cd ..
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo Running Web Crawler Directly...
    cd batch_files
    call run_direct_with_custom_python.bat
    cd ..
    goto menu
)

if "%choice%"=="3" (
    echo.
    echo Installing Dependencies...
    cd batch_files
    call install_dependencies_with_custom_python.bat
    cd ..
    goto menu
)

if "%choice%"=="4" (
    echo.
    echo Downloading NLTK Data...
    cd batch_files
    call download_nltk_data_with_custom_python.bat
    cd ..
    goto menu
)

if "%choice%"=="5" (
    echo.
    echo Testing Web Crawler...
    cd batch_files
    call test_crawler_with_custom_python.bat
    cd ..
    goto menu
)

if "%choice%"=="6" (
    echo.
    echo Managing Checkpoints...
    cd batch_files
    call manage_checkpoints.bat
    cd ..
    goto menu
)

if "%choice%"=="7" (
    echo.
    echo Viewing Logs...
    if not exist logs (
        echo No logs directory found.
        echo Run the crawler first to generate logs.
        pause
        goto menu
    )
    
    echo Available log files:
    echo -------------------
    dir /b logs\*.log 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo No log files found in logs directory.
    )
    echo.
    echo Press any key to return to menu...
    pause > nul
    goto menu
)

if "%choice%"=="8" (
    echo.
    echo Viewing Gemini API Logs...
    if not exist gemini_logs (
        echo No Gemini logs directory found.
        echo Run the crawler with Gemini API first to generate logs.
        pause
        goto menu
    )
    
    echo Available Gemini API log files:
    echo -----------------------------
    dir /b gemini_logs\*.json 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo No Gemini API log files found.
        pause
        goto menu
    )
    
    echo.
    echo Enter the name of the log file to view (or press Enter to return to menu):
    set log_file=
    set /p log_file=
    
    if "%log_file%"=="" (
        goto menu
    )
    
    if exist "gemini_logs\%log_file%" (
        echo.
        echo Contents of %log_file%:
        echo -------------------
        type "gemini_logs\%log_file%"
        echo.
        echo.
        echo Press any key to return to menu...
        pause > nul
    ) else (
        echo File not found: %log_file%
        pause
    )
    goto menu
)

if "%choice%"=="9" (
    echo.
    echo Exiting Web Crawler Launcher...
    exit /b 0
)

:invalid_choice
echo.
echo Invalid choice. Please try again.
pause
goto menu 