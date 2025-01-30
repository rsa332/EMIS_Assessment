# Use official Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the necessary files
COPY . /app


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for database connection (override via `docker-compose.yml`)
ENV PYTHONPATH="/app"

# Run the pipeline
CMD ["python", "scripts/main.py"]
