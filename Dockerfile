# Use Ubuntu as the base image
FROM ubuntu:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the binary 'shortlang' to /usr/bin
COPY shortlang /usr/bin/
