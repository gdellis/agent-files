"""Make the skill's script importable as ``get_transcript`` in tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
