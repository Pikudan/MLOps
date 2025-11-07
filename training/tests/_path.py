"""Helper to ensure training package is importable during tests."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if "src" not in sys.modules:
    spec = importlib.util.spec_from_file_location("src", SRC / "__init__.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    module.__path__ = [str(SRC)]  # type: ignore[attr-defined]
    sys.modules["src"] = module
    spec.loader.exec_module(module)

