#!/usr/bin/env bash 

# Add rendered images from the diagrams to the README.org 

# Use a ** Diagrams ** section in the README.org file to add the rendered images.
diagrams_start="#+DIAGRAMS_START"
diagrams_end="#+DIAGRAMS_END"

# Error if the Diagrams section does not exist.
if ! grep -q "$diagrams_start" README.org; then
	echo "ERROR: Diagrams section not found in README.org"
	exit 1
fi

if ! grep -q "$diagrams_end" README.org; then
	echo "ERROR: Diagrams section not found in README.org"
	exit 1
fi

# Remove the existing Diagrams section.
if grep -q "$diagrams_start" README.org; then
	sed -i "/$diagrams_start/,/$diagrams_end/d" README.org
fi
