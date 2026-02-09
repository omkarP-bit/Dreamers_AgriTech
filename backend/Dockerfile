FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for SSL and MongoDB
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 10000

# Run the application
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}
