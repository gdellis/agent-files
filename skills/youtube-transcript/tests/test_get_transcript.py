"""Unit tests for get_transcript.py. No test touches the network."""

import http.server
import io
import json
import sys
import threading
from types import SimpleNamespace
from typing import ClassVar

import get_transcript as gt
import pytest
import requests
import youtube_transcript_api as yta
import yt_dlp

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
    if isinstance(name, Exception):
        return name
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
    """The real list is iterable; selection is done by the code under test."""

    def __init__(self, transcripts):
        self._transcripts = transcripts

    def __iter__(self):
        return iter(self._transcripts)


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


def test_fetch_language_priority_beats_manual_preference(fake_api):
    fake_api([("de", "German", True), ("en", "English", False)])
    t = gt.fetch_snippets(ID, ["de", "en"])
    assert (t.language_code, t.is_generated) == ("de", True)


def test_fetch_regional_variant_of_first_language_beats_second_language(fake_api):
    fake_api([("de", "German", False), ("en-US", "English (United States)", False)])
    assert gt.fetch_snippets(ID, ["en", "de"]).language_code == "en-US"


def test_fetch_regional_prefers_manual(fake_api):
    fake_api([("en-GB", "English (UK)", True), ("en-US", "English (US)", False)])
    t = gt.fetch_snippets(ID, ["en"])
    assert (t.language_code, t.is_generated) == ("en-US", False)


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


class _CaptionHandler(http.server.BaseHTTPRequestHandler):
    BODIES: ClassVar[dict[str, str]] = {
        "/sample": SAMPLE,
        "/not-json": "not json",
        "/list": "[]",
    }

    def do_GET(self):
        body = self.BODIES.get(self.path)
        if body is None:
            self.send_response(429)
            self.end_headers()
            return
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def caption_server():
    """A loopback server standing in for YouTube's caption endpoint."""
    server = http.server.HTTPServer(("127.0.0.1", 0), _CaptionHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture
def ytdlp(monkeypatch, caption_server):
    """Real yt-dlp with only the YouTube extraction step replaced.

    ``subtitles`` and ``automatic_captions`` map a language code to a path on
    the caption server. The caption download itself is yt-dlp's real code.
    """

    def tracks(mapping):
        return {
            code: [
                {"ext": "vtt", "url": f"{caption_server}/vtt"},
                *(
                    []
                    if path is None
                    else [
                        {
                            "ext": "json3",
                            "url": f"{caption_server}{path}",
                            "impersonate": True,
                        }
                    ]
                ),
            ]
            for code, path in mapping.items()
        }

    def install(subtitles=None, automatic_captions=None, raises=None):
        calls = []

        def extract_info(self, url, download=True):
            calls.append((url, download))
            if raises:
                raise raises
            return {
                "id": ID,
                "subtitles": tracks(subtitles or {}),
                "automatic_captions": tracks(automatic_captions or {}),
            }

        monkeypatch.setattr(yt_dlp.YoutubeDL, "extract_info", extract_info)
        return calls

    return install


def test_ytdlp_converts_manual_json3(ytdlp):
    calls = ytdlp(subtitles={"en": "/sample"})
    t = gt.fetch_snippets_ytdlp(ID, ["en"])
    assert (t.source, t.is_generated, t.language_code) == ("yt-dlp", False, "en")
    assert t.video_id == ID
    assert t.snippets == [
        gt.Snippet("Hello there", 0.0, 1.5),
        gt.Snippet("bye", 3.2, 0.7),
    ]
    assert calls == [(f"https://www.youtube.com/watch?v={ID}", False)]


def test_ytdlp_picks_by_language_priority(ytdlp):
    ytdlp(subtitles={"en": "/sample", "de": "/sample"})
    assert gt.fetch_snippets_ytdlp(ID, ["de", "en"]).language_code == "de"


def test_ytdlp_prefers_exact_code_over_regional(ytdlp):
    ytdlp(subtitles={"en-US": "/sample", "en": "/sample"})
    assert gt.fetch_snippets_ytdlp(ID, ["en"]).language_code == "en"


def test_ytdlp_matches_regional_track(ytdlp):
    ytdlp(subtitles={"en-US": "/sample"})
    assert gt.fetch_snippets_ytdlp(ID, ["en"]).language_code == "en-US"


def test_ytdlp_prefers_manual_over_original_auto_captions(ytdlp):
    ytdlp(subtitles={"en": "/sample"}, automatic_captions={"en-orig": "/sample"})
    assert gt.fetch_snippets_ytdlp(ID, ["en"]).is_generated is False


def test_ytdlp_falls_back_to_original_auto_captions(ytdlp):
    ytdlp(automatic_captions={"en-orig": "/sample", "en": "/sample"})
    t = gt.fetch_snippets_ytdlp(ID, ["de", "en"])
    assert (t.language_code, t.is_generated) == ("en", True)


def test_ytdlp_never_returns_machine_translated_captions(ytdlp):
    # A German-only video: yt-dlp lists "en" and "en-de" as auto-translations.
    ytdlp(
        subtitles={"de": "/sample"},
        automatic_captions={"en": "/sample", "en-de": "/sample"},
    )
    with pytest.raises(gt.TranscriptError) as exc:
        gt.fetch_snippets_ytdlp(ID, ["en"])
    assert exc.value.exit_code == 3


def test_ytdlp_no_captions_is_exit_3_not_blocked(ytdlp):
    ytdlp()
    with pytest.raises(gt.TranscriptError) as exc:
        gt.fetch_snippets_ytdlp(ID, ["en", "de"])
    assert exc.value.exit_code == 3
    assert not isinstance(exc.value, gt.BlockedError)
    assert "en, de" in str(exc.value)


def test_ytdlp_ignores_live_chat_and_tracks_without_json3(ytdlp):
    ytdlp(subtitles={"live_chat": "/sample", "en": None})
    with pytest.raises(gt.TranscriptError) as exc:
        gt.fetch_snippets_ytdlp(ID, ["live_chat", "en"])
    assert exc.value.exit_code == 3


def test_ytdlp_extraction_failure_is_blocked_with_reason(ytdlp, capsys):
    ytdlp(
        raises=yt_dlp.utils.DownloadError(
            "ERROR: [youtube] dQw4w9WgXcQ: Sign in to confirm you\u2019re not a bot"
        )
    )
    with pytest.raises(gt.BlockedError) as exc:
        gt.fetch_snippets_ytdlp(ID, ["en"])
    assert str(exc.value).startswith("yt-dlp failed: [youtube]")
    assert "Sign in to confirm" in str(exc.value)
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("path", ["/rate-limited", "/not-json", "/list"])
def test_ytdlp_bad_caption_download_is_blocked(ytdlp, capsys, path):
    ytdlp(subtitles={"en": path})
    with pytest.raises(gt.BlockedError) as exc:
        gt.fetch_snippets_ytdlp(ID, ["en"])
    assert exc.value.exit_code == 5
    assert "\n" not in str(exc.value)
    assert capsys.readouterr().err == ""


def test_ytdlp_not_installed_is_blocked(monkeypatch):
    monkeypatch.setitem(sys.modules, "yt_dlp", None)
    with pytest.raises(gt.BlockedError, match="not installed"):
        gt.fetch_snippets_ytdlp(ID, ["en"])


def test_ytdlp_available_reflects_installed_package(monkeypatch):
    assert gt.ytdlp_available() is True
    monkeypatch.setattr(gt.importlib.util, "find_spec", lambda name: None)
    assert gt.ytdlp_available() is False


@pytest.fixture
def patched(monkeypatch):
    """Replace the network-facing functions that ``main`` orchestrates."""

    def install(fetch=None, ytdlp=None, languages=None, ytdlp_installed=False):
        calls = SimpleNamespace(fetch=[], ytdlp=[], languages=[])

        def respond(log, outcome):
            def call(*args):
                log.append(args)
                if isinstance(outcome, Exception):
                    raise outcome
                return outcome

            return call

        monkeypatch.setattr(gt, "fetch_snippets", respond(calls.fetch, fetch))
        monkeypatch.setattr(gt, "fetch_snippets_ytdlp", respond(calls.ytdlp, ytdlp))
        monkeypatch.setattr(
            gt, "available_languages", respond(calls.languages, languages)
        )
        monkeypatch.setattr(gt, "ytdlp_available", lambda: ytdlp_installed)
        return calls

    return install


def test_main_prints_text(patched, capsys):
    patched(fetch=make([("hi", 0.0, 1.0)]))
    assert gt.main([f"https://youtu.be/{ID}"]) == 0
    assert capsys.readouterr() == ("hi\n", "")


def test_main_passes_languages_and_flags(patched, capsys):
    calls = patched(fetch=make([("hi", 65.0, 1.0)]))
    assert gt.main([ID, "--lang", "de", "en", "--timestamps"]) == 0
    assert calls.fetch == [(ID, ["de", "en"])]
    assert capsys.readouterr().out == "[01:05] hi\n"


def test_main_defaults_to_english(patched):
    calls = patched(fetch=make([("hi", 0.0, 1.0)]))
    gt.main([ID])
    assert calls.fetch == [(ID, ["en"])]


def test_main_json(patched, capsys):
    patched(fetch=make([("hi", 0.0, 1.0)]))
    assert gt.main([ID, "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["video_id"] == ID


def test_main_output_file(patched, capsys, tmp_path):
    patched(fetch=make([("héllo", 0.0, 1.0)]))
    target = tmp_path / "t.txt"
    assert gt.main([ID, "--output", str(target)]) == 0
    assert target.read_text(encoding="utf-8") == "héllo\n"
    assert capsys.readouterr().out == ""


def test_main_output_unwritable(patched, capsys, tmp_path):
    patched(fetch=make([("hi", 0.0, 1.0)]))
    assert gt.main([ID, "--output", str(tmp_path / "missing" / "t.txt")]) == 1
    err = capsys.readouterr().err
    assert err.startswith("error:")
    assert "Traceback" not in err


def test_main_list(patched, capsys):
    calls = patched(languages=["en\tEnglish\tmanual"])
    assert gt.main([ID, "--list"]) == 0
    assert capsys.readouterr().out == "en\tEnglish\tmanual\n"
    assert calls.fetch == []


def test_main_list_blocked_does_not_fall_back(patched):
    calls = patched(languages=gt.BlockedError("blocked"), ytdlp_installed=True)
    assert gt.main([ID, "--list"]) == 5
    assert calls.ytdlp == []


def test_main_invalid_input(patched, capsys):
    calls = patched()
    assert gt.main(["https://vimeo.com/1"]) == 2
    err = capsys.readouterr().err
    assert "https://vimeo.com/1" in err
    assert "youtu.be/ID" in err
    assert calls.fetch == []


def test_main_leading_hyphen_id(patched):
    calls = patched(fetch=make([("hi", 0.0, 1.0)]))
    assert gt.main(["--", HYPHEN_ID]) == 0
    assert calls.fetch[0][0] == HYPHEN_ID


@pytest.mark.parametrize("code", [1, 3, 4])
def test_main_error_codes_do_not_fall_back(patched, capsys, code):
    calls = patched(fetch=gt.TranscriptError("nope", code), ytdlp_installed=True)
    assert gt.main([ID]) == code
    assert calls.ytdlp == []
    out, err = capsys.readouterr()
    assert out == ""
    assert "error: nope" in err


def test_main_blocked_falls_back_to_ytdlp(patched, capsys):
    calls = patched(
        fetch=gt.BlockedError("blocked"),
        ytdlp_installed=True,
        ytdlp=make([("hi", 0.0, 1.0)], source="yt-dlp", is_generated=None),
    )
    assert gt.main([ID, "--lang", "de"]) == 0
    assert calls.ytdlp == [(ID, ["de"])]
    assert capsys.readouterr().out == "hi\n"


def test_main_blocked_without_ytdlp(patched, capsys):
    calls = patched(fetch=gt.BlockedError("blocked"), ytdlp_installed=False)
    assert gt.main([ID]) == 5
    assert calls.ytdlp == []
    err = capsys.readouterr().err
    assert "error: blocked" in err
    assert "SKILL.md" in err


def test_main_blocked_and_fallback_fails(patched, capsys):
    patched(
        fetch=gt.BlockedError("blocked"),
        ytdlp_installed=True,
        ytdlp=gt.BlockedError("yt-dlp failed"),
    )
    assert gt.main([ID]) == 5
    err = capsys.readouterr().err
    assert "yt-dlp failed" in err
    assert "SKILL.md" in err


def test_main_empty_transcript_is_exit_3(patched, capsys):
    patched(fetch=make([("  ", 0.0, 1.0)]))
    assert gt.main([ID]) == 3
    out, err = capsys.readouterr()
    assert out == ""
    assert err.startswith("error:")


def test_main_unexpected_exception_is_exit_1_without_traceback(patched, capsys):
    patched(fetch=RuntimeError("connection reset"))
    assert gt.main([ID]) == 1
    err = capsys.readouterr().err
    assert "connection reset" in err
    assert "Traceback" not in err


def test_main_survives_non_utf8_stdout(patched, monkeypatch):
    patched(fetch=make([("日本語", 0.0, 1.0)]))
    buffer = io.BytesIO()
    monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(buffer, encoding="ascii"))
    assert gt.main([ID]) == 0
    sys.stdout.flush()
    assert "日本語".encode() in buffer.getvalue()


def test_fetch_network_failure_is_one_clean_line(fake_api):
    fake_api([], raises=requests.exceptions.ProxyError("Tunnel connection failed"))
    with pytest.raises(gt.TranscriptError) as exc:
        gt.fetch_snippets(ID, ["en"])
    assert exc.value.exit_code == 1
    assert not isinstance(exc.value, gt.BlockedError)
    assert str(exc.value) == (
        "could not reach YouTube (ProxyError): Tunnel connection failed"
    )


def test_main_output_unwritable_names_the_path(patched, capsys, tmp_path):
    patched(fetch=make([("hi", 0.0, 1.0)]))
    target = tmp_path / "missing" / "t.txt"
    assert gt.main([ID, "--output", str(target)]) == 1
    err = capsys.readouterr().err
    assert err.startswith(f"error: cannot write {target}:")
    assert "None" not in err


def test_main_fallback_reporting_no_captions_is_exit_3(patched, capsys):
    patched(
        fetch=gt.BlockedError("blocked"),
        ytdlp_installed=True,
        ytdlp=gt.TranscriptError("no captions in: en", 3),
    )
    assert gt.main([ID]) == 3
    assert "SKILL.md" not in capsys.readouterr().err


def test_ytdlp_failure_reason_drops_bug_report_boilerplate(ytdlp):
    ytdlp(
        raises=yt_dlp.utils.DownloadError(
            "ERROR: [youtube] x: Unable to download API page; please report this "
            "issue on https://github.com/yt-dlp/yt-dlp/issues?q= , filling out..."
        )
    )
    with pytest.raises(gt.BlockedError) as exc:
        gt.fetch_snippets_ytdlp(ID, ["en"])
    assert str(exc.value) == "yt-dlp failed: [youtube] x: Unable to download API page"
