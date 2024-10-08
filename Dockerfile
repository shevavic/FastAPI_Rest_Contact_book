# Stage 1: Build
FROM python:3.12-bullseye AS builder

# Set environment variables to prevent Python from writing .pyc files and to buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Update packages and install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Optionally, try upgrading libpq-dev if needed for SNI support
RUN apt-get update && apt-get install -y libpq5

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Upgrade pip and install dependencies
RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt

# Copy the rest of the project code
COPY . /app/

# Stage 2: Final
FROM python:3.12-bullseye

# Set environment variables to prevent Python from writing .pyc files and to buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Update packages and install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Optionally, try upgrading libpq-dev in the runtime environment as well
RUN apt-get update && apt-get install -y libpq5

# Set the working directory
WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local /usr/local

# Copy the rest of the project code
COPY . /app/

# Command to run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]