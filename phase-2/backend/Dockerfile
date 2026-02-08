FROM python:3.13-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Hugging Face uses 7860 by default)
EXPOSE 7860

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
