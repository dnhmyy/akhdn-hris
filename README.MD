🏆 Master Setup & Deployment Guide (Cloudflare Tunnel)
Panduan ini menjelaskan setup "Lengkap" menggunakan Docker Compose, Nginx, dan Cloudflare Tunnel.

🏗️ Arsitektur Sistem
Alur data Anda sekarang sangat profesional dan aman: User --> Cloudflare (Internet) --> Tunnel (Container) --> Nginx (Container) --> App/Static Data

Cloudflare Tunnel: Pintu masuk rahasia (tidak perlu buka port 80 di router).
Nginx: Web server utama yang melayani file Frontend secara cepat dan mengirim permintaan API ke Backend.
App (Flask/Gunicorn): Mesin backend yang mengolah logika bisnis dan database.
MySQL: Database tempat semua data absensi tersimpan.
phpMyAdmin: Alat visual untuk mengelola database MySQL (tersedia di port 8080).
📂 Struktur File Final
text
hris-website/
├── backend/            # Logic Python
├── frontend/           # HTML, JS, CSS
├── nginx/
│   └── nginx.conf      # Konfigurasi Web Server
├── Dockerfile          # Instruksi Build Backend
├── docker-compose.yml  # Orkestrasi Seluruh Sistem (MySQL, Nginx, phpMyAdmin, Tunnel)
└── .env                # Password & Token (RAHASIA)
🚀 Langkah Menjalankan (Deployment)
Isi Token Cloudflare: Buka file 
.env
 dan masukkan CLOUDFLARE_TUNNEL_TOKEN yang Anda dapat dari dashboard Cloudflare Zero Trust.
Jalankan Seluruh Sistem:
bash
docker compose up -d --build
Perintah ini akan mendownload MySQL, Nginx, dan membangun backend Anda otomatis.
Inisialisasi Database (Sekali Saja):
bash
docker exec -it hris_app python3 backend/init_db.py
☁️ Setting di Dashboard Cloudflare
Pada bagian Public Hostname di Cloudflare Tunnel:

Subdomain: hris
Domain: tokoanda.com
Service Type: HTTP
URL: web:80 (Ini sangat penting! Tunnel sekarang mengarah ke kontainer web atau Nginx, bukan langsung ke app).
✅ Mengapa Menggunakan Nginx?
Kecepatan: Nginx jauh lebih cepat dalam mengirimkan file CSS/JS dibanding Flask.
Keamanan: Bertindak sebagai tameng tambahan sebelum masuk ke kodingan Python Anda.
Standar Industri: Inilah cara aplikasi profesional dideploy di server nyata.