"""Local model adapter abstraction for sovereign on-premise inference."""
from __future__ import annotations
from typing import Any, Callable


class LocalModelAdapter:
    """Offline / sovereign local model adapter.
    
    Operates strictly without cloud dependencies, API keys, or external network calls.
    Allows injecting custom local inference functions (e.g. llama-cpp, local models,
    or test fixtures) while preserving a deterministic fallback.
    """

    def __init__(self, inference_fn: Callable[[str], str] | None = None) -> None:
        self._inference_fn = inference_fn

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generates text completion using the local inference callable."""
        if self._inference_fn is not None:
            return self._inference_fn(prompt)
        raise RuntimeError(
            "LocalModelAdapter: No local inference engine configured. "
            "Deterministic query engine operates without an LLM."
        )
