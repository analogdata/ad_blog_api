#!/bin/bash
# Simple wrapper script to execute the kill_uvicorn.py script

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Execute the Python script with direnv
cd "$SCRIPT_DIR" && direnv exec . uv run helper_scripts/kill_uvicorn.py "$@"
