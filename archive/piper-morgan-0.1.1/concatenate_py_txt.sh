#!/bin/bash

OUTPUT_FILE="concatenated_code_and_text.txt"
SOURCE_DIR="." # Or replace with your directory, e.g., "/path/to/your/files"

# Clear the output file if it exists, or create a new one
> "$OUTPUT_FILE"

echo "Concatenating .py and .txt files from '$SOURCE_DIR' into '$OUTPUT_FILE'..."
echo "--- Start of Concatenated Files ---" >> "$OUTPUT_FILE"

# Use find to get files and explicitly exclude the output file
find "$SOURCE_DIR" -maxdepth 1 -type f \( -name "*.py" -o -name "*.txt" \) -not -name "$(basename "$OUTPUT_FILE")" | while read -r file; do
    FILENAME=$(basename "$file")
    echo -e "\n### Start of file: $FILENAME ###\n" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    echo -e "\n### End of file: $FILENAME ###\n" >> "$OUTPUT_FILE"
done

echo "--- End of Concatenated Files ---" >> "$OUTPUT_FILE"
echo "Concatenation complete!"