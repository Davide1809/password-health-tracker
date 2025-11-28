# Use a slim Python image for a smaller final container size
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- CRITICAL FIX: Copy all Python files from the build context root to /app ---
# The previous build error indicated 'backend/' was not found in the context.
# We assume app.py and any other necessary files are at the root of the build context.
COPY app.py .
COPY test_app.py .

# Expose the port the application will run on
EXPOSE 8080

# The command to run the application using gunicorn
# This command starts the Gunicorn web server, binding to port 8080, 
# and running the 'app' variable from the 'app.py' module.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]