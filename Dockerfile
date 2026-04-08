# Use the official Python image
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir openenv-core pydantic openai fastapi uvicorn
COPY . /app
EXPOSE 7860
# FastAPI server on port 7860 
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]