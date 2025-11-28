# Use an official Python runtime image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# This is where 'cryptography' and others will be installed
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application source code
# We need to copy the backend folder, not just the root
COPY backend/ ./backend/
COPY . .

# Cloud Run injects the port via the $PORT environment variable
ENV PORT 8080

# Command to run the application using Gunicorn
# CRITICAL FIX: Changed 'app:app' to 'backend.main:app' 
# because the Flask app ('app') is inside 'backend/main.py'.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 backend.main:app