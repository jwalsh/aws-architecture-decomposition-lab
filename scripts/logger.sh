#!/usr/bin/env bash

# Script to print colored messages to the console

# ANSI Escape Codes for Colors and Styles
RESET="\033[0m"
RED="\033[31m"
BLUE="\033[34m"
GREEN="\033[32m"
YELLOW="\033[33m" # Added yellow for warnings
BOLD="\033[1m"    # Added bold for emphasis

# Function to print a warning message
warn() {
    echo -e "${YELLOW}${BOLD}⚠️ WARNING: $@${RESET}" >&2 # Use yellow and bold for warnings
}

# Function to print an informational message
info() {
    echo -e "${BLUE}🔵 INFO: $@${RESET}" >&2
}

# Function to print a success message
pass() {
    echo -e "${GREEN}${BOLD}✅ SUCCESS: $@${RESET}" >&2 # Use bold for success
}

# Function to print an error message
error() {
    echo -e "${RED}${BOLD}❌ ERROR: $@${RESET}" >&2 # Use bold for errors
}
