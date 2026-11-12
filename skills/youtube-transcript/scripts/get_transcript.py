# /// script
# requires-python = ">=3.10"
# dependencies = ["youtube-transcript-api>=1.2,<2"]
# ///
"""Fetch the transcript of a single YouTube video as text or JSON."""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from typing import Any, TypeVar
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import (
    AgeRestricted,
    InvalidVideoId,
    NoTranscriptFound,
    PoTokenRequired,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
    VideoUnplayable,
    YouTubeTranscriptApi,
    YouTubeTranscriptApiException,
)

T = TypeVar("T")

EXIT_OTHER = 1
EXIT_INVALID_INPUT = 2
EXIT_NO_CAPTIONS = 3
EXIT_UNAVAILABLE = 4
EXIT_BLOCKED = 5

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


class TranscriptError(Exception):
    """A transcript could not be fetched. Carries the process exit code."""

    def __init__(self, message: str, exit_code: int = EXIT_OTHER) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class BlockedError(TranscriptError):
    """YouTube refused the request, usually because of the network address."""

    def __init__(self, message: str) -> None:
        super().__init__(message, EXIT_BLOCKED)


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


def _translate(error: YouTubeTranscriptApiException, video_id: str) -> TranscriptError:
    """Turn a library exception into a one-line ``TranscriptError``."""
    if isinstance(error, (RequestBlocked, PoTokenRequired)):
        return BlockedError(f"YouTube blocked the transcript request for {video_id}")
    if isinstance(error, TranscriptsDisabled):
        return TranscriptError(
            f"captions are disabled for video {video_id}", EXIT_NO_CAPTIONS
        )
    if isinstance(error, AgeRestricted):
        return TranscriptError(
            f"video {video_id} is age-restricted and needs a signed-in session",
            EXIT_UNAVAILABLE,
        )
    if isinstance(error, VideoUnplayable):
        reason = _collapse(str(getattr(error, "reason", "") or "no reason given"))
        return TranscriptError(
            f"video {video_id} cannot be played: {reason}", EXIT_UNAVAILABLE
        )
    if isinstance(error, VideoUnavailable):
        return TranscriptError(
            f"video {video_id} is unavailable (removed, private, or wrong ID)",
            EXIT_UNAVAILABLE,
        )
    if isinstance(error, InvalidVideoId):
        return TranscriptError(f"invalid video ID: {video_id}", EXIT_INVALID_INPUT)
    return TranscriptError(
        f"could not retrieve a transcript for {video_id} ({type(error).__name__})",
        EXIT_OTHER,
    )


def _call_library(video_id: str, action: Callable[[], T]) -> T:
    """Run a library call, translating its exceptions."""
    try:
        return action()
    except YouTubeTranscriptApiException as error:
        raise _translate(error, video_id) from error


def _regional_matches(languages: Iterable[str], available: Iterable[str]) -> list[str]:
    """Return available codes like ``en-US`` for requested codes like ``en``."""
    available = list(available)
    return [
        code
        for language in languages
        for code in available
        if code.split("-")[0].lower() == language.lower() and code != language
    ]


def _select(transcripts: Any, video_id: str, languages: list[str]) -> Any:
    """Pick the best transcript: manual before generated, then regional."""
    try:
        return transcripts.find_transcript(languages)
    except NoTranscriptFound:
        pass
    codes = list(dict.fromkeys(t.language_code for t in transcripts))
    regional = _regional_matches(languages, codes)
    if regional:
        try:
            return transcripts.find_transcript(regional)
        except NoTranscriptFound:
            pass
    requested = ", ".join(languages)
    if codes:
        detail = f"available languages: {', '.join(codes)}"
    else:
        detail = "the video has no transcripts"
    raise TranscriptError(
        f"no transcript for video {video_id} in: {requested}; {detail}",
        EXIT_NO_CAPTIONS,
    )


def fetch_snippets(video_id: str, languages: list[str]) -> Transcript:
    """Fetch a transcript with youtube-transcript-api.

    Raises:
        TranscriptError: For every failure; ``BlockedError`` when YouTube
            refuses the request.
    """

    def action() -> Transcript:
        chosen = _select(YouTubeTranscriptApi().list(video_id), video_id, languages)
        snippets = [
            Snippet(text=s.text, start=float(s.start), duration=float(s.duration))
            for s in chosen.fetch()
        ]
        return Transcript(
            video_id=video_id,
            language_code=chosen.language_code,
            is_generated=chosen.is_generated,
            source="youtube-transcript-api",
            snippets=snippets,
        )

    return _call_library(video_id, action)


def available_languages(video_id: str) -> list[str]:
    """List transcripts as ``code<TAB>language<TAB>manual|generated`` lines.

    Raises:
        TranscriptError: For every failure, as in ``fetch_snippets``.
    """

    def action() -> list[str]:
        return [
            f"{t.language_code}\t{t.language}\t"
            f"{'generated' if t.is_generated else 'manual'}"
            for t in YouTubeTranscriptApi().list(video_id)
        ]

    return _call_library(video_id, action)
