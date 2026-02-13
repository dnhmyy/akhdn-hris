-- seed_data.sql
-- Script untuk mengisi data dummy HRIS (60 karyawan + absensi 7 hari)
-- Gunakan phpMyAdmin di port 8080 untuk import file ini.

USE hris;

-- 1. Hapus data dummy lama jika ada (agar tidak bentrok)
DELETE FROM attendance WHERE employee_id LIKE 'DUMMY_%';
DELETE FROM employees WHERE id LIKE 'DUMMY_%';

-- 2. Insert 60 Karyawan
-- Format: id, name, position, branch_id, shift_start, shift_end, start_date, is_active
INSERT INTO employees (id, name, position, branch_id, shift_start, shift_end, start_date, is_active) VALUES
('DUMMY_001', 'TEST - User 1', 'Staff', 'p9', '08:00', '17:00', '2024-01-10', 1),
('DUMMY_002', 'TEST - User 2', 'Baker', 'enchante', '08:00', '17:00', '2024-01-11', 1),
('DUMMY_003', 'TEST - User 3', 'Supervisor', 'dapursolvang', '08:00', '17:00', '2024-01-12', 1),
('DUMMY_004', 'TEST - User 4', 'Manager', 'pastrysolvang', '08:00', '17:00', '2024-01-13', 1),
('DUMMY_005', 'TEST - User 5', 'Cashier', 'sorrento', '08:00', '17:00', '2024-01-14', 1),
('DUMMY_006', 'TEST - User 6', 'Baker', 'beryl', '08:00', '17:00', '2024-01-15', 1),
('DUMMY_007', 'TEST - User 7', 'Staff', 'downtown', '08:00', '17:00', '2024-01-16', 1),
('DUMMY_008', 'TEST - User 8', 'Staff', 'greenlake', '08:00', '17:00', '2024-01-17', 1),
('DUMMY_009', 'TEST - User 9', 'Baker', 'mkg', '08:00', '17:00', '2024-01-18', 1),
('DUMMY_010', 'TEST - User 10', 'Supervisor', 'grandindonesia', '08:00', '17:00', '2024-01-19', 1),
('DUMMY_011', 'TEST - User 11', 'Staff', 'p9', '08:00', '17:00', '2024-01-20', 1),
('DUMMY_012', 'TEST - User 12', 'Baker', 'enchante', '08:00', '17:00', '2024-01-21', 1),
('DUMMY_013', 'TEST - User 13', 'Staff', 'dapursolvang', '08:00', '17:00', '2024-01-22', 1),
('DUMMY_014', 'TEST - User 14', 'Staff', 'pastrysolvang', '08:00', '17:00', '2024-01-23', 1),
('DUMMY_015', 'TEST - User 15', 'Manager', 'sorrento', '08:00', '17:00', '2024-01-24', 1),
('DUMMY_016', 'TEST - User 16', 'Baker', 'beryl', '08:00', '17:00', '2024-01-25', 1),
('DUMMY_017', 'TEST - User 17', 'Staff', 'downtown', '08:00', '17:00', '2024-01-26', 1),
('DUMMY_018', 'TEST - User 18', 'Cashier', 'greenlake', '08:00', '17:00', '2024-01-27', 1),
('DUMMY_019', 'TEST - User 19', 'Baker', 'mkg', '08:00', '17:00', '2024-01-28', 1),
('DUMMY_020', 'TEST - User 20', 'Staff', 'grandindonesia', '08:00', '17:00', '2024-01-29', 1),
('DUMMY_021', 'TEST - User 21', 'Staff', 'p9', '08:00', '17:00', '2024-01-30', 1),
('DUMMY_022', 'TEST - User 22', 'Baker', 'enchante', '08:00', '17:00', '2024-01-31', 1),
('DUMMY_023', 'TEST - User 23', 'Staff', 'dapursolvang', '08:00', '17:00', '2024-02-01', 1),
('DUMMY_024', 'TEST - User 24', 'Staff', 'pastrysolvang', '08:00', '17:00', '2024-02-02', 1),
('DUMMY_025', 'TEST - User 25', 'Manager', 'sorrento', '08:00', '17:00', '2024-02-03', 1),
('DUMMY_026', 'TEST - User 26', 'Baker', 'beryl', '08:00', '17:00', '2024-02-04', 1),
('DUMMY_027', 'TEST - User 27', 'Staff', 'downtown', '08:00', '17:00', '2024-02-05', 1),
('DUMMY_028', 'TEST - User 28', 'Cashier', 'greenlake', '08:00', '17:00', '2024-02-06', 1),
('DUMMY_029', 'TEST - User 29', 'Baker', 'mkg', '08:00', '17:00', '2024-02-07', 1),
('DUMMY_030', 'TEST - User 30', 'Staff', 'grandindonesia', '08:00', '17:00', '2024-02-08', 1),
('DUMMY_031', 'TEST - User 31', 'Staff', 'p9', '08:00', '17:00', '2024-02-09', 1),
('DUMMY_032', 'TEST - User 32', 'Baker', 'enchante', '08:00', '17:00', '2024-02-10', 1),
('DUMMY_033', 'TEST - User 33', 'Staff', 'dapursolvang', '08:00', '17:00', '2024-02-11', 1),
('DUMMY_034', 'TEST - User 34', 'Staff', 'pastrysolvang', '08:00', '17:00', '2024-02-12', 1),
('DUMMY_035', 'TEST - User 35', 'Manager', 'sorrento', '08:00', '17:00', '2024-02-13', 1),
('DUMMY_036', 'TEST - User 36', 'Baker', 'beryl', '08:00', '17:00', '2024-02-14', 1),
('DUMMY_037', 'TEST - User 37', 'Staff', 'downtown', '08:00', '17:00', '2024-02-15', 1),
('DUMMY_038', 'TEST - User 38', 'Cashier', 'greenlake', '08:00', '17:00', '2024-02-16', 1),
('DUMMY_039', 'TEST - User 39', 'Baker', 'mkg', '08:00', '17:00', '2024-02-17', 1),
('DUMMY_040', 'TEST - User 40', 'Staff', 'grandindonesia', '08:00', '17:00', '2024-02-18', 1),
('DUMMY_041', 'TEST - User 41', 'Staff', 'p9', '08:00', '17:00', '2024-02-19', 1),
('DUMMY_042', 'TEST - User 42', 'Baker', 'enchante', '08:00', '17:00', '2024-02-20', 1),
('DUMMY_043', 'TEST - User 43', 'Staff', 'dapursolvang', '08:00', '17:00', '2024-02-21', 1),
('DUMMY_044', 'TEST - User 44', 'Staff', 'pastrysolvang', '08:00', '17:00', '2024-02-22', 1),
('DUMMY_045', 'TEST - User 45', 'Manager', 'sorrento', '08:00', '17:00', '2024-02-23', 1),
('DUMMY_046', 'TEST - User 46', 'Baker', 'beryl', '08:00', '17:00', '2024-02-24', 1),
('DUMMY_047', 'TEST - User 47', 'Staff', 'downtown', '08:00', '17:00', '2024-02-25', 1),
('DUMMY_048', 'TEST - User 48', 'Cashier', 'greenlake', '08:00', '17:00', '2024-02-26', 1),
('DUMMY_049', 'TEST - User 49', 'Baker', 'mkg', '08:00', '17:00', '2024-02-27', 1),
('DUMMY_050', 'TEST - User 50', 'Staff', 'grandindonesia', '08:00', '17:00', '2024-03-01', 1),
('DUMMY_051', 'TEST - User 51', 'Staff', 'p9', '08:00', '17:00', '2024-03-02', 1),
('DUMMY_052', 'TEST - User 52', 'Baker', 'enchante', '08:00', '17:00', '2024-03-03', 1),
('DUMMY_053', 'TEST - User 53', 'Staff', 'dapursolvang', '08:00', '17:00', '2024-03-04', 1),
('DUMMY_054', 'TEST - User 54', 'Staff', 'pastrysolvang', '08:00', '17:00', '2024-03-05', 1),
('DUMMY_055', 'TEST - User 55', 'Manager', 'sorrento', '08:00', '17:00', '2024-03-06', 1),
('DUMMY_056', 'TEST - User 56', 'Baker', 'beryl', '08:00', '17:00', '2024-03-07', 1),
('DUMMY_057', 'TEST - User 57', 'Staff', 'downtown', '08:00', '17:00', '2024-03-08', 1),
('DUMMY_058', 'TEST - User 58', 'Cashier', 'greenlake', '08:00', '17:00', '2024-03-09', 1),
('DUMMY_059', 'TEST - User 59', 'Baker', 'mkg', '08:00', '17:00', '2024-03-10', 1),
('DUMMY_060', 'TEST - User 60', 'Staff', 'grandindonesia', '08:00', '17:00', '2024-03-11', 1);

-- 3. Insert Absensi Hari Ini (CURDATE)
INSERT INTO attendance (employee_id, date, check_in, check_out, late_minutes, overtime_minutes, status)
SELECT id, CURDATE(), '08:05', '17:30', 5, 30, 'present'
FROM employees WHERE id LIKE 'DUMMY_%';

-- 4. Insert Absensi 7 Hari Terakhir
INSERT INTO attendance (employee_id, date, check_in, check_out, late_minutes, overtime_minutes, status)
SELECT id, DATE_SUB(CURDATE(), INTERVAL 1 DAY), '08:02', '17:15', 2, 15, 'present' FROM employees WHERE id LIKE 'DUMMY_%' UNION ALL
SELECT id, DATE_SUB(CURDATE(), INTERVAL 2 DAY), '08:10', '17:00', 10, 0, 'present' FROM employees WHERE id LIKE 'DUMMY_%' UNION ALL
SELECT id, DATE_SUB(CURDATE(), INTERVAL 3 DAY), '08:00', '18:00', 0, 60, 'present' FROM employees WHERE id LIKE 'DUMMY_%' UNION ALL
SELECT id, DATE_SUB(CURDATE(), INTERVAL 4 DAY), '08:05', '17:45', 5, 45, 'present' FROM employees WHERE id LIKE 'DUMMY_%' UNION ALL
SELECT id, DATE_SUB(CURDATE(), INTERVAL 5 DAY), '08:01', '17:10', 1, 10, 'present' FROM employees WHERE id LIKE 'DUMMY_%' UNION ALL
SELECT id, DATE_SUB(CURDATE(), INTERVAL 6 DAY), '08:00', '17:00', 0, 0, 'present' FROM employees WHERE id LIKE 'DUMMY_%';
