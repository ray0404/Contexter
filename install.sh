#!/usr/bin/env bash

# This script automates the installation of the Contexter tool suite.
# It installs required Python packages and then installs the Contexter
# commands in an "editable" mode, so changes to the source are immediately reflected.

echo "🚀 Starting Contexter installation..."

# 1. Check if pip (Python's package installer) is available
if ! command -v pip &> /dev/null
then
    echo "❌ Error: 'pip' command not found."
    echo "   Please ensure Python and pip are installed and in your system's PATH."
    exit 1
fi

# 2. Install dependencies from the requirements.txt file
echo "📦 Installing required Python packages from requirements.txt..."
pip install -r requirements.txt

# Check if the dependency installation was successful
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies. Aborting installation."
    exit 1
fi

# 3. Install the Contexter package itself in editable mode
# The '-e' flag makes it so you can edit the source files and the
# changes will be live without needing to reinstall.
echo "🛠️  Installing the Contexter commands..."
pip install -e .

# Check if the main package installation was successful
if [ $? -ne 0 ]; then
    echo "❌ Failed to install the Contexter package. Aborting installation."
    exit 1
fi

echo ""
echo "🎉 Success! The Contexter tool suite is now installed."
echo "   You can now run commands like 'buildcontext --help' from any directory."