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
    streamlit \
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

# Expose Streamlit port
EXPOSE 8501

# Set environment variables for Streamlit
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]