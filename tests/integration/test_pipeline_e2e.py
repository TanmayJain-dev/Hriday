"""End-to-end integration tests for the HRIDAY pipeline."""
import json
from pathlib import Path
from backend.intelligence.graph.builder import build_graph
from backend.orchestration.pipeline import Pipeline, PipelineStageResult

ROOT = Path(__file__).resolve().parents[2]


class DummyIngestion:
    def ingest(self, doc):
        return doc


class DummyExtraction:
    def extract(self, ingested):
        return ingested


class DummyTopology:
    def reconstruct(self, extracted):
        return extracted


def test_pipeline_process_simple_pid():
    fixture_path = ROOT / "data/fixtures/simple_pid.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    pipeline = Pipeline(
        ingestion=DummyIngestion(),
        extraction=DummyExtraction(),
        topology=DummyTopology(),
        graph_builder=build_graph,
    )

    store = pipeline.process(data)
    assert len(store.all_nodes()) == 4
    assert len(store.all_edges()) == 3

    downstream = store.downstream("P-101")
    assert ["P-101", "E-101"] in downstream


def test_pipeline_process_with_provenance_and_uncertainties():
    fixture_path = ROOT / "data/fixtures/ambiguous_junction.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    pipeline = Pipeline(
        ingestion=DummyIngestion(),
        extraction=DummyExtraction(),
        topology=DummyTopology(),
        graph_builder=build_graph,
    )

    result: PipelineStageResult = pipeline.process_with_provenance(data)
    assert result.document_id == "demo-ambiguous-001"
    assert len(result.uncertainties) == 1
    assert result.uncertainties[0]["reason"] == "crossing_vs_junction_ambiguous"
    assert result.graph_dict["document_id"] == "demo-ambiguous-001"
    assert result.graph_dict["edges"] == []
