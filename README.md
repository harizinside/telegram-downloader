# telegram-downloader

Bot Telegram yang download video dari Facebook, X/Twitter, Instagram, dan TikTok lewat yt-dlp, lalu mengirimkannya balik ke chat.

Alur: `/start` → klik tombol platform (Twitter/X, Facebook, TikTok, Instagram) → bot minta link → kirim link → bot balas video-nya.

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

Push ke `main` men-trigger `.github/workflows/docker-publish.yml` yang build & push image ke `ghcr.io/<owner>/telegram-downloader:latest`. Di VPS, edit `docker-compose.prod.yml` (ganti `OWNER`), lalu:

```
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

Kalau mau limit 2GB, tambahkan `--profile local-api` di kedua command di atas, dan pastikan `.env` di VPS berisi `TELEGRAM_API_ID`/`TELEGRAM_API_HASH`.

ffmpeg dan yt-dlp sudah ada di dalam image — VPS tidak perlu install apa-apa selain Docker.

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
