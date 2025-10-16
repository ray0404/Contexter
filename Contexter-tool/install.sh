#!/bin/bash

# Exit on any error
set -e

echo "Starting the installation of Contexter..."

# Update package list and install Python and pip for Termux
echo "Updating packages and installing Python..."
pkg update -y
pkg upgrade -y
pkg install -y python

# Install project dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Install the Contexter project
echo "Installing Contexter..."
pip install .

echo "Contexter has been successfully installed!"
echo "You can now use the Contexter tools from your terminal."
