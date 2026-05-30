from __future__ import annotations

import click

from aviation_agentic_ai.web.server import serve_web_app


@click.group()
def web() -> None:
    """Local web demo commands."""


@web.command("serve")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", type=int, default=8000, show_default=True)
@click.option("--reload/--no-reload", default=False, show_default=True)
@click.option(
    "--enable-live-query/--disable-live-query",
    default=None,
    help="Force-enable or force-disable live LLM querying. Default: auto-detect readiness.",
)
def web_serve(host: str, port: int, reload: bool, enable_live_query: bool | None) -> None:
    """Serve the offline-first FastAPI web demo."""
    try:
        serve_web_app(
            host=host,
            port=port,
            reload=reload,
            enable_live_query=enable_live_query,
        )
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc
