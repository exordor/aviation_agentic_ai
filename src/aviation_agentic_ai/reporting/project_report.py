from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.config import load_yaml
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.hygiene import build_hygiene_plan


PROJECT_REPORT_SECTIONS = (
    "Project motivation and course objective alignment",
    "Architecture overview",
    "Ontology/TBox generation and evaluation",
    "KG/ABox extraction and validation",
    "Chunking comparison design",
    "Hybrid RAG protocol and layered metrics",
    "Current results and limitations",
    "Advisory assistant boundary",
    "Next work plan",
    "Reproducibility appendix",
)

LLMRunner = Callable[[str, float, int], str]


def _read_text_source(
    path: Path,
    *,
    base: str | Path = PROJECT_ROOT,
    max_chars: int = 4000,
) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": project_relative_path(path, base=base),
            "present": False,
            "excerpt": "",
        }
    text = path.read_text(encoding="utf-8")
    return {
        "path": project_relative_path(path, base=base),
        "present": True,
        "excerpt": text[:max_chars],
        "truncated": len(text) > max_chars,
    }


def _read_yaml_source(path: Path, *, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": project_relative_path(path, base=base),
            "present": False,
            "data": {},
        }
    return {
        "path": project_relative_path(path, base=base),
        "present": True,
        "data": load_yaml(path),
    }


def _read_json_source(path: Path, *, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": project_relative_path(path, base=base),
            "present": False,
            "data": {},
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": project_relative_path(path, base=base),
        "present": True,
        "data": data if isinstance(data, dict) else {"value": data},
    }


def build_project_evidence_pack(
    *,
    project_root: str | Path = PROJECT_ROOT,
    stage_index_path: str | Path | None = None,
    stage_dir: str | Path | None = None,
    reviews_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(project_root)
    stages = Path(stage_dir) if stage_dir is not None else root / "reports" / "stages"
    reviews = Path(reviews_dir) if reviews_dir is not None else root / "reports" / "reviews"
    index_path = Path(stage_index_path) if stage_index_path is not None else stages / "index.json"
    if index_path.exists():
        stage_index = _read_json_source(index_path, base=root)
    else:
        stage_index = {
            "path": project_relative_path(index_path, base=root),
            "present": False,
            "data": build_hygiene_plan(
                stages,
                root / "reports" / "archive",
                reviews,
                base=root,
            ),
        }
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "report_sections": list(PROJECT_REPORT_SECTIONS),
        "advisory_boundary": ADVISORY_BOUNDARY,
        "stage_index": stage_index,
        "readme": _read_text_source(root / "README.md", base=root),
        "course_goal": _read_text_source(root / "tmp" / "goal.md", base=root),
        "configs": {
            "default": _read_yaml_source(root / "configs" / "default.yaml", base=root),
            "ontology_generation": _read_yaml_source(
                root / "configs" / "ontology_generation.yaml",
                base=root,
            ),
            "extraction_profile": _read_yaml_source(
                root / "configs" / "extraction_profile.yaml",
                base=root,
            ),
        },
        "source_policy": {
            "env_files_read": False,
            "secrets_allowed": False,
            "missing_results_policy": "Use TBD / Not yet run; do not invent results.",
        },
    }


def _present_marker(source: dict[str, Any]) -> str:
    return "present" if source.get("present") else "missing"


def build_project_report_draft(evidence: dict[str, Any]) -> str:
    stage_index = evidence.get("stage_index", {}).get("data", {})
    categories = stage_index.get("categories", {})
    config_default = evidence.get("configs", {}).get("default", {}).get("data", {})
    retrieval_config = config_default.get("retrieval", {}) if isinstance(config_default, dict) else {}
    lines = [
        "# Aviation Agentic AI Project Report",
        "",
        "## Project motivation and course objective alignment",
        "",
        "This project investigates a reproducible aviation-domain RAG pipeline that turns "
        "FAA training text into ontology, KG, retrieval, and grounded-answer artifacts. "
        f"Course goal evidence: `{evidence['course_goal']['path']}` "
        f"({_present_marker(evidence['course_goal'])}).",
        "",
        "## Architecture overview",
        "",
        "The implementation is CLI-first and separates ontology, KG extraction, chunking, "
        "retrieval, evaluation, and reporting modules. Primary configuration evidence is "
        "`configs/default.yaml`, `configs/ontology_generation.yaml`, and "
        "`configs/extraction_profile.yaml`.",
        "",
        "## Ontology/TBox generation and evaluation",
        "",
        f"Stage index category count: {len(categories.get('ontology_evaluation', []))}. "
        "Detailed completed metrics should be cited from the archived ontology evaluation "
        "artifacts listed in the stage index.",
        "",
        "## KG/ABox extraction and validation",
        "",
        "The KG stage is designed around focused triples with provenance and deterministic "
        "validation against the extraction profile. If no validated KG experiment report is "
        "listed in the evidence pack, mark end-to-end KG results as Not yet run.",
        "",
        "## Chunking comparison design",
        "",
        f"RAG experiment artifacts listed: {len(categories.get('rag_experiments', []))}. "
        "Chunking comparison should discuss retrieval tradeoffs rather than collapse them "
        "into a single score.",
        "",
        "## Hybrid RAG protocol and layered metrics",
        "",
        "Hybrid RAG uses separate retrieval, KG evidence, and LLM answer metrics. "
        f"Configured retrieval defaults include vector_top_k="
        f"{retrieval_config.get('vector_top_k', 'TBD')}, graph_hops="
        f"{retrieval_config.get('graph_hops', 'TBD')}, and hybrid_top_k="
        f"{retrieval_config.get('hybrid_top_k', 'TBD')}.",
        "",
        "## Current results and limitations",
        "",
        "Current results must be reported only when present in the evidence pack. Missing "
        "full-loop experiments should be labeled TBD / Not yet run.",
        "",
        "## Advisory assistant boundary",
        "",
        evidence["advisory_boundary"],
        "",
        "## Next work plan",
        "",
        "1. Run report hygiene to maintain a readable stage dashboard.",
        "2. Run chunking comparison and Hybrid RAG experiments with recorded run manifests.",
        "3. Refine gold labels from source-page to chunk/span evidence.",
        "4. Use the AI report command to polish this deterministic draft.",
        "",
        "## Reproducibility appendix",
        "",
        "- `uv run aviation-ai report hygiene --apply`",
        "- `uv run aviation-ai report project --no-ai`",
        "- `uv run aviation-ai report project --ai`",
        "",
        "## Evidence Sources",
        "",
        f"- Stage index: `{evidence['stage_index']['path']}` "
        f"({_present_marker(evidence['stage_index'])})",
        f"- README: `{evidence['readme']['path']}` ({_present_marker(evidence['readme'])})",
        f"- Goal: `{evidence['course_goal']['path']}` "
        f"({_present_marker(evidence['course_goal'])})",
        "- Configs: `configs/default.yaml`, `configs/ontology_generation.yaml`, "
        "`configs/extraction_profile.yaml`",
        "",
    ]
    return "\n".join(lines)


def build_project_report_prompt(evidence: dict[str, Any], draft: str) -> str:
    evidence_json = json.dumps(evidence, indent=2, sort_keys=True)
    return (
        "Write a complete Markdown project report for the Aviation Agentic AI project.\n\n"
        "Rules:\n"
        "- Use only the evidence pack and deterministic draft below.\n"
        "- Cite source file paths inline when making factual claims.\n"
        "- Do not invent completed experiments, metrics, models, or results.\n"
        "- If evidence is missing, write TBD or Not yet run.\n"
        "- Do not include API keys, tokens, secrets, or environment variable values.\n"
        "- Preserve the advisory boundary and do not claim the assistant replaces POH, "
        "checklists, ATC, instructor guidance, or pilot judgment.\n"
        "- Keep all required sections from the deterministic draft.\n\n"
        f"Deterministic draft:\n---\n{draft}\n---\n\n"
        f"Evidence pack JSON:\n---\n{evidence_json[:20000]}\n---\n"
    )


def _invoke_llm_project_report(prompt: str, temperature: float, max_tokens: int) -> str:
    try:
        from langchain_core.messages import HumanMessage
    except ImportError as exc:
        raise RuntimeError(
            "AI project report generation requires optional ontology-generation dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    from aviation_agentic_ai.llm.providers import get_llm

    response = get_llm(temperature=temperature, max_tokens=max_tokens).invoke(
        [HumanMessage(content=prompt)]
    )
    return str(getattr(response, "content", response)).strip()


def write_project_report_sources(evidence: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_project_report_markdown(markdown: str, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    return path


def write_project_report(
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    stage_index_path: str | Path | None = None,
    use_ai: bool = False,
    llm_runner: LLMRunner | None = None,
    temperature: float = 0.0,
    max_tokens: int = 4096,
) -> tuple[Path, Path, dict[str, Any]]:
    evidence = build_project_evidence_pack(
        project_root=project_root,
        stage_index_path=stage_index_path,
    )
    draft = build_project_report_draft(evidence)
    prompt = build_project_report_prompt(evidence, draft)
    if use_ai:
        runner = llm_runner or _invoke_llm_project_report
        markdown = runner(prompt, temperature, max_tokens)
    else:
        markdown = draft
    output = Path(output_dir)
    md_path = write_project_report_markdown(markdown, output / "project_report.md")
    sources_path = write_project_report_sources(evidence, output / "project_report_sources.json")
    return md_path, sources_path, {
        "used_ai": use_ai,
        "prompt": prompt,
        "markdown": markdown,
        "sources": evidence,
        "output_paths": {
            "markdown": project_relative_path(md_path),
            "sources": project_relative_path(sources_path),
        },
    }
