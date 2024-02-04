#!/bin/bash

# Define the virtual environment directory
VENV_DIR="venv"

# Check for Python 3.6+ installation
if ! command -v python3 &> /dev/null || [ $(python3 -c 'import sys; print(sys.version_info.major)') -lt 3 ] || { [ $(python3 -c 'import sys; print(sys.version_info.major)') -eq 3 ] && [ $(python3 -c 'import sys; print(sys.version_info.minor)') -lt 6 ]; }; then
    echo "Python 3.6 or newer is not installed. Please install Python 3.6+ before running this script."
    exit 1
fi

# Create a Python virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating a Python virtual environment..."
    python3 -m venv $VENV_DIR
    echo "Installing requirements..."
    source $VENV_DIR/bin/activate
    pip install -r requirements.txt
else
    echo "Activating the virtual environment..."
    source $VENV_DIR/bin/activate
fi


# Start the application
echo "Starting the application...use ctl+c to exit"
python matrix_crypto.py


