FROM python:3.13.3-slim

# System deps:
#   libgl1 + libglib2.0-0  — OpenCV/PIL image handling used by Surya
#   libgomp1               — OpenMP, required by torch CPU inference
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first so this layer is cached independently of code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000