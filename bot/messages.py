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


def tldv_ask_token() -> str:
    return (
        "To download from tl;dv, I need your bearer token.\n\n"
        "How to get it:\n"
        "1. Open tldv.io and log in.\n"
        "2. Press F12 → Console tab.\n"
        "3. Run: JSON.parse(localStorage.getItem(\"_cap_jwt\")).token\n"
        "4. Copy the output.\n\n"
        "Send the token here. It will only be used for this one download and discarded afterwards."
    )


def tldv_ask_url() -> str:
    return "Sekarang kirim URL meeting tl;dv-nya (contoh: https://tldv.io/app/meetings/...)."


def tldv_invalid_url() -> str:
    return "URL-nya kelihatannya bukan meeting tl;dv yang valid. Format: https://tldv.io/app/meetings/<id>"
