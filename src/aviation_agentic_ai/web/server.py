from __future__ import annotations

from pathlib import Path

from aviation_agentic_ai.paths import PROJECT_ROOT


def serve_web_app(
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    enable_live_query: bool | None = None,
    project_root: str | Path = PROJECT_ROOT,
) -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError(
            "The web demo server requires uvicorn. Install with: uv sync --extra web"
        ) from exc

    from aviation_agentic_ai.web.app import create_app

    app = create_app(project_root=project_root, enable_live_query=enable_live_query)
    uvicorn.run(app, host=host, port=port, reload=reload)
