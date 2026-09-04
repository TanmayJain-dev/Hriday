from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.intelligence.graph.interfaces import GraphStore
    from backend.intelligence.query.models import Answer


@dataclass
class QueryOrchestrator:
    """Orchestrates query execution over graph facts using the Member 5 query engine."""
    query_engine: Any = None

    def __post_init__(self) -> None:
        if self.query_engine is None:
            from backend.intelligence.query.engine import QueryEngine
            self.query_engine = QueryEngine()

    def execute_query(
        self,
        question: str,
        graph: GraphStore,
        document_id: str = "demo-pid",
    ) -> Answer:
        """Routes query through Member 5 query engine to GraphStore."""
        return self.query_engine.query(question, graph, document_id=document_id)


@dataclass
class Pipeline:
    ingestion: object
    extraction: object
    topology: object
    graph_builder: object
    query_orchestrator: QueryOrchestrator = field(default_factory=QueryOrchestrator)

    def process(self, document):
        ingested = self.ingestion.ingest(document)
        extracted = self.extraction.extract(ingested)
        topology = self.topology.reconstruct(extracted)
        return self.graph_builder(topology)

    def query(self, graph: GraphStore, question: str, document_id: str = "demo-pid") -> Answer:
        """Convenience method to query graph through orchestration layer."""
        return self.query_orchestrator.execute_query(question, graph, document_id=document_id)
