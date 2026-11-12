# /// script
# requires-python = ">=3.10"
# dependencies = ["youtube-transcript-api>=1.2,<2"]
# ///
"""Fetch the transcript of a single YouTube video as text or JSON."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
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

YTDLP_TIMEOUT_SECONDS = 120
BLOCKED_HELP = (
    "YouTube is blocking requests from this network. Retry from another "
    "network, or pass a proxy or browser cookies; see SKILL.md."
)

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


def ytdlp_available() -> bool:
    """Report whether the ``yt-dlp`` executable is on ``PATH``."""
    return shutil.which("yt-dlp") is not None


def _snippets_from_json3(payload: str) -> list[Snippet]:
    """Convert a YouTube ``json3`` subtitle document into snippets.

    Auto-generated captions repeat lines as they scroll, so events that are
    empty or repeat the previously kept text are dropped.
    """
    snippets: list[Snippet] = []
    for event in json.loads(payload)["events"]:
        text = _collapse("".join(seg.get("utf8", "") for seg in event.get("segs", [])))
        if not text or (snippets and snippets[-1].text == text):
            continue
        snippets.append(
            Snippet(
                text=text,
                start=event.get("tStartMs", 0) / 1000,
                duration=event.get("dDurationMs", 0) / 1000,
            )
        )
    return snippets


def _pick_subtitle_file(
    directory: Path, video_id: str, languages: list[str]
) -> tuple[Path, str] | None:
    """Choose a downloaded subtitle file: exact language first, then regional."""
    by_code = {
        path.name[len(video_id) + 1 : -len(".json3")]: path
        for path in sorted(directory.glob("*.json3"))
        if path.name.startswith(f"{video_id}.")
    }
    for code in [*languages, *_regional_matches(languages, by_code)]:
        if code in by_code:
            return by_code[code], code
    return None


def fetch_snippets_ytdlp(video_id: str, languages: list[str]) -> Transcript:
    """Fetch a transcript with the ``yt-dlp`` executable.

    Raises:
        BlockedError: For every failure, since this is the last resort.
    """
    with tempfile.TemporaryDirectory() as tmp:
        command = [
            "yt-dlp",
            "--skip-download",
            "--no-playlist",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            ",".join(f"{language}.*" for language in languages),
            "--sub-format",
            "json3",
            "-o",
            str(Path(tmp) / "%(id)s"),
            "--",
            f"https://www.youtube.com/watch?v={video_id}",
        ]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=YTDLP_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise BlockedError(
                f"yt-dlp timed out after {YTDLP_TIMEOUT_SECONDS} seconds"
            ) from error
        except OSError as error:
            raise BlockedError(f"yt-dlp could not be run: {error}") from error

        if result.returncode != 0:
            lines = [line for line in result.stderr.splitlines() if line.strip()]
            detail = _collapse(lines[-1]) if lines else f"exit {result.returncode}"
            raise BlockedError(f"yt-dlp failed: {detail}")

        picked = _pick_subtitle_file(Path(tmp), video_id, languages)
        if picked is None:
            raise BlockedError(f"yt-dlp found no subtitles in: {', '.join(languages)}")
        path, code = picked
        try:
            snippets = _snippets_from_json3(path.read_text(encoding="utf-8"))
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            raise BlockedError(
                "yt-dlp returned subtitles in an unexpected format"
            ) from error

    return Transcript(
        video_id=video_id,
        language_code=code,
        is_generated=None,
        source="yt-dlp",
        snippets=snippets,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="get_transcript.py",
        description="Print the transcript of a single YouTube video.",
        epilog="Put -- before a video ID that starts with a hyphen.",
    )
    parser.add_argument("video", help="YouTube URL or 11-character video ID")
    parser.add_argument(
        "--lang",
        nargs="+",
        default=["en"],
        metavar="CODE",
        help="language codes in priority order (default: en)",
    )
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="prefix each text line with [mm:ss]",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="output format (default: text)",
    )
    parser.add_argument(
        "--output", metavar="FILE", help="write to FILE instead of stdout"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list the available transcript languages and exit",
    )
    return parser


def _fail(message: str, exit_code: int) -> int:
    """Print an error to stderr and return the exit code."""
    print(f"error: {message}", file=sys.stderr)
    if exit_code == EXIT_BLOCKED:
        print(BLOCKED_HELP, file=sys.stderr)
    return exit_code


def _fetch_with_fallback(video_id: str, languages: list[str]) -> Transcript:
    """Fetch a transcript, trying yt-dlp only when the request was blocked."""
    try:
        return fetch_snippets(video_id, languages)
    except BlockedError:
        if not ytdlp_available():
            raise
        return fetch_snippets_ytdlp(video_id, languages)


def _run(args: argparse.Namespace) -> int:
    try:
        video_id = extract_video_id(args.video)
    except ValueError as error:
        return _fail(f"{error}; {ACCEPTED_FORMS}", EXIT_INVALID_INPUT)

    if args.list:
        output = "".join(f"{line}\n" for line in available_languages(video_id))
    else:
        transcript = _fetch_with_fallback(video_id, args.lang)
        if not any(snippet.text.strip() for snippet in transcript.snippets):
            return _fail(
                f"the transcript for video {video_id} is empty", EXIT_NO_CAPTIONS
            )
        output = format_transcript(transcript, args.format, args.timestamps)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the command line interface and return the process exit code."""
    args = _build_parser().parse_args(argv)
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")
    try:
        return _run(args)
    except TranscriptError as error:
        return _fail(str(error), error.exit_code)
    except OSError as error:
        return _fail(f"{error.strerror or error}: {error.filename}", EXIT_OTHER)
    except Exception as error:  # noqa: BLE001 - last resort: no tracebacks for agents
        return _fail(f"{type(error).__name__}: {error}", EXIT_OTHER)


if __name__ == "__main__":
    sys.exit(main())
