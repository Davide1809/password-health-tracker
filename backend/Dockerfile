# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This assumes your main Flask file is named app.py
COPY . .

# Expose the port your app runs on (Cloud Run defaults to $PORT, but 8080 is a good standard)
ENV PORT 8080

# Run the application using Gunicorn, specifying your app file (app.py) and instance name (app)
# If your main file is main.py, change 'app:app' to 'main:app'
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app