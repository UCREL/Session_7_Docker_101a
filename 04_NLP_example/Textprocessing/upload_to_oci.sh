#!/bin/bash
### ./upload_to_oci.sh
# Define the bucket name
BUCKET_NAME="demo-bucket"
# Define the target folder in the bucket
TARGET_FOLDER="lang-lat"
# The directory containing the files to upload
DIRECTORY="/Users/katiana/Documents/Historicalcorpus/Textprocessing/output"

# Loop over each file in the directory

for FILE in "$DIRECTORY"/*
do
    if [ -f "$FILE" ]; then  # Check if it's a regular file
         # Extract filename from path
        FILE_NAME=$(basename "$FILE")
         # Construct the object name with the folder path
        OBJECT_NAME="$TARGET_FOLDER/$FILE_NAME"

        echo "Uploading $FILE_NAME..."
        # Upload file to the specified folder in the OCI bucket
        oci os object put --bucket-name $BUCKET_NAME --file "$FILE" --name "$OBJECT_NAME"
    else
        echo "Skipping non-file: $FILE"
    fi
done

echo "Upload complete."