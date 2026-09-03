import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_fixtures_are_valid_json():
    for path in (ROOT / "data" / "fixtures").glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
