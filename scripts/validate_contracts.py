"""Validate that every HRIDAY JSON contract is syntactically valid."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
for path in sorted((root / "contracts").glob("*.json")):
    json.loads(path.read_text(encoding="utf-8"))
    print(f"OK  {path.relative_to(root)}")
print("All contract JSON files parse successfully.")
