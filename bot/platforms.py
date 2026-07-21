from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass(frozen=True)
class Platform:
    key: str
    name: str
    domain_hints: tuple[str, ...]


# Only used to make status messages nicer (e.g. "Downloading from TikTok...").
# Detection is NOT a whitelist -- any URL yt-dlp can extract will be attempted,
# known or not.
FACEBOOK = Platform("fb", "Facebook", ("facebook.com", "fb.watch"))
X = Platform("x", "X/Twitter", ("x.com", "twitter.com"))
INSTAGRAM = Platform("ig", "Instagram", ("instagram.com",))
TIKTOK = Platform("tk", "TikTok", ("tiktok.com", "vm.tiktok.com", "vt.tiktok.com"))
YOUTUBE = Platform("yt", "YouTube", ("youtube.com", "youtu.be"))

KNOWN_PLATFORMS: tuple[Platform, ...] = (FACEBOOK, X, INSTAGRAM, TIKTOK, YOUTUBE)

_URL_RE = re.compile(r"https?://\S+")


def extract_url(text: str) -> Optional[str]:
    """Pull the first URL out of a message, accepting a bare domain too."""
    if not text:
        return None
    text = text.strip()
    match = _URL_RE.search(text)
    if match:
        return match.group(0)
    if " " in text or "\n" in text:
        return None
    candidate = f"https://{text}"
    parsed = urlparse(candidate)
    if parsed.netloc and "." in parsed.netloc:
        return candidate
    return None


def detect_platform(url: str) -> Optional[Platform]:
    host = urlparse(url).netloc.lower()
    for platform in KNOWN_PLATFORMS:
        if any(hint in host for hint in platform.domain_hints):
            return platform
    return None


def display_label(url: str) -> str:
    platform = detect_platform(url)
    if platform:
        return platform.name
    return urlparse(url).netloc or "link"
