-- cleanup_data.sql
-- Script untuk menghapus SEMUA data dummy (ID yang mulai dengan DUMMY_)
-- Jalankan di tab SQL phpMyAdmin atau import file ini.

USE hris;

-- 1. Hapus data absensi dummy
DELETE FROM attendance WHERE employee_id LIKE 'DUMMY_%';

-- 2. Hapus data karyawan dummy
DELETE FROM employees WHERE id LIKE 'DUMMY_%';

SELECT 'Data dummy berhasil dihapus!' as status;
