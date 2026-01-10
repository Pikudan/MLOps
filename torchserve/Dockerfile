# TorchServe Dockerfile for tomato disease classification
# Build: docker build -t mymodel-serve:v1 -f torchserve/Dockerfile .
# Run: docker run -d -p 8080:8080 -p 8081:8081 mymodel-serve:v1

FROM pytorch/torchserve:latest

# Set environment variables
ENV MODEL_NAME=tomato-disease
ENV MODEL_STORE=/home/model-server/model-store

# Switch to root for installation
USER root

# Install additional dependencies
RUN pip install --no-cache-dir pillow torchvision

# Create model store directory
RUN mkdir -p ${MODEL_STORE}

# Copy handler
COPY torchserve/handler.py /home/model-server/handler.py

# Copy config
COPY torchserve/config.properties /home/model-server/config.properties

# Copy pre-built MAR file if exists
# (alternatively, build MAR during container startup)
COPY torchserve/model-store/*.mar ${MODEL_STORE}/ 2>/dev/null || true

# Switch back to model-server user
USER model-server

# Expose ports
# 8080: Inference API
# 8081: Management API  
# 8082: Metrics API
EXPOSE 8080 8081 8082

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/ping || exit 1

# Start TorchServe
CMD ["torchserve", \
     "--start", \
     "--model-store", "/home/model-server/model-store", \
     "--ts-config", "/home/model-server/config.properties", \
     "--foreground"]

