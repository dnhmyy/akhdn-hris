// js/config.js - Konfigurasi RotiKebanggaan
const API_BASE = '/api'; // Relatif - otomatis pakai domain yang sama (dev & production)
const HRIS_DOMAIN = 'hris.tamvan.web.id'; // Domain untuk API push mesin absensi
const HRIS_CONFIG = {
  branches: [
    { id: 'sorrento', name: 'Sorrento', colorClass: 'sorrento' },
    { id: 'beryl', name: 'Beryl', colorClass: 'beryl' },
    { id: 'downtown', name: 'Downtown', colorClass: 'downtown' },
    { id: 'greenlake', name: 'Greenlake', colorClass: 'greenlake' },
    { id: 'mkg', name: 'MKG', colorClass: 'mkg' },
    { id: 'grandindonesia', name: 'Grand Indonesia', colorClass: 'grandindonesia' },
    { id: 'p9', name: 'P9', colorClass: 'p9' },
    { id: 'dapursolvang', name: 'Dapur Solvang', colorClass: 'dapursolvang' },
    { id: 'pastrysolvang', name: 'Pastry Solvang', colorClass: 'pastrysolvang' },
    { id: 'enchante', name: 'Enchante', colorClass: 'enchante' },
  ]
};
