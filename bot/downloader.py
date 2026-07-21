from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Optional

import yt_dlp

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    pass


class UnsupportedError(DownloadError):
    pass


class UnavailableError(DownloadError):
    pass


class AuthRequiredError(DownloadError):
    pass


class DownloadTimeoutError(DownloadError):
    pass


class TooLargeError(DownloadError):
    pass


class GenericDownloadError(DownloadError):
    pass


# e.g. "NSFW tweet requires authentication. Use --cookies, ..." (Twitter/X sensitive
# media), or similar "login required" messages from other extractors.
_AUTH_REQUIRED_HINTS = ("requires authentication", "login required", "log in to confirm", "sign in to confirm")
_UNAVAILABLE_HINTS = ("private", "unavailable", "removed", "not available")


def _download_sync(url: str, out_dir: Path, timeout: float, cookiefile: Optional[Path]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": timeout,
    }
    if cookiefile is not None:
        ydl_opts["cookiefile"] = str(cookiefile)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except yt_dlp.utils.DownloadError as exc:
        message = str(exc)
        lowered = message.lower()
        if "Unsupported URL" in message:
            raise UnsupportedError(message) from exc
        if any(hint in lowered for hint in _AUTH_REQUIRED_HINTS):
            raise AuthRequiredError(message) from exc
        if any(hint in lowered for hint in _UNAVAILABLE_HINTS):
            raise UnavailableError(message) from exc
        raise GenericDownloadError(message) from exc

    video_id = info.get("id") if info else None
    if not video_id:
        raise GenericDownloadError("yt-dlp did not return a video id")

    path = out_dir / f"{video_id}.mp4"
    if not path.exists():
        candidates = sorted(out_dir.glob(f"{video_id}.*"))
        if not candidates:
            raise GenericDownloadError("Downloaded file not found on disk")
        path = candidates[0]
    return path


async def download(
    url: str,
    out_dir: Path,
    timeout: float,
    max_size_mb: int,
    cookiefile: Optional[Path] = None,
) -> Path:
    try:
        path = await asyncio.wait_for(
            asyncio.to_thread(_download_sync, url, out_dir, timeout, cookiefile),
            timeout=timeout,
        )
    except asyncio.TimeoutError as exc:
        raise DownloadTimeoutError() from exc

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        path.unlink(missing_ok=True)
        raise TooLargeError()
    return path
