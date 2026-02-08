# refund-handler Dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY handler.py .
EXPOSE 8080
CMD ["python", "handler.py"]
