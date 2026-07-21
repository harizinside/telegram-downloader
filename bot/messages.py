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


def ask_for_cookies() -> str:
    return (
        "🔒 Media ini ditandai sensitive/NSFW — platform-nya butuh akun yang login buat akses.\n\n"
        "Cara dapetin cookies-nya:\n"
        "1. Install extension browser \"Get cookies.txt LOCALLY\" (Chrome/Edge) atau "
        "\"cookies.txt\" (Firefox)\n"
        "2. Login ke akun kamu di situs itu (misal x.com) lewat browser yang sama\n"
        "3. Buka halaman video/postingan yang mau didownload, klik icon extension-nya, "
        "lalu export/download cookies-nya (jadi file .txt)\n"
        "4. Kirim file .txt itu ke sini\n\n"
        "⚠️ Cookies itu setara akses sementara ke akun kamu — cuma saya pakai buat download ini "
        "doang dan langsung dihapus setelahnya. Jangan kirim cookies akun yang gak kamu percaya, "
        "dan jangan share file cookies ini ke orang lain."
    )


def invalid_cookies() -> str:
    return "Saya butuh file cookies.txt (atau paste isi cookies-nya sebagai teks). Kirim ulang ya."


def error_cookies_failed() -> str:
    return "Masih gagal walau pakai cookies itu — mungkin cookies-nya sudah expired atau bukan buat akun yang tepat."


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
