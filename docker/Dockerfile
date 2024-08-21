FROM python:3.12

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libsasl2-dev \
    python3-dev \
    libldap2-dev \
    libssl-dev && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir gunicorn

# Expose port
EXPOSE 5001

# Set environment variables
ENV TIMEOUT=60 \
    ENABLE_HTTPS=False \
    WORKERS=1

# Copy and set entrypoint script
COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

# Define the command to run the application
CMD ["/start.sh"]
