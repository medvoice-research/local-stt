FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Clone and build whisper.cpp
RUN git clone https://github.com/ggml-org/whisper.cpp.git /tmp/whisper.cpp \
    && cd /tmp/whisper.cpp \
    && cmake -B build \
    && cmake --build build --config Release \
    && cp /tmp/whisper.cpp/build/bin/whisper-cli /usr/local/bin/ \
    && cp -r /tmp/whisper.cpp/models /app/ \
    && rm -rf /tmp/whisper.cpp

# Copy application files
COPY src/ /app/src/
COPY models/ /app/models/
COPY README_FASTAPI_SERVICE.md /app/README.md

# Create required directories
RUN mkdir -p /app/temp_uploads

# Create a non-root user to run the app
RUN useradd -m -u 1000 appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port 8000 for the FastAPI service
EXPOSE 8000

# Set the working directory
WORKDIR /app

# Command to run the application
CMD ["python3", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
