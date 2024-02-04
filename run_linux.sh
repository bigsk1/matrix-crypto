#!/bin/bash

# Define cleanup function
cleanup() {
    echo ""
    echo "Script interrupted. If you want to run the application again with different options,"
    echo "first activate the virtual environment using:"
    echo "source venv/bin/activate"
    echo "Then, you can run the application manually, for example:"
    echo "python matrix_crypto.py --help"
    exit 0
}

# Trap SIGINT (Ctrl+C) and execute the cleanup function
trap cleanup SIGINT

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


trap - SIGINT

echo "Script completed successfully. Remember to activate the virtual environment with 'source venv/bin/activate' before running commands manually."