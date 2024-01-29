# Use Apline as the base image
FROM alpine:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the binary 'shortlang' to /usr/bin
COPY shortlang /usr/bin/

# Give execute permissions to the shortlang binary
RUN chmod +x /usr/bin/shortlang
