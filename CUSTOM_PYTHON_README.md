# Web Crawler - Custom Python Setup

This README provides instructions for running the web crawler with a custom Python environment.

## Custom Python Environment

The batch files in this directory are configured to use the following Python environment:

- **Python Path**: `C:\Users\sagar\miniconda3\envs\test_env\python.exe`
- **Python Version**: Python 3.10.15

## Available Batch Files

The following batch files are available for use with the custom Python environment:

1. **run_with_custom_python.bat**
   - Runs the web crawler using the run_crawler.py script
   - Falls back to direct execution if there are import errors

2. **run_direct_with_custom_python.bat**
   - Runs the web crawler directly by executing main.py in the src directory
   - Use this if you encounter import errors with run_with_custom_python.bat

3. **install_dependencies_with_custom_python.bat**
   - Installs the required dependencies using pip
   - Offers to download NLTK data after installation

4. **test_crawler_with_custom_python.bat**
   - Runs the test crawler script to verify functionality

## Usage

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

or

```
run_direct_with_custom_python.bat --keywords "python web crawler" --max-depth 2 --output results.json
```

### Testing the Web Crawler

To run a simple test of the web crawler:

```
test_crawler_with_custom_python.bat
```

## Troubleshooting

If you encounter import errors when running the web crawler, try using the direct execution method with `run_direct_with_custom_python.bat`.

If you need to modify the Python path or add additional batch files, you can use the `manual_python_select.bat` script to generate new batch files with a different Python path. 