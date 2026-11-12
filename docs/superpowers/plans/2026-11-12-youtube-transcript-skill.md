# YouTube Transcript Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** An Agent Skill that turns one YouTube URL into clean transcript text
on stdout, or a clear reason why it could not.

**Architecture:** A `SKILL.md` tells the agent to run one Python script. The
script parses the URL, fetches snippets with `youtube-transcript-api`, falls
back to the `yt-dlp` executable when YouTube blocks the request, and formats
the result. All logic lives in one file with separately testable functions.

**Tech Stack:** Python 3.10+, `youtube-transcript-api` 1.2.x, optional
`yt-dlp` executable, `uv` for running, `pytest` and `ruff` for checks.

**Spec:** `docs/superpowers/specs/2026-11-12-youtube-transcript-skill-design.md`

## Global Constraints

- Work on branch `ccr-e659fd08-rkvfn2`; draft PR #5 is already open. Never
  commit to `main`.
- Script: `skills/youtube-transcript/scripts/get_transcript.py`. Tests:
  `skills/youtube-transcript/tests/test_get_transcript.py`.
- The script starts with inline metadata (PEP 723):
  `requires-python = ">=3.10"`,
  `dependencies = ["youtube-transcript-api>=1.2,<2"]`.
- Tests never touch the network. Mock `YouTubeTranscriptApi` and
  `subprocess.run`.
- Test command, referred to below as **TEST**:
  `uv run --with pytest --with "youtube-transcript-api>=1.2,<2" pytest skills/youtube-transcript/tests -v`
- Lint command, referred to below as **LINT**:
  `ruff check skills/ && ruff format --check skills/ && npx markdownlint-cli2 "**/*.md"`
- Follow `rules/python.md`: type hints on every signature, 88-character lines,
  docstrings on public functions.
- Transcript text goes to stdout or the `--output` file. Everything else goes
  to stderr.
- Exit codes: 0 success, 1 other failure, 2 invalid URL or ID, 3 no captions,
  4 video unavailable, 5 blocked.
- Commit messages use conventional commits, for example
  `feat(skills): add video ID extraction`.

## Review Focus

Inputs the spec implies but does not spell out. Each has a test in the task
named.

1. **Requested `en`, only `en-US` or `en-GB` exists.** Expect the regional
   transcript, not exit 3. Task 3.
2. **URL pasted without a scheme or with stray whitespace**, such as
   `" youtu.be/dQw4w9WgXcQ\n"`. Expect it to be accepted. Task 1.
3. **Video ID that starts with a hyphen**, such as `-abcdefghij`. Expect
   `get_transcript.py -- -abcdefghij` to work and `SKILL.md` to say so.
   Task 5.
4. **Non-ASCII transcript on a terminal that is not UTF-8.** Expect output, not
   a `UnicodeEncodeError`. Task 5.
5. **`--output` path that cannot be written**, such as a missing parent
   directory. Expect exit 1 and a one-line message, not a traceback. Task 5.

## File Structure

| File | Responsibility |
| --- | --- |
| `skills/youtube-transcript/SKILL.md` | When to use the skill, the command, how to react to each exit code |
| `skills/youtube-transcript/scripts/get_transcript.py` | All logic and the CLI |
| `skills/youtube-transcript/tests/conftest.py` | Puts `scripts/` on `sys.path` so tests can `import get_transcript` |
| `skills/youtube-transcript/tests/test_get_transcript.py` | Unit tests |
| `README.md`, `AGENTS.md` | Document the new `skills/` directory |
| `.github/workflows/lint.yml` | New job running ruff and pytest |

---

### Task 1: Scaffold and `extract_video_id`

**Files:**

- Create: `skills/youtube-transcript/scripts/get_transcript.py`
- Create: `skills/youtube-transcript/tests/conftest.py`
- Create: `skills/youtube-transcript/tests/test_get_transcript.py`

**Interfaces:**

- Produces: `extract_video_id(value: str) -> str`. Raises `ValueError` whose
  message contains the rejected input.

- [ ] **Step 1: Create `conftest.py`** that inserts
  `Path(__file__).parent.parent / "scripts"` at the front of `sys.path`.

- [ ] **Step 2: Write the failing tests**

```python
import pytest
import get_transcript as gt

ID = "dQw4w9WgXcQ"

@pytest.mark.parametrize("value", [
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
    "-abcdefghij",
])
def test_extract_video_id_accepts(value):
    expected = "-abcdefghij" if value == "-abcdefghij" else ID
    assert gt.extract_video_id(value) == expected

@pytest.mark.parametrize("value", [
    "",
    "not a url",
    "dQw4w9WgXc",                               # 10 characters
    "dQw4w9WgXcQQ",                             # 12 characters
    "https://vimeo.com/123456789",
    "https://www.youtube.com/watch?list=PL123",
    "https://www.youtube.com/watch?v=short",
    "https://www.youtube.com/playlist?list=PL123",
    f"https://evil.example/watch?v={ID}",
])
def test_extract_video_id_rejects(value):
    with pytest.raises(ValueError):
        gt.extract_video_id(value)
```

- [ ] **Step 3: Run TEST.** Expected: FAIL, `get_transcript` has no
  `extract_video_id`.

- [ ] **Step 4: Implement `extract_video_id`** in `get_transcript.py`, below
  the PEP 723 header and a module docstring.

  Decisions: strip whitespace; a bare ID matches `[A-Za-z0-9_-]{11}` exactly;
  otherwise prepend `https://` when there is no scheme and parse with
  `urllib.parse`. Allowed hosts are `youtube.com`, `youtu.be` and
  `youtube-nocookie.com`, each optionally prefixed by `www.`, `m.` or
  `music.`. Path prefixes carrying the ID are `/shorts/`, `/embed/`, `/live/`
  and `/v/`.

- [ ] **Step 5: Run TEST.** Expected: all pass.

- [ ] **Step 6: Run `ruff check skills/ && ruff format --check skills/`**, fix
  anything reported, then commit.

---

### Task 2: Data types and `format_transcript`

**Files:**

- Modify: `skills/youtube-transcript/scripts/get_transcript.py`
- Modify: `skills/youtube-transcript/tests/test_get_transcript.py`

**Interfaces:**

- Produces:

```python
@dataclass(frozen=True)
class Snippet:
    text: str
    start: float      # seconds
    duration: float   # seconds

@dataclass(frozen=True)
class Transcript:
    video_id: str
    language_code: str
    is_generated: bool | None   # None when the source cannot tell
    source: str                 # "youtube-transcript-api" or "yt-dlp"
    snippets: list[Snippet]

def format_transcript(transcript: Transcript, fmt: str, timestamps: bool) -> str
```

- [ ] **Step 1: Write the failing tests**

```python
def make(snips, **kw):
    base = dict(video_id=ID, language_code="en", is_generated=False,
                source="youtube-transcript-api")
    return gt.Transcript(snippets=[gt.Snippet(*s) for s in snips], **{**base, **kw})

def test_format_text_one_line_per_snippet_whitespace_collapsed():
    t = make([("Hello\nthere", 0.0, 1.5), ("  how   are you ", 1.5, 2.0),
              ("   ", 3.5, 1.0)])
    assert gt.format_transcript(t, "text", False) == "Hello there\nhow are you\n"

def test_format_text_timestamps():
    t = make([("a", 5.0, 1.0), ("b", 125.9, 1.0), ("c", 3725.0, 1.0)])
    assert gt.format_transcript(t, "text", True) == (
        "[00:05] a\n[02:05] b\n[1:02:05] c\n")

def test_format_json_shape():
    t = make([("Hello", 0.0, 1.5)], is_generated=None, source="yt-dlp")
    assert json.loads(gt.format_transcript(t, "json", False)) == {
        "video_id": ID, "language_code": "en", "is_generated": None,
        "source": "yt-dlp",
        "snippets": [{"text": "Hello", "start": 0.0, "duration": 1.5}],
    }

def test_format_json_keeps_non_ascii():
    assert "héllo" in gt.format_transcript(make([("héllo", 0.0, 1.0)]), "json", False)

def test_format_rejects_unknown_format():
    with pytest.raises(ValueError):
        gt.format_transcript(make([]), "xml", False)
```

- [ ] **Step 2: Run TEST.** Expected: the new tests fail.

- [ ] **Step 3: Implement the dataclasses and `format_transcript`.**

  Decisions: text output ends with one newline; snippets that are empty after
  collapsing whitespace are dropped in text output only; times truncate to
  whole seconds; JSON uses `ensure_ascii=False`, `indent=2`, and ignores
  `timestamps`.

- [ ] **Step 4: Run TEST.** Expected: all pass.

- [ ] **Step 5: Lint with ruff and commit.**

---

### Task 3: `fetch_snippets`, `available_languages` and error mapping

**Files:**

- Modify: `skills/youtube-transcript/scripts/get_transcript.py`
- Modify: `skills/youtube-transcript/tests/test_get_transcript.py`

**Interfaces:**

- Consumes: `Snippet`, `Transcript` from Task 2.
- Produces:

```python
class TranscriptError(Exception):
    exit_code: int                 # set by __init__(message, exit_code)

class BlockedError(TranscriptError):   # exit_code is always 5
    ...

def fetch_snippets(video_id: str, languages: list[str]) -> Transcript
def available_languages(video_id: str) -> list[str]
```

  `available_languages` returns one string per transcript, formatted
  `"{code}\t{language name}\t{manual|generated}"`. Both functions raise only
  `TranscriptError` or its subclass for library failures.

**Library facts (version 1.2.5):**

- `YouTubeTranscriptApi().list(video_id)` returns a `TranscriptList`. Iterating
  it yields objects with `language`, `language_code`, `is_generated` and
  `fetch()`.
- `TranscriptList.find_transcript(codes)` already prefers manual over
  generated across the given codes, and raises `NoTranscriptFound`.
- `fetch()` returns an iterable of snippets with `text`, `start`, `duration`.
- Exceptions come from `youtube_transcript_api._errors`. `IpBlocked` is a
  subclass of `RequestBlocked`.

**Exception mapping:**

| Library exception | Raised as | Exit code |
| --- | --- | --- |
| `RequestBlocked`, `IpBlocked`, `PoTokenRequired` | `BlockedError` | 5 |
| `TranscriptsDisabled`, `NoTranscriptFound` | `TranscriptError` | 3 |
| `VideoUnavailable`, `VideoUnplayable`, `AgeRestricted` | `TranscriptError` | 4 |
| `InvalidVideoId` | `TranscriptError` | 2 |
| Any other `YouTubeTranscriptApiException` | `TranscriptError` | 1 |

- [ ] **Step 1: Write the failing tests.** Build a `fake_api(transcripts,
  raises=None)` helper that patches `gt.YouTubeTranscriptApi` so `.list()`
  returns a fake list. The fake list is iterable and implements
  `find_transcript` with the real precedence, raising the real
  `NoTranscriptFound`.

```python
def test_fetch_prefers_manual_over_generated(fake_api):
    fake_api([("en", "English", True), ("en", "English", False)])
    t = gt.fetch_snippets(ID, ["en"])
    assert (t.is_generated, t.source) == (False, "youtube-transcript-api")
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
    assert "de" in str(exc.value) and "fr" in str(exc.value)

@pytest.mark.parametrize("error, code, cls", [
    ("TranscriptsDisabled", 3, gt.TranscriptError),
    ("VideoUnavailable", 4, gt.TranscriptError),
    ("VideoUnplayable", 4, gt.TranscriptError),
    ("AgeRestricted", 4, gt.TranscriptError),
    ("RequestBlocked", 5, gt.BlockedError),
    ("IpBlocked", 5, gt.BlockedError),
    ("PoTokenRequired", 5, gt.BlockedError),
    ("YouTubeDataUnparsable", 1, gt.TranscriptError),
])
def test_fetch_maps_library_errors(fake_api, error, code, cls):
    fake_api([], raises=error)
    with pytest.raises(cls) as exc:
        gt.fetch_snippets(ID, ["en"])
    assert exc.value.exit_code == code

def test_fetch_error_during_snippet_download_is_mapped(fake_api):
    fake_api([("en", "English", False)], fetch_raises="IpBlocked")
    with pytest.raises(gt.BlockedError):
        gt.fetch_snippets(ID, ["en"])

def test_available_languages(fake_api):
    fake_api([("en", "English", False), ("de", "German", True)])
    assert gt.available_languages(ID) == [
        "en\tEnglish\tmanual", "de\tGerman\tgenerated"]
```

- [ ] **Step 2: Run TEST.** Expected: the new tests fail.

- [ ] **Step 3: Implement.**

  Decisions: call `find_transcript(languages)` first. On `NoTranscriptFound`,
  retry with every available code whose part before the first `-` equals a
  requested code, kept in requested order. If there is still no match, raise
  exit 3 with a message that lists the available codes, or says no
  transcripts exist. Messages are one line and do not include the library's
  multi-paragraph text. Put the mapping in one helper used by both public
  functions.

- [ ] **Step 4: Run TEST.** Expected: all pass.

- [ ] **Step 5: Lint with ruff and commit.**

---

### Task 4: `fetch_snippets_ytdlp`

**Files:**

- Modify: `skills/youtube-transcript/scripts/get_transcript.py`
- Modify: `skills/youtube-transcript/tests/test_get_transcript.py`

**Interfaces:**

- Consumes: `Snippet`, `Transcript`, `BlockedError`.
- Produces:
  `fetch_snippets_ytdlp(video_id: str, languages: list[str]) -> Transcript`,
  with `source="yt-dlp"` and `is_generated=None`. Raises `BlockedError` for
  every failure. Also `ytdlp_available() -> bool`, which is
  `shutil.which("yt-dlp") is not None`.

**Command to run**, in a `tempfile.TemporaryDirectory()`, with
`capture_output=True, text=True, timeout=120`:

```text
yt-dlp --skip-download --no-playlist --write-subs --write-auto-subs
       --sub-langs "<lang>.*,<lang>.*" --sub-format json3
       -o "<tmpdir>/%(id)s" -- https://www.youtube.com/watch?v=<video_id>
```

It writes `<video_id>.<lang>.json3`. The payload looks like:

```json
{"events": [
  {"tStartMs": 0, "dDurationMs": 1500, "segs": [{"utf8": "Hello "}, {"utf8": "there"}]},
  {"tStartMs": 1500, "dDurationMs": 10},
  {"tStartMs": 1500, "dDurationMs": 900, "segs": [{"utf8": "\n"}]},
  {"tStartMs": 2400, "dDurationMs": 800, "segs": [{"utf8": "Hello there"}]},
  {"tStartMs": 3200, "dDurationMs": 700, "segs": [{"utf8": "bye"}]}
]}
```

- [ ] **Step 1: Write the failing tests.** Patch `gt.subprocess.run` with a
  fake that writes given files into the directory taken from the `-o`
  argument and returns a given return code and stderr.

```python
def test_ytdlp_converts_json3(fake_ytdlp):
    fake_ytdlp(files={f"{ID}.en.json3": SAMPLE})     # the payload above
    t = gt.fetch_snippets_ytdlp(ID, ["en"])
    assert (t.source, t.is_generated, t.language_code) == ("yt-dlp", None, "en")
    assert t.snippets == [gt.Snippet("Hello there", 0.0, 1.5),
                          gt.Snippet("bye", 3.2, 0.7)]

def test_ytdlp_picks_by_language_priority(fake_ytdlp):
    fake_ytdlp(files={f"{ID}.en.json3": SAMPLE, f"{ID}.de.json3": SAMPLE})
    assert gt.fetch_snippets_ytdlp(ID, ["de", "en"]).language_code == "de"

def test_ytdlp_matches_regional_file(fake_ytdlp):
    fake_ytdlp(files={f"{ID}.en-US.json3": SAMPLE})
    assert gt.fetch_snippets_ytdlp(ID, ["en"]).language_code == "en-US"

def test_ytdlp_passes_id_after_double_dash(fake_ytdlp):
    calls = fake_ytdlp(files={"-abcdefghij.en.json3": SAMPLE})
    gt.fetch_snippets_ytdlp("-abcdefghij", ["en"])
    argv = calls[0]
    assert argv[argv.index("--") + 1].endswith("watch?v=-abcdefghij")

@pytest.mark.parametrize("kwargs", [
    dict(files={}, returncode=1, stderr="ERROR: Sign in to confirm"),
    dict(files={}, returncode=0),
    dict(files={f"{ID}.en.json3": "not json"}),
    dict(raises=subprocess.TimeoutExpired("yt-dlp", 120)),
    dict(raises=FileNotFoundError()),
])
def test_ytdlp_failures_are_blocked_errors(fake_ytdlp, kwargs):
    fake_ytdlp(**kwargs)
    with pytest.raises(gt.BlockedError):
        gt.fetch_snippets_ytdlp(ID, ["en"])
```

- [ ] **Step 2: Run TEST.** Expected: the new tests fail.

- [ ] **Step 3: Implement.**

  Decisions: snippet text is the event's `utf8` segments joined, with
  whitespace collapsed. Skip events with no `segs`, events whose text is
  empty, and events whose text equals the previously kept snippet's text.
  Times are milliseconds divided by 1000. Choose the file by requested
  language order, exact code before regional variant. A `BlockedError`
  message from a non-zero exit includes the last non-empty stderr line.

- [ ] **Step 4: Run TEST.** Expected: all pass.

- [ ] **Step 5: Lint with ruff and commit.**

---

### Task 5: CLI `main`, fallback rule and exit codes

**Files:**

- Modify: `skills/youtube-transcript/scripts/get_transcript.py`
- Modify: `skills/youtube-transcript/tests/test_get_transcript.py`

**Interfaces:**

- Consumes: everything from Tasks 1 to 4.
- Produces: `main(argv: list[str] | None = None) -> int`, and
  `if __name__ == "__main__": sys.exit(main())`.

**Arguments:** positional `video` (URL or ID); `--lang CODE [CODE ...]`,
default `["en"]`; `--timestamps`; `--format {text,json}`, default `text`;
`--output FILE`; `--list`.

**Messages on stderr**, each prefixed `error:`:

| Exit | Message |
| --- | --- |
| 2 | `not a YouTube video URL or ID: <input>` plus the accepted forms |
| 3, 4, 1 | the `TranscriptError` message |
| 5 | the message, then `YouTube is blocking requests from this network. Retry from another network, or pass a proxy or browser cookies; see SKILL.md.` |

- [ ] **Step 1: Write the failing tests.** Patch `gt.fetch_snippets`,
  `gt.fetch_snippets_ytdlp`, `gt.available_languages` and
  `gt.ytdlp_available` directly; use `capsys` and `tmp_path`.

```python
def test_main_prints_text(patched, capsys):
    patched(fetch=make([("hi", 0.0, 1.0)]))
    assert gt.main([f"https://youtu.be/{ID}"]) == 0
    out, err = capsys.readouterr()
    assert (out, err) == ("hi\n", "")

def test_main_passes_languages_and_flags(patched, capsys):
    calls = patched(fetch=make([("hi", 65.0, 1.0)]))
    assert gt.main([ID, "--lang", "de", "en", "--timestamps"]) == 0
    assert calls.fetch == [(ID, ["de", "en"])]
    assert capsys.readouterr().out == "[01:05] hi\n"

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
    assert capsys.readouterr().err.startswith("error:")

def test_main_list(patched, capsys):
    patched(languages=["en\tEnglish\tmanual"])
    assert gt.main([ID, "--list"]) == 0
    assert capsys.readouterr().out == "en\tEnglish\tmanual\n"

def test_main_invalid_input(patched, capsys):
    patched()
    assert gt.main(["https://vimeo.com/1"]) == 2
    assert "https://vimeo.com/1" in capsys.readouterr().err

def test_main_leading_hyphen_id(patched):
    calls = patched(fetch=make([("hi", 0.0, 1.0)]))
    assert gt.main(["--", "-abcdefghij"]) == 0
    assert calls.fetch[0][0] == "-abcdefghij"

@pytest.mark.parametrize("code", [1, 3, 4])
def test_main_error_codes_do_not_fall_back(patched, capsys, code):
    calls = patched(fetch=gt.TranscriptError("nope", code), ytdlp_installed=True)
    assert gt.main([ID]) == code
    assert calls.ytdlp == []
    assert "error: nope" in capsys.readouterr().err

def test_main_blocked_falls_back_to_ytdlp(patched, capsys):
    patched(fetch=gt.BlockedError("blocked"), ytdlp_installed=True,
            ytdlp=make([("hi", 0.0, 1.0)], source="yt-dlp", is_generated=None))
    assert gt.main([ID]) == 0
    assert capsys.readouterr().out == "hi\n"

def test_main_blocked_without_ytdlp(patched, capsys):
    calls = patched(fetch=gt.BlockedError("blocked"), ytdlp_installed=False)
    assert gt.main([ID]) == 5
    assert calls.ytdlp == []
    assert "SKILL.md" in capsys.readouterr().err

def test_main_blocked_and_fallback_fails(patched, capsys):
    patched(fetch=gt.BlockedError("blocked"), ytdlp_installed=True,
            ytdlp=gt.BlockedError("yt-dlp failed"))
    assert gt.main([ID]) == 5

def test_main_empty_transcript_is_exit_3(patched, capsys):
    patched(fetch=make([]))
    assert gt.main([ID]) == 3

def test_main_survives_non_utf8_stdout(patched, monkeypatch):
    patched(fetch=make([("日本語", 0.0, 1.0)]))
    buffer = io.BytesIO()
    monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(buffer, encoding="ascii"))
    assert gt.main([ID]) == 0
    sys.stdout.flush()
    assert "日本語".encode("utf-8") in buffer.getvalue()
```

- [ ] **Step 2: Run TEST.** Expected: the new tests fail.

- [ ] **Step 3: Implement `main`.**

  Decisions: reconfigure stdout to UTF-8 when it supports `reconfigure`.
  `--list` never uses the fallback. Only `BlockedError` from
  `fetch_snippets` triggers `fetch_snippets_ytdlp`, and only when
  `ytdlp_available()` is true. `OSError` while writing maps to exit 1. Any
  unexpected exception maps to exit 1 with its message and no traceback.
  Argparse usage errors keep argparse's own exit code 2.

- [ ] **Step 4: Run TEST.** Expected: all pass.

- [ ] **Step 5: Check the script runs standalone.**

  Run: `uv run skills/youtube-transcript/scripts/get_transcript.py --help`
  Expected: usage text listing all six arguments, exit 0.

- [ ] **Step 6: Lint with ruff and commit.**

---

### Task 6: `SKILL.md`, repository docs, CI and smoke test

**Files:**

- Create: `skills/youtube-transcript/SKILL.md`
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `.github/workflows/lint.yml`

**Interfaces:**

- Consumes: the CLI and exit codes from Task 5.

- [ ] **Step 1: Write `SKILL.md`.** Frontmatter:

```yaml
---
name: youtube-transcript
description: >-
  Fetch the transcript of a single YouTube video as plain text or JSON. Use
  when the user shares a YouTube link or video ID and wants it summarized,
  quoted, searched, or turned into notes, or asks what a video says.
---
```

  Body sections, in this order, under 80 lines in total:

  1. **Usage**: `uv run scripts/get_transcript.py "<url-or-id>"`, relative to
     the skill directory, and the options table from the spec. Say to quote
     the URL and to use `--` before an ID that starts with a hyphen.
  2. **Choosing options**: default text for reading; `--timestamps` when the
     user wants to cite moments; `--format json` for structured use;
     `--list` then `--lang` when exit code 3 reports other languages;
     `--output` for long videos, to avoid flooding the context.
  3. **Exit codes**: the table from Global Constraints, with what to tell the
     user for each. Never invent transcript content on failure.
  4. **When YouTube blocks requests** (exit 5): common on cloud and CI
     machines. Remedies: run from another network; install `yt-dlp` so the
     fallback can run; or run `yt-dlp` by hand with `--cookies-from-browser`
     or `--proxy` using the command from Task 4.
  5. **Without uv**: `pip install "youtube-transcript-api>=1.2,<2"` then
     `python scripts/get_transcript.py`.
  6. **Limits**: single videos only; no playlists, translation, or audio
     transcription.

- [ ] **Step 2: Update `README.md`.** Add a "Using Skills" subsection after
  "Using Agent Personas" that names the skill, gives its raw `SKILL.md` URL in
  the existing URL style, and shows installing by copying
  `skills/youtube-transcript/` into the agent's skills directory, for example
  `~/.claude/skills/`. Add a row to the Quick Reference URLs table and to any
  directory listing in the file.

- [ ] **Step 3: Update `AGENTS.md`.** Add `skills/` to the Project Structure
  tree; add a "Skills" list linking `./skills/youtube-transcript/SKILL.md`;
  add the Python commands (TEST and the ruff commands) under Commands; add
  an "Adding New Skills" procedure: create `skills/<name>/SKILL.md` with
  `name` and `description` frontmatter, put code in `scripts/` and tests in
  `tests/`, update `README.md`, run the linters and tests.

- [ ] **Step 4: Add a `python` job to `.github/workflows/lint.yml`** next to
  the existing jobs: `actions/checkout@v4`, `astral-sh/setup-uv@v6`, then
  `uvx ruff check skills/`, `uvx ruff format --check skills/`, and TEST.

- [ ] **Step 5: Run LINT and TEST.** Expected: 0 Markdown issues, ruff clean,
  all tests pass.

- [ ] **Step 6: Smoke test against a real video.**

  Run:
  `uv run skills/youtube-transcript/scripts/get_transcript.py "https://www.youtube.com/watch?v=jNQXAC9IVRw" --timestamps`
  Expected: transcript lines and exit 0. Exit 5 from a cloud machine is an
  acceptable result; record whichever happened, with the exit code, in the
  PR description. Also run with `--list` and with `https://vimeo.com/1` and
  record the exit codes.

- [ ] **Step 7: Commit, push, and update the PR #5 description** with what
  was built, the test results, and the smoke test outcome.
