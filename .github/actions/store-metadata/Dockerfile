FROM python:3.10-slim

# Set up the working directory
WORKDIR /app

# Copy files into the container, maintaining directory structure
COPY extract /app/extract
COPY utils /app/utils
COPY main.py /app/main.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command
CMD ["python", "main.py", "./"]