from __future__ import annotations

from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.faa_order_document import (
    build_faa_order_source_package,
)
from aviation_agentic_ai.agent_system.faa_order_ingestion import (
    register_faa_order_source,
)
from aviation_agentic_ai.agent_system.source_retrieval import build_source_record_chunks
from aviation_agentic_ai.utils.pdf import PdfPage


def test_faa_order_source_registration_persists_version_anchors_and_chunks(
    tmp_path,
) -> None:
    package = build_faa_order_source_package(
        (
            PdfPage(
                page_number=410,
                text="18−10−1. POLICY\nGDP policy text.\n",
            ),
        ),
        pdf_sha256="c" * 64,
        pdf_byte_count=456,
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:faa-order",
        create=True,
    )
    try:
        result = register_faa_order_source(store, package)

        assert result.status == "ok"
        assert result.chunk_count == len(build_source_record_chunks((package.source_version,)))
        assert store.get_source_version(package.source_version_id) is not None
        assert store.get_source_anchor(package.cards[0].source_anchor_id) is not None
        assert store.get_source_chunk(result.chunk_ids[0]) is not None
    finally:
        store.close()
