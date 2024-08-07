#!/bin/bash

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
    find . -type d -name "$S"
    find . -type d -name "*_$S"

    # Prune those directories
    find . -type d -name "$S" -exec rm -rf {} \;
    find . -type d -name "*_$S" -exec rm -rf {} \;

    # Find any matching files that still look like unsafe dimensions
    find . -type f -name "*_${S}x${S}.${SAFE_EXT}" -exec rm {} \;
  done
done

# Print the final size
FINAL_SIZE=$(du -mh . | tail -n 1 | awk '{print $1}')

echo "Baseline size: $BASELINE_SIZE"
echo "Final size: $FINAL_SIZE"
