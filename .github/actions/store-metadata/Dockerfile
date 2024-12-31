FROM python:3.10-slim

# Install git and other necessary packages
RUN apt-get update && apt-get install -y git && apt-get clean

# Set up the working directory for the action
WORKDIR /action

# Copy the action's code (preserving directory structure)
COPY extract /action/extract
COPY utils /action/utils
COPY main.py /action/main.py
COPY requirements.txt /action/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /action/requirements.txt

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the entrypoint script as the container's default command
ENTRYPOINT ["/entrypoint.sh"]
