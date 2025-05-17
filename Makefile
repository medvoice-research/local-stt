# Whisper.cpp FastAPI Service Makefile
#
# This Makefile provides convenient commands for working with the whisper.cpp FastAPI service

.PHONY: help install start stop clean models download-model docker docker-build docker-up docker-down test venv link-whisper

# Default Python interpreter
PYTHON ?= python3

# Default port for the service
PORT ?= 8000

# Default to base.en model
MODEL ?= base.en

# Enable reload by default for dev mode
RELOAD ?= true

# Default container name to match compose service
CONTAINER ?= whisper-api

# Help command
help:
	@echo "Whisper.cpp FastAPI Service Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make help                 - Show this help message"
	@echo "  make install              - Install Python dependencies"
	@echo "  make start                - Start the FastAPI service"
	@echo "  make stop                 - Stop the running service"
	@echo "  make clean                - Clean temporary files"
	@echo "  make models               - List available models"
	@echo "  make download-model       - Download a model (MODEL=model_name)"
	@echo "  make docker-build         - Build the Docker image"
	@echo "  make docker-up            - Start the Docker container"
	@echo "  make docker-down          - Stop the Docker container"
	@echo "  make test                 - Run tests"
	@echo "  make build-whisper        - Build whisper.cpp from source"
	@echo "  make link-whisper         - Create symlink to whisper-cli"
	@echo "  make setup-all            - Full setup: install, build whisper, link, download base models"
	@echo ""
	@echo "Environment variables:"
	@echo "  PORT                      - Port for the FastAPI service (default: 8000)"
	@echo "  MODEL                     - Model to use (default: base.en)"
	@echo "  RELOAD                    - Enable hot-reloading (default: true)"
	@echo "  CONTAINER                 - Docker container name (default: whisper-api)"

# Install Python dependencies
install:
	@echo "Installing Python dependencies..."
	$(PYTHON) -m pip install -r requirements.txt

# Create Python virtual environment
venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv venv
	@echo "Activate with: source venv/bin/activate"
	@bash -c "source venv/bin/activate"

# Start the service
start:
	@echo "Starting whisper.cpp FastAPI service on port $(PORT)..."
	@if [ "$(RELOAD)" = "true" ]; then \
		cd src && $(PYTHON) main.py --port $(PORT) --host 0.0.0.0 --reload; \
	else \
		cd src && $(PYTHON) main.py --port $(PORT) --host 0.0.0.0; \
	fi

# Stop the running service
stop:
	@echo "Stopping whisper.cpp FastAPI service..."
	-pkill -f "python main.py"
	@echo "Service stopped."

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	-rm -rf temp_uploads/*
	-rm -rf src/temp_uploads/*
	-rm -rf __pycache__
	-rm -rf src/__pycache__
	-find . -name "*.pyc" -delete
	-find . -name "*.json" -path "*/temp_uploads/*" -delete
	@echo "Temporary files cleaned."

# List available models
models:
	@echo "Listing available models..."
	@curl -s http://localhost:$(PORT)/models | jq

# Download a model
download-model:
	@echo "Downloading model $(MODEL)..."
	@if [ -f "whisper.cpp/models/download-ggml-model.sh" ]; then \
		cd whisper.cpp && bash models/download-ggml-model.sh $(MODEL); \
		echo "Model $(MODEL) downloaded to whisper.cpp/models/"; \
		# Copy model to src/models for use by the service \
		mkdir -p src/models; \
		cp whisper.cpp/models/ggml-$(MODEL).bin src/models/ 2>/dev/null || true; \
		echo "Copied model to src/models/ for service use"; \
	else \
		echo "Error: download script not found in whisper.cpp/models/"; \
		exit 1; \
	fi

# Build whisper.cpp
build-whisper:
	@echo "Building whisper.cpp..."
	@if [ -d "whisper.cpp" ]; then \
		cd whisper.cpp && cmake -B build && cmake --build build --config Release; \
	else \
		echo "Error: whisper.cpp directory not found."; \
		exit 1; \
	fi

# Link whisper-cli to system path
link-whisper:
	@echo "Creating symlink for whisper-cli..."
	@if [ -f "whisper.cpp/build/bin/whisper-cli" ]; then \
		sudo ln -sf "$(PWD)/whisper.cpp/build/bin/whisper-cli" /usr/local/bin/whisper-cli; \
		echo "Symlink created at /usr/local/bin/whisper-cli"; \
	else \
		echo "Error: whisper-cli binary not found. Build whisper.cpp first with 'make build-whisper'."; \
		exit 1; \
	fi

# Full setup
setup-all: venv install build-whisper link-whisper
	@echo "Downloading base models..."
	@cd whisper.cpp && bash models/download-ggml-model.sh base.en
	@cd whisper.cpp && bash models/download-ggml-model.sh small.en-tdrz
	@echo "Setup complete. You can now run 'make start' to start the service."
