# /// script
# requires-python = ">=3.10"
# dependencies = ["youtube-transcript-api>=1.2,<2"]
# ///
"""Fetch the transcript of a single YouTube video as text or JSON."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

VIDEO_ID_RE = re.compile(r"[A-Za-z0-9_-]{11}")
HOST_RE = re.compile(
    r"(?:(?:www|m|music)\.)?(?:youtube\.com|youtu\.be|youtube-nocookie\.com)"
)
ID_PATH_PREFIXES = ("/shorts/", "/embed/", "/live/", "/v/")
ACCEPTED_FORMS = (
    "accepted forms: an 11-character video ID, or a youtube.com/watch?v=ID, "
    "youtu.be/ID, /shorts/ID, /embed/ID or /live/ID URL"
)


def extract_video_id(value: str) -> str:
    """Return the video ID from a YouTube URL or a bare ID.

    Raises:
        ValueError: If ``value`` is not a recognizable YouTube video URL or ID.
    """
    text = value.strip()
    if VIDEO_ID_RE.fullmatch(text):
        return text

    url = urlparse(text if "://" in text else f"https://{text}")
    host = (url.hostname or "").lower()
    candidate = ""
    if HOST_RE.fullmatch(host):
        if host.endswith("youtu.be"):
            candidate = url.path.lstrip("/").split("/")[0]
        elif url.path == "/watch":
            candidate = parse_qs(url.query).get("v", [""])[0]
        else:
            for prefix in ID_PATH_PREFIXES:
                if url.path.startswith(prefix):
                    candidate = url.path[len(prefix) :].split("/")[0]
                    break

    if not VIDEO_ID_RE.fullmatch(candidate):
        raise ValueError(f"not a YouTube video URL or ID: {value!r}")
    return candidate
