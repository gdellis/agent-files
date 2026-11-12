"""Unit tests for get_transcript.py. No test touches the network."""

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import get_transcript as gt
import pytest
import youtube_transcript_api as yta

ID = "dQw4w9WgXcQ"
HYPHEN_ID = "-abcdefghij"


@pytest.mark.parametrize(
    "value",
    [
        ID,
        f"https://www.youtube.com/watch?v={ID}",
        f"https://youtube.com/watch?feature=share&v={ID}&t=42s",
        f"https://m.youtube.com/watch?v={ID}",
        f"https://music.youtube.com/watch?v={ID}",
        f"https://youtu.be/{ID}?si=abc123",
        f"https://www.youtube.com/shorts/{ID}",
        f"https://www.youtube.com/embed/{ID}",
        f"https://www.youtube.com/live/{ID}?feature=share",
        f"http://youtu.be/{ID}",
        f"youtu.be/{ID}",
        f"www.youtube.com/watch?v={ID}",
        f"  https://youtu.be/{ID}\n",
    ],
)
def test_extract_video_id_accepts(value):
    assert gt.extract_video_id(value) == ID


def test_extract_video_id_accepts_leading_hyphen_id():
    assert gt.extract_video_id(HYPHEN_ID) == HYPHEN_ID


@pytest.mark.parametrize(
    "value",
    [
        "",
        "not a url",
        "dQw4w9WgXc",  # 10 characters
        "dQw4w9WgXcQQ",  # 12 characters
        "https://vimeo.com/123456789",
        "https://www.youtube.com/watch?list=PL123",
        "https://www.youtube.com/watch?v=short",
        "https://www.youtube.com/playlist?list=PL123",
        f"https://evil.example/watch?v={ID}",
    ],
)
def test_extract_video_id_rejects(value):
    with pytest.raises(ValueError, match="YouTube"):
        gt.extract_video_id(value)


def make(snips, **overrides):
    fields = {
        "video_id": ID,
        "language_code": "en",
        "is_generated": False,
        "source": "youtube-transcript-api",
    }
    fields.update(overrides)
    return gt.Transcript(snippets=[gt.Snippet(*s) for s in snips], **fields)


def test_format_text_one_line_per_snippet_whitespace_collapsed():
    t = make(
        [("Hello\nthere", 0.0, 1.5), ("  how   are you ", 1.5, 2.0), ("   ", 3.5, 1.0)]
    )
    assert gt.format_transcript(t, "text", False) == "Hello there\nhow are you\n"


def test_format_text_timestamps():
    t = make([("a", 5.0, 1.0), ("b", 125.9, 1.0), ("c", 3725.0, 1.0)])
    assert gt.format_transcript(t, "text", True) == (
        "[00:05] a\n[02:05] b\n[1:02:05] c\n"
    )


def test_format_json_shape():
    t = make([("Hello", 0.0, 1.5)], is_generated=None, source="yt-dlp")
    assert json.loads(gt.format_transcript(t, "json", False)) == {
        "video_id": ID,
        "language_code": "en",
        "is_generated": None,
        "source": "yt-dlp",
        "snippets": [{"text": "Hello", "start": 0.0, "duration": 1.5}],
    }


def test_format_json_keeps_non_ascii():
    assert "héllo" in gt.format_transcript(make([("héllo", 0.0, 1.0)]), "json", False)


def test_format_rejects_unknown_format():
    with pytest.raises(ValueError, match="xml"):
        gt.format_transcript(make([]), "xml", False)


VARGS = {"VideoUnplayable": (ID, "reason", [])}


def library_error(name):
    return getattr(yta, name)(*VARGS.get(name, (ID,)))


class FakeLibraryTranscript:
    def __init__(self, code, language, is_generated, fetch_raises=None):
        self.language_code = code
        self.language = language
        self.is_generated = is_generated
        self._fetch_raises = fetch_raises

    def fetch(self):
        if self._fetch_raises:
            raise library_error(self._fetch_raises)
        return [SimpleNamespace(text="hi", start=0.0, duration=1.0)]


class FakeTranscriptList:
    """Mirrors the real lookup order: manual first, then generated."""

    def __init__(self, transcripts):
        self._transcripts = transcripts

    def __iter__(self):
        return iter(self._transcripts)

    def find_transcript(self, codes):
        for generated in (False, True):
            for code in codes:
                for transcript in self._transcripts:
                    if (transcript.language_code, transcript.is_generated) == (
                        code,
                        generated,
                    ):
                        return transcript
        raise yta.NoTranscriptFound(ID, codes, self)


@pytest.fixture
def fake_api(monkeypatch):
    def install(transcripts, raises=None, fetch_raises=None):
        class FakeApi:
            def list(self, video_id):
                assert video_id == ID
                if raises:
                    raise library_error(raises)
                return FakeTranscriptList(
                    [
                        FakeLibraryTranscript(*entry, fetch_raises=fetch_raises)
                        for entry in transcripts
                    ]
                )

        monkeypatch.setattr(gt, "YouTubeTranscriptApi", FakeApi)

    return install


def test_fetch_prefers_manual_over_generated(fake_api):
    fake_api([("en", "English", True), ("en", "English", False)])
    t = gt.fetch_snippets(ID, ["en"])
    assert (t.is_generated, t.source) == (False, "youtube-transcript-api")
    assert (t.video_id, t.language_code) == (ID, "en")
    assert t.snippets == [gt.Snippet("hi", 0.0, 1.0)]


def test_fetch_respects_language_priority(fake_api):
    fake_api([("en", "English", False), ("de", "German", False)])
    assert gt.fetch_snippets(ID, ["de", "en"]).language_code == "de"


def test_fetch_falls_back_to_regional_variant(fake_api):
    fake_api([("en-US", "English (United States)", False)])
    assert gt.fetch_snippets(ID, ["en"]).language_code == "en-US"


def test_fetch_no_match_lists_available(fake_api):
    fake_api([("de", "German", False), ("fr", "French", True)])
    with pytest.raises(gt.TranscriptError) as exc:
        gt.fetch_snippets(ID, ["en"])
    assert exc.value.exit_code == 3
    assert "de" in str(exc.value)
    assert "fr" in str(exc.value)
    assert "\n" not in str(exc.value)


def test_fetch_no_transcripts_at_all(fake_api):
    fake_api([])
    with pytest.raises(gt.TranscriptError) as exc:
        gt.fetch_snippets(ID, ["en"])
    assert exc.value.exit_code == 3


@pytest.mark.parametrize(
    ("error", "code", "cls"),
    [
        ("TranscriptsDisabled", 3, gt.TranscriptError),
        ("VideoUnavailable", 4, gt.TranscriptError),
        ("VideoUnplayable", 4, gt.TranscriptError),
        ("AgeRestricted", 4, gt.TranscriptError),
        ("InvalidVideoId", 2, gt.TranscriptError),
        ("RequestBlocked", 5, gt.BlockedError),
        ("IpBlocked", 5, gt.BlockedError),
        ("PoTokenRequired", 5, gt.BlockedError),
        ("YouTubeDataUnparsable", 1, gt.TranscriptError),
    ],
)
def test_fetch_maps_library_errors(fake_api, error, code, cls):
    fake_api([], raises=error)
    with pytest.raises(cls) as exc:
        gt.fetch_snippets(ID, ["en"])
    assert exc.value.exit_code == code
    assert "\n" not in str(exc.value)


def test_fetch_error_during_snippet_download_is_mapped(fake_api):
    fake_api([("en", "English", False)], fetch_raises="IpBlocked")
    with pytest.raises(gt.BlockedError):
        gt.fetch_snippets(ID, ["en"])


def test_available_languages(fake_api):
    fake_api([("en", "English", False), ("de", "German", True)])
    assert gt.available_languages(ID) == [
        "en\tEnglish\tmanual",
        "de\tGerman\tgenerated",
    ]


def test_available_languages_maps_library_errors(fake_api):
    fake_api([], raises="IpBlocked")
    with pytest.raises(gt.BlockedError):
        gt.available_languages(ID)


SAMPLE = json.dumps(
    {
        "events": [
            {
                "tStartMs": 0,
                "dDurationMs": 1500,
                "segs": [{"utf8": "Hello "}, {"utf8": "there"}],
            },
            {"tStartMs": 1500, "dDurationMs": 10},
            {"tStartMs": 1500, "dDurationMs": 900, "segs": [{"utf8": "\n"}]},
            {"tStartMs": 2400, "dDurationMs": 800, "segs": [{"utf8": "Hello there"}]},
            {"tStartMs": 3200, "dDurationMs": 700, "segs": [{"utf8": "bye"}]},
        ]
    }
)


@pytest.fixture
def fake_ytdlp(monkeypatch):
    def install(files=None, returncode=0, stderr="", raises=None):
        calls = []

        def run(argv, **kwargs):
            calls.append(argv)
            assert kwargs["timeout"] == 120
            if raises:
                raise raises
            out_dir = Path(argv[argv.index("-o") + 1]).parent
            for name, content in (files or {}).items():
                (out_dir / name).write_text(content, encoding="utf-8")
            return subprocess.CompletedProcess(argv, returncode, "", stderr)

        monkeypatch.setattr(gt.subprocess, "run", run)
        return calls

    return install


def test_ytdlp_converts_json3(fake_ytdlp):
    fake_ytdlp(files={f"{ID}.en.json3": SAMPLE})
    t = gt.fetch_snippets_ytdlp(ID, ["en"])
    assert (t.source, t.is_generated, t.language_code) == ("yt-dlp", None, "en")
    assert t.video_id == ID
    assert t.snippets == [
        gt.Snippet("Hello there", 0.0, 1.5),
        gt.Snippet("bye", 3.2, 0.7),
    ]


def test_ytdlp_picks_by_language_priority(fake_ytdlp):
    fake_ytdlp(files={f"{ID}.en.json3": SAMPLE, f"{ID}.de.json3": SAMPLE})
    assert gt.fetch_snippets_ytdlp(ID, ["de", "en"]).language_code == "de"


def test_ytdlp_prefers_exact_code_over_regional(fake_ytdlp):
    fake_ytdlp(files={f"{ID}.en-US.json3": SAMPLE, f"{ID}.en.json3": SAMPLE})
    assert gt.fetch_snippets_ytdlp(ID, ["en"]).language_code == "en"


def test_ytdlp_matches_regional_file(fake_ytdlp):
    fake_ytdlp(files={f"{ID}.en-US.json3": SAMPLE})
    assert gt.fetch_snippets_ytdlp(ID, ["en"]).language_code == "en-US"


def test_ytdlp_requests_subtitles_only(fake_ytdlp):
    calls = fake_ytdlp(files={f"{ID}.en.json3": SAMPLE})
    gt.fetch_snippets_ytdlp(ID, ["de", "en"])
    argv = calls[0]
    assert argv[0] == "yt-dlp"
    assert "--skip-download" in argv
    assert argv[argv.index("--sub-langs") + 1] == "de.*,en.*"
    assert argv[argv.index("--sub-format") + 1] == "json3"


def test_ytdlp_passes_id_after_double_dash(fake_ytdlp):
    calls = fake_ytdlp(files={f"{HYPHEN_ID}.en.json3": SAMPLE})
    gt.fetch_snippets_ytdlp(HYPHEN_ID, ["en"])
    argv = calls[0]
    assert argv[argv.index("--") + 1].endswith(f"watch?v={HYPHEN_ID}")


def test_ytdlp_nonzero_exit_reports_last_stderr_line(fake_ytdlp):
    fake_ytdlp(returncode=1, stderr="WARNING: x\nERROR: Sign in to confirm\n\n")
    with pytest.raises(gt.BlockedError, match="Sign in to confirm"):
        gt.fetch_snippets_ytdlp(ID, ["en"])


@pytest.mark.parametrize(
    "kwargs",
    [
        {"files": {}, "returncode": 0},
        {"files": {f"{ID}.en.json3": "not json"}},
        {"files": {f"{ID}.en.json3": "[]"}},
        {"raises": subprocess.TimeoutExpired("yt-dlp", 120)},
        {"raises": FileNotFoundError()},
    ],
)
def test_ytdlp_failures_are_blocked_errors(fake_ytdlp, kwargs):
    fake_ytdlp(**kwargs)
    with pytest.raises(gt.BlockedError) as exc:
        gt.fetch_snippets_ytdlp(ID, ["en"])
    assert exc.value.exit_code == 5


def test_ytdlp_available_reflects_path(monkeypatch):
    monkeypatch.setattr(gt.shutil, "which", lambda name: None)
    assert gt.ytdlp_available() is False
    monkeypatch.setattr(gt.shutil, "which", lambda name: f"/usr/bin/{name}")
    assert gt.ytdlp_available() is True
