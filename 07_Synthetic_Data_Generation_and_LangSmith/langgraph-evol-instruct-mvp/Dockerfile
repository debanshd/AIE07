FROM python:3.11-slim

WORKDIR /app

# Copy requirements from backend directory
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files from backend directory
COPY backend/api_server.py .
COPY backend/langgraph_app.py .

# Set default port (Fly.io will override with $PORT)
ENV PORT=8000

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["sh", "-c", "uvicorn api_server:app --host 0.0.0.0 --port $PORT"] 