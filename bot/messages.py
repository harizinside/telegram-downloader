def welcome() -> str:
    return (
        "Halo! Kirim aja link video-nya (TikTok, Instagram, Facebook, X/Twitter, "
        "YouTube, atau situs lain yang didukung) — saya download-in otomatis."
    )


def busy_downloading() -> str:
    return "⏳ Masih ada proses download yang berjalan, tunggu sampai selesai ya."


def not_a_link() -> str:
    return "Itu kelihatannya bukan link. Kirim link video-nya buat saya download-in."


def starting() -> str:
    return "⏳ Oke, mulai download..."


def queued() -> str:
    return "⏳ Antre giliran download..."


def downloading(label: str) -> str:
    return f"⬇️ Downloading dari {label}..."


def uploading() -> str:
    return "📤 Upload ke Telegram..."


def error_unsupported() -> str:
    return "Link itu kelihatannya gak didukung buat didownload. Coba link lain."


def error_unavailable() -> str:
    return "Gagal download — videonya mungkin private, sudah dihapus, atau region-locked."


def error_timeout() -> str:
    return "Download kelamaan jadi dibatalkan. Coba video yang lebih pendek/kecil."


def error_too_large() -> str:
    return "Videonya kebesaran buat saya kirim. Maaf!"


def error_generic() -> str:
    return "Ada yang salah pas download. Coba lagi sebentar lagi."
