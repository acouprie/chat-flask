# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python", "main.py"]