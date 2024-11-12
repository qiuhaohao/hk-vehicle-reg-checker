#!/bin/bash

# Check if folder argument is provided
if [ $# -ne 1 ]; then
    echo "Error: Please provide a folder path" >&2
    echo "Usage: $0 <folder_path>" >&2
    exit 1
fi

# Check if folder exists
if [ ! -d "$1" ]; then
    echo "Error: Folder '$1' not found" >&2
    exit 1
fi

# Print CSV header
echo "plate,status,update_time"

# Process each HTML file in the specified directory
for file in "$1"/*.html; do
    # Skip if no HTML files found
    [ -e "$file" ] || continue
    
    # Extract plate number from filename
    plate=$(basename "$file" .html)
    
    # Get file modification time in ISO 8601 format
    update_time=$(date -r "$file" "+%Y-%m-%d %H:%M:%S")
    
    # Check content and determine status
    if grep -q "This registration mark is available" "$file"; then
        status="available"
    elif grep -q "This vehicle registration mark has been reserved by others" "$file"; then
        status="reserved"
    elif grep -q "This vehicle registration mark has been allocated" "$file"; then
        status="allocated"
    elif grep -q "There is another application for reservation of this vehicle registration mark being processed" "$file"; then
        status="processing"
    else
        status="other"
    fi
    
    # Output to stdout
    echo "$plate,$status,$update_time"
done