# Flask AI Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and TensorFlow
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt* ./

# Install Python dependencies
RUN pip install --no-cache-dir \
    flask \
    tensorflow \
    opencv-python-headless \
    numpy \
    Pillow

# Copy application code
COPY app.py .
COPY db.py .
COPY *.h5 ./ 2>/dev/null || true

# Create face_data directory
RUN mkdir -p face_data

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run the application
CMD ["python", "app.py"]
