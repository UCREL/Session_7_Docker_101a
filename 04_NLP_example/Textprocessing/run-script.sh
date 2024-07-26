#!/bin/bash

# Directory containing  files
input_directory="/Users/katiana/Documents/Historicalcorpus/TextProcessing/0118"
main_directory="/Users/katiana/Documents/Historicalcorpus/TextProcessing"
# Output directory
output_directory="/Users/katiana/Documents/Historicalcorpus/TextProcessing/output"

# Get the number of CPU cores
CORES=$(sysctl -n hw.ncpu)
echo "Number of CPU cores: $CORES"

# Function to process a single file with Docker
process_file() {
    local filename=$(basename "$1")
    echo "Processing $filename"

    # Run Docker container for the file
    docker run -d \
        -v "${input_directory}:${input_directory}" \
        -v "${output_directory}:${output_directory}" \
        -e INPUT_DIRECTORY="${input_directory}" \
        -e OUTPUT_DIRECTORY="${output_directory}" \
        -e FILE_NAME="$filename" \
        textprocessor
}

# Export process_file function to be used by xargs
export -f process_file

# Use xargs to run the process in parallel
ls $input_directory/*.json | xargs -P $CORES -I {} bash -c 'process_file "$@"' _ {}