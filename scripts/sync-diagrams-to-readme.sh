#!/usr/bin/env bash

# Script to update image links in a README.org file with colored logging

# Configuration
README_FILE="README.org"
RENDERED_IMAGES_DIR="docs/images"
RENDERED_IMAGES_FILETYPE="png"
DIAGRAMS_SECTION_START="#+DIAGRAMS_START"
DIAGRAMS_SECTION_END="#+DIAGRAMS_END"
SED_COMMAND="sed"

# Load logger.sh
SCRIPT_DIR=$(dirname "$0")
source "$SCRIPT_DIR/logger.sh"

# --- Helper Functions ---
check_macos() {
    if [[ $OSTYPE == "darwin"* ]]; then
        SED_COMMAND="gsed"
        info "Using gsed for macOS compatibility"
    fi
}

check_section_markers() {
    if ! grep -q "$DIAGRAMS_SECTION_START" "$README_FILE" || ! grep -q "$DIAGRAMS_SECTION_END" "$README_FILE"; then
        error "Diagrams section markers not found in $README_FILE"
        exit 1
    fi
}

check_rendered_images_dir() {
    if [ ! -d "$RENDERED_IMAGES_DIR" ]; then
        error "Rendered images directory $RENDERED_IMAGES_DIR not found"
        exit 1
    fi

    if [ ! "$(ls -A $RENDERED_IMAGES_DIR)" ]; then
        info "No rendered images found in $RENDERED_IMAGES_DIR"
        exit 0
    fi
}

update_diagrams_section() {
    local tmpfile=$(mktemp)

    echo "$DIAGRAMS_SECTION_START" >> "$tmpfile"
    echo "*** Available Diagrams" >> "$tmpfile"
    echo "The following diagrams are available in this project:" >> "$tmpfile"

    for image in "$RENDERED_IMAGES_DIR"/*."$RENDERED_IMAGES_FILETYPE"; do
        local image_name=$(basename "$image")
        local image_title=$(echo "$image_name" | sed 's/\.png$//' | sed 's/_/ /g' | sed 's/\b\(.\)/\u\1/g')
        
        info "Adding image $image_name"
        echo "**** $image_title" >> "$tmpfile"
        echo "[[file:$image]]" >> "$tmpfile"
        echo "" >> "$tmpfile"
    done

    echo "$DIAGRAMS_SECTION_END" >> "$tmpfile"

    info "Updating Diagrams section in $README_FILE"
    if $SED_COMMAND -i "/$DIAGRAMS_SECTION_START/,/$DIAGRAMS_SECTION_END/{ /$DIAGRAMS_SECTION_START/r $tmpfile
        /$DIAGRAMS_SECTION_START/,/$DIAGRAMS_SECTION_END/d
    }" "$README_FILE"; then
        pass "Successfully updated Diagrams section in $README_FILE"
    else
        error "Failed to update $README_FILE"
        rm "$tmpfile"
        exit 1
    fi

    rm "$tmpfile"
}

# --- Main Script Logic ---
main() {
    info "Updating image links in $README_FILE"

    check_macos
    check_section_markers
    check_rendered_images_dir
    update_diagrams_section

    pass "Script completed successfully"
}

main
