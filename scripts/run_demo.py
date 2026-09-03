"""Load the simple fixture and demonstrate deterministic graph traversal."""
from pathlib import Path
import json

from backend.intelligence.graph.builder import build_graph

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "data/fixtures/simple_pid.json").read_text(encoding="utf-8"))
# Fixture uses `edges` and `entities`; the graph builder expects topology-shaped names.
topology = {"nodes": data["entities"], "edges": data["edges"]}
graph = build_graph(topology)
print("Downstream of P-101:")
for path in graph.downstream("P-101"):
    print("  " + " -> ".join(path))
