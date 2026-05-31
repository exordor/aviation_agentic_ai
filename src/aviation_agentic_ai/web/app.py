from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from aviation_agentic_ai.config import load_environment
from aviation_agentic_ai.llm.providers import (
    SUPPORTED_LLM_PROVIDERS,
    configured_llm_model,
    configured_llm_provider,
)
from aviation_agentic_ai.paths import PROJECT_ROOT
from aviation_agentic_ai.retrieval.hybrid import run_query
from aviation_agentic_ai.retrieval.sufficiency import evaluate_evidence_sufficiency
from aviation_agentic_ai.web.data import (
    STRUCTURE_AWARE_CHUNKS,
    STRUCTURE_AWARE_COLLECTION,
    STRUCTURE_AWARE_KG,
    WebDataReadError,
    build_demo_explanation,
    build_demo_status,
    build_experiment_summary,
    build_question_detail,
    build_question_kg_graph,
    build_questions,
)


class QueryRequest(BaseModel):
    question: str = Field(..., max_length=2000)
    mode: Literal["vector", "graph", "hybrid"] = "hybrid"
    max_tokens: int = Field(1200, ge=1, le=8192)
    temperature: float = Field(0.0, ge=0.0, le=2.0)


def _llm_metadata() -> dict[str, str]:
    load_environment()
    provider = configured_llm_provider()
    return {"provider": provider, "model": configured_llm_model(provider)}


def build_live_query_readiness(
    project_root: str | Path = PROJECT_ROOT,
    *,
    enable_live_query: bool | None = None,
) -> dict[str, Any]:
    metadata = _llm_metadata()
    root = Path(project_root)
    chunks_path = root / STRUCTURE_AWARE_CHUNKS
    kg_path = root / STRUCTURE_AWARE_KG
    index_dir = root / "data" / "indexes" / "chroma"
    base = {
        "enabled": False,
        "reason": "",
        "provider": metadata["provider"],
        "model": metadata["model"],
        "collection_name": STRUCTURE_AWARE_COLLECTION,
    }
    if enable_live_query is False:
        return {**base, "reason": "Live query disabled by --disable-live-query."}

    missing_artifacts = [
        str(path.relative_to(root))
        for path in (chunks_path, kg_path, index_dir)
        if not path.exists()
    ]
    if missing_artifacts:
        return {
            **base,
            "reason": "Missing live query artifacts: " + ", ".join(missing_artifacts),
        }

    missing_dependencies = [
        module
        for module in ("chromadb", "langchain_core", "langchain_openai")
        if importlib.util.find_spec(module) is None
    ]
    if missing_dependencies:
        return {
            **base,
            "reason": (
                "Missing optional dependencies: "
                + ", ".join(missing_dependencies)
                + ". Install with: uv sync --extra graphrag --extra ontology-generation --extra web"
            ),
        }

    provider = metadata["provider"]
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        return {**base, "reason": "OPENAI_API_KEY is not configured."}
    if provider == "deepseek" and not os.getenv("DEEPSEEK_API_KEY"):
        return {**base, "reason": "DEEPSEEK_API_KEY is not configured."}
    if provider not in SUPPORTED_LLM_PROVIDERS:
        return {**base, "reason": f"Unsupported LLM_PROVIDER: {provider}"}

    return {**base, "enabled": True, "reason": "Live query is ready."}


def build_evidence_summary(result: dict[str, Any]) -> dict[str, Any]:
    chunks = result.get("fused_chunks") or []
    triples = result.get("graph_triples") or []
    top_chunk = chunks[0] if chunks else {}
    top_triple = triples[0] if triples else {}
    return {
        "chunk_count": len(chunks),
        "triple_count": len(triples),
        "top_chunk": {
            "chunk_id": top_chunk.get("chunk_id"),
            "page": top_chunk.get("page"),
            "source": top_chunk.get("source"),
        }
        if top_chunk
        else None,
        "top_triple": {
            "triple_id": top_triple.get("triple_id"),
            "page": top_triple.get("page"),
            "subject": top_triple.get("subject"),
            "predicate": top_triple.get("predicate"),
            "object": top_triple.get("object"),
        }
        if top_triple
        else None,
    }


def create_app(
    *,
    project_root: str | Path = PROJECT_ROOT,
    enable_live_query: bool | None = None,
):
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import FileResponse, Response
        from fastapi.staticfiles import StaticFiles
    except ImportError as exc:  # pragma: no cover - exercised by CLI error handling.
        raise RuntimeError(
            "The web demo requires optional web dependencies. "
            "Install with: uv sync --extra web"
        ) from exc

    root = Path(project_root)
    static_dir = Path(__file__).resolve().parent / "static"
    app = FastAPI(title="Aviation Agentic AI Web Demo")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def index():
        return FileResponse(static_dir / "index.html")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return Response(status_code=204)

    @app.get("/api/status")
    def status():
        try:
            readiness = build_live_query_readiness(root, enable_live_query=enable_live_query)
            payload = build_demo_status(root, live_query_enabled=readiness["enabled"])
            payload["live_query_readiness"] = readiness
            return payload
        except WebDataReadError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc

    @app.get("/api/demo/explanation")
    def demo_explanation():
        try:
            return build_demo_explanation(root)
        except WebDataReadError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc

    @app.get("/api/questions")
    def questions():
        try:
            return {"questions": build_questions(root)}
        except WebDataReadError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc

    @app.get("/api/questions/{cq_id}")
    def question_detail(cq_id: str):
        try:
            detail = build_question_detail(cq_id, root)
        except WebDataReadError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc
        if detail is None:
            raise HTTPException(status_code=404, detail=f"Unknown CQ id: {cq_id}")
        return detail

    @app.get("/api/questions/{cq_id}/kg-graph")
    def question_kg_graph(
        cq_id: str,
        experiment: Literal["fixed_window", "structure_aware"] = "structure_aware",
        mode: Literal["vector", "graph", "hybrid"] = "hybrid",
    ):
        try:
            graph = build_question_kg_graph(cq_id, root, experiment=experiment, mode=mode)
        except WebDataReadError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc
        if graph is None:
            raise HTTPException(status_code=404, detail=f"Unknown CQ id: {cq_id}")
        return graph

    @app.get("/api/experiments/summary")
    def experiments_summary():
        try:
            return build_experiment_summary(root)
        except WebDataReadError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc

    @app.post("/api/query")
    def live_query(request: QueryRequest):
        readiness = build_live_query_readiness(root, enable_live_query=enable_live_query)
        if not readiness["enabled"]:
            raise HTTPException(
                status_code=503,
                detail=readiness["reason"],
            )
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question is required.")
        boundary_decision = evaluate_evidence_sufficiency(question, {})
        if boundary_decision["risk_category"] != "training_question":
            result = {
                "question": question,
                "mode": request.mode,
                "answer": (
                    "The retrieved evidence is insufficient for a grounded answer. "
                    f"Reason: {boundary_decision['reason']}"
                ),
                "fused_chunks": [],
                "graph_triples": [],
                "graph_paths": [],
                "sufficiency_decision": boundary_decision,
            }
            result["evidence_summary"] = build_evidence_summary(result)
            return result
        try:
            result = run_query(
                question,
                request.mode,
                root / STRUCTURE_AWARE_CHUNKS,
                root / STRUCTURE_AWARE_KG,
                root / "data" / "indexes" / "chroma",
                collection_name=STRUCTURE_AWARE_COLLECTION,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except (RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:
            import logging

            logging.getLogger(__name__).exception("Live query failed")
            raise HTTPException(
                status_code=502, detail="Live query failed due to an internal error."
            ) from exc
        result["evidence_summary"] = build_evidence_summary(result)
        return result

    return app
