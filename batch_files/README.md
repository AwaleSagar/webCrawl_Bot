# Web Crawler - Batch Files

This directory contains batch files for running the web crawler with a custom Python environment.

## Custom Python Environment

The batch files in this directory are configured to use the following Python environment:

- **Python Path**: `C:\Users\sagar\miniconda3\envs\test_env\python.exe`
- **Python Version**: Python 3.10.15

## Available Batch Files

The following batch files are available:

1. **run_with_custom_python.bat**
   - Runs the web crawler using the run_crawler.py script
   - Falls back to direct execution if there are import errors
   - Supports resuming from checkpoints

2. **run_direct_with_custom_python.bat**
   - Runs the web crawler directly by executing main.py in the src directory
   - Use this if you encounter import errors with run_with_custom_python.bat
   - Supports resuming from checkpoints

3. **install_dependencies_with_custom_python.bat**
   - Installs the required dependencies using pip
   - Offers to download NLTK data after installation

4. **test_crawler_with_custom_python.bat**
   - Runs the test crawler script to verify functionality

5. **download_nltk_data_with_custom_python.bat**
   - Downloads NLTK data packages required for advanced keyword processing

6. **manage_checkpoints.bat**
   - Provides a menu-based interface for managing checkpoints
   - List, resume from, and delete checkpoints

## Usage

All batch files are designed to be run from the `batch_files` directory. They will automatically navigate to the parent directory to access the required files and return to the `batch_files` directory when finished.

### Installing Dependencies

Run the following batch file to install the required dependencies:

```
install_dependencies_with_custom_python.bat
```

### Running the Web Crawler

You can run the web crawler using either of the following batch files:

```
run_with_custom_python.bat
```

or

```
run_direct_with_custom_python.bat
```

### Command Line Arguments

You can pass command line arguments to the web crawler by adding them after the batch file name:

```
run_with_custom_python.bat --keywords "python web crawler" --max-depth 2 --output results.json
```

### Testing the Web Crawler

To run a simple test of the web crawler:

```
test_crawler_with_custom_python.bat
```

### Downloading NLTK Data

To download NLTK data packages:

```
download_nltk_data_with_custom_python.bat
```

### Managing Checkpoints

To manage checkpoints (list, resume from, delete):

```
manage_checkpoints.bat
```

## Checkpoint Functionality

The web crawler now includes checkpoint functionality to save progress at regular intervals, providing a failsafe for network connection issues. By default, checkpoints are saved every 5 minutes (300 seconds) to the `checkpoints` directory.

### Checkpoint Types

- **Auto Checkpoints**: Saved automatically at regular intervals during crawling
- **Final Checkpoints**: Saved when the crawler completes successfully
- **Interrupt Checkpoints**: Saved when the crawler is interrupted (Ctrl+C)

### Resuming from Checkpoints

When running the crawler, you will be asked if you want to resume from a checkpoint. If you choose to do so, you will be shown a list of available checkpoints and prompted to enter the name of the checkpoint file to resume from.

### Checkpoint Management

The `manage_checkpoints.bat` file provides a menu-based interface for managing checkpoints:

1. **List available checkpoints**: Shows all available checkpoint files with details
2. **Resume crawling from a checkpoint**: Resumes crawling from a selected checkpoint
3. **Delete a checkpoint**: Deletes a selected checkpoint file
4. **Delete all checkpoints**: Deletes all checkpoint files

## Troubleshooting

If you encounter import errors when running the web crawler, try using the direct execution method with `run_direct_with_custom_python.bat`. 