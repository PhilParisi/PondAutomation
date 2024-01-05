#!/bin/bash

# This file should be run by crontab upon reboot. It starts the reboot_pond.py script.

# Change to the desired directory
cd ~/PondAutomation

# Run the Python script
python3 reboot_pond.py
