# Base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port Flask (5000)
EXPOSE 5000

# Jalankan Flask tanpa Gunicorn
CMD ["python", "app.py"]
