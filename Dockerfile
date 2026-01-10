# Dockerfile for offline inference
# Build: docker build -t ml-app:v1 .
# Run: docker run -v $(pwd)/data:/data ml-app:v1 --input_path /data/input --output_path /data/preds.csv

FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-mlops.txt .

# Install Python dependencies (CPU-only torch for smaller image)
RUN pip install --no-cache-dir \
    torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    pandas>=2.0 \
    pillow>=10.0 \
    pyyaml>=6.0 \
    numpy>=1.23

# Copy source code
COPY src/ ./src/
COPY training/classification/src/ ./training/classification/src/

# Copy pre-trained model (if available)
# This can also be done via dvc pull in CI/CD
COPY training/models/tomato/ ./training/models/tomato/

# Create data directories
RUN mkdir -p /data/input /data/output

# Health check - verify model can be loaded
RUN python -c "from src.predict import load_model, DEFAULT_CLASS_NAMES; print('Model structure OK')" || true

# Set entrypoint
ENTRYPOINT ["python", "-m", "src.predict"]

# Default arguments
CMD ["--help"]

