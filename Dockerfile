FROM mcr.microsoft.com/playwright/python:v1.53.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY web.py .

# Environment
ENV PYTHONUNBUFFERED=1

# Run the web server (which will also run the bot)
CMD ["python", "web.py"]