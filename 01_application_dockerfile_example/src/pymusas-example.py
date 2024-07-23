import spacy
import sys
from tqdm import tqdm

# Just a little print function that forces the terminal to write immediately
# so we can see what is going on in real-time.
def printf( data ):
    print( data )
    sys.stdout.flush()

if __name__ == "__main__":
    # We exclude the following components as we do not need them. 
    printf( "Loading the parser..." )
    nlp = spacy.load( 'en_core_web_sm', exclude=['parser', 'ner'] )

    # Load the English PyMUSAS rule-based tagger in a separate spaCy pipeline
    printf( "Loading the tagger..." )
    english_tagger_pipeline = spacy.load( 'en_dual_none_contextual' )

    # Adds the English PyMUSAS rule-based tagger to the main spaCy pipeline
    printf( "Configuring spacy..." )
    nlp.add_pipe( 'pymusas_rule_based_tagger', source=english_tagger_pipeline )

    printf( "Go!" )

    # Grab a line count just so we get a nice progress bar :)
    with open( '/input', 'r', encoding='utf8' ) as f:
        total_lines = sum(1 for line in f)

    with open( '/input', 'r', encoding='utf8' ) as input:
        with open( '/output/output.txt', 'w', encoding='utf8' ) as output:

            for line in tqdm( input, ncols=100, desc="Processing file: ", unit="line", file=sys.stdout, total=total_lines ):
                tokens = nlp( line )
                for token in tokens:
                    output.write( f'{token.text}\t{token.lemma_}\t{token.pos_}\t{token._.pymusas_tags}\n' )
                
                # Avoid flushing on every write, as keeping high-burst rates often mean faster overall throughput
                output.flush()
        
    printf( "Done! Bye :)" )