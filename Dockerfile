# Use paddlepaddle/paddle as base image
FROM paddlepaddle/paddle:3.0.0b1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    libzbar0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install \
    pyzbar \
    Pillow \
    paddleocr

# Set working directory
WORKDIR /app

# Copy application files from src directory
COPY src/app.py .
COPY src/invoice_processor.py .
COPY src/ocr_processor.py .
COPY src/qr_processor.py .
COPY src/main.py .

# Create data directory and copy sample data
RUN mkdir -p /app/data
COPY data /app/data
