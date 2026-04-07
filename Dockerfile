# Use the official Python image
FROM python:3.11-slim
WORKDIR /app
COPY . /app
# installing all dependencies in a single layer (faster builds, smaller image)
RUN pip install --no-cache-dir openenv-core pydantic openai fastapi uvicorn
# HuggingFace Spaces requires port 7860
EXPOSE 7860
# Start the FastAPI server on port 7860 
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]