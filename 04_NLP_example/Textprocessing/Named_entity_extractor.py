import spacy
from spacy.tokens import Span
from spacy import displacy
from collections import OrderedDict
from lemminflect import getLemma, getInflection

import requests
import re
import aiohttp
import asyncio
BG_COLOR = {
    'PLANT': '#a9dfbf',  ### the added plant name
    'PLNAME':'#feca74',
	'GEONOUN': '#9cc9cc',
	'GPE':'#feca74',
	'CARDINAL':'#e4e7d2',
	'FAC':'#9cc9cc',
	'QUANTITY':'#e4e7d2',
	'PERSON':'#aa9cfc',
	'ORDINAL':'#e4e7d2',
	'ORG':'#7aecec',
	'NORP':'#d9fe74',
	'LOC':'#9ac9f5',
	'DATE':'#c7f5a9',
	'DISTANCE':'#edf5a9',
	'EVENT': '#e1a9f5',
	'TIME':'#a9f5bc',
	'WORK_OF_ART':'#e6c1d7',
	'LAW':'#e6e6c1',
	'LOCADV':'##f79188',
	'SP-PREP':'#f5b5cf',
	'PERCENT':'#c9ebf5',
	'MONEY':'#b3d6f2',
	'+EMOTION':'#94f72a',
	'-EMOTION':'#f75252',
	'TIME-SEM':'#d0e0f2', 
	'MOVEMENT':'#f2d0d0',
	'no_tag':'#FFFFFF'
}

# Example usage
""" text = "The Nile is a major north-flowing river in Northeastern Africa."
extractor = NamedEntityExtractor()
entities = extractor.process_text(text)
extractor.visualize_entities(text)
print(entities) """
## Result
'''[('The', 'O', None), ('Nile', 'O', None), ('is', 'O', None), ('a', 'O', None), ('major', 'O', None), ('north', 'O', None), ('-', 'O', None), ('flowing', 'O', None), ('river', 'B-GEONOUN', None), ('in', 'O', None),
 ('Northeastern', 'B-GPE', {'latitude': '46.2588615', 'longitude': '-83.6403313'}), ('Africa', 'I-GPE', {'latitude': '46.2588615', 'longitude': '-83.6403313'}),
   ('.', 'O', None)]'''

class NamedEntityExtractor:
    def __init__(self, nlp_model):
        self.nlp = nlp_model
        self.nlp.add_pipe("sentencizer")
        self.ruler = self.nlp.add_pipe("entity_ruler", before='ner')
        self.setup_entity_patterns()
        self.combine = lambda x, y: (x[0], x[1], x[2]+' '+y[2], x[3])
        self.geolocation_tags = ['GEO', 'PLNAME', 'GPE']  # Tags for which to perform geocoding
        self.geocode_cache = {}


    def setup_entity_patterns(self):
        # Get the list of placenames and geonouns
        place_names = [name.strip().title().replace("'S", "'s") for name in open('resources/LD_placenames.txt').readlines()] #read and convert to title case
        place_names += [name.upper() for name in place_names] #retain the upper case versions
        geonouns = self.get_inflections([noun.strip() for noun in open('resources/geo_feature_nouns.txt').readlines()])

        # Get the locative adverbs
        loc_advs = [l.split()[0] for l in open('resources/locative_adverbs.txt').readlines()]
        sp_prep  = [l.strip() for l in open('resources/spatial_prepositions.txt').readlines()
                                                                    if len(l.strip())>2]
        # Get distances
        distances = [l.strip() for l in open('resources/distances.txt').readlines()]

        # Get dates
        dates     = [l.strip() for l in open('resources/dates.txt').readlines()]

        # Get times
        times     = [l.strip() for l in open('resources/times.txt').readlines()]

        # Get events
        events    = [l.strip() for l in open('resources/events.txt').readlines()]

        # Get Plant- names this is new adding the plant names list to the NES
        pnames = [l.strip() for l in open('resources/Plant_list.txt').readlines()]

        # Get the list of positive and negative words from the sentiment lexicon
        pos_words = [w.strip() for w in open('resources/positive-words.txt','r', encoding='latin-1').readlines()[35:]]
        neg_words = [w.strip() for w in open('resources/negative-words.txt','r', encoding='latin-1').readlines()[35:]]

        


        # Define the patterns for the EntityRuler by labelling all the names with the tag PLNAME
        patterns = [{"label": "PLANT", "pattern": word} for word in pnames]
        patterns +=  [{"label": "PLNAME",  "pattern": plname} for plname in set(place_names)]
        patterns += [{"label": "GEONOUN", "pattern": noun} for noun in geonouns]
        patterns += [{"label": "+EMOTION", "pattern": word} for word in pos_words]
        patterns += [{"label": "-EMOTION", "pattern": word} for word in neg_words]
        patterns += [{"label": "EVENT",   "pattern": word} for word in events]
        patterns += [{"label": "DATE", "pattern": word} for word in dates]
        patterns += [{"label": "TIME", "pattern": word} for word in times]
        patterns += [{"label": "DISTANCE", "pattern": word} for word in distances]
        patterns += [{"label": "LOCADV", "pattern": word} for word in loc_advs]
        patterns += [{"label": "SP-PREP", "pattern": word} for word in sp_prep]


        self.ruler.add_patterns(patterns)


    
    # Get inflections and lemmas of geo nouns
    def get_inflections(self,names_list):
        gf_names_inflected = []
        for w in names_list:
            gf_names_inflected.append(w)
            gf_names_inflected.extend(list(getInflection(w.strip(), tag='NNS', inflect_oov=False)))
            gf_names_inflected.extend(list(getLemma(w.strip(), 'NOUN', lemmatize_oov=False)))
        return list(set(gf_names_inflected))
    
    # Generates a dictionary of entities with the indexes as keys
    def extract_entities(self,text, ent_list, tag='PLNAME'):
        sorted(set(ent_list), key=lambda x:len(x), reverse=True)
        extracted_entities = {}
        for ent in ent_list:
            for match in re.finditer(f' {ent}[\.,\s\n;:]', text):
            
                extracted_entities[match.start()+1]=text[match.start()+1:match.end()-1], tag
        return {i:extracted_entities[i] for i in sorted(extracted_entities.keys())}


    def combine_multi_tokens(self,a_list):
        new_list = [a_list.pop()]
        while a_list:
            last = a_list.pop()
            if new_list[-1][0] - last[0] == 1:
                new_list.append(self.combine(last, new_list.pop()))
            else:
                new_list.append(last)
        return sorted(new_list)

     # Generates a dictionary of semantic entities combining adjacent ones
    def extract_sem_entities(self,processed_text, tag_types):
        entities, tokens = {}, [token.text for token in processed_text]
        for tag_type in tag_types:
            tag_indices = [(i, token.idx, token.text, tag_type) for i, token in enumerate(processed_text) 
                                if token._.pymusas_tags[0].startswith(tag_type[0])]
            if tag_indices:
                for i, idx, token, tag in self.combine_multi_tokens(tag_indices):
                    entities[idx] = token, tag
        return OrderedDict(sorted(entities.items()))



    # Generates a list of all tokens, tagged and untagged, for visualisation
    def get_tagged_list(text, entities):
        begin, tokens_tags = 0, []
        for start, (ent, tag) in entities.items():
            if begin <= start:
                tokens_tags.append((text[begin:start], None))
                tokens_tags.append((text[start:start+len(ent)], tag))
                begin = start+len(ent)
        tokens_tags.append((text[begin:], None)) #add the last untagged chunk
        return tokens_tags

    def merge_entities(self, doc):
        merged_entities = []
        temp_entity = {"text": "", "start": None, "end": None, "label": None}

        for ent in doc.ents:
            if temp_entity["label"] == ent.label_ and (temp_entity["end"] == ent.start_char or temp_entity["end"] + 1 == ent.start_char):
                temp_entity["text"] += " " + ent.text
                temp_entity["end"] = ent.end_char
            else:
                if temp_entity["text"]:
                    merged_entities.append(temp_entity.copy())
                temp_entity = {"text": ent.text, "start": ent.start_char, "end": ent.end_char, "label": ent.label_}

        if temp_entity["text"]:
            merged_entities.append(temp_entity.copy())

        return merged_entities



    async def geocode(self, place_name):
        if place_name in self.geocode_cache:
            return self.geocode_cache[place_name]

        base_url = "https://nominatim.openstreetmap.org/search"
        params = {'q': place_name, 'format': 'json'}
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        result = {'latitude': data[0].get('lat'), 'longitude': data[0].get('lon')}
                        self.geocode_cache[place_name] = result
                        return result
        return {'latitude': None, 'longitude': None}

    async def convert_to_iob_format(self, merged_entities, doc):
        iob_entities = []
        for sent in doc.sents:
            sent_entities = [e for e in merged_entities if e["start"] >= sent.start_char and e["end"] <= sent.end_char]
            for token in sent:
                merged_entity = next((e for e in sent_entities if e["start"] <= token.idx < e["end"]), None)
                if merged_entity:
                    tag_prefix = 'B-' if token.idx == merged_entity["start"] else 'I-'
                    base_label = merged_entity["label"].split('-')[-1]
                    print('base_label:',base_label )  
                    if base_label in ["PLNAME", "GEONOUN",  "GPE"]:
                        geolocation = await self.geocode(merged_entity["text"])
                        
                    else:
                        geolocation = None
                    iob_entities.append((token.text, tag_prefix + merged_entity["label"], geolocation))
                else:
                    iob_entities.append((token.text, 'O', None))
        return iob_entities

    async def process_text(self, text):
        doc = self.nlp(text)
        merged_entities = self.merge_entities(doc)
        return await self.convert_to_iob_format(merged_entities, doc)

    def visualize_entities(self, text):
        doc = self.nlp(text)
        options = {"ents": list(BG_COLOR.keys()), "colors": BG_COLOR}
        displacy.render(doc, style="ent", options=options)



