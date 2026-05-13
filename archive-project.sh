#!/bin/bash
# Shell script to archive project with timestamped folder
# Usage: ./archive-project.sh [project_path] [archive_path]
# Output: Creates timestamped folder in archive/ with complete project snapshot
# Note: Add "archive/" to .gitignore to keep archives local and avoid repo bloat

# Set default parameters
PROJECT_PATH="${1:-.}"
ARCHIVE_PATH="${2:-./archive}"

# Generate timestamp in format YYYY-MM-DD_HHmmss
TIMESTAMP=$(date +"%Y-%m-%d_%H%M%S")
ARCHIVE_FOLDER="$ARCHIVE_PATH/$TIMESTAMP"

# Create archive directory if it doesn't exist
if [ ! -d "$ARCHIVE_PATH" ]; then
    mkdir -p "$ARCHIVE_PATH"
fi

# Create timestamped archive directory
if [ ! -d "$ARCHIVE_FOLDER" ]; then
    mkdir -p "$ARCHIVE_FOLDER"
    echo "Created archive directory: $ARCHIVE_FOLDER"
else
    echo "Archive directory already exists: $ARCHIVE_FOLDER"
    exit 1
fi

# Define exclude patterns
EXCLUDE_PATTERNS=(".git" "archive" ".venv" "__pycache__" "*.pyc" ".DS_Store" "node_modules" "target" "build" "dist")

# Function to check if item should be excluded
should_exclude() {
    local item="$1"
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        case "$item" in
            $pattern) return 0 ;;
        esac
    done
    return 1
}

# Copy entire project to archive (excluding specified patterns)
cd "$PROJECT_PATH" || exit 1

total_items=0
for item in * .*; do
    # Skip . and .. directories
    if [ "$item" = "." ] || [ "$item" = ".." ]; then
        continue
    fi
    
    # Skip if item doesn't exist (handles case where no dotfiles exist)
    if [ ! -e "$item" ]; then
        continue
    fi
    
    # Check if item should be excluded
    if should_exclude "$item"; then
        continue
    fi
    
    # Copy item to archive folder
    if [ -d "$item" ]; then
        cp -r "$item" "$ARCHIVE_FOLDER/"
    else
        cp "$item" "$ARCHIVE_FOLDER/"
    fi
    ((total_items++))
done

echo "Archive created successfully at: $ARCHIVE_FOLDER"
echo "$total_items items archived"
