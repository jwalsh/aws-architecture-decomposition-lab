#!/bin/bash
#
# Filename: aws-architecture-diagrams-assets.sh
# URL: https://aws.amazon.com/architecture/icons/
# Description:
#   This script downloads the AWS Architecture Icons asset package, extracts it, and prepares the icons for use in Mermaid diagrams.
#   It removes unnecessary directories and files, ensuring only the required icons are kept.

# Check if required commands are installed
if ! command -v wget &> /dev/null; then
  echo "Error: wget is not installed. Please install it before running this script."
  exit 1
fi

if ! command -v unzip &> /dev/null; then
  echo "Error: unzip is not installed. Please install it before running this script."
  exit 1
fi

# AWS Architecture Diagrams > Assets for Mermaid diagrams

# Get the assets https://aws.amazon.com/architecture/icons/
# Show base size of the archive

ASSET_BASE="Asset-Package_06072024.b5d9f0b1179c4a995a3f1e42042defabb0ba0fd2"

if [ ! -f "${ASSET_BASE}.zip" ]; then
  wget "https://d1.awsstatic.com/webteam/architecture-icons/${ASSET_BASE}.zip"
fi

if [ ! -d "${ASSET_BASE}" ]; then
  unzip "${ASSET_BASE}.zip"
fi

cd "${ASSET_BASE}"

# Get the baseline size
BASELINE_SIZE=$(du -mh . | tail -n 1 | awk '{print $1}')

for B in */; do
  SAFE_EXT="png"
  SAFE_SIZE="48"

  # Safety for the group can be different
  if [ "$B" == "Architecture-Group-Icons_06072024/" ]; then
    SAFE_SIZE="32"
  fi

  # First clean all directories that are not safe and clearly are thumbnailed to that size
  for S in 16 32 64; do
    if [ "$SAFE_SIZE" -eq "$S" ]; then
      echo "$S is safe for $B"
      continue
    fi

    # Audit the directories
    echo "Directories to be pruned for $B with size $S:"
    find . -type d -name "$S"
    find . -type d -name "*_$S"

    # Get user input to confirm prune
    read -p "Prune these directories? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
      # Prune those directories
      find . -type d -name "$S" -exec rm -rf {} \;
      find . -type d -name "*_$S" -exec rm -rf {} \;

      # Find any matching files that still look like unsafe dimensions
      find . -type f -name "*_${S}x${S}.${SAFE_EXT}" -exec rm {} \;
    else
      echo "Skipping prune for $B with size $S"
    fi
  done
done

# Print the final size
FINAL_SIZE=$(du -mh . | tail -n 1 | awk '{print $1}')

echo "Baseline size: $BASELINE_SIZE"
echo "Final size: $FINAL_SIZE"
