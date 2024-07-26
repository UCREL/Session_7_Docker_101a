# IAA-Oracle-ULTEC Project

## Project Summary

**Objective**: Leverage historical texts to enhance modern landscape management. total of 14,306 Books

**Methods**:
- Utilize NLP and Machine Learning to analyze the British Library's 19th-century corpus using Oracle Cloud.
- Extract and map historical records of plant species using Oracle Apex.

**Goals**:
- Develop a comprehensive database of species names and locations.
- Improve precision and recall in data extraction.
- Create detailed maps of historical species distributions for ecological analysis.

**Outcome**:
- Inform landscape management with historical data.
- Enable ecological comparison of past and present vegetation.


# IAA Oracle ULTEC Text Processing

This repository, part of the UCREL IAA Oracle ULTEC project, focuses on advanced text processing techniques and tools designed for linguistic analysis.
## Getting Started

### Prerequisites

- **Docker**: Ensure Docker is installed on your system to utilize the repository within a Docker container. Visit [Docker's official site](https://www.docker.com/get-started) for installation instructions.

### Using the Repository with Docker

1. **Clone the Repository**: First, clone the repository to your local machine.

   ```bash
   git clone https://github.com/UCREL/IAA-Oracle-ULTEC.git
   cd IAA-Oracle-ULTEC/Textprocessing
   ```

2. **Build the Docker Image**: Create a Dockerfile in the root of the `Textprocessing` directory if not already present. Then, build a Docker image based on the Dockerfile.  
      ## [`Dockerfile`](https://github.com/UCREL/IAA-Oracle-ULTEC/blob/main/Textprocessing/Dockerfile)

      **Base Image**: `python:3.8-slim`

      **Key Operations**:
      - Sets the working directory.
      - Copies current directory contents.
      - Installs required Python packages and spaCy English model.
      - Installs `pymusas` model.
      - Defines environment variables for input and output directories.
      - Specifies the command to run `TextProcessor.py` on container launch.


      ## [`jobfile.sh`](https://github.com/UCREL/IAA-Oracle-ULTEC/blob/main/Textprocessing/jobfile.sh)

      **Purpose**: Processes individual JSON files by running a Docker container for each file.

      **Operation**:
      - Receives a filename as an argument.
      - Defines input and output directories.
      - Uses `docker run` to execute the processing in a container, mapping local directories to container directories and setting relevant environment variables.

      ## [`dispatch.sh`](https://github.com/UCREL/IAA-Oracle-ULTEC/blob/main/Textprocessing/dispatch.sh)

      **Purpose**: Automates the parallel processing of JSON files in a specified directory, utilizing all available CPU cores.

      **Operation**:
      - Calculates the number of CPU cores.
         ```bash
          CORES=$(nproc)
          echo "Number of CPU cores: $CORES"
         ```
      - Uses `find` and `xargs` to process `.json` files in parallel with `jobfile.sh`.
        ```bash
         # Use xargs to run the process in parallel and print filename
         find "$input_directory" -name '*.json' | xargs -P "$CORES" -I {} bash -c './jobfile.sh "$1"' _ {}
        ```
---

This setup provides a scalable and efficient framework for processing large datasets, leveraging Docker for consistent runtime environments and parallel execution to utilize system resources effectively.


4. **Build Docker image**:

   ```bash
   docker build -t textprocessing .
   ```

5. **Run the Docker Container**: Start a container

   ```bash
   ./dispatch.sh
   ```

# [TextProcessor](https://github.com/UCREL/IAA-Oracle-ULTEC/blob/main/Textprocessing/TextProcessor.py)

## Overview

The `TextProcessor` class is designed for processing textual data extracted from documents. It leverages a Natural Language Processing (NLP) model to tokenize text, extract linguistic features, and identify named entities with geographical coordinates (latitude and longitude). This class is intended for use with cleaned text data, ideally after OCR (Optical Character Recognition) processing.

## Features

- **Initialization Parameters:**
  - `input_path`: The file path to the directory containing text files to be processed.
  - `NLP_MODEL`: A pre-loaded spaCy NLP model used for text tokenization and feature extraction.

- **Main Methods:**
  - `process_file`: Asynchronously processes a single file from the input directory, extracting text features and named entity information.
  - `load_json_data`: Loads text data from a JSON file, expecting a specific format.
  - `process_data`: Processes the textual data using the NLP model, extracting various linguistic features such as lemmas, POS tags, and named entities with their corresponding USAS tags and geographical coordinates (if available).
  - `save_processed_data`: Saves the processed data into a new JSON file, organizing the data by page numbers.
  - `write_to_file`: Writes processed page data to a file in JSON format, naming the files according to the original file and page number.

- **NLP and Named Entity Extraction:**
  The class uses a global spaCy NLP model (`NLP_MODEL`) with a custom pipeline for rule-based tagging (`pymusas_rule_based_tagger`). This setup enables the extraction of standard linguistic features and the identification of semantic tags specific to the USAS (UCREL Semantic Analysis System) framework. Additionally, the `NamedEntityExtractor` component is utilized for extracting named entities, particularly focusing on entities with geographical information.

- **Asynchronous Processing:**
  The class is designed to handle file processing asynchronously, making it efficient for processing multiple files or large datasets.

## Usage Example

To use the `TextProcessor` class, instantiate it with the path to your input directory and the pre-loaded NLP model. Then, call the `process_file` method with the filename you wish to process. The class is designed to be used in an asynchronous context, leveraging Python's `asyncio` library for efficient processing.

```python
import asyncio
async def main():
    processor = TextProcessor('path/to/input/directory', NLP_MODEL)
    await processor.process_file(file_name)

asyncio.run(main())
```

# [NamedEntityExtractor](https://github.com/UCREL/IAA-Oracle-ULTEC/blob/main/Textprocessing/Named_entity_extractor.py)

## Overview

The `NamedEntityExtractor` class is designed to enrich text with semantic information by identifying and tagging entities such as place names, geonouns, emotions, events, dates, and more. It uses a combination of spaCy's NLP capabilities and custom pattern matching to locate and label entities within text. The code is adapted and modified from an existing demo at https://github.com/SpaceTimeNarratives/demo. Additionally, this class can geocode certain entities to provide latitude and longitude information.

## Features

- **Entity Recognition and Tagging:**
  - Utilizes spaCy's NLP model and entity ruler for tagging predefined entities in text.
  - Supports a wide range of entities including geographical names, emotional words, events, dates, distances, and more.

- **Geocoding:**
  - Capable of geocoding entities tagged as geographical locations, using the Nominatim API via asynchronous HTTP requests.
  - Caches geocode results to optimize performance and reduce duplicate requests.

- **Custom Entity Patterns:**
  - Implements custom entity patterns using lists of place names, geonouns, locative adverbs, spatial prepositions, and other lexical resources.
  - Extensible pattern setup allowing for easy addition of new entity types.

- **Visualization:**
  - Provides a method for visualizing tagged entities in text using spaCy's `displacy` with custom color coding for different entity types.

## Initialization Parameters

- `nlp_model`: A pre-loaded spaCy NLP model object. This model is augmented with a sentencizer and an entity ruler for entity recognition.

## Main Methods

- `setup_entity_patterns()`: Initializes the entity ruler with patterns for various entity types based on external lexical resources.
- `process_text(text: str)`: Asynchronously processes the input text, tagging entities and optionally geocoding geographical locations. Returns a list of entities with their tags and, for certain entities, geographical coordinates.
- `visualize_entities(text: str)`: Visualizes entities in the input text with different colors for each entity type, using spaCy's `displacy` tool.

## Usage Example

```python
import spacy
from NamedEntityExtractor import NamedEntityExtractor

# Load a spaCy model
nlp = spacy.load('en_core_web_sm')

# Initialize the NamedEntityExtractor with the spaCy model
extractor = NamedEntityExtractor(nlp)

# Process text to identify and tag entities
text = "The Nile is a major north-flowing river in Northeastern Africa."
entities = await extractor.process_text(text)

# Visualize the entities in the text
extractor.visualize_entities(text)
 ```

# Plant names
https://github.com/IsabelMeraner/BotanicalNER/tree/master

# DB structure
![Data base Structure](images/British_books_DB.jpg)


### Contacts
- [Nouran Khallaf](https://github.com/Nouran-Khallaf)
- [Paul Rayson](https://github.com/perayson)
