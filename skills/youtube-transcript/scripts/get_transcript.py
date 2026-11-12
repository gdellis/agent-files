# /// script
# requires-python = ">=3.10"
# dependencies = ["youtube-transcript-api>=1.2,<2"]
# ///
"""Fetch the transcript of a single YouTube video as text or JSON."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
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


@dataclass(frozen=True)
class Snippet:
    """One timed piece of transcript text. Times are in seconds."""

    text: str
    start: float
    duration: float


@dataclass(frozen=True)
class Transcript:
    """A fetched transcript and where it came from."""

    video_id: str
    language_code: str
    is_generated: bool | None  # None when the source cannot tell
    source: str  # "youtube-transcript-api" or "yt-dlp"
    snippets: list[Snippet]


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


def _collapse(text: str) -> str:
    """Collapse every run of whitespace, including newlines, to one space."""
    return " ".join(text.split())


def _timestamp(seconds: float) -> str:
    """Format seconds as ``mm:ss``, or ``h:mm:ss`` from one hour on."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_transcript(transcript: Transcript, fmt: str, timestamps: bool) -> str:
    """Render a transcript as plain text or JSON.

    Text output has one line per snippet and skips empty snippets. JSON output
    ignores ``timestamps`` because every snippet already carries its times.

    Raises:
        ValueError: If ``fmt`` is neither ``"text"`` nor ``"json"``.
    """
    if fmt == "json":
        return json.dumps(asdict(transcript), ensure_ascii=False, indent=2) + "\n"
    if fmt != "text":
        raise ValueError(f"unknown format: {fmt!r}")

    lines = []
    for snippet in transcript.snippets:
        text = _collapse(snippet.text)
        if not text:
            continue
        lines.append(f"[{_timestamp(snippet.start)}] {text}" if timestamps else text)
    return "".join(f"{line}\n" for line in lines)
