"""End-to-end P&ID processing pipeline orchestration."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.intelligence.graph.interfaces import GraphStore


@dataclass
class PipelineStageResult:
    """Execution output of an end-to-end pipeline processing run."""
    document_id: str
    graph: GraphStore
    graph_dict: dict[str, Any]
    uncertainties: list[dict[str, Any]]
    raw_extraction: Any = None
    raw_topology: Any = None


@dataclass
class QueryOrchestrator:
    """Orchestrates query execution over graph facts using the query engine."""
    query_engine: Any = None

    def __post_init__(self) -> None:
        if self.query_engine is None:
            try:
                from backend.intelligence.query.engine import QueryEngine
                self.query_engine = QueryEngine()
            except ImportError:
                self.query_engine = None

    def execute_query(
        self,
        question: str,
        graph: GraphStore,
        document_id: str = "demo-pid",
    ) -> Any:
        """Route natural-language query through the query engine to GraphStore."""
        if self.query_engine is None:
            raise RuntimeError("QueryEngine is not available in current environment")
        return self.query_engine.query(question, graph, document_id=document_id)


@dataclass
class Pipeline:
    """Orchestrates the stage-by-stage P&ID transformation lifecycle."""
    ingestion: object
    extraction: object
    topology: object
    graph_builder: object
    query_orchestrator: QueryOrchestrator = field(default_factory=QueryOrchestrator)

    def process(self, document: Any) -> Any:
        """Execute stage pipeline: Ingest -> Extract -> Reconstruct -> Build Graph."""
        ingested = self.ingestion.ingest(document) if hasattr(self.ingestion, "ingest") else document
        extracted = self.extraction.extract(ingested) if hasattr(self.extraction, "extract") else ingested
        topology = self.topology.reconstruct(extracted) if hasattr(self.topology, "reconstruct") else extracted

        if callable(self.graph_builder):
            return self.graph_builder(topology)
        return topology

    def process_with_provenance(self, document: Any) -> PipelineStageResult:
        """Execute stage pipeline preserving stage intermediates and uncertainties."""
        doc_id = getattr(document, "document_id", None) or (
            document.get("document_id") if isinstance(document, dict) else "pid-unknown"
        )
        ingested = self.ingestion.ingest(document) if hasattr(self.ingestion, "ingest") else document
        extracted = self.extraction.extract(ingested) if hasattr(self.extraction, "extract") else ingested
        topology = self.topology.reconstruct(extracted) if hasattr(self.topology, "reconstruct") else extracted

        from backend.intelligence.graph.builder import build_graph_with_uncertainties

        store, uncertainties = build_graph_with_uncertainties(topology)
        return PipelineStageResult(
            document_id=str(doc_id),
            graph=store,
            graph_dict=store.to_dict(str(doc_id)),
            uncertainties=uncertainties,
            raw_extraction=extracted,
            raw_topology=topology,
        )

    def query(self, graph: GraphStore, question: str, document_id: str = "demo-pid") -> Any:
        """Convenience method to route a natural-language query through orchestration."""
        return self.query_orchestrator.execute_query(question, graph, document_id=document_id)
