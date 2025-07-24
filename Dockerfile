# Multi-stage build for minimal final image size
FROM --platform=linux/amd64 python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install to separate layer
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime image
FROM --platform=linux/amd64 python:3.11-slim

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Set working directory
WORKDIR /app

# Create required directories
RUN mkdir -p /app/input /app/output

# Copy source code (optimized layer ordering)
COPY src/ ./src/
COPY main.py .

# Set optimization flags
ENV PYTHONOPTIMIZE=1
ENV PYTHONUNBUFFERED=1

# Ensure executable permissions
RUN chmod +x main.py

# Health check for container validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Entry point as required by competition
ENTRYPOINT ["python", "main.py", "/app/input", "/app/output"]





# # Use AMD64 architecture explicitly as required
# FROM --platform=linux/amd64 python:3.11-slim

# # Set working directory
# WORKDIR /app

# # Create input and output directories
# RUN mkdir -p /app/input /app/output

# # Copy requirements first for better caching
# COPY requirements.txt .

# # Install dependencies with no cache to keep image small
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy source code
# COPY . .

# # Make sure the script is executable
# RUN chmod +x main.py

# # Set entrypoint as specified in requirements
# ENTRYPOINT ["python", "main.py", "/app/input", "/app/output"]
