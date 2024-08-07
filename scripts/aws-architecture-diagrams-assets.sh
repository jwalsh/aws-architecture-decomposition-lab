#!/bin/bash
#
# Filename: aws-architecture-diagrams-assets.sh
# URL: https://aws.amazon.com/architecture/icons/
# Description:
#   This script downloads the AWS Architecture Icons asset package, extracts it,
#   and prepares the icons for use in Mermaid diagrams. It removes unnecessary
#   directories and files, ensuring only the required icons are kept.

set -euo pipefail

ASSET_BASE="Asset-Package_06072024.b5d9f0b1179c4a995a3f1e42042defabb0ba0fd2"
WORK_DIR="aws-icons-workdir-$$"
OUTPUT_DIR="pruned-assets"
BASE_URL="https://wal.sh/static/images/aws-architecture-diagrams-assets/"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if required commands are installed
for cmd in wget unzip; do
    if ! command_exists "$cmd"; then
        echo "Error: $cmd is not installed. Please install it before running this script."
        exit 1
    fi
done

# Download the asset package if it doesn't exist
if [ ! -f "${ASSET_BASE}.zip" ]; then
    echo "Downloading ${ASSET_BASE}.zip..."
    wget "https://d1.awsstatic.com/webteam/architecture-icons/${ASSET_BASE}.zip"
fi

# Create and enter the work directory
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Unzip the asset package
echo "Extracting assets..."
unzip -q "../${ASSET_BASE}.zip"

# Remove __MACOSX directories
find . -type d -name "__MACOSX" -exec rm -rf {} +

# Function to process directories
process_directories() {
    local dir="$1"
    local safe_size="$2"

    echo "Processing $dir (safe size: ${safe_size}px)"
    
    # Remove directories with unwanted sizes
    for size in 16 32 64; do
        if [ "$safe_size" -ne "$size" ]; then
            find "$dir" -type d \( -name "$size" -o -name "*_$size" \) -exec rm -rf {} +
        fi
    done

    # Remove non-PNG files
    find "$dir" -type f ! -name "*.png" -delete
}

# Process each component directory
for dir in */; do
    safe_size=48
    [ "$dir" = "Architecture-Group-Icons_06072024/" ] && safe_size=32
    process_directories "$dir" "$safe_size"
done

# Create output directory and copy pruned assets
mkdir -p "../$OUTPUT_DIR"
find . -type f -name "*.png" -exec cp {} "../$OUTPUT_DIR/" \;

# Generate review HTML
cd "../$OUTPUT_DIR"
{
    echo "<!DOCTYPE html>"
    echo "<html lang='en'>"
    echo "<head>"
    echo "    <meta charset='UTF-8'>"
    echo "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    echo "    <title>AWS Architecture Icons Review</title>"
    echo "    <style>"
    echo "        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }"
    echo "        .icon-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; }"
    echo "        .icon-item { text-align: center; }"
    echo "        .icon-item img { max-width: 64px; height: auto; }"
    echo "        .icon-item p { margin: 5px 0; font-size: 12px; word-break: break-all; }"
    echo "    </style>"
    echo "</head>"
    echo "<body>"
    echo "    <h1>AWS Architecture Icons</h1>"
    echo "    <div class='icon-grid'>"
    for icon in *.png; do
        echo "        <div class='icon-item'>"
        echo "            <img src='$BASE_URL$icon' alt='$icon'>"
        echo "            <p>$icon</p>"
        echo "        </div>"
    done
    echo "    </div>"
    echo "</body>"
    echo "</html>"
} > review.html

echo "Review the pruned assets in $(pwd)/review.html"

# Generate Mermaid diagrams
STEP=50
TOTAL=$(ls -1 *.png | wc -l)
PAGES=$((TOTAL / STEP + 1))

for page in $(seq 1 $PAGES); do
    echo "Generating Mermaid diagram page $page"
    mmf="all-assets-$page.mmd"
    {
        echo "graph TD"
        ls -1 *.png | head -n $((page * STEP)) | tail -n $STEP | while read -r icon; do
            node_name=$(echo "$icon" | sed 's/\.png//' | sed 's/[^a-zA-Z0-9]/_/g' | tr '[:upper:]' '[:lower:]')
            echo "    $node_name[<img src='$BASE_URL$icon' width='40' height='40' />]"
        done
    } > "$mmf"
    
    # Uncomment the following line if you have mmdc (Mermaid CLI) installed
    # mmdc -i "$mmf" -o "all-assets-$page.png"
done

echo "Script completed. Pruned assets are in $(pwd)"
echo "Review HTML: $(pwd)/review.html"
echo "Mermaid diagram files: $(pwd)/all-assets-*.mmd"
