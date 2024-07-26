#!/bin/bash

# This script expects a filename as an argument
file="$1"

input_directory="[PATH TO FOLDER]/Textprocessing"
output_directory="[PATH TO FOLDER]/Textprocessing/output"

filename=$(basename "$file")
echo "Processing $filename"

# Run Docker container for the file
docker run \
    -v "${input_directory}:${input_directory}" \
    -v "${output_directory}:${output_directory}" \
    -e INPUT_DIRECTORY="${input_directory}" \
    -e OUTPUT_DIRECTORY="${output_directory}" \
    -e FILE_NAME="$filename" \
    textprocessor
