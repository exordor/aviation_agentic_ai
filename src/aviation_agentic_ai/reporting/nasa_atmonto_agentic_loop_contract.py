from __future__ import annotations

from pathlib import Path


DEFAULT_CQ_MANIFEST_PATH = Path("data/evaluation/nasa_atmonto/atcscc_cq_query_manifest.json")
DEFAULT_PREDICTION_VALIDATION_PATH = Path(
    "reports/stages/nasa_atmonto_prediction_output_validation.json"
)
DEFAULT_EXTRACTION_SCHEMA_PATH = Path(
    "data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json"
)
DEFAULT_SOURCE_BRIEF_REPORT_NAME = "atcscc_source_brief"
DEFAULT_SRD_REPORT_NAME = "atcscc_semantic_requirements"
DEFAULT_TIP_REPORT_NAME = "atcscc_technical_implementation_plan"
DEFAULT_PLAN_REPORT_NAME = "atcscc_extraction_validation_plan"
DEFAULT_EXTRACTION_PLAN_REPORT_NAME = "atcscc_extraction_plan"
DEFAULT_VALIDATION_FINDINGS_REPORT_NAME = "atcscc_validation_findings"
DEFAULT_EVIDENCE_SUPPORT_FINDINGS_REPORT_NAME = "atcscc_evidence_support_findings"
DEFAULT_REPAIR_PLAN_REPORT_NAME = "atcscc_repair_plan"

METHOD_FAMILIES: tuple[dict[str, str], ...] = (
    {
        "family": "Claim KG and GraphRAG",
        "transferred_principle": (
            "Treat extracted claims/triples as testable artifacts, then evaluate them "
            "against downstream retrieval and question-answering behavior."
        ),
    },
    {
        "family": "Multi-agent ontology generation",
        "transferred_principle": (
            "Separate extractor, validator, critic, and refiner roles so validation "
            "failures drive a bounded repair loop instead of a one-shot extraction."
        ),
    },
    {
        "family": "Ontology engineering and competency questions",
        "transferred_principle": (
            "Use CQs as an executable requirements contract rather than as informal "
            "examples of expected questions."
        ),
    },
    {
        "family": "KG quality and evidence provenance",
        "transferred_principle": (
            "Score semantic correctness, structural conformance, and evidence support "
            "as separate dimensions."
        ),
    },
    {
        "family": "GraphRAG evaluation",
        "transferred_principle": (
            "Keep graph quality tied to answerability, citation support, and abstention "
            "behavior instead of ontological completeness alone."
        ),
    },
)

PIPELINE_STAGES: tuple[dict[str, str], ...] = (
    {
        "stage_id": "P01",
        "name": "method_synthesis",
        "role": "Research method abstraction from multiple reference papers.",
    },
    {
        "stage_id": "P02",
        "name": "semantic_requirements",
        "role": "Source Requirement Document (SRD): domain entities, predicates, constraints, and CQs.",
    },
    {
        "stage_id": "P03",
        "name": "technical_implementation_plan",
        "role": "TIP: ontology reuse decisions, profile gaps, schema slices, and extraction routes.",
    },
    {
        "stage_id": "P04",
        "name": "candidate_extraction",
        "role": "Extractor agent produces schema-bound candidate triples with evidence text.",
    },
    {
        "stage_id": "P05",
        "name": "validation",
        "role": "Validator agent checks JSON schema, ontology/profile constraints, and evidence presence.",
    },
    {
        "stage_id": "P06",
        "name": "critic_review",
        "role": "Critic agent flags unsupported, over-broad, or source-unbounded facts.",
    },
    {
        "stage_id": "P07",
        "name": "repair_or_abstain",
        "role": "Refiner repairs facts only when evidence and schema constraints permit it.",
    },
    {
        "stage_id": "P08",
        "name": "graph_and_graphrag_evaluation",
        "role": "Materialize graph queries and later GraphRAG answer-set/citation evaluations.",
    },
    {
        "stage_id": "P09",
        "name": "code_review_gate",
        "role": "Abnormal experiment diagnostics trigger code review before another extraction pass.",
    },
)
