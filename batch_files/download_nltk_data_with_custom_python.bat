@echo off
echo Downloading NLTK Data with Custom Python
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

:: Check if download_nltk_data.py exists
if not exist src\download_nltk_data.py (
    echo Error: src\download_nltk_data.py not found.
    echo Make sure you are running this script from the correct directory.
    pause
    cd batch_files
    exit /b 1
)

echo Downloading NLTK data...
"C:\Users\sagar\miniconda3\envs\test_env\python.exe" src\download_nltk_data.py
if %ERRORLEVEL% NEQ 0 (
    echo Error downloading NLTK data.
    pause
    cd batch_files
    exit /b %ERRORLEVEL%
)

echo.
echo NLTK data downloaded successfully.

:: Return to batch_files directory
cd batch_files
pause 