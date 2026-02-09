CARA JALANKAN HRIS SYSTEM:

1. INSTALASI:
   - Install Python 3.x
   - Install Flask: pip install flask

2. JALANKAN BACKEND:
   Buka CMD:
   cd backend
   python init_db.py    ← Buat database
   python app.py        ← Jalankan server (port 5000)

3. AKSES SISTEM:
   - Buka browser: http://localhost:5000
   - Dashboard: Lihat statistik
   - Karyawan: Tambah/lihat karyawan

4. API ENDPOINTS:
   - GET /api/employees     : Ambil semua karyawan
   - POST /api/employees    : Tambah karyawan baru
   - GET /api/branches      : Data cabang
   - GET /api/dashboard/stats : Statistik

5. TROUBLESHOOTING:
   - Backend tidak jalan? Cek port 5000
   - Database error? Hapus database.db, jalankan init_db.py lagi
   - Frontend error? F12 → Console