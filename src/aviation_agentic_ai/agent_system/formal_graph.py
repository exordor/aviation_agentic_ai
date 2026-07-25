"""Formal Graph Kernel: the deterministic gate between model output and the
formal knowledge graph (plan §4, §5.4).

This is **deterministic infrastructure**, not an Agent (plan §4.3). It takes a
parsed Graph Patch and the resolved evidence cards, runs every proposed fact
through the authority/schema/source/evidence checks in plan §5.4, and emits
``ValidatedFact`` objects only for facts that pass all checks. A single
non-publishable result must not produce formal graph artifacts.

Checks per proposed fact (in order):

1. Subject is the program-supplied event IRI or a known canonical entity.
2. Class and property belong to the active Schema Guide.
3. An object-property object exists in the canonical registry.
4. Object class satisfies the declared range.
5. Subject class satisfies the declared domain.
6. Literal datatype is the Schema Guide datatype.
7. Enumerated value is in the active allowed-value set.
8. Every source ID is registered and non-empty.
9. Every fact binds to source-contained evidence.
10. Applicable exact-cardinality constraints are satisfied.

Graph-level constraints (plan §5.4 GroundStop):

- exactly one ``atm:controlledNASelement``;
- exactly one ``atm:extensionProbability``;
- the active allowed values for extension probability;
- the active allowed values for impacting condition when present.

Provenance (plan §4.2) is derived here, not from the KG Construction Agent:
every accepted fact carries the source IDs and bound evidence texts.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.contracts import (
    EvidenceCard,
    EvidenceClaim,
    FactTraceRow,
    GraphPatchBlock,
    GraphPatchLine,
    GraphValidationResult,
    ProfileGap,
    RejectedFact,
    SourceSnapshot,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.schema_guide import (
    SchemaGuide,
    TRACE_PREDICATES,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id

# Predicate that asserts an entity's ontology class.
RDF_TYPE = "rdf:type"

# Datatype validation (plan §5.4 check 6). Mirrors the materializer's literal
# checks so the kernel and the (deferred) RDF writer agree on what is valid.
_DATE_TIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})$"
)

# Required (class, property) exact-cardinality constraints enforced for the
# Ground Stop mainline (plan §5.4). The kernel looks these up via SchemaGuide;
# this table names the constraints the slice must declare for atm:GroundStopTMI.
GROUND_STOP_REQUIRED: tuple[tuple[str, str], ...] = (
    ("atm:GroundStopTMI", "atm:controlledNASelement"),
    ("atm:GroundStopTMI", "atm:extensionProbability"),
)


# ---------------------------------------------------------------------------
# Evidence index (claim-level, source-contained)
# ---------------------------------------------------------------------------


def build_evidence_index(
    evidence_cards: list[EvidenceCard], source_snapshot: SourceSnapshot
) -> dict[str, list[EvidenceClaim]]:
    """Index ``source_id -> [EvidenceClaim, ...]`` (source-contained claims only).

    Plan §11.1-3: the evidence gate is fact-to-claim, not source-to-source.
    Only claims whose ``evidence_text`` appears verbatim in the source snapshot
    survive (plan §5.2). The Formal Graph Kernel then binds each proposed fact
    to the *specific* claim that supports it via :func:`_bind_claim`.
    """

    index: dict[str, list[EvidenceClaim]] = defaultdict(list)
    snapshot_content = source_snapshot.content
    for card in evidence_cards:
        for claim in card.claims:
            if not claim.source_id or not claim.evidence_text:
                continue
            # Source-containment gate: drop any claim whose text is not verbatim
            # in the snapshot content for its source.
            if claim.evidence_text not in snapshot_content:
                continue
            index[claim.source_id].append(claim)
    return dict(index)


# Datatype-value normalization for fact-to-claim value comparison (plan §11.2,
# §12). The advisory parse layer anchors period tokens to full UTC timestamps
# (e.g. ``2026-05-19T21:00:00Z``); the formal graph stores the same xsd:dateTime
# form. The Kernel compares COMPLETE normalized UTC timestamps — it must not
# discard year or month, and it must not infer a missing calendar context from a
# proposed patch (plan §12).

_ISO_DT_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?$"
)


def _canonical_period_key(value: str) -> str:
    """The canonical comparable form of an effective-time value (plan §12).

    A complete UTC timestamp (``YYYY-MM-DDTHH:MM:SSZ``) is returned as-is. A raw
    ``DD/HHMMZ`` token has NO calendar context in the Kernel and is returned
    unchanged so it cannot match a full timestamp — the advisory parse layer is
    the only place that anchors a raw token to a full date. The Kernel never
    discards year or month and never guesses a calendar context.
    """

    raw = (value or "").strip()
    if _ISO_DT_RE.match(raw):
        return raw
    return raw


def _normalize_dt(value: str) -> str:
    """Canonical form for dateTime comparison: the complete UTC timestamp."""

    return _canonical_period_key(value)


_DATE_TIME_NORMALIZERS = {
    "atm:effectiveStartTime": _normalize_dt,
    "atm:effectiveEndTime": _normalize_dt,
    "atm:issuedTime": _normalize_dt,
}


def _normalize_claim_value(claim: EvidenceClaim, predicate: str) -> str:
    """Normalize an advisory claim value for comparison against a patch value."""

    raw = (claim.value or "").strip()
    if predicate in _DATE_TIME_NORMALIZERS:
        return _DATE_TIME_NORMALIZERS[predicate](raw)
    return raw


def _normalize_patch_value(value: str, predicate: str) -> str:
    """Normalize a patch literal for comparison against a claim value."""

    raw = (value or "").strip()
    if predicate in _DATE_TIME_NORMALIZERS:
        return _DATE_TIME_NORMALIZERS[predicate](raw)
    return raw


def _bind_claim(
    line: GraphPatchLine,
    *,
    predicate: str,
    object_value: str,
    subject_class: str,
    evidence_index: dict[str, list[EvidenceClaim]],
) -> EvidenceClaim | None:
    """Deterministic fact-to-claim binding (plan §11.2).

    Returns the single EvidenceClaim that supports this proposed fact, or None.
    There is no generic fallback from a source ID to arbitrary evidence in that
    source — each predicate binds to the specific claim field/ontology target/
    canonical ref/value it represents.
    """

    norm_patch = _normalize_patch_value(object_value, predicate)
    for sid in line.source_ids:
        for claim in evidence_index.get(sid, []):
            if _claim_matches(claim, predicate=predicate, object_value=object_value,
                              norm_patch=norm_patch):
                return claim
    return None


def _claim_matches(
    claim: EvidenceClaim,
    *,
    predicate: str,
    object_value: str,
    norm_patch: str,
) -> bool:
    """Whether ``claim`` is the specific evidence for this predicate+object."""

    # rdf:type -> a terminology claim whose ontology_target equals the class.
    if predicate == RDF_TYPE:
        return bool(claim.ontology_target) and claim.ontology_target == object_value
    # atm:controlledNASelement -> a facility claim whose canonical_ref is the object.
    if predicate == "atm:controlledNASelement":
        return bool(claim.canonical_ref) and claim.canonical_ref == object_value
    # atm:advisoryNumber -> the advisory-number claim with the same value.
    if predicate == "atm:advisoryNumber":
        return claim.field_name == "advisory_number" and (claim.value or "").strip() == norm_patch
    # atm:effectiveStartTime/EndTime -> the matching advisory claim after dt normalization.
    if predicate in ("atm:effectiveStartTime", "atm:effectiveEndTime"):
        wanted = "effective_start" if predicate == "atm:effectiveStartTime" else "effective_end"
        return claim.field_name == wanted and _normalize_claim_value(claim, predicate) == norm_patch
    # atm:extensionProbability -> the extension-probability claim with the same value.
    if predicate == "atm:extensionProbability":
        return claim.field_name == "extension_probability" and (claim.value or "").strip() == norm_patch
    # atm:impactingCondition -> the impacting-condition claim with the same value.
    if predicate == "atm:impactingCondition":
        return claim.field_name == "impacting_condition" and (claim.value or "").strip() == norm_patch
    return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def validate_graph_patch(
    *,
    block: GraphPatchBlock,
    event_iri: str,
    event_class: str,
    schema_guide: SchemaGuide,
    canonical_entities: dict[str, str],
    known_source_ids: set[str],
    evidence_cards: list[EvidenceCard],
    source_snapshot: SourceSnapshot,
) -> GraphValidationResult:
    """Run the Formal Graph Kernel over one parsed Graph Patch (plan §5.4).

    Returns a :class:`GraphValidationResult`. ``publishable`` is True only when
    at least one fact is accepted, no row is rejected, and every required
    graph-level constraint for the event class is satisfied.
    """

    evidence_index = build_evidence_index(evidence_cards, source_snapshot)
    known_entities = dict(canonical_entities or {})
    # The event entity itself is a known subject of class event_class.
    known_entities[event_iri] = event_class

    accepted: list[ValidatedFact] = []
    rejected: list[RejectedFact] = []
    graph_errors: list[str] = []

    for line in block.patch_lines:
        outcome = _validate_line(
            line,
            event_iri=event_iri,
            event_class=event_class,
            schema_guide=schema_guide,
            known_entities=known_entities,
            known_source_ids=known_source_ids,
            evidence_index=evidence_index,
        )
        if isinstance(outcome, ValidatedFact):
            accepted.append(outcome)
        else:
            rejected.append(outcome)

    # Surface explicit, source-supported PROFILE_GAPS entries (plan §12). A
    # profile gap is NOT a formal fact and NOT a rejected row; it is recorded
    # only when its evidence is a verbatim source substring, and it must not
    # enter the formal graph.
    profile_gaps = _collect_profile_gaps(block, source_snapshot)

    # Graph-level required-property/cardinality/enum enforcement for GroundStop.
    if event_class == "atm:GroundStopTMI":
        graph_errors.extend(_ground_stop_graph_errors(accepted, schema_guide))

    publishable = bool(accepted) and not rejected and not graph_errors
    return GraphValidationResult(
        accepted=accepted,
        rejected=rejected,
        profile_gaps=profile_gaps,
        graph_errors=graph_errors,
        publishable=publishable,
    )


def _collect_profile_gaps(
    block: GraphPatchBlock, source_snapshot: SourceSnapshot
) -> list[ProfileGap]:
    """Return the parsed PROFILE_GAPS whose evidence is source-contained (§12).

    A profile gap records a source-supported field the active profile cannot
    represent. Its evidence must be a verbatim source substring; gaps whose
    evidence is not source-contained are dropped (they cannot be audited).
    """

    gaps: list[ProfileGap] = []
    for gap in block.profile_gaps:
        if gap.evidence and gap.evidence in source_snapshot.content:
            gaps.append(gap)
    return gaps


# ---------------------------------------------------------------------------
# Per-line validation (plan §5.4 checks 1-10)
# ---------------------------------------------------------------------------


def _validate_line(
    line: GraphPatchLine,
    *,
    event_iri: str,
    event_class: str,
    schema_guide: SchemaGuide,
    known_entities: dict[str, str],
    known_source_ids: set[str],
    evidence_index: dict[str, list[tuple[str, str]]],
) -> ValidatedFact | RejectedFact:
    """Validate one Graph Patch line; return a ValidatedFact or RejectedFact."""

    raw_line = _line_text(line)
    pred = line.predicate.strip()
    subject = line.subject.strip()
    obj = line.object.strip()

    # Check 1: subject is the event IRI or a known canonical entity.
    if subject != event_iri and subject not in known_entities:
        return _reject(raw_line, "subject", f"subject {subject!r} is neither the event IRI nor a known canonical entity")

    subject_class = event_class if subject == event_iri else known_entities[subject]

    # Check 8: every source ID is registered and non-empty.
    if not line.source_ids:
        return _reject(raw_line, "source_id", "no source IDs cited")
    unknown_sources = [s for s in line.source_ids if s not in known_source_ids]
    if unknown_sources:
        return _reject(
            raw_line, "source_id",
            f"source IDs not registered: {unknown_sources}",
        )

    # rdf:type assertion.
    if pred == RDF_TYPE:
        # Check 2: object must be a schema class.
        if not schema_guide.has_class(obj):
            return _reject(raw_line, "class_membership", f"rdf:type object {obj!r} is not a schema class")
        # The asserted type must be compatible (self or superclass) with the
        # subject's known class.
        if obj != subject_class and obj not in schema_guide.superclasses(subject_class):
            return _reject(
                raw_line, "class_membership",
                f"rdf:type {obj!r} incompatible with subject class {subject_class!r}",
            )
        # §11.2: rdf:type binds to a terminology claim whose ontology_target
        # equals the proposed class. No generic source-to-source fallback.
        claim = _bind_claim(line, predicate=pred, object_value=obj,
                            subject_class=subject_class, evidence_index=evidence_index)
        if claim is None:
            return _reject(raw_line, "evidence", f"no terminology claim binds rdf:type {obj!r}")
        return _to_fact(line, subject_class_iri=schema_guide.classes[obj].iri if obj in schema_guide.classes else "",
                        predicate_iri=_RDF_TYPE_IRI, object_kind="iri", object_value=obj,
                        object_class_iri=schema_guide.classes[obj].iri if obj in schema_guide.classes else None,
                        bound_claim=claim)

    # Source-trace predicate (prov:wasDerivedFrom): deterministic provenance —
    # the cited registered source snapshot is the binding (plan §11.2, §4.2).
    if pred in TRACE_PREDICATES:
        if obj not in known_source_ids:
            return _reject(
                raw_line, "provenance_endpoint",
                f"prov:wasDerivedFrom object {obj!r} is not a registered source ID",
            )
        return _to_fact(line, subject_class_iri=_class_iri(schema_guide, subject_class),
                        predicate_iri=_PROV_WAS_DERIVED_FROM_IRI, object_kind="iri", object_value=obj,
                        object_class_iri=None, bound_claim=None)

    # Object property.
    if schema_guide.is_object_property(pred):
        # Check 2: property belongs to the active Schema Guide (is_object_property
        # already confirms membership).
        # Check 5: subject class satisfies the declared domain.
        if not schema_guide.object_property_domain_ok(pred, subject_class):
            return _reject(
                raw_line, "domain",
                f"object property {pred!r} domain not satisfied by {subject_class!r}",
            )
        # Check 3: object exists in the canonical registry.
        if obj not in known_entities:
            return _reject(
                raw_line, "canonical_object",
                f"object {obj!r} is not a known canonical entity",
            )
        obj_class = known_entities[obj]
        # Check 4: object class satisfies the declared range.
        if not schema_guide.object_property_range_ok(pred, obj_class):
            return _reject(
                raw_line, "range",
                f"object property {pred!r} range not satisfied by {obj_class!r}",
            )
        # §11.2: atm:controlledNASelement binds to a facility claim whose
        # canonical_ref equals the proposed object. No generic fallback.
        claim = _bind_claim(line, predicate=pred, object_value=obj,
                            subject_class=subject_class, evidence_index=evidence_index)
        if claim is None:
            return _reject(raw_line, "evidence", f"no facility claim binds {pred} {obj!r}")
        return _to_fact(line, subject_class_iri=_class_iri(schema_guide, subject_class),
                        predicate_iri=_object_property_iri(schema_guide, pred),
                        object_kind="iri", object_value=obj,
                        object_class_iri=_class_iri(schema_guide, obj_class),
                        bound_claim=claim)

    # Datatype property.
    if schema_guide.is_datatype_property(pred):
        # Check 5: subject class satisfies the declared domain.
        if not schema_guide.datatype_property_ok(pred, subject_class):
            return _reject(
                raw_line, "domain",
                f"datatype property {pred!r} domain not satisfied by {subject_class!r}",
            )
        # Check 6: literal datatype is the Schema Guide datatype.
        dt_error = _check_datatype_value(pred, obj, schema_guide)
        if dt_error:
            return _reject(raw_line, "datatype", f"literal {obj!r}: {dt_error}")
        # Check 7: enumerated value is in the active allowed-value set.
        allowed = schema_guide.allowed_values(subject_class, pred)
        if allowed and obj not in allowed:
            return _reject(
                raw_line, "enum",
                f"value {obj!r} not in allowed values {sorted(allowed)} for {subject_class}.{pred}",
            )
        # §11.2: the datatype fact binds to the specific advisory claim for this
        # predicate whose normalized value matches the patch value.
        claim = _bind_claim(line, predicate=pred, object_value=obj,
                            subject_class=subject_class, evidence_index=evidence_index)
        if claim is None:
            return _reject(raw_line, "evidence", f"no advisory claim binds {pred} {obj!r}")
        return _to_fact(line, subject_class_iri=_class_iri(schema_guide, subject_class),
                        predicate_iri=_datatype_property_iri(schema_guide, pred),
                        object_kind="literal", object_value=obj,
                        datatype_iri=_datatype_iri(schema_guide, pred),
                        bound_claim=claim)

    # Property exists in source but not in the current profile slice -> gap.
    return _reject(
        raw_line, "schema_membership",
        f"predicate {pred!r} not in the current ATCSCC profile slice",
    )


def _to_fact(
    line: GraphPatchLine,
    *,
    subject_class_iri: str,
    predicate_iri: str,
    object_kind: str,
    object_value: str,
    bound_claim: EvidenceClaim | None,
    object_class_iri: str | None = None,
    datatype_iri: str | None = None,
) -> ValidatedFact:
    """Assemble a ValidatedFact bound to the single matched claim's evidence.

    Plan §11.3: store only the matched claim evidence on each ValidatedFact.
    ``bound_claim`` is None only for deterministic provenance
    (``prov:wasDerivedFrom``), whose binding is the cited registered source.
    """

    evidence_texts: list[str] = []
    if bound_claim is not None and bound_claim.evidence_text:
        evidence_texts.append(bound_claim.evidence_text)
    return ValidatedFact(
        fact_id=stable_id("fact", line.subject, line.predicate, object_value),
        subject_iri=line.subject,
        subject_class_iri=subject_class_iri,
        predicate_iri=predicate_iri,
        object_kind=object_kind,
        object_value=object_value,
        object_class_iri=object_class_iri,
        datatype_iri=datatype_iri,
        source_ids=list(line.source_ids),
        evidence_texts=evidence_texts,
    )


def _reject(line_text: str, rule: str, reason: str) -> RejectedFact:
    return RejectedFact(graph_patch_line=line_text, rule=rule, reason=reason)


def _line_text(line: GraphPatchLine) -> str:
    return (
        f"{line.subject} | {line.predicate} | {line.object} | "
        f"{', '.join(line.source_ids)}"
    )


# ---------------------------------------------------------------------------
# Datatype / IRI helpers
# ---------------------------------------------------------------------------


def _check_datatype_value(predicate: str, value: str, guide: SchemaGuide) -> str | None:
    """Plan §5.4 check 6: validate a literal against the slice's datatype."""

    del guide  # datatype declaration consulted by caller; kept for symmetry
    stripped = value.strip()
    if not stripped:
        return "empty literal"
    if predicate in ("atm:effectiveStartTime", "atm:effectiveEndTime", "atm:issuedTime"):
        if not _DATE_TIME_RE.match(stripped):
            return "not a valid xsd:dateTime literal"
        return None
    if predicate == "atm:advisoryNumber":
        if not stripped.isdigit():
            return "not a valid xsd:integer literal"
        return None
    return None


def _class_iri(guide: SchemaGuide, prefixed: str) -> str:
    cls = guide.classes.get(prefixed)
    return cls.iri if cls is not None else ""


def _object_property_iri(guide: SchemaGuide, prefixed: str) -> str:
    op = guide.object_properties.get(prefixed)
    return op.iri if op is not None else ""


def _datatype_property_iri(guide: SchemaGuide, prefixed: str) -> str:
    dp = guide.datatype_properties.get(prefixed)
    return dp.iri if dp is not None else ""


def _datatype_iri(guide: SchemaGuide, prefixed: str) -> str | None:
    dp = guide.datatype_properties.get(prefixed)
    if dp is None or not dp.datatype:
        return None
    # The slice carries prefixed datatypes (xsd:dateTime). Convert to IRI form.
    dt = next(iter(dp.datatype))
    if dt.startswith("xsd:"):
        return f"http://www.w3.org/2001/XMLSchema#{dt.split(':', 1)[1]}"
    return dt


# Standard RDF / PROV predicate IRIs (plan §6.1 batch two uses these; the
# kernel records them now so RDF and Neo4j never reinterpret the strings).
_RDF_TYPE_IRI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
_PROV_WAS_DERIVED_FROM_IRI = "http://www.w3.org/ns/prov#wasDerivedFrom"


# ---------------------------------------------------------------------------
# GroundStop graph-level enforcement (plan §5.4)
# ---------------------------------------------------------------------------


def _ground_stop_graph_errors(
    accepted: list[ValidatedFact], guide: SchemaGuide
) -> list[str]:
    """Enforce GroundStop required exact-cardinality and enum constraints."""

    errors: list[str] = []
    # Exactly one atm:controlledNASelement on the event subject.
    controlled = [
        f for f in accepted
        if f.predicate_iri == _object_property_iri(guide, "atm:controlledNASelement")
    ]
    required_count = guide.exact_cardinality("atm:GroundStopTMI", "atm:controlledNASelement")
    if required_count is not None and len(controlled) != required_count:
        errors.append(
            f"atm:controlledNASelement exact cardinality {required_count} not satisfied "
            f"(found {len(controlled)})"
        )
    # Exactly one atm:extensionProbability.
    ext_prob = [
        f for f in accepted
        if f.predicate_iri == _datatype_property_iri(guide, "atm:extensionProbability")
    ]
    required_ext = guide.exact_cardinality("atm:GroundStopTMI", "atm:extensionProbability")
    if required_ext is not None and len(ext_prob) != required_ext:
        errors.append(
            f"atm:extensionProbability exact cardinality {required_ext} not satisfied "
            f"(found {len(ext_prob)})"
        )
    return errors


__all__ = [
    "GROUND_STOP_REQUIRED",
    "build_evidence_index",
    "validate_graph_patch",
    "write_fact_trace",
]


# Defensive: keep Any referenced for downstream typing without ruff dropping it.
_ = Any


# ---------------------------------------------------------------------------
# Fact trace (plan §5.5)
# ---------------------------------------------------------------------------


def write_fact_trace(
    *,
    result: GraphValidationResult,
    block: GraphPatchBlock,
    evidence_cards: list[EvidenceCard],
    source_snapshot: SourceSnapshot,
    output_dir: str | Path,
) -> Path:
    """Write ``fact_trace.jsonl``, one row per accepted fact (plan §5.5, §11.3).

    Each row records the fact id, the exact Graph Patch line it came from, the
    source id, the exact source-contained evidence text of the *matched* claim,
    the evidence-card agent role, and the source snapshot SHA-256. The trace
    uses the same fact-to-claim binding stored on each ValidatedFact (plan
    §11.3); it must not select an unrelated claim from the source.
    """

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "fact_trace.jsonl"
    # fact_id -> graph_patch_line lookup from the parsed block.
    line_by_fact: dict[str, str] = {}
    for line in block.patch_lines:
        fact_id = stable_id("fact", line.subject, line.predicate, line.object.strip())
        line_by_fact[fact_id] = _line_text(line)
    # evidence_text -> (agent_role, source_id) lookup so the trace can recover
    # which agent role and source the bound claim came from.
    evidence_role: dict[str, tuple[str, str]] = {}
    for card in evidence_cards:
        for claim in card.claims:
            if claim.evidence_text and claim.evidence_text in source_snapshot.content:
                evidence_role.setdefault(claim.evidence_text, (card.agent_role, claim.source_id))
    rows: list[str] = []
    for fact in result.accepted:
        line_text = line_by_fact.get(fact.fact_id, "")
        # The ValidatedFact already carries only the matched claim's evidence
        # (plan §11.3). For deterministic provenance (no bound claim) the trace
        # records the cited source with no advisory evidence text.
        evidence_text = fact.evidence_texts[0] if fact.evidence_texts else ""
        agent_role, bound_source = evidence_role.get(evidence_text, ("", ""))
        if not bound_source:
            bound_source = fact.source_ids[0] if fact.source_ids else ""
        row = FactTraceRow(
            fact_id=fact.fact_id,
            graph_patch_line=line_text,
            source_id=bound_source,
            evidence_text=evidence_text,
            evidence_agent_role=agent_role or "provenance",
            source_snapshot_sha256=source_snapshot.content_sha256,
        )
        rows.append(row.model_dump_json())
    path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")
    return path
