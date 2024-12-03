FROM python:3.10-slim

# Set up the working directory
WORKDIR /app

# Copy files into the container
COPY store_metadata.py /app/store_metadata.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command
CMD ["python", "/app/store_metadata.py"]
