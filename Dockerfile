FROM python:3.12-slim

# Install ffmpeg at the Linux system level
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your agent scripts
COPY . .

# Start the engine
CMD ["python", "main.py"]