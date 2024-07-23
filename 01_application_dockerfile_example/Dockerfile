# Start from the base 'python' image, version 3
FROM python:3

# Work inside the at the path /usr/src/app
WORKDIR /opt/pymusas-worker

# Not using a requirements.txt this time, just to show you can do it this way too!
# Generally follows the guides for pymusas here: https://ucrel.github.io/pymusas/usage/how_to/tag_text
RUN pip install --no-cache-dir spacy pymusas tqdm
RUN pip install https://github.com/UCREL/pymusas-models/releases/download/en_dual_none_contextual-0.3.3/en_dual_none_contextual-0.3.3-py3-none-any.whl
RUN python -m spacy download en_core_web_sm

# Note that every 'RUN' directive here creates a new intermediate layer - consider how this could be condensed into a single RUN command :)

# Copy our application sources over
COPY src/ .

# Tell the image how it should start our application 
CMD [ "python", "./pymusas-example.py" ]