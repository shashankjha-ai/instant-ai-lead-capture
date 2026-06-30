# Use official Python 3.11 slim image for a lightweight, secure base footprint
FROM python:3.11-slim

# Set working directory inside the container to standardize file relative paths
WORKDIR /app

# Copy dependency manifest first to leverage Docker build layer caching
COPY requirements.txt .

# Install production dependencies without storing cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code into container working directory
COPY src/ ./src/

# Expose port 8000 for incoming external HTTP requests
EXPOSE 8000

# Set default command to run Uvicorn production server bound to all network interfaces
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
