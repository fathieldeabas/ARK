# Use official Python image from the Docker Hub
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirments.txt /app/
RUN pip install -r requirments.txt

# Copy project files
COPY . /app/

# Expose port
EXPOSE 8000

# Command to run Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
