# Use Python base image for amd64
FROM --platform=linux/amd64 python:3.10-slim

LABEL authors="dines"

# System dependencies
RUN apt-get update && \
    apt-get install -y build-essential poppler-utils libglib2.0-0 libsm6 libxrender1 libxext6 git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variable for HuggingFace cache (optional)
ENV TRANSFORMERS_CACHE=/app/cache
ENV HF_HOME=/app/cache
ENV SENTENCE_TRANSFORMERS_HOME=/app/cache

# Create app directories
WORKDIR /app

# Copy and install requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 🔽 Pre-download the model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')"

# Copy your app code
COPY . /app

# Run the app
CMD ["python", "main.py"]
