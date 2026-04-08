# ─────────────────────────────────────────────────────────
#  Email Sorting OpenEnv — Dockerfile
#  Base: Python 3.10 slim
# ─────────────────────────────────────────────────────────

FROM python:3.10-slim

# Metadata
LABEL maintainer="OpenEnv Hackathon Team"
LABEL description="Email Sorting OpenEnv — AI email classification environment"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Copy dependency manifest first (layer cache optimisation)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Default command: run the baseline agent on all difficulty levels
CMD ["python", "baseline.py"]
