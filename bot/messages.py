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


def choose_format() -> str:
    return "Mau download sebagai apa?"


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


def transcribe_ask_audio() -> str:
    return (
        "Kirim voice note atau file audio yang mau di-transcribe jadi teks "
        "(voice note Telegram, atau file suara yang diteruskan dari WhatsApp/lainnya)."
    )


def transcribing() -> str:
    return "🎙️ Transcribing audio..."


def error_not_audio() -> str:
    return "Itu bukan voice note atau file audio. Kirim voice note atau file audio ya."


def error_unsupported_audio_format() -> str:
    return "Format audio-nya gak didukung. Coba format lain (ogg/opus, mp3, wav, m4a, flac, webm)."


def error_audio_too_large(max_mb: int) -> str:
    return f"File audio-nya kebesaran (maks {max_mb}MB buat fitur transcribe ini). Coba file yang lebih pendek."


def error_transcription_not_configured() -> str:
    return "Fitur transcribe belum aktif — admin bot belum set GROQ_API_KEY."


def error_transcription_timeout() -> str:
    return "Transcribe kelamaan jadi dibatalkan. Coba lagi sebentar lagi."


def error_transcription_busy() -> str:
    return "Layanan transcribe lagi rate-limited, coba lagi sebentar lagi."


def error_transcription_failed() -> str:
    return "Gagal transcribe audio-nya. Coba lagi sebentar lagi."


def error_no_speech_detected() -> str:
    return "Gak kedengeran ada ucapan di audio itu."


def transcript_too_long_caption() -> str:
    return "Transkrip-nya kepanjangan buat dikirim langsung, jadi dikirim sebagai file .txt."
