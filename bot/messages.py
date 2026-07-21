from bot.platforms import Platform


def welcome() -> str:
    return "Halo! Pilih platform video yang mau kamu download:"


def ask_for_link(platform: Platform) -> str:
    return f"Kirim link video {platform.name}-nya ya."


def busy_downloading() -> str:
    return "⏳ Masih ada proses download yang berjalan, tunggu sampai selesai ya."


def invalid_link(platform: Platform) -> str:
    return f"Itu kelihatannya bukan link {platform.name} yang valid. Coba kirim lagi linknya."


def starting() -> str:
    return "⏳ Oke, mulai download..."


def queued() -> str:
    return "⏳ Antre giliran download..."


def downloading(platform: Platform) -> str:
    return f"⬇️ Downloading dari {platform.name}..."


def uploading() -> str:
    return "📤 Upload ke Telegram..."


def error_unsupported(platform: Platform) -> str:
    return f"Link itu kelihatannya bukan video {platform.name} yang didukung. Coba cek lagi linknya."


def error_unavailable() -> str:
    return "Gagal download — videonya mungkin private, sudah dihapus, atau region-locked."


def error_timeout() -> str:
    return "Download kelamaan jadi dibatalkan. Coba video yang lebih pendek/kecil."


def error_too_large() -> str:
    return "Videonya lebih dari 2GB, kebesaran buat saya kirim. Maaf!"


def error_generic() -> str:
    return "Ada yang salah pas download. Coba lagi sebentar lagi."
