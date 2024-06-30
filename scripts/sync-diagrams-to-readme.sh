#!/usr/bin/env bash

# Script to add rendered images to a README.org file with colored logging

# Configuration (Optional)
README_FILE="README.org"
rendered_images_dir="docs/images"
rendered_images_filetype="png"
diagrams_section_start="#+DIAGRAMS_START"
diagrams_section_end="#+DIAGRAMS_END"
sed_command="sed" 

# Load logger.sh
SCRIPT_DIR=$(dirname "$0")
source "$SCRIPT_DIR/logger.sh"

# --- Helper Functions ---
if [[ "$OSTYPE" == "darwin"* ]]; then  # Check for macOS
    sed_command="gsed"  
    info "Using gsed for macOS compatibility"
fi

# --- Main Script Logic ---

info "Adding rendered images to $README_FILE"

# Check if the Diagrams section exists
if ! grep -q "$diagrams_section_start" "$README_FILE"; then
    error "Diagrams section start marker ($diagrams_section_start) not found in $README_FILE"
    exit 1
fi

if ! grep -q "$diagrams_section_end" "$README_FILE"; then
    error "Diagrams section end marker ($diagrams_section_end) not found in $README_FILE"
    exit 1
fi

# Remove the list of rendered images from the Diagrams section
# info "Removing existing images from $README_FILE"
# $sed_command -i "/$diagrams_section_start/,/$diagrams_section_end/d" "$README_FILE"

# Check if the rendered images directory exists
if [ ! -d "$rendered_images_dir" ]; then
	error "Rendered images directory $rendered_images_dir not found"
	exit 1
fi

# Check if there are any rendered images to add
if [ ! "$(ls -A $rendered_images_dir)" ]; then
	info "No rendered images found in $rendered_images_dir"
	exit 0
fi

# Create a temporary file to store the updated Diagrams section
tmpfile=$(mktemp)


# Add the rendered images to the Diagrams section in the temporary file
for image in "$rendered_images_dir"/*."$rendered_images_filetype"; do
    info "Adding image $image"
    echo "[[file:$image]]" >> "$tmpfile"
done


# Insert the updated Diagrams section back into the README.org file
if $sed_command -i "/$diagrams_section_start/{r $tmpfile
d}" "$README_FILE"; then
    pass "Successfully added rendered images to $README_FILE"
else
    error "Failed to update $README_FILE"
    rm "$tmpfile"
    exit 1
fi

# Remove the temporary file
rm "$tmpfile"
