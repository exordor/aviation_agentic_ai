from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from aviation_agentic_ai.ontology.cq import load_cq_artifact
from aviation_agentic_ai.paths import project_relative_path


@dataclass(frozen=True)
class EvidenceSpan:
    page: int
    text: str
    char_start: int | None = None
    char_end: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceSpan":
        return cls(
            page=int(data["page"]),
            text=str(data.get("text", "")),
            char_start=int(data["char_start"]) if data.get("char_start") is not None else None,
            char_end=int(data["char_end"]) if data.get("char_end") is not None else None,
        )


@dataclass(frozen=True)
class GoldLabel:
    cq_id: str
    source_document: str
    source_page: int
    question: str = ""
    question_type: str = ""
    expected_chunk_ids: tuple[str, ...] = ()
    evidence_spans: tuple[EvidenceSpan, ...] = ()
    key_entities: tuple[str, ...] = ()
    answer_key: str = ""
    gold_level: str = "page"
    expected_abstention: bool = False

    @classmethod
    def from_cq(cls, cq: dict[str, Any]) -> "GoldLabel":
        return cls(
            cq_id=str(cq["id"]),
            source_document=str(cq.get("source_document", "")),
            source_page=int(cq["source_page"]),
            question=str(cq.get("competency_question", "")),
            question_type=str(cq.get("cq_type", "")),
            key_entities=tuple(str(item) for item in cq.get("key_entities", [])),
            answer_key=str(cq.get("expected_answer", "")),
            gold_level="page",
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GoldLabel":
        spans = tuple(
            EvidenceSpan.from_dict(item)
            for item in data.get("evidence_spans", [])
            if isinstance(item, dict)
        )
        chunk_ids = tuple(str(item) for item in data.get("expected_chunk_ids", []))
        explicit_level = str(data.get("gold_level", "")).strip().lower()
        expected_abstention = bool(data.get("expected_abstention", False))
        inferred_level = (
            "no_answer" if expected_abstention else "span" if spans else "chunk" if chunk_ids else "page"
        )
        return cls(
            cq_id=str(data.get("cq_id") or data.get("id")),
            source_document=str(data.get("source_document", "")),
            source_page=int(data.get("source_page", -1)),
            question=str(data.get("question") or data.get("competency_question", "")),
            question_type=str(data.get("question_type") or data.get("cq_type", "")),
            expected_chunk_ids=chunk_ids,
            evidence_spans=spans,
            key_entities=tuple(str(item) for item in data.get("key_entities", [])),
            answer_key=str(data.get("answer_key") or data.get("expected_answer", "")),
            gold_level=explicit_level or inferred_level,
            expected_abstention=expected_abstention
            or (explicit_level in {"no_answer", "none", "unsupported", "insufficient_evidence"}),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GoldLabelReadError(ValueError):
    """Raised when a gold-label artifact cannot be parsed with useful context."""


def load_boundary_questions(cq_path: str | Path) -> list[dict[str, Any]]:
    artifact = load_cq_artifact(cq_path)
    questions: list[dict[str, Any]] = []
    for document_id, pages in artifact.items():
        for page, items in pages.items():
            for item in items:
                questions.append({**item, "source_document": document_id, "source_page": int(page)})
    return questions


def _read_gold_payload(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if path.suffix == ".jsonl":
        labels: list[dict[str, Any]] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise TypeError("expected JSON object")
            except (json.JSONDecodeError, TypeError) as exc:
                raise GoldLabelReadError(
                    f"Invalid gold label JSONL record in {project_relative_path(path)} "
                    f"at line {line_number}: {exc}"
                ) from exc
            labels.append(item)
        return labels
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise GoldLabelReadError(
            f"Invalid gold label JSON in {project_relative_path(path)}: {exc}"
        ) from exc
    if isinstance(payload, dict):
        labels = payload.get("labels", [])
        if not isinstance(labels, list):
            raise GoldLabelReadError(
                f"Gold label file has non-list labels: {project_relative_path(path)}"
            )
        return [item for item in labels if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    raise GoldLabelReadError(f"Unsupported gold label payload: {project_relative_path(path)}")


def load_gold_labels(path: str | Path) -> dict[str, GoldLabel]:
    labels: dict[str, GoldLabel] = {}
    gold_path = Path(path)
    for index, item in enumerate(_read_gold_payload(gold_path), start=1):
        try:
            label = GoldLabel.from_dict(item)
        except (KeyError, TypeError, ValueError) as exc:
            raise GoldLabelReadError(
                f"Invalid gold label record in {project_relative_path(gold_path)} "
                f"at label {index}: {exc}"
            ) from exc
        labels[label.cq_id] = label
    return labels


def gold_labels_for_questions(
    questions: list[dict[str, Any]],
    gold_labels_path: str | Path | None = None,
) -> dict[str, GoldLabel]:
    labels = {str(question["id"]): GoldLabel.from_cq(question) for question in questions}
    if gold_labels_path is None:
        return labels
    path = Path(gold_labels_path)
    if not path.exists():
        raise FileNotFoundError(f"Gold label file not found: {project_relative_path(path)}")
    labels.update(load_gold_labels(path))
    return labels
