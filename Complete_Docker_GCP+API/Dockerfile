FROM python:3.11-slim

# System deps for pandas/pyarrow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

# Where we store model artifacts
RUN mkdir -p /app/models

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Cloud Run (and many platforms) default to PORT=8080; here we just run a script
CMD ["uvicorn", "src.api_app:app", "--host", "0.0.0.0", "--port", "8000"]
