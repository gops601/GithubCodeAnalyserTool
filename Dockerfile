# Use Python 3.10 slim as base
FROM python:3.10-slim

# Install system dependencies
# git: for cloning repos
# openjdk-17-jre-headless: required for sonar-scanner
# curl/unzip: for downloading the scanner
RUN apt-get update && apt-get install -y \
    git \
    openjdk-21-jre-headless \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Download and install Sonar-Scanner CLI (Stable version 5.0.1)
RUN curl -o /tmp/sonar-scanner.zip -L https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip && \
    unzip /tmp/sonar-scanner.zip -d /opt && \
    rm /tmp/sonar-scanner.zip && \
    mv /opt/sonar-scanner-5.0.1.3006-linux /opt/sonar-scanner

# Add sonar-scanner to PATH
ENV PATH="/opt/sonar-scanner/bin:${PATH}"

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Set environment variables for production
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Run the application with Gunicorn
# Using 4 workers and increased timeout for stability
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
