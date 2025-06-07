# Dockerfile
# Gunakan base image Python yang ringan
FROM python:3.9-slim

# Set direktori kerja di dalam container
WORKDIR /app

# Salin file requirements dan install dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin sisa kode aplikasi ke dalam direktori kerja
COPY . .

# Expose port yang digunakan oleh Flask
EXPOSE 5000

# Perintah untuk menjalankan aplikasi saat container dimulai
CMD ["flask", "run", "--host=0.0.0.0"]
