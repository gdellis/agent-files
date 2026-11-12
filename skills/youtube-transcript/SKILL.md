---
name: youtube-transcript
description: >-
  Fetch the transcript of a single YouTube video as plain text or JSON. Use
  when the user shares a YouTube link or video ID and wants it summarized,
  quoted, searched, or turned into notes, or asks what a video says.
---

# YouTube Transcript

Fetch the captions of one YouTube video so you can read them.

## Usage

Run the script from this skill's directory. Quote the URL and put it first.

```bash
uv run scripts/get_transcript.py "<url-or-id>" [options]
```

| Option | Default | Effect |
| --- | --- | --- |
| `--lang CODE ...` | `en` | Language codes in priority order |
| `--timestamps` | off | Prefix each line with `[mm:ss]` |
| `--format text\|json` | `text` | `json` returns snippets with start and duration |
| `--output FILE` | stdout | Write the transcript to a file |
| `--list` | off | List the available languages and exit |

It accepts `watch?v=`, `youtu.be/`, `/shorts/`, `/embed/` and `/live/` URLs, or
a bare 11-character ID. For an ID that starts with a hyphen, put `--` first:
`uv run scripts/get_transcript.py -- -abcdefghij`.

## Choosing options

- Read the default text output for summaries and questions.
- Add `--timestamps` when the user wants to cite or jump to moments.
- Use `--format json` when another program consumes the result. It also says
  whether the captions are auto-generated.
- Use `--output FILE` for long videos, then read the file in parts instead of
  printing an hour of speech into the conversation.
- A request for `en` also matches regional variants such as `en-US`.

Auto-generated captions have no punctuation and contain recognition errors.
Say so when you quote them.

## Exit codes

The transcript goes to stdout. Errors go to stderr as one line starting with
`error:`.

| Code | Meaning | What to do |
| --- | --- | --- |
| 0 | Success | Use the transcript |
| 1 | Network or other failure | Report the message; retry once if it looks transient |
| 2 | Not a YouTube video URL or ID | Ask the user for the correct link |
| 3 | No captions in the requested language | The message lists available languages; retry with `--lang`, or tell the user the video has no captions |
| 4 | Video unavailable, private or age-restricted | Tell the user; do not retry |
| 5 | YouTube blocked the request | See the next section |

Never invent or guess transcript content when the script fails.

## When YouTube blocks requests

Exit code 5 is common on cloud and CI machines, because YouTube blocks many
data-center addresses. The script already retries through `yt-dlp` when that
program is installed. If it still fails:

1. Run the command from another network, such as the user's own machine.
2. Install `yt-dlp` if it is missing, so the fallback can run.
3. Ask the user whether to use their browser cookies or a proxy, then run
   `yt-dlp` directly:

```bash
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "en.*" \
  --sub-format json3 --cookies-from-browser firefox -o "%(id)s" -- "<url>"
```

Replace `--cookies-from-browser firefox` with `--proxy <url>` to use a proxy.

## Without uv

```bash
pip install "youtube-transcript-api>=1.2,<2"
python scripts/get_transcript.py "<url-or-id>"
```

## Limits

- One video per run. Playlists and channels are not supported.
- No translation, and no transcription of audio for videos without captions.
