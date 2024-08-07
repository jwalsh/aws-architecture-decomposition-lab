#!/bin/bash
#
# Filename: aws-architecture-diagrams-assets.sh
# URL: https://aws.amazon.com/architecture/icons/
# Description:
#   This script processes AWS Architecture Icons and generates Mermaid diagrams
#   and an HTML review page for the icons.

set -euo pipefail

WORK_DIR="aws-icons-workdir-$$"
OUTPUT_DIR="pruned-assets"
BASE_URL="https://wal.sh/static/images/aws-architecture-diagrams-assets/"

# Create output directory
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

# Generate review HTML
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
ICONS_PER_DIAGRAM=10
TOTAL=$(ls -1 *.png | wc -l)
PAGES=$(( (TOTAL + ICONS_PER_DIAGRAM - 1) / ICONS_PER_DIAGRAM ))

for page in $(seq 1 $PAGES); do
    echo "Generating Mermaid diagram page $page"
    mmf="all-assets-$page.mmd"
    {
        echo "graph TD"
        ls -1 *.png | sed -n "$((($page-1)*ICONS_PER_DIAGRAM+1)),$((page*ICONS_PER_DIAGRAM))p" | while read -r icon; do
            node_name=$(echo "$icon" | sed 's/\.png//' | sed 's/[^a-zA-Z0-9]/_/g' | tr '[:upper:]' '[:lower:]')
            echo "    $node_name[<img src='$BASE_URL$icon' width='40' height='40' />]"
        done
    } > "$mmf"
    
    # Uncomment the following line if you have mmdc (Mermaid CLI) installed
    mmdc -i "$mmf" -o "all-assets-$page.png"
done

echo "Script completed. Pruned assets are in $(pwd)"
echo "Review HTML: $(pwd)/review.html"
echo "Mermaid diagram files: $(pwd)/all-assets-*.mmd"
