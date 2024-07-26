import os
import json
from pathlib import Path
import spacy
from Named_entity_extractor import NamedEntityExtractor
import aiohttp
import asyncio
# Global spaCy model
NLP_MODEL = spacy.load('en_core_web_sm', exclude=['parser'])
english_tagger_pipeline = spacy.load('en_dual_none_contextual')
NLP_MODEL.add_pipe('pymusas_rule_based_tagger', source=english_tagger_pipeline)

'''it needs the cleaned version from the OCR tags'''
class TextProcessor:
    def __init__(self, input_path, NLP_MODEL):
        self.input_path = Path(input_path)
        self.output_path = Path(output_folder_path)
        
        self.nlp = NLP_MODEL
        self.nee = NamedEntityExtractor(NLP_MODEL)


    async def process_file(self, file_name):
        file_path = self.input_path / file_name
        print(f'Processing file {file_path}')
        
        data = self.load_json_data(file_path)
        if data is not None:
            corrected_data = await self.process_data(data)
            self.save_processed_data(file_path, corrected_data)
        else:
            print(f"Failed to load data from {file_path}")
            

    @staticmethod
    def load_json_data(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except IOError:
            print(f"Error: File {file_path} does not appear to exist.")
            return None

    async def process_data(self, data):
        """
            Processes textual data from a list of pages. Each page is tokenized into words using a NLP pipeline, 
            and for each word, linguistic features are extracted.

            Parameters:
            - data (list of tuples): Each tuple contains a page number and its corresponding text.
                - page_number (int): The number of the page. This is used for tracking and referencing the source of each tokenized word.
                - text (str): The textual content of the page. This text is processed and tokenized into individual words or tokens.
                - start_char and end_char to be used later in KWIC and collocations

            Returns:
            - list of dicts: Each dictionary contains information about a token, including its text, lemma,
            POS tag, semantic tag, page number, and character positions.
        """


        processed_data = []
        for page in data:
            page_number, text = page
            doc = self.nlp(text)
            ne_data = await self.nee.process_text(text)  # Process text for named entities
                        # Extract latitude and longitude if they exist
           
            for token in doc:
                # Find the named entity in ne_data that corresponds to the token
                ne_info = next((ne for ne in ne_data if ne[0] == token.text), None)
                latitude = None
                longitude = None
                if ne_info and len(ne_info) > 2 and isinstance(ne_info[2], dict):
                    latitude_str = ne_info[2].get('latitude')
                    longitude_str = ne_info[2].get('longitude')

                    if latitude_str is not None and longitude_str is not None:
                        try:
                            latitude = float(latitude_str)
                            longitude = float(longitude_str)
                        except ValueError:
                            # Handle the case where latitude or longitude is not a valid number
                            print(f"Invalid latitude or longitude value for {token.text}: latitude={latitude_str}, longitude={longitude_str}")

                token_data = {
                    'text': token.text,
                    'lemma': token.lemma_,
                    'POS': token.pos_,
                    'USAS_tags': token._.pymusas_tags,
                    'page_id': page_number,
                    'start_char': token.idx,  # Character start position
                    'end_char': token.idx + len(token),  # Character end position
                    'NE': ne_info,  # Add named entity information
                    'latitude': latitude,  # Add latitude
                    'longitude': longitude  # Add longitude
                }
                processed_data.append(token_data)
        return processed_data

    def save_processed_data(self, original_file_path, data):
        current_page_id = None
        page_data = []

        for item in data:
            if current_page_id is None:
                current_page_id = item['page_id']
            
            if item['page_id'] != current_page_id:
                # Save the data accumulated so far for the previous page
                self.write_to_file(original_file_path, page_data, current_page_id)
                page_data = []  # Reset page_data for the new page
                current_page_id = item['page_id']
            
            page_data.append(item)

        # Don't forget to save the last page's data
        if page_data:
            self.write_to_file(original_file_path, page_data, current_page_id)

    def write_to_file(self, original_file_path, page_data, page_id):
        output_file = self.output_path / f"{original_file_path.stem}_page_{page_id}.json"
        with open(output_file, 'w') as file:
            json.dump(page_data, file, indent=4)
        print(f'Saved file {output_file}')




# Use environment variables for input and output folder paths
input_folder_path = os.getenv('INPUT_FOLDER_PATH', '[PATH TO FOLDER]/Textprocessing/0118')
output_folder_path = os.getenv('OUTPUT_FOLDER_PATH', '[PATH TO FOLDER]/Textprocessing/output')

# Get the filename from environment variable
file_name = os.getenv('FILE_NAME')


async def main():
    processor = TextProcessor(input_folder_path, NLP_MODEL)
    await processor.process_file(file_name)

# Run the async main function
asyncio.run(main())

