# Use Ubuntu as the base image
FROM ubuntu:20.04

# Metadata as described above
LABEL maintainer="hli197@my.bcit.ca" 

# Update and install Python, pip
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip

# Copy only requirements.txt first to cache it
COPY ./requirements.txt /app/requirements.txt

# Set the working directory in the container
WORKDIR /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . /app

# Specify the command to run on container start
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
