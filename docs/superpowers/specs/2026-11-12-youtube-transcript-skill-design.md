# YouTube Transcript Skill Design

Date: 2026-11-12

## Goal

Give an AI coding agent a reliable way to turn a single YouTube video URL into
clean transcript text it can summarize, answer questions about, or take notes
from.

Success means: the agent runs one command with a URL and gets readable text on
stdout, or a short message that says why no transcript is available and what to
do next.

## Scope

In scope:

- One video per invocation, given as a URL or a bare video ID.
- Language selection, optional timestamps, text or JSON output.
- A fallback path when YouTube blocks the primary tool.

Out of scope:

- Playlists, channels, and bulk archiving.
- Downloading audio or video, or transcribing audio with a speech model.
- Translation of transcripts.
- A plain Markdown version of the skill for agents without skill support.

## Decisions

| Decision | Choice | Reason |
| --- | --- | --- |
| Form | Agent Skill folder with `SKILL.md` and a bundled script | Chosen by the repository owner |
| Primary tool | `youtube-transcript-api` | Light, pure Python, returns structured snippets |
| Fallback tool | `yt-dlp`, used only if installed | Different request path, sometimes works when the primary is blocked |
| Logic location | Python script, not prose in `SKILL.md` | URL parsing, formatting and errors are deterministic |
| Dependency handling | Inline script metadata (PEP 723), run with `uv run` | No virtual environment for the agent to manage |

## Layout

```text
skills/youtube-transcript/
├── SKILL.md
├── scripts/
│   └── get_transcript.py
└── tests/
    └── test_get_transcript.py
```

This adds a new top-level `skills/` directory next to `rules/`, `agents/` and
`guides/`.

## SKILL.md

Frontmatter:

- `name`: `youtube-transcript`
- `description`: states what the skill does and when to use it, for example
  when the user shares a YouTube link and asks to summarize, quote, or answer
  questions about the video.

Body, kept short:

1. The command to run and its options.
2. How to read the output and the exit codes.
3. What to tell the user for each failure, including the proxy and cookies
   remedies when YouTube blocks requests.
4. The `pip install youtube-transcript-api` alternative for machines without
   `uv`.

## Script interface

```text
get_transcript.py <url-or-id> [--lang CODE ...] [--timestamps]
                  [--format text|json] [--output FILE] [--list]
```

| Option | Default | Behavior |
| --- | --- | --- |
| `<url-or-id>` | required | A YouTube URL or an 11-character video ID |
| `--lang` | `en` | Language codes in priority order |
| `--timestamps` | off | Prefix each line with `[mm:ss]`, or `[h:mm:ss]` past one hour |
| `--format` | `text` | `text` for reading, `json` for structured snippets |
| `--output` | stdout | Write to a file instead of stdout |
| `--list` | off | Print the available transcript languages and exit |

Accepted URL forms: `youtube.com/watch?v=ID`, `youtu.be/ID`,
`youtube.com/shorts/ID`, `youtube.com/embed/ID`, `youtube.com/live/ID`, with or
without `www.`, `m.` or `music.` prefixes and extra query parameters.

## Behavior

1. Extract the video ID from the argument. Reject anything that does not yield
   an 11-character ID.
2. List the transcripts for the video. Within the requested languages, pick a
   manually created transcript before an auto-generated one.
3. Fetch the snippets. Each has `text`, `start` and `duration`.
4. Format the output:
   - `text`: snippet texts joined into lines, whitespace collapsed. With
     `--timestamps`, one line per snippet with its time marker.
   - `json`: an object with `video_id`, `language_code`, `is_generated`,
     `source` (`youtube-transcript-api` or `yt-dlp`) and `snippets`.
5. Write the transcript to stdout or the `--output` file. Diagnostics go to
   stderr only.

## Units

The script is one file with four functions that can be tested separately:

| Function | Input | Output | Depends on |
| --- | --- | --- | --- |
| `extract_video_id` | URL or ID string | Video ID, or raises `ValueError` | Standard library |
| `fetch_snippets` | Video ID, languages | Snippets plus language metadata | `youtube-transcript-api` |
| `fetch_snippets_ytdlp` | Video ID, languages | Same shape as `fetch_snippets` | `yt-dlp` executable |
| `format_transcript` | Snippets, format, timestamps flag | Output string | Standard library |

`main` parses arguments, calls these in order, and maps exceptions to exit
codes.

## Error handling

| Situation | Exit code | Message on stderr |
| --- | --- | --- |
| Success | 0 | none |
| Invalid URL or ID | 2 | What was received and the accepted forms |
| Captions disabled, or none in the requested languages | 3 | The reason, plus available language codes if any |
| Video unavailable, private, or age-restricted | 4 | The reason |
| Blocked by YouTube after the fallback also failed, or no fallback installed | 5 | Explanation, plus the proxy and cookies remedies |
| Any other failure | 1 | The exception message |

Fallback rule: only a blocked-request error from the primary tool triggers the
`yt-dlp` attempt, and only when `yt-dlp` is on `PATH`. The fallback requests
subtitles in `json3` format with `--skip-download`, then converts the events
into the same snippet shape, dropping empty and duplicate segments.

The fallback asks for manual subtitles first, then for the original
auto-generated track only (`<code>-orig`). It never returns a machine
translation. When `yt-dlp` reaches YouTube but finds no captions in the
requested languages, the exit code is 3, not 5.

Blocks are often by IP address and can affect both tools. The script does not
promise the fallback works; it reports plainly when both paths fail.

## Testing

Unit tests with `pytest`, no network access:

- `extract_video_id`: every accepted URL form, a bare ID, and rejections
  (wrong host, missing ID, wrong length).
- `format_transcript`: text, text with timestamps under and over one hour,
  JSON shape, whitespace collapsing.
- `fetch_snippets`: manual preferred over generated, language priority order,
  each library exception mapped to the right exit code. The library is mocked.
- `fetch_snippets_ytdlp`: a sample `json3` payload converted to snippets;
  missing executable handled. The subprocess call is mocked.
- `main`: exit codes and stderr messages for each row of the error table.

One manual smoke test against a real public video, recorded in the pull
request description. It may fail from cloud or CI machines if YouTube blocks
the address, so it is not part of CI.

## Repository changes

- `README.md`: add a Skills section that lists the skill and how to install it
  (copy or link `skills/youtube-transcript/` into the agent's skills
  directory).
- `AGENTS.md`: add `skills/` to the project structure, add a Skills list, and
  add an "Adding New Skills" procedure.
- `.github/workflows/lint.yml`: add a job that runs `ruff check` and `pytest`
  for `skills/`.
- `.markdownlint.json`: no change expected. `MD041` is already off, so YAML
  frontmatter in `SKILL.md` should pass; verify with `markdownlint-cli2`.

The Python code follows `rules/python.md`.

## Build order

1. Scaffold `skills/youtube-transcript/` and write failing tests.
2. Implement `extract_video_id` and `format_transcript`.
3. Implement `fetch_snippets` and the exit-code mapping in `main`.
4. Implement `fetch_snippets_ytdlp` and the fallback rule.
5. Write `SKILL.md`.
6. Update `README.md`, `AGENTS.md` and the CI workflow.
7. Run the linters and tests, run the smoke test, open a draft pull request.
