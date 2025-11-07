# pyright: reportMissingImports=false

"""Ensure training package is importable in tests."""

import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

