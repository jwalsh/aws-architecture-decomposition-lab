#!/bin/bash

explore_dir() {
    local dir="${1:-$(pwd)}"

    echo "Exploration prompt for LLM:"
    echo "The following content represents the structure and contents of the '$dir' directory:"
    echo

    # Find all non-hidden files, excluding .git and other dot directories
    find "$dir" -type f \
        ! -path '*/\.*' \
        ! -path '*/\.git/*' \
        -print0 | sort -z | while IFS= read -r -d '' file; do
        relative_path="${file#$dir/}"
        mime_type=$(file --brief --mime-type "$file")

        echo "--- File: $relative_path ($mime_type) ---"

        if [[ $mime_type == text/* ]]; then
            echo
            cat "$file"
            echo
        fi

        echo
    done

    echo "End of exploration prompt."
}

# Run if no arguments are provided, otherwise use the provided directory
if [ $# -eq 0 ]; then
    explore_dir
else
    explore_dir "$1"
fi
