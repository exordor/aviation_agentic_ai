from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from aviation_agentic_ai.paths import PROJECT_ROOT
from aviation_agentic_ai.retrieval.hybrid import run_query
from aviation_agentic_ai.web.data import (
    STRUCTURE_AWARE_CHUNKS,
    STRUCTURE_AWARE_COLLECTION,
    STRUCTURE_AWARE_KG,
    build_demo_status,
    build_experiment_summary,
    build_question_detail,
    build_questions,
)


class QueryRequest(BaseModel):
    question: str
    mode: Literal["vector", "graph", "hybrid"] = "hybrid"
    max_tokens: int = 1200
    temperature: float = 0.0


def create_app(
    *,
    project_root: str | Path = PROJECT_ROOT,
    enable_live_query: bool = False,
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
        return build_demo_status(root, live_query_enabled=enable_live_query)

    @app.get("/api/questions")
    def questions():
        return {"questions": build_questions(root)}

    @app.get("/api/questions/{cq_id}")
    def question_detail(cq_id: str):
        detail = build_question_detail(cq_id, root)
        if detail is None:
            raise HTTPException(status_code=404, detail=f"Unknown CQ id: {cq_id}")
        return detail

    @app.get("/api/experiments/summary")
    def experiments_summary():
        return build_experiment_summary(root)

    @app.post("/api/query")
    def live_query(request: QueryRequest):
        if not enable_live_query:
            raise HTTPException(
                status_code=403,
                detail="Live query is disabled. Start with --enable-live-query to call the LLM.",
            )
        return run_query(
            request.question,
            request.mode,
            root / STRUCTURE_AWARE_CHUNKS,
            root / STRUCTURE_AWARE_KG,
            root / "data" / "indexes" / "chroma",
            collection_name=STRUCTURE_AWARE_COLLECTION,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

    return app
