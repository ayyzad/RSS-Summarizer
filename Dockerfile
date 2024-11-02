# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set timezone environment variable
ENV TZ=America/New_York

# Install system dependencies and set timezone
RUN apt-get update && apt-get install -y \
    build-essential \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p articles/processed articles/summaries logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application in scheduled mode
CMD ["python", "main.py"]