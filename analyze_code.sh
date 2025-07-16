#!/bin/bash
# Wrapper script to run the static analysis CLI from the root directory

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/app"
python analyze_code.py "$@"
