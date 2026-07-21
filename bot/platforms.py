from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Platform:
    command: str
    name: str
    domain_hints: tuple[str, ...]


FACEBOOK = Platform("fb", "Facebook", ("facebook.com", "fb.watch"))
X = Platform("x", "X/Twitter", ("x.com", "twitter.com"))
INSTAGRAM = Platform("ig", "Instagram", ("instagram.com",))
TIKTOK = Platform("tk", "TikTok", ("tiktok.com", "vm.tiktok.com", "vt.tiktok.com"))

PLATFORMS: dict[str, Platform] = {p.command: p for p in (FACEBOOK, X, INSTAGRAM, TIKTOK)}


def validate_url(platform: Platform, raw: str) -> str | None:
    raw = raw.strip()
    if not raw:
        return None
    candidate = raw if "://" in raw else f"https://{raw}"
    parsed = urlparse(candidate)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    host = parsed.netloc.lower()
    if any(hint in host for hint in platform.domain_hints):
        return candidate
    return None
