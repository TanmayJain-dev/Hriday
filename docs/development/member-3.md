# Member 3 — Visual Extraction

Own `backend/intelligence/extraction/**` and `tests/extraction/**`.

Mission: turn input documents into observable structured evidence.

Build adapters for preprocessing, OCR, object/entity detection, tag association, coordinates, and line candidates.

Do not silently decide final connectivity. Emit observations, candidates, confidence, and uncertainty for the topology subsystem.

Prototype success: produce contract-valid `ExtractionResult` for supported drawings and fixtures.
