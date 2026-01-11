# Dockerfile for offline inference
# Build: docker build -t ml-app:v1 .
# Run: docker run -v $(pwd)/data:/data ml-app:v1 --input_path /data/input --output_path /data/preds.csv

FROM python:3.10-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (CPU-only torch for smaller image)
RUN pip install --no-cache-dir --target=/app/deps \
    "numpy<2" \
    torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --target=/app/deps \
    torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --target=/app/deps \
    pandas>=2.0 \
    pillow>=10.0 \
    pyyaml>=6.0 \
    tqdm

# Remove unnecessary files to reduce size
RUN find /app/deps -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /app/deps -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
    find /app/deps -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /app/deps -name "*.pyc" -delete 2>/dev/null || true && \
    find /app/deps -name "*.pyo" -delete 2>/dev/null || true && \
    find /app/deps -name "*.so" -exec strip --strip-unneeded {} + 2>/dev/null || true && \
    rm -rf /app/deps/torch/include /app/deps/torch/share || true && \
    rm -rf /app/deps/caffe2 || true

# Final stage
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/deps:/app

WORKDIR /app

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy dependencies from builder
COPY --from=builder /app/deps /app/deps

# Copy source code
COPY src/ ./src/
COPY training/classification/src/ ./training/classification/src/

# Create directories
RUN mkdir -p ./training/models/tomato ./training/models/tomato_large /data/input /data/output

# Set entrypoint
ENTRYPOINT ["python", "-m", "src.predict"]

# Default arguments
CMD ["--help"]
