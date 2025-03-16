@echo off
echo Installing Dependencies with Custom Python
echo Python path: C:\Users\sagar\miniconda3\envs\test_env\python.exe
echo Version: Python 3.10.15
echo.

:: Change to parent directory
cd ..

:: Check if requirements.txt exists
if not exist requirements.txt (
    echo Error: requirements.txt not found.
    echo Make sure you are running this script from the correct directory.
    pause
    cd batch_files
    exit /b 1
)

echo Installing dependencies...
"C:\Users\sagar\miniconda3\envs\test_env\python.exe" -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error installing dependencies.
    pause
    cd batch_files
    exit /b %ERRORLEVEL%
)

echo.
echo Dependencies installed successfully.
echo.
echo Would you like to download NLTK data now? (Y/N)
set /p download_nltk=

if /i "%download_nltk%"=="Y" (
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

    echo.
    echo Downloading NLTK data...
    "C:\Users\sagar\miniconda3\envs\test_env\python.exe" src\download_nltk_data.py
)

echo.
echo Setup complete!

:: Return to batch_files directory
cd batch_files
pause 