# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and required browsers
RUN pip install --no-cache-dir playwright && \
    playwright install --with-deps

# Copy the rest of the application code into the container
COPY . .

# Expose the port FastAPI is running on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
