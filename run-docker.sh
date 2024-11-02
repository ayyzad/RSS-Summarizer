#!/bin/bash

# Build the Docker image
docker-compose build

# Run the container
docker-compose up -d

# Show the logs
docker-compose logs -f