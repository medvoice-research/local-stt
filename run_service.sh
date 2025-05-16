#!/bin/bash

# Whisper.cpp FastAPI Service startup script
# This script activates the virtual environment and starts the service

# Default configuration
PORT=8000
HOST="0.0.0.0"
RELOAD=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    --host)
      HOST="$2"
      shift 2
      ;;
    --reload)
      RELOAD=true
      shift
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check for models directory
if [ ! -d "models" ]; then
    echo "Creating models directory..."
    mkdir -p models
fi

# Check for temp uploads directory
if [ ! -d "temp_uploads" ]; then
    echo "Creating temp uploads directory..."
    mkdir -p temp_uploads
fi

# Start the service
echo "Starting Whisper.cpp FastAPI Service on $HOST:$PORT..."

if [ "$RELOAD" = true ]; then
    cd src && python main.py --port $PORT --host $HOST --reload
else
    cd src && python main.py --port $PORT --host $HOST
fi
