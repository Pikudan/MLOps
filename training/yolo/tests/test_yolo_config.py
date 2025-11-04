from importlib import util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "train_yolo.py"


def load_module():
    spec = util.spec_from_file_location("train_yolo", MODULE_PATH)
    module = util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


def test_load_config(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text("project_name: test\nmodel:\n  weights: yolov8n.pt\n", encoding="utf-8")

    module = load_module()
    cfg = module.load_config(cfg_path)
    assert cfg["project_name"] == "test"
    assert cfg["model"]["weights"] == "yolov8n.pt"


def test_apply_overrides_verbose() -> None:
    module = load_module()
    cfg = {"data": {"epochs": 10}, "logging": {"level": "INFO"}}

    class Args:
        epochs = 5
        batch = 2
        device = "cpu"
        verbose = True

    updated = module.apply_overrides(cfg, Args)
    assert updated["data"]["epochs"] == 5
    assert updated["data"]["batch"] == 2
    assert updated["data"]["device"] == "cpu"
    assert updated["logging"]["level"] == "DEBUG"

