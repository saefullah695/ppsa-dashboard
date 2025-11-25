# 1. Gunakan Python 3.11 sebagai base image
FROM python:3.11-slim

# 2. Set working directory di dalam container
WORKDIR /app

# 3. Install library sistem yang dibutuhkan
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev libssl-dev git curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements.txt dan install package Python
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# 5. Copy seluruh kode aplikasi
COPY . .

# 6. Buka port default Dash
EXPOSE 8050

# 7. Jalankan app menggunakan gunicorn
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8050"]
