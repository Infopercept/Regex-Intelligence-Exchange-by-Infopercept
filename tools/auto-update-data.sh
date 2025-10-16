#!/bin/bash
# Auto Update Data Script
# This script updates all data files and statistics in the repository

echo "Updating all data files and statistics..."

# Run the Python script to update all data
python3 tools/update-all-data.py

echo "Data update completed!"