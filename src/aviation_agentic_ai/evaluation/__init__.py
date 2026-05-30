"""Evaluation utilities."""

from aviation_agentic_ai.evaluation.document_metadata import DocumentMetadata, SectionRecord
from aviation_agentic_ai.evaluation.gold import EvidenceSpan, GoldLabel, GoldLabelReadError
from aviation_agentic_ai.evaluation.metrics import (
    answer_metrics,
    kg_evidence_metrics,
    retrieval_metrics,
)
from aviation_agentic_ai.evaluation.protocol import build_run_manifest

__all__ = [
    "DocumentMetadata",
    "EvidenceSpan",
    "GoldLabel",
    "GoldLabelReadError",
    "SectionRecord",
    "answer_metrics",
    "build_run_manifest",
    "kg_evidence_metrics",
    "retrieval_metrics",
]
