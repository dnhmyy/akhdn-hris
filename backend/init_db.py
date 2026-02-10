# backend/init_db.py
import mysql.connector
import os
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

_env_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_env_dir)
load_dotenv(os.path.join(_env_dir, '.env'))
load_dotenv(os.path.join(_root_dir, '.env'))
load_dotenv(os.path.join(_env_dir, '.env.local'), override=True)
load_dotenv(os.path.join(_root_dir, '.env.local'), override=True)

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

    # Tabel mesin absensi (info lengkap per mesin).
    # device_key = password rahasia per mesin (diisi kamu, dipakai saat mesin/middleware push ke API).
    # device_ip = domain (misal hris.tamvan.web.id) atau IP, untuk referensi; API pakai domain.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_devices (
            id VARCHAR(50) PRIMARY KEY,
            branch_id VARCHAR(50),
            device_name VARCHAR(255),
            device_ip VARCHAR(50),
            last_sync TIMESTAMP,
            status VARCHAR(50) DEFAULT 'active',
            serial_no VARCHAR(100),
            mac_address VARCHAR(50),
            model VARCHAR(100),
            platform VARCHAR(100),
            manufacturer VARCHAR(100),
            device_key VARCHAR(255)
        )
    ''')

    # Kolom tambahan jika tabel sudah ada (migrasi)
    for col, defn in [
        ('serial_no', 'VARCHAR(100)'),
        ('mac_address', 'VARCHAR(50)'),
        ('model', 'VARCHAR(100)'),
        ('platform', 'VARCHAR(100)'),
        ('manufacturer', 'VARCHAR(100)'),
        ('device_key', 'VARCHAR(255)'),
    ]:
        try:
            cursor.execute(f'ALTER TABLE attendance_devices ADD COLUMN {col} {defn}')
        except mysql.connector.Error:
            pass

    try:
        cursor.execute('ALTER TABLE employees ADD COLUMN device_pin VARCHAR(50)')
    except mysql.connector.Error:
        pass  # Kolom sudah ada
    try:
        cursor.execute('ALTER TABLE employees ADD COLUMN device_fingerprint_index INT')
    except mysql.connector.Error:
        pass  # Kolom sudah ada

    # Satu mesin patokan (X105). Cabang lain: copy row ini, ubah id/serial_no/branch_id/device_key.
    # - id = serial number mesin (dari menu Info Mesin)
    # - device_key = password rahasia yang kamu buat; isi sama di middleware/mesin saat push ke API
    # - device_ip = domain server (hris.tamvan.web.id) atau IP, untuk referensi saja
    # API push: POST https://hris.tamvan.web.id/api/attendance/push  body: device_id, device_key, records[]
    devices = [
        # Template mesin X105 (Solution) - ganti branch_id & device_key per cabang
        (
            'CKEB223560955',           # id = serial number mesin
            'p9',                # branch_id (ganti untuk cabang lain)
            'X105 Fingerprint',        # device_name
            'hris.tamvan.web.id',     # device_ip = domain (bukan IP)
            'ganti_dengan_key_rahasia', # device_key = isi sendiri, rahasia per mesin
            'CKEB223560955',           # serial_no
            '00:17:61:12:7e:04',       # mac_address
            'X105',                     # model
            'ZLM60_TFT',                # platform
            'Solution',                 # manufacturer
        ),
    ]
    for d in devices:
        cursor.execute('''
            INSERT INTO attendance_devices 
            (id, branch_id, device_name, device_ip, device_key, serial_no, mac_address, model, platform, manufacturer)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            branch_id = VALUES(branch_id),
            device_name = VALUES(device_name),
            device_ip = VALUES(device_ip),
            device_key = VALUES(device_key),
            serial_no = VALUES(serial_no),
            mac_address = VALUES(mac_address),
            model = VALUES(model),
            platform = VALUES(platform),
            manufacturer = VALUES(manufacturer)
        ''', d)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()