"""Unit tests for get_transcript.py. No test touches the network."""

import get_transcript as gt
import pytest

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
