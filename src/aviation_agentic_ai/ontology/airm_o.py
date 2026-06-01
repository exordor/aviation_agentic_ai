from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from hashlib import sha256
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path


USER_AGENT = "aviation-agentic-ai-research/0.1"
AIRM_O_EXTERNAL_DIR = Path("data/ontology/external/airm_o")
AIRM_O_ALIGNMENT_JSONL = Path("data/ontology/mappings/atmonto_airm_alignment.jsonl")
AIRM_O_REPORT_JSON = Path("reports/stages/airm_o_ontology_alignment.json")
AIRM_O_REPORT_MD = Path("reports/stages/airm_o_ontology_alignment.md")

RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS_NS = "http://www.w3.org/2000/01/rdf-schema#"
OWL_NS = "http://www.w3.org/2002/07/owl#"
NS = {"rdf": RDF_NS, "rdfs": RDFS_NS, "owl": OWL_NS}


@dataclass(frozen=True)
class AirmOArtifact:
    source_id: str
    title: str
    url: str
    file_name: str
    role: str
    format: str


AIRM_O_ARTIFACTS: tuple[AirmOArtifact, ...] = (
    AirmOArtifact(
        source_id="airm_o_readme",
        title="AIRM-O README",
        url="https://raw.githubusercontent.com/airm-o/airm-o/master/README.md",
        file_name="README.md",
        role="citation_and_license_note",
        format="markdown",
    ),
    AirmOArtifact(
        source_id="airm_o_owl",
        title="AIRM-O OWL ontology",
        url="https://raw.githubusercontent.com/airm-o/airm-o/master/airm-o.owl",
        file_name="airm-o.owl",
        role="external_reference_ontology",
        format="owl_xml",
    ),
    AirmOArtifact(
        source_id="airm_o_ttl",
        title="AIRM-O Turtle serialization",
        url="https://raw.githubusercontent.com/airm-o/airm-o/master/docs/ontology.ttl",
        file_name="ontology.ttl",
        role="external_reference_ontology_serialization",
        format="turtle",
    ),
    AirmOArtifact(
        source_id="atmonto2airm_equivalence",
        title="ATMONTO to AIRM-O equivalence reference alignment",
        url=(
            "https://raw.githubusercontent.com/airm-o/atmonto2airm/master/"
            "ReferenceAlignment-ATMONTO-AIRM-EQUIVALENCE.rdf"
        ),
        file_name="ReferenceAlignment-ATMONTO-AIRM-EQUIVALENCE.rdf",
        role="schema_alignment",
        format="alignment_rdf",
    ),
    AirmOArtifact(
        source_id="atmonto2airm_subsumption",
        title="ATMONTO to AIRM-O subsumption reference alignment",
        url=(
            "https://raw.githubusercontent.com/airm-o/atmonto2airm/master/"
            "ReferenceAlignment-ATMONTO-AIRM-SUBSUMPTION.rdf"
        ),
        file_name="ReferenceAlignment-ATMONTO-AIRM-SUBSUMPTION.rdf",
        role="schema_alignment",
        format="alignment_rdf",
    ),
)


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def digest_bytes(body: bytes) -> str:
    return sha256(body).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True, ensure_ascii=False) for record in records)
        + ("\n" if records else ""),
        encoding="utf-8",
    )


def term_name(iri: str | None) -> str:
    if not iri:
        return ""
    if "#" in iri:
        return iri.rsplit("#", 1)[-1]
    return iri.rstrip("/").rsplit("/", 1)[-1]


def node_resource(node: ET.Element | None) -> str | None:
    if node is None:
        return None
    return node.attrib.get(f"{{{RDF_NS}}}resource")


def node_about(node: ET.Element) -> str | None:
    return node.attrib.get(f"{{{RDF_NS}}}about") or node.attrib.get(f"{{{RDF_NS}}}ID")


def first_text(node: ET.Element, tag: str) -> str:
    child = node.find(tag, NS)
    if child is None or child.text is None:
        return ""
    return " ".join(child.text.split())


def resources(node: ET.Element, tag: str) -> list[str]:
    values = [
        term_name(resource)
        for child in node.findall(tag, NS)
        if (resource := node_resource(child))
    ]
    return [value for value in values if value]


def ontology_terms(root: ET.Element, owl_type: str) -> dict[str, dict[str, object]]:
    terms: dict[str, dict[str, object]] = {}
    for node in root.findall(f".//owl:{owl_type}", NS):
        iri = node_about(node)
        name = term_name(iri)
        if not name:
            continue
        entry: dict[str, object] = {
            "iri": iri,
            "comment": first_text(node, "rdfs:comment"),
        }
        if owl_type in {"ObjectProperty", "DatatypeProperty"}:
            entry["domain"] = resources(node, "rdfs:domain")
            entry["range"] = resources(node, "rdfs:range")
        terms[name] = entry
    return terms


def parse_airm_o_ontology(body: bytes) -> dict[str, object]:
    """Parse high-level AIRM-O ontology inventory from OWL/XML bytes."""
    root = ET.fromstring(body)
    ontology = root.find("owl:Ontology", NS)
    ontology_iri = node_about(ontology) if ontology is not None else None
    version_iri = None
    if ontology is not None:
        version_iri = node_resource(ontology.find("owl:versionIRI", NS))

    classes = ontology_terms(root, "Class")
    object_properties = ontology_terms(root, "ObjectProperty")
    datatype_properties = ontology_terms(root, "DatatypeProperty")
    named_individuals = ontology_terms(root, "NamedIndividual")

    return {
        "ontology_iri": ontology_iri,
        "version_iri": version_iri,
        "counts": {
            "classes": len(classes),
            "object_properties": len(object_properties),
            "datatype_properties": len(datatype_properties),
            "named_individuals": len(named_individuals),
            "domain_axioms": len(root.findall(".//rdfs:domain", NS)),
            "range_axioms": len(root.findall(".//rdfs:range", NS)),
            "comments": len(root.findall(".//rdfs:comment", NS)),
        },
        "terms": {
            "classes": classes,
            "object_properties": object_properties,
            "datatype_properties": datatype_properties,
            "named_individuals": named_individuals,
        },
    }


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def find_child_by_local_name(node: ET.Element, name: str) -> ET.Element | None:
    for child in node:
        if local_name(child.tag) == name:
            return child
    return None


def is_atmonto_iri(iri: str | None) -> bool:
    return bool(
        iri
        and (
            "data.nasa.gov/ontologies/atmonto" in iri
            or "atmweb.arc.nasa.gov/ontology" in iri
        )
    )


def is_airm_iri(iri: str | None) -> bool:
    return bool(iri and ("airm-o" in iri or "w3id.org/airm-o" in iri))


def relation_kind(symbol: str, *, atmonto_is_entity1: bool) -> str:
    if symbol == "=":
        return "equivalent"
    if symbol == "<":
        return "atmonto_subclass_of_airm" if atmonto_is_entity1 else "airm_subclass_of_atmonto"
    if symbol == ">":
        return "atmonto_superclass_of_airm" if atmonto_is_entity1 else "airm_superclass_of_atmonto"
    return "unclassified_alignment"


def parse_atmonto_airm_alignment(
    body: bytes,
    *,
    source_id: str,
    source_file: str,
) -> list[dict[str, object]]:
    """Parse Alignment API RDF cells into project mapping-rule seed records."""
    root = ET.fromstring(body)
    cells = [node for node in root.iter() if local_name(node.tag) == "Cell"]
    records: list[dict[str, object]] = []
    for index, cell in enumerate(cells, start=1):
        entity1 = node_resource(find_child_by_local_name(cell, "entity1"))
        entity2 = node_resource(find_child_by_local_name(cell, "entity2"))
        relation_node = find_child_by_local_name(cell, "relation")
        symbol = (relation_node.text or "").strip() if relation_node is not None else ""
        measure_node = find_child_by_local_name(cell, "measure")
        confidence = None
        if measure_node is not None and measure_node.text:
            try:
                confidence = float(measure_node.text.strip())
            except ValueError:
                confidence = None

        entity1_is_atmonto = is_atmonto_iri(entity1)
        entity2_is_atmonto = is_atmonto_iri(entity2)
        if entity1_is_atmonto and is_airm_iri(entity2):
            atmonto_iri, airm_iri = entity1, entity2
            atmonto_is_entity1 = True
        elif entity2_is_atmonto and is_airm_iri(entity1):
            atmonto_iri, airm_iri = entity2, entity1
            atmonto_is_entity1 = False
        else:
            atmonto_iri, airm_iri = entity1, entity2
            atmonto_is_entity1 = True

        records.append(
            {
                "mapping_id": f"{source_id}:{index:04d}",
                "source_alignment": source_id,
                "source_file": source_file,
                "entity1_iri": entity1,
                "entity2_iri": entity2,
                "atmonto_iri": atmonto_iri,
                "airm_iri": airm_iri,
                "atmonto_term": term_name(atmonto_iri),
                "airm_term": term_name(airm_iri),
                "relation_symbol": symbol,
                "relation_kind": relation_kind(symbol, atmonto_is_entity1=atmonto_is_entity1),
                "confidence": confidence,
                "use_scope": "schema_mapping_audit",
                "boundary": "reference_alignment_not_abox_fact",
            }
        )
    return records


def default_fetch_bytes(url: str, timeout: int) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_artifact(
    artifact: AirmOArtifact,
    output_dir: Path,
    *,
    repo_root: Path,
    timeout: int,
    resume: bool,
    fetch_bytes: Callable[[str, int], bytes],
) -> tuple[bytes, dict[str, object]]:
    raw_path = output_dir / artifact.file_name
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    cached = resume and raw_path.exists() and raw_path.stat().st_size > 0
    if cached:
        body = raw_path.read_bytes()
    else:
        body = fetch_bytes(artifact.url, timeout)
        tmp_path = raw_path.with_name(f".{raw_path.name}.tmp")
        tmp_path.write_bytes(body)
        tmp_path.replace(raw_path)
    return body, {
        "source_id": artifact.source_id,
        "title": artifact.title,
        "source_url": artifact.url,
        "raw_file": project_relative_path(raw_path, repo_root),
        "raw_payload_hash": digest_bytes(body),
        "bytes": len(body),
        "cached": cached,
        "role": artifact.role,
        "format": artifact.format,
    }


def write_markdown_report(path: Path, report: dict[str, object]) -> None:
    ontology_counts = report["ontology_inventory"]["counts"]  # type: ignore[index]
    relation_counts = report["relation_counts"]
    lines = [
        "# AIRM-O Ontology Alignment",
        "",
        f"- Snapshot date: {report['snapshot_date']}",
        f"- Retrieved at: {report['retrieved_at']}",
        f"- Role: `{report['role']}`",
        f"- Boundary: `{report['boundary']}`",
        f"- Manifest: `{report['manifest']}`",
        f"- Alignment JSONL: `{report['alignment_jsonl']}`",
        "",
        "## AIRM-O Inventory",
        "",
        f"- Classes: {ontology_counts['classes']}",
        f"- Object properties: {ontology_counts['object_properties']}",
        f"- Datatype properties: {ontology_counts['datatype_properties']}",
        f"- Named individuals: {ontology_counts['named_individuals']}",
        f"- Domain axioms: {ontology_counts['domain_axioms']}",
        f"- Range axioms: {ontology_counts['range_axioms']}",
        "",
        "## ATMONTO Alignment",
        "",
        f"- Mapping records: {report['mapping_record_count']}",
    ]
    assert isinstance(relation_counts, dict)
    for relation, count in sorted(relation_counts.items()):
        lines.append(f"- `{relation}`: {count}")
    lines.extend(
        [
            "",
            "## Use In Project Pipeline",
            "",
            "- Use NASA ATMONTO as the primary schema constraint.",
            "- Use AIRM-O as an external ATM interoperability reference.",
            "- Use the alignment JSONL for profile coverage, mapping audits, and extension-gap analysis.",
            "- Do not treat AIRM-O or the alignment records as ABox facts or experiment ground truth.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def collect_airm_o_pipeline(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    snapshot_date: str | None = None,
    timeout: int = 180,
    resume: bool = True,
    fetch_bytes: Callable[[str, int], bytes] = default_fetch_bytes,
) -> dict[str, object]:
    repo_root = Path(repo_root).resolve()
    snapshot_date = snapshot_date or date.today().isoformat()
    external_dir = repo_root / AIRM_O_EXTERNAL_DIR
    mapping_path = repo_root / AIRM_O_ALIGNMENT_JSONL
    report_json_path = repo_root / AIRM_O_REPORT_JSON
    report_md_path = repo_root / AIRM_O_REPORT_MD
    retrieved_at = utc_now()

    bodies: dict[str, bytes] = {}
    files: list[dict[str, object]] = []
    for artifact in AIRM_O_ARTIFACTS:
        body, entry = fetch_artifact(
            artifact,
            external_dir,
            repo_root=repo_root,
            timeout=timeout,
            resume=resume,
            fetch_bytes=fetch_bytes,
        )
        bodies[artifact.source_id] = body
        files.append(entry)

    ontology_inventory = parse_airm_o_ontology(bodies["airm_o_owl"])

    alignment_records: list[dict[str, object]] = []
    raw_file_by_source_id = {
        str(entry["source_id"]): str(entry["raw_file"])
        for entry in files
    }
    for source_id in ("atmonto2airm_equivalence", "atmonto2airm_subsumption"):
        alignment_records.extend(
            parse_atmonto_airm_alignment(
                bodies[source_id],
                source_id=source_id,
                source_file=raw_file_by_source_id[source_id],
            )
        )
    write_jsonl(mapping_path, alignment_records)

    relation_counts = Counter(str(record["relation_kind"]) for record in alignment_records)
    manifest_path = external_dir / "manifest.json"
    manifest: dict[str, object] = {
        "source_family": "airm_o_external_ontology",
        "snapshot_date": snapshot_date,
        "retrieved_at": retrieved_at,
        "role": "external_reference_ontology",
        "boundary": "external_reference_not_experiment_ground_truth",
        "scope": {
            "primary_schema": "NASA ATMONTO remains the project schema constraint.",
            "airm_o_role": (
                "AIRM-O supplies an external ATM interoperability vocabulary and "
                "domain/range reference for mapping audits."
            ),
            "alignment_role": (
                "ATMONTO2AIRM cells seed profile coverage and extension-gap analysis; "
                "they are not ABox facts."
            ),
        },
        "license_or_access_note": (
            "AIRM-O README declares the ontology under Creative Commons Attribution 4.0; "
            "alignment files are used as public reference artifacts."
        ),
        "parser_version": "aviation_agentic_ai.ontology.airm_o",
        "ontology_inventory": ontology_inventory,
        "mapping_record_count": len(alignment_records),
        "relation_counts": dict(sorted(relation_counts.items())),
        "alignment_jsonl": project_relative_path(mapping_path, repo_root),
        "known_limitations": [
            "AIRM-O is an external EUROCONTROL/AIRM-derived ontology, not a NASA/FAA data source.",
            "Alignment cells are schema-level references and require review before runtime validation use.",
            "AIRM-O domain/range constraints can inform audits but do not prove extracted triple truth.",
        ],
        "files": files,
    }
    write_json(manifest_path, manifest)

    report = {
        "source_family": manifest["source_family"],
        "snapshot_date": snapshot_date,
        "retrieved_at": retrieved_at,
        "role": manifest["role"],
        "boundary": manifest["boundary"],
        "manifest": project_relative_path(manifest_path, repo_root),
        "alignment_jsonl": project_relative_path(mapping_path, repo_root),
        "mapping_record_count": len(alignment_records),
        "relation_counts": dict(sorted(relation_counts.items())),
        "ontology_inventory": ontology_inventory,
        "files": files,
        "pipeline_integration": {
            "stage": "ontology_alignment_reference",
            "before": "runtime profile coverage and mapping-rule review",
            "after": "NASA ATMONTO profile construction and KG extraction validation",
        },
    }
    write_json(report_json_path, report)
    write_markdown_report(report_md_path, report)

    return {
        "manifest": project_relative_path(manifest_path, repo_root),
        "alignment_jsonl": project_relative_path(mapping_path, repo_root),
        "report_json": project_relative_path(report_json_path, repo_root),
        "report_markdown": project_relative_path(report_md_path, repo_root),
        "mapping_record_count": len(alignment_records),
        "ontology_counts": ontology_inventory["counts"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect AIRM-O and ATMONTO2AIRM artifacts.")
    parser.add_argument(
        "--snapshot-date",
        default=date.today().isoformat(),
        help="Snapshot date, YYYY-MM-DD. Defaults to today's local date.",
    )
    parser.add_argument(
        "--repo-root",
        default=PROJECT_ROOT,
        type=Path,
        help="Repository root.",
    )
    parser.add_argument("--timeout", default=180, type=int, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Fetch every file again even when a non-empty local file already exists.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = collect_airm_o_pipeline(
        args.repo_root,
        snapshot_date=args.snapshot_date,
        timeout=args.timeout,
        resume=not args.no_resume,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"AIRM-O collection failed: {exc}", file=sys.stderr)
        raise
