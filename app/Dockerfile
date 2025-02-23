# Flask application Dockerfile
FROM python:3.11-slim

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies file and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

EXPOSE 5000

# Run Flask application
CMD ["flask", "run", "--host=0.0.0.0"]
