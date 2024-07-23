# Start from the base 'python' image, version 3
FROM python:3

# Work inside the at the path /opt/server
WORKDIR /opt/worker

# Copy our requirements.txt to inside our image, and run pip to install everything inside the image
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy our application sources over
COPY src/ .

# Mark this image as having a service on port 8080/tcp
# Note: This does not actually open the port, this is just a suggestion
EXPOSE 8080/tcp

# Tell the image how it should start our application 
CMD [ "python", "./simple_worker.py" ]