# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Kunci rahasia diperlukan untuk menggunakan session (autentikasi)
app.secret_key = os.urandom(24)

# --- Autentikasi Sederhana ---
# Data user (bisa diganti dengan data dari database pada aplikasi nyata)
app_user = os.environ.get('APP_USER', 'admin')
app_password = os.environ.get('APP_PASSWORD', 'password123')
USER_CREDENTIALS = {
    app_user: app_password
}
app.logger.info('Aplikasi Data Karyawan dimulai.')

# --- Database In-Memory Sederhana ---
# Untuk kesederhanaan, kita gunakan list of dictionaries sebagai database
employees = [
    {'id': 1, 'name': 'Darul Rizz', 'position': 'Software Engineer', 'salary': 8000000},
    {'id': 2, 'name': 'Deddy Batman', 'position': 'Project Manager', 'salary': 12000000}
]
# Counter untuk ID karyawan baru
next_id = 3

# --- Decorator untuk Cek Login ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Harap login terlebih dahulu.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rute untuk Autentikasi ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('Login berhasil!', 'success')
            app.logger.info(f"User '{username}' berhasil login.") # <-- TAMBAHKAN INI
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah.', 'danger')
            app.logger.warning(f"Percobaan login gagal untuk user '{username}'.") # <-- TAMBAHKAN INI
        return render_template('login.html')
@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

# --- Rute untuk Operasi CRUD ---

# Read (Menampilkan semua data karyawan)
@app.route('/')
@login_required
def index():
    return render_template('index.html', employees=employees)

# Create (Menambahkan karyawan baru)
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        global next_id
        try:
            salary = int(request.form['salary'])
        except ValueError:
            flash('Gaji harus berupa angka.', 'danger')
            return redirect(url_for('add_employee'))
        new_employee = {
            'id': next_id,
            'name': request.form['name'],
            'position': request.form['position'],
            'salary': salary
        }
        employees.append(new_employee)
        next_id += 1
        flash('Karyawan berhasil ditambahkan!', 'success')
        app.logger.info(f"Karyawan baru '{new_employee['name']}' berhasil ditambahkan.") # <-- TAMBAHKAN INI
        return redirect(url_for('index'))
    return render_template('add.html')

# Update (Mengedit data karyawan)
@app.route('/edit/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def edit_employee(employee_id):
    # Cari karyawan berdasarkan ID
    employee = next((emp for emp in employees if emp['id'] == employee_id), None)
    if not employee:
        return "Karyawan tidak ditemukan", 404

    if request.method == 'POST':
        try:
            employee['salary'] = int(request.form['salary'])
        except ValueError:
            flash('Gaji harus berupa angka.', 'danger')
            return redirect(url_for('edit_employee', employee_id=employee_id))
        employee['name'] = request.form['name']
        employee['position'] = request.form['position']
        flash('Data karyawan berhasil diperbarui!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', employee=employee)

# Delete (Menghapus data karyawan)
@app.route('/delete/<int:employee_id>')
@login_required
def delete_employee(employee_id):
    global employees
    # Filter karyawan, buang yang ID-nya cocok
    employees = [emp for emp in employees if emp['id'] != employee_id]
    flash('Karyawan berhasil dihapus!', 'warning')
    app.logger.info(f"Karyawan dengan ID {employee_id} berhasil dihapus.")
    return redirect(url_for('index'))

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
