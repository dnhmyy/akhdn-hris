from flask import Flask, jsonify, request, send_from_directory, send_file, session, redirect, url_for
import mysql.connector
import os
import base64
import uuid
from werkzeug.security import check_password_hash
from functools import wraps
from dotenv import load_dotenv

# Load env: .env dulu, lalu .env.local dengan override=True agar local menang (DB_HOST=localhost)
_env_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_env_dir)
load_dotenv(os.path.join(_env_dir, '.env'))
load_dotenv(os.path.join(_root_dir, '.env'))
load_dotenv(os.path.join(_env_dir, '.env.local'), override=True)
load_dotenv(os.path.join(_root_dir, '.env.local'), override=True)

app = Flask(__name__, static_folder='../frontend')
app.secret_key = os.getenv('SECRET_KEY', 'super-secret-key-roti-kebanggaan-2026')

# Folder simpan foto dari mesin absensi
UPLOAD_ATTENDANCE = os.path.join(os.path.dirname(__file__), 'uploads', 'attendance')
os.makedirs(UPLOAD_ATTENDANCE, exist_ok=True)

# ============================================
# FUNGSI BANTUAN UNTUK DATABASE & AUTH
# ============================================
def get_db():
    """Koneksi ke database MySQL"""
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'hris'),
        port=int(os.getenv('DB_PORT', 3306))
    )
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized', 'message': 'Please login first'}), 401
        return f(*args, **kwargs)
    return decorated_function

def calculate_minutes_diff(time1, time2):
    """Menghitung selisih menit antara dua string waktu (HH:MM:SS atau HH:MM)"""
    if not time1 or not time2:
        return 0
    
    def to_min(t):
        parts = t.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    
    return to_min(time1) - to_min(time2)

# ============================================
# ROUTE UNTUK FRONTEND
# ============================================
@app.route('/')
def serve_frontend():
    """Tampilkan halaman utama frontend"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve file CSS, JS, dll"""
    return send_from_directory('../frontend', filename)

# ============================================
# API ENDPOINTS (AUTHENTICATION)
# ============================================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
        
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({
            'message': 'Login successful',
            'user': {
                'username': user['username'],
                'role': user['role']
            }
        }), 200
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'username': session.get('username'),
                'role': session.get('role')
            }
        }), 200
    return jsonify({'authenticated': False}), 200

# --- Mesin Absensi: Terima data push dari mesin ---
@app.route('/api/attendance/push', methods=['POST'])
def attendance_push():
    """
    Format data dari mesin absensi:
    {
        "device_id": "CKEB223560955",  # ID Mesin P9 (sesuai database)
        "device_key": "kunci_rahasia_mesin",
        "records": [
            {
                "pin": "10024050",  # ID karyawan di mesin
                "timestamp": "2026-02-05 08:15:30",
                "status": 0,  # 0=checkin, 1=checkout
                "verification": 1  # 1=fingerprint, 2=card
            }
        ]
    }
    """
    data = request.json
    print(f"DEBUG: Received push request from {request.remote_addr}")
    # print(f"DEBUG: Data: {data}") # Uncomment for full data log
    
    device_id = data.get('device_id')
    device_key = data.get('device_key')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Validasi mesin dari database (attendance_devices)
    cursor.execute('SELECT id, device_key FROM attendance_devices WHERE status = %s', ('active',))
    rows = cursor.fetchall()
    valid_devices = {r['id']: (r.get('device_key') or '') for r in rows if r.get('device_key')}

    if not device_id or device_id not in valid_devices or valid_devices[device_id] != device_key:
        print(f"DEBUG: Unauthorized device attempt: ID={device_id}, Key={device_key}")
        conn.close()
        return jsonify({"error": "Unauthorized device"}), 401

    # Process each record
    for record in data.get('records', []):
        # Cari karyawan: device_pin atau id
        cursor.execute('SELECT id, shift_start, shift_end FROM employees WHERE device_pin = %s OR id = %s', (record['pin'], record['pin']))
        employee = cursor.fetchone()

        if not employee:
            print(f"DEBUG: Employee not found for PIN: {record['pin']}")
            continue

        if employee:
            employee_id = employee['id']
            shift_start = employee['shift_start']
            shift_end = employee['shift_end']
            timestamp = record['timestamp']
            date = timestamp.split()[0]
            time = timestamp.split()[1]
            
            # Tentukan check_in atau check_out
            if record['status'] == 0:  # Check-in
                late = max(0, calculate_minutes_diff(time, shift_start))
                cursor.execute('''
                    INSERT INTO attendance 
                    (employee_id, date, check_in, late_minutes)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    check_in = VALUES(check_in),
                    late_minutes = VALUES(late_minutes)
                ''', (employee_id, date, time, late))
            else:  # Check-out
                overtime = max(0, calculate_minutes_diff(time, shift_end))
                cursor.execute('''
                    INSERT INTO attendance 
                    (employee_id, date, check_out, overtime_minutes)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    check_out = VALUES(check_out),
                    overtime_minutes = VALUES(overtime_minutes)
                ''', (employee_id, date, time, overtime))
            
            print(f"DEBUG: Processed record for {employee_id} on {date} {time} (status: {record['status']})")

    # Update Last Sync untuk mesin ini
    cursor.execute('UPDATE attendance_devices SET last_sync = NOW() WHERE id = %s', (device_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": f"{len(data['records'])} records processed"}), 200


# GET /api/attendance-devices - Daftar mesin absensi (untuk halaman monitoring)
@app.route('/api/attendance-devices', methods=['GET'])
@login_required
def get_attendance_devices():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT id, branch_id, device_name, device_ip, last_sync, status,
               serial_no, mac_address, model, platform, manufacturer
        FROM attendance_devices
        WHERE status = %s
        ORDER BY branch_id, device_name
    ''', ('active',))
    devices = cursor.fetchall()
    conn.close()
    # Format datetime untuk last_sync
    for d in devices:
        if d.get('last_sync'):
            d['last_sync'] = d['last_sync'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(d['last_sync'], 'strftime') else str(d['last_sync'])
        else:
            d['last_sync'] = None
    return jsonify(devices)


# --- Karyawan ---
@app.route('/api/employees/<string:employee_id>', methods=['PUT'])
@login_required
def update_employee(employee_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Ambil data yang dikirim, hanya update field yang dikirim
    allowed_fields = [
        'name', 'position', 'department', 'branch_id', 
        'shift_start', 'shift_end', 'is_active', 
        'start_date', 'contract_duration_months', 'contract_end_date'
    ]
    
    update_data = {}
    for field in allowed_fields:
        if field in data:
            val = data[field]
            # Convert empty strings to None for date/int fields to avoid MySQL errors
            if field in ['start_date', 'contract_end_date', 'contract_duration_months'] and val == '':
                val = None
            update_data[field] = val
    
    if not update_data:
        return jsonify({'error': 'No data to update'}), 400
    
    try:
        # Gunakan list comprehension untuk membangun query dinamis
        set_clause = ', '.join([f"{field} = %s" for field in update_data.keys()])
        params = list(update_data.values())
        params.append(employee_id)
        
        sql = f"UPDATE employees SET {set_clause} WHERE id = %s"
        cursor.execute(sql, params)
        
        conn.commit()
        return jsonify({'message': 'Employee updated successfully'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# DELETE: Nonaktifkan karyawan (soft delete)
@app.route('/api/employees/<string:employee_id>', methods=['DELETE'])
@login_required
def delete_employee(employee_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE employees 
            SET is_active=0 
            WHERE id=%s
        ''', (employee_id,))
        conn.commit()
        return jsonify({'message': 'Employee deactivated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# GET: Ambil data absensi dengan filter
@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    date = request.args.get('date')
    branch = request.args.get('branch')

    query = '''
        SELECT a.*, e.name, e.branch_id, e.shift_start, e.shift_end
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        WHERE 1=1
    '''
    params = []

    if date:
        query += ' AND a.date = %s'
        params.append(date)
    if branch:
        query += ' AND e.branch_id = %s'
        params.append(branch)

    query += ' ORDER BY a.date DESC, e.name'

    cursor.execute(query, params)
    result = cursor.fetchall()

    conn.close()
    return jsonify(result)

# POST: Tambah data absensi
@app.route('/api/attendance', methods=['POST'])
def add_attendance():
    data = request.json
    required_fields = ['employee_id', 'date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Cek apakah karyawan ada
    cursor.execute('SELECT id FROM employees WHERE id=%s', (data['employee_id'],))
    if not cursor.fetchone():
        return jsonify({'error': 'Employee not found'}), 404
    
    # Cek apakah sudah ada data attendance di tanggal tersebut untuk karyawan tersebut
    cursor.execute('''
        SELECT id FROM attendance 
        WHERE employee_id=%s AND date=%s
    ''', (data['employee_id'], data['date']))
    
    existing = cursor.fetchone()
    
    try:
        if existing:
            # Update
            update_fields = []
            values = []
            for field in ['check_in', 'check_out', 'overtime_minutes', 'late_minutes', 'status']:
                if field in data:
                    update_fields.append(f"{field}=%s")
                    values.append(data[field])
            values.append(existing['id'])
            cursor.execute(f'''
                UPDATE attendance 
                SET {', '.join(update_fields)}
                WHERE id=%s
            ''', values)
            message = 'Attendance updated'
        else:
            # Insert
            cursor.execute('''
                INSERT INTO attendance (employee_id, date, check_in, check_out, overtime_minutes, late_minutes, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                data['employee_id'],
                data['date'],
                data.get('check_in'),
                data.get('check_out'),
                data.get('overtime_minutes', 0),
                data.get('late_minutes', 0),
                data.get('status', 'present')
            ))
            message = 'Attendance added'
        
        conn.commit()
        return jsonify({'message': message}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# GET /api/employees
@app.route('/api/employees', methods=['GET'])
@login_required
def get_all_employees():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Ambil parameter filter
    branch = request.args.get('branch')
    active = request.args.get('active')
    
    query = 'SELECT * FROM employees'
    conditions = []
    params = []
    
    if branch:
        conditions.append('branch_id=%s')
        params.append(branch)
    if active is not None:
        if active.lower() == 'true':
            conditions.append('is_active=1')
        elif active.lower() == 'false':
            conditions.append('is_active=0')
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY name'
    
    cursor.execute(query, params)
    employees = cursor.fetchall()
    
    conn.close()
    return jsonify(employees)
    
# POST /api/employees
@app.route('/api/employees', methods=['POST'])
@login_required
def add_employee():
    # Ambil data dari frontend (JSON)
    data = request.json
    
    # Validasi
    if not data or 'id' not in data or 'name' not in data:
        return jsonify({'error': 'ID dan Nama wajib diisi'}), 400
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Hitung contract_end_date jika ada start_date dan contract_duration_months
        contract_end_date = None
        start_date = data.get('start_date')
        if not start_date: # Handle empty string or None
            start_date = None
            
        contract_duration = data.get('contract_duration_months')
        if contract_duration == '':
            contract_duration = None

        if start_date and contract_duration:
            from datetime import datetime, timedelta
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                # Approximate: 1 month = 30 days
                months = int(contract_duration)
                end = start + timedelta(days=months * 30)
                contract_end_date = end.strftime('%Y-%m-%d')
            except ValueError:
                start_date = None # Invalid format, treat as None
        
        cursor.execute('''
            INSERT INTO employees (id, name, position, department, branch_id, shift_start, shift_end, 
                                   start_date, contract_duration_months, contract_end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['id'],
            data['name'],
            data.get('position', ''),
            data.get('department', ''),
            data.get('branch_id', 'sorrento'),
            data.get('shift_start', '09:00'),
            data.get('shift_end', '17:00'),
            start_date,
            contract_duration,
            contract_end_date
        ))
        
        conn.commit()
        return jsonify({'message': 'Karyawan berhasil ditambahkan!', 'id': data['id']}), 201
        
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'ID karyawan sudah ada!'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# --- Cabang ---
# GET /api/branches
@app.route('/api/branches', methods=['GET'])
def get_branches():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name, color_class FROM branches ORDER BY name')
    rows = cursor.fetchall()
    conn.close()

    # Format sama dengan config.js: id, name, colorClass
    branches = [
        {
            'id': row['id'],
            'name': row['name'],
            'colorClass': row['color_class'] or row['id']
        }
        for row in rows
    ]
    return jsonify(branches)

# --- Dashboard ---
# GET /api/dashboard/stats
@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def dashboard_stats():  
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Total karyawan aktif
    cursor.execute("SELECT COUNT(*) as total FROM employees WHERE is_active = 1")
    total = cursor.fetchone()['total']
    
    # Hadir hari ini (Sudah check-in tapi BELUM check-out)
    cursor.execute('''
        SELECT COUNT(*) as present 
        FROM attendance 
        WHERE date = CURDATE() 
        AND check_in IS NOT NULL 
        AND check_out IS NULL
    ''')
    present = cursor.fetchone()['present']

    # Hadir per cabang (untuk update card dashboard)
    cursor.execute('''
        SELECT e.branch_id, COUNT(a.id) as count
        FROM employees e
        JOIN attendance a ON e.id = a.employee_id
        WHERE a.date = CURDATE() 
        AND a.check_in IS NOT NULL 
        AND a.check_out IS NULL
        GROUP BY e.branch_id
    ''')
    branch_counts = {row['branch_id']: row['count'] for row in cursor.fetchall()}
    
    conn.close()
    
    return jsonify({
        'total_employees': total,
        'present_today': present,
        'branch_counts': branch_counts
    })

# GET /api/attendance/today
@app.route('/api/attendance/today', methods=['GET'])
@login_required
def attendance_today():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Gabungkan data karyawan dengan absensi
    cursor.execute('''
        SELECT e.id as employee_id, e.name, e.branch_id, e.shift_start, e.shift_end,
               a.check_in, a.check_out, a.late_minutes, a.overtime_minutes,
               COALESCE(a.date, CURDATE()) as record_date
        FROM employees e
        LEFT JOIN attendance a ON e.id = a.employee_id AND a.date = CURDATE()
        WHERE e.is_active = 1
    ''')
    
    attendance = []
    for row in cursor.fetchall():
        attendance.append({
            'employee_id': row['employee_id'],
            'name': row['name'],
            'branch_id': row['branch_id'],
            'shift_start': str(row['shift_start']) if row['shift_start'] else '-',
            'shift_end': str(row['shift_end']) if row['shift_end'] else '-',
            'check_in': str(row['check_in']) if row['check_in'] else '-',
            'check_out': str(row['check_out']) if row['check_out'] else '-',
            'date': str(row['record_date']),
            'overtime_minutes': row['overtime_minutes'] or 0,
            'late_minutes': row['late_minutes'] or 0
        })
    
    conn.close()
    return jsonify(attendance)

# GET /api/reports/monthly - Laporan dengan date range
@app.route('/api/reports/monthly', methods=['GET'])
@login_required
def monthly_report():
    """
    Endpoint untuk laporan dengan date range
    Query params:
    - start_date: format YYYY-MM-DD (contoh: 2026-02-01)
    - end_date: format YYYY-MM-DD (contoh: 2026-02-28)
    - branch: optional, filter by branch_id
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    branch = request.args.get('branch')
    
    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date parameters required (format: YYYY-MM-DD)'}), 400
    
    # Query untuk mengambil data detail absensi di range tanggal tersebut
    query = '''
        SELECT 
            a.date,
            e.id,
            e.name,
            e.position,
            e.branch_id,
            e.shift_start,
            e.shift_end,
            a.check_in,
            a.check_out,
            a.late_minutes,
            a.overtime_minutes
        FROM employees e
        JOIN attendance a ON e.id = a.employee_id 
        WHERE a.date BETWEEN %s AND %s
          AND e.is_active = 1
    '''
    
    params = [start_date, end_date]
    
    if branch:
        query += ' AND e.branch_id = %s'
        params.append(branch)
    
    query += ' ORDER BY a.date DESC, e.branch_id, e.name'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Format hasil
    report_data = []
    total_present = 0
    total_overtime = 0
    total_late = 0
    unique_employees = set()
    
    for row in rows:
        unique_employees.add(row['id'])
        total_present += 1
        total_overtime += row['overtime_minutes'] or 0
        total_late += row['late_minutes'] or 0
        
        report_data.append({
            'date': row['date'],
            'employee_id': row['id'],
            'name': row['name'],
            'position': row['position'],
            'branch_id': row['branch_id'],
            'shift_start': str(row['shift_start']),
            'shift_end': str(row['shift_end']),
            'check_in': str(row['check_in']) if row['check_in'] else '-',
            'check_out': str(row['check_out']) if row['check_out'] else '-',
            'late_minutes': row['late_minutes'] or 0,
            'overtime_minutes': row['overtime_minutes'] or 0
        })
    
    # Summary per cabang
    branch_summary_query = '''
        SELECT 
            e.branch_id,
            COUNT(DISTINCT e.id) as total_employees,
            COUNT(a.id) as total_attendance,
            COALESCE(SUM(a.overtime_minutes), 0) as total_overtime,
            COUNT(CASE WHEN a.late_minutes > 0 THEN 1 END) as total_late_count
        FROM employees e
        LEFT JOIN attendance a ON e.id = a.employee_id 
            AND a.date BETWEEN %s AND %s
        WHERE e.is_active = 1
    '''
    
    branch_params = [start_date, end_date]
    if branch:
        branch_summary_query += ' AND e.branch_id = %s'
        branch_params.append(branch)
    
    branch_summary_query += ' GROUP BY e.branch_id'
    
    cursor.execute(branch_summary_query, branch_params)
    branch_rows = cursor.fetchall()
    
    branch_summary = []
    for row in branch_rows:
        # Hitung persentase kehadiran berdasarkan jumlah hari di range
        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        working_days = (end - start).days + 1
        attendance_rate = (row['total_attendance'] / (row['total_employees'] * working_days) * 100) if row['total_employees'] > 0 else 0
        
        branch_summary.append({
            'branch_id': row['branch_id'],
            'total_employees': row['total_employees'],
            'attendance_rate': round(attendance_rate, 1),
            'total_overtime_hours': round(row['total_overtime'] / 60, 1),
            'total_late_count': row['total_late_count']
        })
    
    conn.close()
    
    return jsonify({
        'start_date': start_date,
        'end_date': end_date,
        'summary': {
            'total_employees': len(unique_employees),
            'total_present': total_present,
            'total_overtime_hours': round(total_overtime / 60, 1),
            'total_late_minutes': total_late
        },
        'employees': report_data,
        'branch_summary': branch_summary
    })

# GET /api/reports/export - Export Laporan ke Excel
@app.route('/api/reports/export', methods=['GET'])
@login_required
def export_report():
    try:
        import pandas as pd
        from io import BytesIO
    except ImportError:
        return jsonify({'error': 'Library pandas belum terinstall'}), 500

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    branch = request.args.get('branch')
    
    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date required'}), 400

    # Gunakan logic query yang sama dengan monthly_report
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    query = '''
        SELECT 
            a.date,
            e.id,
            e.name,
            e.position,
            e.department,
            e.branch_id,
            e.shift_start,
            e.shift_end,
            a.check_in,
            a.check_out,
            a.late_minutes,
            a.overtime_minutes
        FROM employees e
        JOIN attendance a ON e.id = a.employee_id 
        WHERE a.date BETWEEN %s AND %s
          AND e.is_active = 1
    '''
    
    params = [start_date, end_date]
    if branch:
        query += ' AND e.branch_id = %s'
        params.append(branch)
    
    query += ' ORDER BY a.date DESC, e.branch_id, e.name'
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # Siapkan data untuk DataFrame
    data = []
    for idx, row in enumerate(rows, 1):
        data.append({
            'No': idx,
            'Tanggal': row['date'],
            'ID Karyawan': row['id'],
            'Nama Lengkap': row['name'],
            'Cabang': row['branch_id'],
            'Shift Masuk': str(row['shift_start']),
            'Shift Keluar': str(row['shift_end']),
            'Check-In': str(row['check_in']) if row['check_in'] else '-',
            'Check-Out': str(row['check_out']) if row['check_out'] else '-',
            'Keterlambatan (Menit)': row['late_minutes'] or 0,
            'Lembur (Menit)': row['overtime_minutes'] or 0
        })

    # Buat DataFrame
    if not data:
        df = pd.DataFrame(columns=['No', 'Tanggal', 'ID Karyawan', 'Nama Lengkap', 'Cabang', 'Shift Masuk', 'Shift Keluar', 'Check-In', 'Check-Out', 'Keterlambatan (Menit)', 'Lembur (Menit)'])
    else:
        df = pd.DataFrame(data)
    
    # Export ke Excel di memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Laporan Absensi')
    
    output.seek(0)
    
    filename = f"Laporan_Absensi_{start_date}_sd_{end_date}.xlsx"
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

# ============================================
# JALANKAN SERVER
# ============================================
if __name__ == '__main__':
    # Cek koneksi database MySQL
    try:
        conn = get_db()
        conn.ping(reconnect=True)
        conn.close()
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
    
    print("\n" + "="*50)
    print("SERVER HRIS BERJALAN")
    print("="*50)
    print("Dashboard (local): http://localhost:5000")
    print("Production: https://hris.tamvan.web.id")
    print("API Karyawan: /api/employees")
    print("API Cabang: /api/branches")
    print("API Push Mesin: /api/attendance/push")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)