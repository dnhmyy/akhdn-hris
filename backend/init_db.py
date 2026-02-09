# backend/init_db.py
import mysql.connector
import os
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

def init_database():
    # Koneksi ke database MySQL
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        port=int(os.getenv('DB_PORT', 3306))
    )
    cursor = conn.cursor()

    # Buat database jika belum ada
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME', 'hris')}")
    cursor.execute(f"USE {os.getenv('DB_NAME', 'hris')}")

    # Buat tabel employees
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            position VARCHAR(255),
            department VARCHAR(255),
            is_active TINYINT(1) DEFAULT 1,
            branch_id VARCHAR(50),
            shift_start VARCHAR(10) DEFAULT '09:00',
            shift_end VARCHAR(10) DEFAULT '17:00'
        )
    ''')

    # Buat tabel attendance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id VARCHAR(50),
            date DATE DEFAULT (CURRENT_DATE),
            check_in TIME,
            check_out TIME,
            overtime_minutes INT DEFAULT 0,
            late_minutes INT DEFAULT 0,
            status VARCHAR(50) DEFAULT 'present',
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            UNIQUE KEY (employee_id, date)
        )
    ''')

    # Buat tabel branches (jika ingin menyimpan cabang di database)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            color_class VARCHAR(50)
        )
    ''')

    # Insert data contoh untuk branches (sesuai dengan config.js)
    branches = [
        ('sorrento', 'Sorrento', 'sorrento'),
        ('beryl', 'Beryl', 'beryl'),
        ('downtown', 'Downtown', 'downtown'),
        ('greenlake', 'Greenlake', 'greenlake'),
        ('mkg', 'MKG', 'mkg'),
        ('grandindonesia', 'Grand Indonesia', 'grandindonesia'),
        ('p9', 'P9', 'p9'),
        ('dapursolvang', 'Dapur Solvang', 'dapursolvang'),
        ('pastrysolvang', 'Pastry Solvang', 'pastrysolvang'),
        ('enchante', 'Enchante', 'enchante'),
    ]
    cursor.executemany('INSERT IGNORE INTO branches (id, name, color_class) VALUES (%s, %s, %s)', branches)

    # Insert data contoh untuk employees (branch_id harus ada di tabel branches)
    employees = [
        ('EMP-001', 'Redzskid', 'Pentester', 'Security', 1, 'sorrento', '09:00', '17:00'),
        ('EMP-002', 'Jane Doe', 'HR Manager', 'HR', 1, 'beryl', '08:00', '16:00'),
        ('EMP-003', 'John Smith', 'Developer', 'IT', 1, 'downtown', '10:00', '18:00'),
    ]
    cursor.executemany('INSERT IGNORE INTO employees (id, name, position, department, is_active, branch_id, shift_start, shift_end) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', employees)

    # Buat tabel users untuk login
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'admin'
        )
    ''')

    # Insert default admin user jika belum ada
    # Password default: admin123 (nanti user bisa ganti)
    cursor.execute('SELECT id FROM users WHERE username = %s', ('admin',))
    admin_exists = cursor.fetchone()
    if not admin_exists:
        hashed_pw = generate_password_hash('admin123')
        cursor.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)', ('admin', hashed_pw, 'admin'))

    # Tabel dan kolom untuk mesin absensi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_devices (
            id VARCHAR(50) PRIMARY KEY,
            branch_id VARCHAR(50),
            device_name VARCHAR(255),
            device_ip VARCHAR(50),
            last_sync TIMESTAMP,
            status VARCHAR(50) DEFAULT 'active'
        )
    ''')

    try:
        cursor.execute('ALTER TABLE employees ADD COLUMN device_pin VARCHAR(50)')
    except mysql.connector.Error:
        pass  # Kolom sudah ada
    try:
        cursor.execute('ALTER TABLE employees ADD COLUMN device_fingerprint_index INT')
    except mysql.connector.Error:
        pass  # Kolom sudah ada

    # Data mesin contoh
    devices = [
        ('MESIN-SORRENTO-001', 'sorrento', 'Mesin Absensi Lobi', '192.168.1.100'),
        ('MESIN-BERYL-001', 'beryl', 'Mesin HRD', '192.168.2.100'),
        ('MESIN-DOWNTOWN-001', 'downtown', 'Mesin Lobi', '192.168.3.100'),
        ('MESIN-GREENLAKE-001', 'greenlake', 'Mesin Lobi', '192.168.4.100'),
        ('MESIN-MKG-001', 'mkg', 'Mesin Lobi', '192.168.5.100'),
        ('MESIN-GRANDINDONESIA-001', 'grandindonesia', 'Mesin Lobi', '192.168.6.100'),
    ]
    for device in devices:
        cursor.execute('''
            INSERT IGNORE INTO attendance_devices (id, branch_id, device_name, device_ip)
            VALUES (%s, %s, %s, %s)
        ''', device)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()