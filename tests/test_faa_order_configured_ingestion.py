from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.ontology_kg_builder import (
    run_ontology_kg_build,
)


def test_configured_faa_order_ingestion_registers_local_pdf(tmp_path: Path) -> None:
    from aviation_agentic_ai.agent_system.faa_order_ingestion import (
        run_faa_order_ingestion,
    )

    pdf_path = tmp_path / "order.pdf"
    pdf_path.write_bytes(b"not a real PDF")
    config = {
        "sources": {"faa_order_7210_3ee": str(pdf_path)},
        "source_urls": {"faa_order_7210_3ee": "https://example.test/order.pdf"},
    }
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:faa-order",
        create=True,
    )
    try:
        # The path check happens before PDF parsing and must report a bounded
        # failure rather than silently switching to a different source.
        summary = run_faa_order_ingestion(config, store)
        assert summary.status == "blocked"
        assert summary.blocked_count == 1
    finally:
        store.close()


def test_configured_ingestion_exposes_document_domain() -> None:
    from aviation_agentic_ai.agent_system.ingestion_pipeline import (
        run_configured_ingestion,
    )

    store = object()
    summary_row = SimpleNamespace(
        discovered_count=1,
        selected_count=1,
        attempted_count=1,
        skipped_count=0,
        ok_count=1,
        insufficient_count=0,
        blocked_count=0,
    )

    calls: list[str] = []

    def document_runner(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        calls.append("document")
        return summary_row

    summary = run_configured_ingestion(
        {"sources": {"faa_order_7210_3ee": "order.pdf"}},
        store,
        domain="document",
        document_runner=document_runner,
    )

    assert calls == ["document"]
    assert summary.document_summary is summary_row


def test_document_is_a_supported_ontology_kg_adapter() -> None:
    summary = run_ontology_kg_build(
        {"sources": {}},
        object(),  # type: ignore[arg-type]
        domain="document",
        allow_live_model=True,
    )

    assert summary.domain == "document"
    assert summary.status == "blocked"
    assert "unsupported ontology KG domain" not in summary.reasons[0]
