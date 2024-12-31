#!/bin/bash
set -e

# Configure Git safe directory
git config --global --add safe.directory /github/workspace

# Execute the Python script with any passed arguments
exec python /action/main.py "$@"
