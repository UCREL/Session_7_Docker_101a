
#!/bin/bash
input_directory="[PATH TO FOLDER]/0118"

# Get the number of CPU cores on Mac
##CORES=$(sysctl -n hw.ncpu)
##echo "Number of CPU cores: $CORES"

## Get the number of CPU cores on Linux
CORES=$(nproc)
echo "Number of CPU cores: $CORES"



# Use xargs to run the process in parallel and print filename
find "$input_directory" -name '*.json' | xargs -P "$CORES" -I {} bash -c './jobfile.sh "$1"' _ {}
