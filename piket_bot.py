import os
import sys
import time
from datetime import datetime
import requests

# ============================================================
# KONFIGURASI
# ============================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

TUGAS_PIKET = [
    "Menyapu lantai & membuang sampah",
    "Merapikan kabel & Menyapu lantai",
    "Merapikan meja, kursi taruna & mematikan AC/lampu",
]

JADWAL_PIKET = {
    "Monday": ["ARSA", "ARMA", "DEWI", "NUHA"],
    "Tuesday": ["AGATA", "FREDEL", "DINI", "HANIF"],
    "Wednesday": ["SANDRA", "BASITH", "FADLY", "ABDUS"],
    "Thursday": ["CRYPTO", "AFIQ", "REO", "MINTO"],
    "Friday": ["NATHAN", "WALDI", "ELVI", "KEYZA"],
}

HARI_ID = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu",
}

# ============================================================
# FORMAT PESAN
# ============================================================

def format_pagi(hari_id: str, petugas: list) -> str:
    baris = []
    for i, nama in enumerate(petugas):
        if i < len(TUGAS_PIKET):
            baris.append(f"• *{nama.upper()}* ➔ {TUGAS_PIKET[i]}")
        else:
            baris.append(f"• *{nama.upper()}* ➔ Danpiket — Lapor ke Ketua Kelas setelah selesai\n")
    daftar = "\n".join(baris)

    return (
        f"🧹 *REMINDER PIKET KELAS*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📅 Hari: *{hari_id}*\n\n"
        f"👥 Petugas piket hari ini:\n\n"
        f"{daftar}\n\n"
        f"_Mohon piket sebelum pelajaran dimulai. 🙏_"
    )

def format_siang(hari_id: str, petugas: list) -> str:
    anggota  = petugas[:-1]
    DANPIKET = petugas[-1].upper()

    baris_anggota = "\n".join(
        f"• *{nama.upper()}* — {tugas}" for nama, tugas in zip(anggota, TUGAS_PIKET)
    )

    return (
        f"🧹 *REMINDER PIKET KELAS*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📅 Hari: *{hari_id}*\n\n"
        f"👥 Jam kuliah hampir selesai, Ini saatnya:\n\n"
        f"{baris_anggota}\n"
        f"• *{DANPIKET}* — Pastikan standar 100% terpenuhi sebelum lapor ke Ketua Kelas.\n\n"
        f"_Terima kasih atas kesadaran dan tanggung jawabnya. 🙏_"
    )

# ============================================================
# FUNGSI UTAMA
# ============================================================

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def kirim_pesan(teks: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": teks, "parse_mode": "Markdown"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if data.get("ok"):
            print(f"[{now()}] Pesan berhasil dikirim.")
        else:
            print(f"[{now()}] ERROR: {data.get('description')}")
    except requests.exceptions.RequestException as e:
        print(f"[{now()}] Koneksi gagal: {e}")

def kirim_reminder_piket(mode: str):
    hari_en = datetime.now().strftime("%A")
    hari_id = HARI_ID.get(hari_en, hari_en)

    if hari_en not in JADWAL_PIKET:
        print(f"[{now()}] {hari_id} — tidak ada jadwal piket.")
        return

    petugas = JADWAL_PIKET[hari_en]

    if mode == "siang":
        pesan = format_siang(hari_id, petugas)
    else:
        pesan = format_pagi(hari_id, petugas)

    kirim_pesan(pesan)

def sinkronisasi_waktu(target_jam_utc: int, target_menit_utc: int):
    """Menahan eksekusi sampai detik jam server menyentuh target secara presisi."""
    print(f"[{now()}] Container menyala. Menunggu waktu presisi {target_jam_utc:02d}:{target_menit_utc:02d} UTC...")
    while True:
        sekarang = datetime.now()
        # Jika waktu server sudah mencapai atau melewati waktu target, lepaskan penahan!
        if sekarang.hour == target_jam_utc and sekarang.minute >= target_menit_utc:
            print(f"[{now()}] Waktu target tercapai! Mengeksekusi pesan...")
            break
        time.sleep(1) # Tahan dan cek lagi setiap 1 detik

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "pagi"
    
    # Kunci eksekusi berdasarkan mode (Target dalam UTC)
    if mode == "pagi":
        # Target pengiriman: 07:40 WIB -> 00:40 UTC
        sinkronisasi_waktu(0, 40)
    elif mode == "siang":
        # Target pengiriman: 15:15 WIB -> 08:15 UTC
        sinkronisasi_waktu(8, 15)

    kirim_reminder_piket(mode)
