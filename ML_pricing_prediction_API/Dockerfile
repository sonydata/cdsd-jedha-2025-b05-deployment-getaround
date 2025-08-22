# Small, stable Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and ensure stdout is unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# All subsequent paths relative to /app
WORKDIR /app

# Use the latest pip (often faster/more compatible)
RUN pip install --no-cache-dir --upgrade pip

# Install Python deps first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project (app.py, model, README, etc.)
COPY . .

# Hugging Face Spaces exposes port 7860 for Docker apps by convention.
# Uvicorn will bind to 0.0.0.0 so the container is reachable externally.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
