# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy your local files into the container
COPY . /app

# Install all dependencies in a single layer (faster builds, smaller image)
RUN pip install --no-cache-dir openenv-core pydantic openai fastapi uvicorn

# Expose the port the FastAPI server runs on
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]