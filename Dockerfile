FROM python:3.12-slim

# Install Stockfish (Linux version) - same UCI protocol as Windows
# This is the official Stockfish package, works identically to the Windows version
RUN apt-get update && apt-get install -y stockfish && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Render uses PORT env variable (default 10000)
ENV PORT=10000
EXPOSE 10000

# Start the FastAPI server
CMD ["sh", "-c", "uvicorn presentation.api.main:app --host 0.0.0.0 --port ${PORT}"]
