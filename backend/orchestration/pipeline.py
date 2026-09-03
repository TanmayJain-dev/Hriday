"""Stage-oriented pipeline shell. Concrete providers plug into these boundaries."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Pipeline:
    ingestion: object
    extraction: object
    topology: object
    graph_builder: object

    def process(self, document):
        ingested = self.ingestion.ingest(document)
        extracted = self.extraction.extract(ingested)
        topology = self.topology.reconstruct(extracted)
        return self.graph_builder(topology)
