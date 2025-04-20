# Dockerfile
FROM python:3.11-slim

# 1) Treat /app as root of imports
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# 2) Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 3) Copy your code
COPY . .

EXPOSE 80 5000

CMD ["python", "src/app.py"]
