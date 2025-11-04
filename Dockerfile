FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps for common Python packages (Postgres client, build tools)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Default command: run Gunicorn WSGI server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web.wsgi:app"]
