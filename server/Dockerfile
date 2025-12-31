# Use a slim Python 3.9 image to keep the file size down
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# 1. Install system dependencies (needed for some python packages)
# 2. Upgrade pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip

# Copy only requirements first (to cache dependencies)
COPY requirements.txt .

# Install Python libraries
# We use --no-cache-dir to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]