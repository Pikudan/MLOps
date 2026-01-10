#!/bin/bash
# Build MAR (Model Archive) file for TorchServe
# Usage: ./torchserve/build_mar.sh

set -e

MODEL_NAME="tomato-disease"
VERSION="1.0"
MODEL_DIR="training/models/tomato"
EXPORT_DIR="torchserve"
MODEL_STORE="torchserve/model-store"

echo "=== Building TorchServe Model Archive ==="

# Step 1: Export model to TorchScript
echo "Step 1: Exporting model to TorchScript..."
python torchserve/export_model.py \
    --model-dir ${MODEL_DIR} \
    --output ${EXPORT_DIR}/model.pt

# Step 2: Create MAR file
echo "Step 2: Creating MAR archive..."
mkdir -p ${MODEL_STORE}

torch-model-archiver \
    --model-name ${MODEL_NAME} \
    --version ${VERSION} \
    --serialized-file ${EXPORT_DIR}/model.pt \
    --handler ${EXPORT_DIR}/handler.py \
    --export-path ${MODEL_STORE} \
    --force

echo "=== MAR file created: ${MODEL_STORE}/${MODEL_NAME}.mar ==="
echo ""
echo "To start TorchServe locally:"
echo "  torchserve --start --model-store ${MODEL_STORE} --models ${MODEL_NAME}=${MODEL_NAME}.mar"
echo ""
echo "To build and run Docker container:"
echo "  docker build -t mymodel-serve:v1 -f torchserve/Dockerfile ."
echo "  docker run -d -p 8080:8080 -p 8081:8081 mymodel-serve:v1"
echo ""
echo "To test the service:"
echo "  curl -X POST http://localhost:8080/predictions/${MODEL_NAME} -T sample_image.jpg"

