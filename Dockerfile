# Use paddlepaddle/paddle as base image
FROM paddlepaddle/paddle:3.0.0b1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    libzbar0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY requirements.txt .

# Install Python packages
RUN pip install -r requirements.txt

# Copy application files from src directory
COPY src/ src/

# Set the default command to run the FastAPI app
CMD ["uvicorn", "src.api:app", "--reload", "--host", "0.0.0.0", "--port", "9845"]
