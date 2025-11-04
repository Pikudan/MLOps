"""Utility to ensure `src` package is available during tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def ensure_src_package() -> ModuleType:
    root = Path(__file__).resolve().parents[1]
    src_path = root / "src"

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    if "src" in sys.modules:
        return sys.modules["src"]

    spec = importlib.util.spec_from_file_location("src", src_path / "__init__.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.__path__ = [str(src_path)]  # type: ignore[attr-defined]
    sys.modules["src"] = module
    return module


ensure_src_package()

