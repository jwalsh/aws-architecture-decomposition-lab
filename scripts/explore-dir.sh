#!/bin/bash

explore_dir() {
    local dir="${1:-$(pwd)}"
    
    echo "## Detailed Exploration of the '$dir' Directory for LLM Analysis:"
    echo

    # Summarize overall directory structure
    echo "### Directory Structure Summary:"
    find "$dir" -type d -print ! -path "\.git" | sed 's@'"$dir"'@@' | awk '{print "- " $0}'  # List subdirectories relative to base
    echo

    # File information and content
    echo "### File Details:"
    find "$dir" -type f \
        ! -path '*/\.*' \
        ! -path '*/\.git/*' \
        -print0 | sort -z | while IFS= read -r -d '' file; do

        relative_path="${file#$dir/}"
        mime_type=$(file --brief --mime-type "$file")
        file_size=$(du -h "$file" | awk '{print $1}')  # Add human-readable file size

        echo "- **File:** $relative_path"
        echo "  - **Type:** $mime_type"
        echo "  - **Size:** $file_size"
        echo "  - **Content (if text):**"
        
        # Selective content display based on file type and size
        if [[ $mime_type == text/* ]] && [[ $file_size != "0" ]]; then  # Only display content if not empty
            head -n 20 "$file"  # Show the first 20 lines (adjust as needed)
            if [[ $(wc -l "$file" | awk '{print $1}') -gt 20 ]]; then
                echo "  ... (truncated - full file content in repository)"
            fi
        fi

        echo
    done
}

# Conditional execution based on argument presence
if [ $# -eq 0 ]; then
    explore_dir  # Explore current directory if no argument is given
else
    explore_dir "$1"  # Explore specified directory
fi
