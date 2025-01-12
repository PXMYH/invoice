# Use paddlepaddle/paddle as base image
FROM paddlepaddle/paddle

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libzbar0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install pyzbar Pillow

# Set working directory
WORKDIR /app