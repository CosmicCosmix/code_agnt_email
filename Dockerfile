# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy your local files into the container
COPY . /app

# Install the required framework and dependencies
RUN pip install --no-cache-dir openenv-core pydantic openai

# Expose the port the FastAPI server runs on
EXPOSE 8000

# The command to start the OpenEnv server
RUN pip install --no-cache-dir fastapi uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]