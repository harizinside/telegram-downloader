# telegram-downloader

Bot Telegram yang download video lewat yt-dlp, lalu mengirimkannya balik ke chat.

Alur: kirim link video **apapun, kapan aja** (gak perlu command atau pilih platform dulu) → bot otomatis deteksi platformnya → download → kirim balik videonya. Karena pakai yt-dlp, situs yang didukung gak dibatasi cuma TikTok/Instagram/Facebook/X/YouTube — apapun yang bisa di-extract yt-dlp bakal dicoba. Kalau link-nya gak didukung, bot balas pesan error yang jelas.

> **Catatan YouTube livestream**: video YouTube biasa dan livestream yang **sudah selesai** (VOD) didownload seperti video biasa. Livestream yang **masih berlangsung** akan didownload dari titik itu terus sampai stream selesai atau kena `DOWNLOAD_TIMEOUT_SECONDS` (default 600 detik) — kalau streamnya panjang, downloadnya bisa gagal karena timeout.

## Setup

1. Buat bot via [@BotFather](https://t.me/BotFather) (`/newbot`) → catat `BOT_TOKEN`.
2. Copy `.env.example` ke `.env`, isi `BOT_TOKEN`.
3. (Opsional, lihat bagian "Limit upload" di bawah) Kalau mau limit upload 2GB alih-alih 50MB standar, daftar app personal di https://my.telegram.org/apps → isi `TELEGRAM_API_ID`/`TELEGRAM_API_HASH` di `.env` juga.

## Jalanin lewat Docker (recommended)

```
docker compose up --build
```

Tidak perlu install Python/yt-dlp/ffmpeg di host — semua sudah dibundel di image.

## Limit upload video: 50MB (default) vs 2GB (opsional)

Telegram cloud API (`api.telegram.org`) hard-cap upload bot di 50MB. Untuk naikin ke 2GB, bot perlu bicara ke local Bot API server sendiri (sidecar container `telegram-bot-api`), yang butuh `api_id`/`api_hash` dari akun Telegram pribadi.

Ini **sepenuhnya dikontrol lewat `.env`**, tidak perlu ubah kode:

- **`TELEGRAM_API_ID`/`TELEGRAM_API_HASH` kosong** → bot otomatis pakai `api.telegram.org`, limit 50MB.
- **`TELEGRAM_API_ID`/`TELEGRAM_API_HASH` diisi** DAN `.env` juga berisi `COMPOSE_PROFILES=local-api` → sidecar `telegram-bot-api` ikut jalan, bot otomatis pakai limit 2GB.

Kalau `COMPOSE_PROFILES=local-api` tidak di-set, sidecar-nya tidak akan start sama sekali walau `docker compose up` dijalankan (default profile cuma menjalankan service `bot`).

## Jalanin lokal tanpa Docker (loop cepat buat dev)

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -U yt-dlp
python -m bot.main
```

Sama seperti di atas: tanpa `TELEGRAM_API_ID`/`TELEGRAM_API_HASH` di-set, bot fallback ke `api.telegram.org` (limit 50MB — cukup buat testing clip pendek). ffmpeg harus sudah ada di PATH (`ffmpeg -version`).

## Deploy ke VPS lewat ghcr.io

Push ke `main` men-trigger `.github/workflows/docker-publish.yml` yang build & push image ke `ghcr.io/harizinside/telegram-downloader:latest`. Di VPS:

```
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

Kalau mau limit 2GB, tambahkan `--profile local-api` di kedua command di atas, dan pastikan `.env` di VPS berisi `TELEGRAM_API_ID`/`TELEGRAM_API_HASH`.

ffmpeg dan yt-dlp sudah ada di dalam image — VPS tidak perlu install apa-apa selain Docker.

## `/tldv` — Download recording tl;dv

Bot ini punya command khusus `/tldv` buat download recording meeting tl;dv.io. Karena tl;dv gak punya akses publik, command ini bakal minta **bearer token** dari akun tl;dv kamu dulu (sekali pakai, gak disimpan), baru minta URL-nya.

Cara dapetin token (dari browser):
1. Buka tldv.io dan login.
2. Tekan F12 → tab Console.
3. Jalankan: `JSON.parse(localStorage.getItem("_cap_jwt")).token`
4. Copy hasilnya.

Token hanya dipakai untuk satu kali download dan langsung dihapus setelah selesai. Paste link tl;dv biasa (tanpa `/tldv`) **tidak** akan diproses oleh bot karena butuh token.

## Environment variables

| Var | Default | Keterangan |
|---|---|---|
| `BOT_TOKEN` | (required) | Token dari BotFather |
| `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` | kosong | Dari my.telegram.org. Kalau diisi (+ `COMPOSE_PROFILES=local-api`), limit upload naik ke 2GB. Kalau kosong, limit 50MB standar |
| `TELEGRAM_API_BASE_URL` | auto | Auto-derived dari ada/tidaknya `TELEGRAM_API_ID`/`HASH`; override manual kalau perlu |
| `DOWNLOAD_DIR` | `/data/downloads` | Folder temp untuk file hasil download |
| `MAX_CONCURRENT_DOWNLOADS` | `2` | Jumlah download yt-dlp paralel maksimum |
| `DOWNLOAD_TIMEOUT_SECONDS` | `600` | Timeout per download |
| `MAX_VIDEO_SIZE_MB` | auto (45 / 1950) | Video di atas ini ditolak; auto menyesuaikan limit 50MB/2GB, override manual kalau perlu |
