@echo off
echo Testing Web Crawler with Custom Python
echo Python path: C:\Users\sagar\miniconda3\envs\test_env\python.exe
echo Version: Python 3.10.15
echo.

:: Change to parent directory
cd ..

:: Check if src directory exists
if not exist src (
    echo Error: src directory not found.
    echo Make sure you are running this script from the correct directory.
    pause
    cd batch_files
    exit /b 1
)

:: Check if test_crawler.py exists
if not exist src\test_crawler.py (
    echo Error: src\test_crawler.py not found.
    echo Make sure you are running this script from the correct directory.
    pause
    cd batch_files
    exit /b 1
)

echo Running test crawler...
"C:\Users\sagar\miniconda3\envs\test_env\python.exe" src\test_crawler.py
if %ERRORLEVEL% NEQ 0 (
    echo Error running the test crawler.
    pause
    cd batch_files
    exit /b %ERRORLEVEL%
)

:: Return to batch_files directory
cd batch_files
pause 