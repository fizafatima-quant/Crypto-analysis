# === Production container for the DEX project ===
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg

# System deps (optional; helps numpy/pandas wheels if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
WORKDIR /app
COPY src/requirements.txt /app/src/requirements.txt
RUN pip install --no-cache-dir -r /app/src/requirements.txt

# Copy source
COPY src/ /app/src/

# Default working dir
WORKDIR /app/src

# Default command: generate dashboard (headless)
CMD ["python", "run_dashboard.py"]
