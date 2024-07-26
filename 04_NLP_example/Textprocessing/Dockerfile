#### docker build -t textprocessor .
#### docker ps -a
#### docker stats
#### docker logs -f
#### htop
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy English model
RUN python -m spacy download en_core_web_sm

# Install the pymusas model from the provided URL
RUN pip install https://github.com/UCREL/pymusas-models/releases/download/en_dual_none_contextual-0.3.2/en_dual_none_contextual-0.3.2-py3-none-any.whl

ENV INPUT_FOLDER_PATH=[PATH TO FOLDER]/Textprocessing/0118
ENV OUTPUT_FOLDER_PATH=[PATH TO FOLDER]/Textprocessing/output
# Run TextProcessor when the container launches, replace with your script name
CMD ["python", "./TextProcessor.py"]
