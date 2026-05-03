FROM python:3.11-slim

# Prevent Python from writing .pyc files to disk and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

WORKDIR /app

# Install OS-level dependencies needed by some Python packages (Pillow, some plotting libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libjpeg-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy app sources
COPY . /app

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit (allow PORT override by host platform)
CMD ["bash", "-c", "streamlit run app.py --server.port ${PORT:-8501} --server.address 0.0.0.0"]
