"""FAA JO 7210.3EE ontology profile and generation-task construction.

ATMONTO remains the semantic authority for aviation entities and TMI classes.
The FAA namespace adds only document/rule/procedure concepts that are absent
from ATMONTO.  An extraction task receives a bounded slice of both namespaces; the
model can propose facts but cannot create terms or write the store.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from aviation_agentic_ai.agent_system.faa_order_document import (
    FAAOrderExtractionChunk,
    FAAOrderSourcePackage,
)
from aviation_agentic_ai.agent_system.kg_generation_contracts import (
    EntityExtractionProposal,
    EntityExtractionTask,
    EntityResolutionResult,
    OntologyExtractionClass,
    OntologyExtractionProperty,
    OntologyExtractionSchema,
    RelationExtractionTask,
    ResolvedKnowledgeEntity,
)
from aviation_agentic_ai.agent_system.ontology_registry import (
    OntologyClassRef,
    OntologyConstraintRef,
    OntologyHierarchyRef,
    OntologyPropertyRef,
    OntologySlice,
    load_ontology_registry,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    DEFAULT_FAA_ORDER_ONTOLOGY_PROFILE_PATH,
    LoadedValidationProfile,
    load_validation_profile_registry,
)
from aviation_agentic_ai.utils.identifiers import stable_id


FAA_ORDER_PROFILE_ID = "faa-jo-7210.3ee-ontology-profile-v2"
FAA_ORDER_NAMESPACE = "urn:aviation-agentic-ai:faa7210.3ee#"
POLICY_PARAGRAPH_CLASS = f"{FAA_ORDER_NAMESPACE}PolicyParagraph"
POLICY_RULE_CLASS = f"{FAA_ORDER_NAMESPACE}PolicyRule"
PROCEDURE_REQUIREMENT_CLASS = f"{FAA_ORDER_NAMESPACE}ProcedureRequirement"
OPERATIONAL_ROLE_CLASS = f"{FAA_ORDER_NAMESPACE}OperationalRole"
ATMONTO_TMI_CLASS = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#TrafficManagementInitiative"
)
ATMONTO_GDP_CLASS = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#GroundDelayProgramTMI"
)
ATMONTO_GROUND_STOP_CLASS = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#GroundStopTMI"
)
ATMONTO_REROUTE_CLASS = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#ReRouteTMI"
)
ATMONTO_ROUTE_SEGMENT_CLASS = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#AirspaceRouteSegment"
)
NAS_FACILITY_CLASS = "https://data.nasa.gov/ontologies/atmonto/NAS#NASfacility"

_ORDER_PROFILE_PROPERTIES = (
    "rdfs:label",
    "faa:hasSection",
    "faa:hasParagraph",
    "faa:heading",
    "faa:paragraphNumber",
    "faa:pageNumber",
    "faa:topic",
    "faa:hasRule",
    "faa:mentionsEntity",
    "faa:documentEdition",
    "faa:effectiveDate",
    "faa:sectionNumber",
    "faa:policyText",
    "faa:requirementText",
    "faa:actionLevel",
    "faa:assignsResponsibilityTo",
    "faa:requiresCoordinationWith",
    "faa:appliesToTMI",
    "faa:targetsFacility",
    "faa:referencesRouteSegment",
    "faa:requires",
)

FAA_ORDER_ENTITY_FEW_SHOTS = (
    """FEW_SHOT_EXAMPLE 1
TEXT: The traffic management unit coordinates a ground stop with the center.
OUTPUT: {"status":"accepted","mentions":[{"mention_id":"e1m1","surface_text":"traffic management unit","class_iri":"urn:aviation-agentic-ai:faa7210.3ee#OperationalRole","evidence_ref":"example-1","concept_or_instance":"instance","confidence":0.94},{"mention_id":"e1m2","surface_text":"ground stop","class_iri":"https://data.nasa.gov/ontologies/atmonto/ATM#GroundStopTMI","evidence_ref":"example-1","concept_or_instance":"concept","confidence":0.99},{"mention_id":"e1m3","surface_text":"center","class_iri":"https://data.nasa.gov/ontologies/atmonto/NAS#ARTCC","evidence_ref":"example-1","concept_or_instance":"instance","confidence":0.78}],"unmapped_mentions":[],"abstentions":[]}""",
    """FEW_SHOT_EXAMPLE 2
TEXT: Facilities must review the reroute before implementation.
OUTPUT: {"status":"accepted","mentions":[{"mention_id":"e2m1","surface_text":"Facilities","class_iri":"https://data.nasa.gov/ontologies/atmonto/NAS#NASfacility","evidence_ref":"example-2","concept_or_instance":"concept","confidence":0.88},{"mention_id":"e2m2","surface_text":"reroute","class_iri":"https://data.nasa.gov/ontologies/atmonto/ATM#ReRouteTMI","evidence_ref":"example-2","concept_or_instance":"concept","confidence":0.98},{"mention_id":"e2m3","surface_text":"review the reroute before implementation","class_iri":"urn:aviation-agentic-ai:faa7210.3ee#ProcedureRequirement","evidence_ref":"example-2","concept_or_instance":"instance","confidence":0.86}],"unmapped_mentions":[],"abstentions":[]}""",
    """FEW_SHOT_EXAMPLE 3
TEXT: This guidance discusses severe weather but names no traffic measure.
OUTPUT: {"status":"accepted","mentions":[{"mention_id":"e3m1","surface_text":"severe weather","class_iri":"https://data.nasa.gov/ontologies/atmonto/data#WeatherCondition","evidence_ref":"example-3","concept_or_instance":"concept","confidence":0.91}],"unmapped_mentions":[],"abstentions":[]}""",
)

FAA_ORDER_RELATION_FEW_SHOTS = (
    """FEW_SHOT_EXAMPLE 1
Use PolicyRule --appliesToTMI--> GroundStop only when both resolved IDs and an exact quote are supplied.""",
    """FEW_SHOT_EXAMPLE 2
Use PolicyRule --requiresCoordinationWith--> OperationalRole only when the source explicitly states coordination.""",
    """FEW_SHOT_EXAMPLE 3
Return status not_applicable when no allowed object property connects the resolved entity classes.""",
)


def _order_profile() -> LoadedValidationProfile:
    registry = load_validation_profile_registry(
        decision_guide=load_schema_guide(),
        include_faa_order=True,
        faa_order_profile_path=DEFAULT_FAA_ORDER_ONTOLOGY_PROFILE_PATH,
    )
    return next(
        profile
        for profile in registry.profiles
        if profile.ref.profile_id == FAA_ORDER_PROFILE_ID
    )


def _local_name(iri: str) -> str:
    return iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def _raw_order_profile() -> dict[str, object]:
    profile = _order_profile()
    payload = json.loads(Path(profile.source_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("FAA order ontology profile must be a JSON object")
    return payload


def _mapping_rows(payload: dict[str, object], field: str) -> tuple[dict[str, object], ...]:
    rows = payload.get(field)
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"FAA order ontology profile has malformed {field}")
    return tuple(rows)


def _aliases(row: dict[str, object]) -> tuple[str, ...]:
    aliases = row.get("aliases", ())
    if not isinstance(aliases, list) or not all(
        isinstance(alias, str) and alias for alias in aliases
    ):
        raise ValueError("FAA order ontology aliases must be a string list")
    return tuple(aliases)


def compile_faa_order_extraction_schema(
    chunk: FAAOrderExtractionChunk,
) -> OntologyExtractionSchema:
    """Compile the active FAA order profile into a compact NER/RE schema."""

    profile = _order_profile()
    payload = _raw_order_profile()
    classes = tuple(
        OntologyExtractionClass(
            iri=str(row["iri"]),
            label=str(row.get("label") or _local_name(str(row["iri"]))),
            description=str(
                row.get("description")
                or f"Profile class {_local_name(str(row['iri']))}."
            ),
            aliases=_aliases(row),
            ancestor_iris=profile.class_ancestors.get(str(row["iri"]), ()),
        )
        for row in _mapping_rows(payload, "class_mappings")
    )
    properties = tuple(
        OntologyExtractionProperty(
            iri=str(row["iri"]),
            label=str(row.get("label") or _local_name(str(row["iri"]))),
            description=str(
                row.get("description")
                or f"Profile property {_local_name(str(row['iri']))}."
            ),
            aliases=_aliases(row),
            kind="object" if row.get("kind") == "object" else "datatype",
            domain_iris=tuple(str(value) for value in row.get("domain_iri_set", ())),
            range_iris=tuple(str(value) for value in row.get("range_iri_set", ())),
        )
        for row in _mapping_rows(payload, "property_mappings")
    )
    canonical = {
        "profile_id": profile.ref.profile_id,
        "profile_checksum": profile.ref.profile_checksum,
        "classes": [row.model_dump(mode="json") for row in classes],
        "properties": [row.model_dump(mode="json") for row in properties],
    }
    schema_checksum = hashlib.sha256(
        json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    prompt_lines = ["classes:"]
    for row in classes:
        aliases = ", ".join(row.aliases) or "none"
        prompt_lines.append(
            f"  - iri: {row.iri}\n"
            f"    label: {row.label}\n"
            f"    aliases: [{aliases}]\n"
            f"    description: {row.description}"
        )
    prompt_lines.append("relations:")
    for row in properties:
        aliases = ", ".join(row.aliases) or "none"
        prompt_lines.append(
            f"  - iri: {row.iri}\n"
            f"    label: {row.label}\n"
            f"    aliases: [{aliases}]\n"
            f"    kind: {row.kind}\n"
            f"    domain: [{', '.join(row.domain_iris)}]\n"
            f"    range: [{', '.join(row.range_iris)}]\n"
            f"    description: {row.description}"
        )
    return OntologyExtractionSchema(
        profile_id=profile.ref.profile_id,
        profile_checksum=profile.ref.profile_checksum,
        schema_checksum=schema_checksum,
        evidence_ref=chunk.evidence_ref,
        classes=classes,
        properties=properties,
        prompt_schema="\n".join(prompt_lines),
    )


def build_faa_order_entity_extraction_task(
    package: FAAOrderSourcePackage,
    chunk: FAAOrderExtractionChunk,
) -> EntityExtractionTask:
    """Create one sealed NER task from an immutable extraction chunk."""

    if chunk.source_version_id != package.source_version_id:
        raise ValueError("document extraction chunk is outside the source package")
    return EntityExtractionTask(
        task_id=stable_id(
            "ontology-entity-extraction-task",
            package.source_version_id,
            chunk.chunk_id,
        ),
        chunk_id=chunk.chunk_id,
        paragraph_id=chunk.paragraph_id,
        evidence_ref=chunk.evidence_ref,
        evidence_text=chunk.evidence_text,
        ontology_schema=compile_faa_order_extraction_schema(chunk),
        few_shot_examples=FAA_ORDER_ENTITY_FEW_SHOTS,
    )


def _normalised_label(value: str) -> str:
    return " ".join(value.casefold().replace("-", " ").split())


def _canonical_entity_identity(
    *,
    package: FAAOrderSourcePackage,
    chunk: FAAOrderExtractionChunk,
    class_iri: str,
    class_label: str,
    surface_text: str,
    concept_or_instance: str,
) -> tuple[str, str]:
    normalised = _normalised_label(surface_text)
    if class_iri == OPERATIONAL_ROLE_CLASS:
        if "atcscc" in normalised or "command center" in normalised:
            return "faa-role:ATCSCC", "Air Traffic Control System Command Center"
        if "artcc" in normalised or "air route traffic control center" in normalised:
            return "faa-role:ARTCC", "Air Route Traffic Control Center"
        return stable_id("faa-operational-role", normalised), surface_text.strip()
    if concept_or_instance == "concept":
        return (
            stable_id("atmonto-concept", class_iri, _normalised_label(class_label)),
            class_label,
        )
    if class_iri.startswith("https://data.nasa.gov/ontologies/atmonto/NAS#"):
        candidate = surface_text.strip().upper()
        label = (
            candidate
            if re.fullmatch(r"[A-Z][A-Z0-9]{2,3}", candidate)
            else surface_text.strip()
        )
        return (
            stable_id("faa-nas-entity", class_iri, _normalised_label(label)),
            label,
        )
    if class_iri.startswith(FAA_ORDER_NAMESPACE):
        return (
            stable_id(
                "ontology-entity",
                package.source_version_id,
                chunk.paragraph_id,
                class_iri,
                normalised,
            ),
            surface_text.strip(),
        )
    return (
        stable_id(
            "ontology-entity",
            package.source_version_id,
            chunk.paragraph_id,
            class_iri,
            normalised,
        ),
        surface_text.strip(),
    )


def normalize_faa_order_entities(
    package: FAAOrderSourcePackage,
    chunk: FAAOrderExtractionChunk,
    proposal: EntityExtractionProposal,
    schema: OntologyExtractionSchema,
) -> EntityResolutionResult:
    """Resolve exact mentions to stable IDs without using model confidence."""

    from aviation_agentic_ai.agent_system.kg_generation import locate_text_span

    classes = {row.iri: row for row in schema.classes}
    unresolved = list(proposal.unmapped_mentions)
    by_id: dict[str, ResolvedKnowledgeEntity] = {}
    for mention in proposal.mentions:
        class_row = classes.get(mention.class_iri)
        if class_row is None or mention.evidence_ref != chunk.evidence_ref:
            unresolved.append(mention.surface_text)
            continue
        local_span = locate_text_span(mention.surface_text, chunk.evidence_text)
        if local_span is None:
            unresolved.append(mention.surface_text)
            continue
        local_start, local_end = local_span
        entity_id, canonical_label = _canonical_entity_identity(
            package=package,
            chunk=chunk,
            class_iri=mention.class_iri,
            class_label=class_row.label,
            surface_text=mention.surface_text,
            concept_or_instance=mention.concept_or_instance,
        )
        global_start = chunk.char_start + local_start
        global_end = chunk.char_start + local_end
        existing = by_id.get(entity_id)
        if existing is None:
            by_id[entity_id] = ResolvedKnowledgeEntity(
                entity_id=entity_id,
                class_iri=mention.class_iri,
                canonical_label=canonical_label,
                aliases=tuple(
                    dict.fromkeys((*class_row.aliases, mention.surface_text.strip()))
                ),
                concept_or_instance=mention.concept_or_instance,
                mention_ids=(mention.mention_id,),
                evidence_ref=mention.evidence_ref,
                evidence_text=package.source_version.content[global_start:global_end],
                source_version_id=package.source_version_id,
                paragraph_id=chunk.paragraph_id,
                char_start=global_start,
                char_end=global_end,
                confidence=mention.confidence,
            )
            continue
        by_id[entity_id] = existing.model_copy(
            update={
                "aliases": tuple(
                    dict.fromkeys((*existing.aliases, mention.surface_text.strip()))
                ),
                "mention_ids": tuple(
                    dict.fromkeys((*existing.mention_ids, mention.mention_id))
                ),
                "confidence": max(existing.confidence, mention.confidence),
            }
        )
    return EntityResolutionResult(
        entities=tuple(sorted(by_id.values(), key=lambda row: row.entity_id)),
        unmapped_mentions=tuple(dict.fromkeys(unresolved)),
    )


def _schema_class_satisfies(
    class_iri: str,
    allowed: tuple[str, ...],
    schema: OntologyExtractionSchema,
) -> bool:
    if not allowed:
        return True
    row = next((item for item in schema.classes if item.iri == class_iri), None)
    represented = {class_iri, *(row.ancestor_iris if row is not None else ())}
    return bool(represented & set(allowed))


def build_faa_order_relation_extraction_task(
    package: FAAOrderSourcePackage,
    chunk: FAAOrderExtractionChunk,
    schema: OntologyExtractionSchema,
    entities: tuple[ResolvedKnowledgeEntity, ...],
) -> RelationExtractionTask | None:
    """Create RE only when at least one legal entity pair exists."""

    if len(entities) < 2:
        return None
    eligible = tuple(
        prop
        for prop in schema.properties
        if prop.kind == "object"
        and any(
            subject.entity_id != object_.entity_id
            and _schema_class_satisfies(subject.class_iri, prop.domain_iris, schema)
            and _schema_class_satisfies(object_.class_iri, prop.range_iris, schema)
            for subject in entities
            for object_ in entities
        )
    )
    if not eligible:
        return None
    relation_schema = schema.model_copy(update={"properties": eligible})
    return RelationExtractionTask(
        task_id=stable_id(
            "ontology-relation-extraction-task",
            package.source_version_id,
            chunk.chunk_id,
            *(row.entity_id for row in entities),
        ),
        chunk_id=chunk.chunk_id,
        paragraph_id=chunk.paragraph_id,
        evidence_ref=chunk.evidence_ref,
        evidence_text=chunk.evidence_text,
        ontology_schema=relation_schema,
        entities=entities,
        few_shot_examples=FAA_ORDER_RELATION_FEW_SHOTS,
    )


def _profile_mapping_by_iri(
    profile: LoadedValidationProfile,
    kind: str,
) -> dict[str, dict[str, str]]:
    mappings = profile.class_mappings if kind == "class" else profile.property_mappings
    return {
        mapping["iri"]: mapping
        for mapping in mappings.values()
        if isinstance(mapping.get("iri"), str)
    }


def build_faa_order_ontology_slice(
    *,
    subject_class_iri: str = POLICY_PARAGRAPH_CLASS,
    candidate_property_names: tuple[str, ...] = _ORDER_PROFILE_PROPERTIES,
    candidate_object_class_iris: tuple[str, ...] = (
        POLICY_RULE_CLASS,
        PROCEDURE_REQUIREMENT_CLASS,
        OPERATIONAL_ROLE_CLASS,
        ATMONTO_TMI_CLASS,
        ATMONTO_GDP_CLASS,
        ATMONTO_REROUTE_CLASS,
        ATMONTO_ROUTE_SEGMENT_CLASS,
        NAS_FACILITY_CLASS,
    ),
) -> OntologySlice:
    """Build a closed slice over the FAA extension plus exact ATMONTO terms."""

    profile = _order_profile()
    atmonto = load_ontology_registry()
    profile_classes = _profile_mapping_by_iri(profile, "class")
    selected_classes = {subject_class_iri, *candidate_object_class_iris}
    for iri in tuple(selected_classes):
        selected_classes.update(profile.class_ancestors.get(iri, ()))

    selected_properties: dict[str, dict[str, str]] = {}
    subject_ancestors = {
        subject_class_iri,
        *profile.class_ancestors.get(subject_class_iri, ()),
    }
    for name in candidate_property_names:
        if name in profile.property_mappings:
            mapping = profile.property_mappings[name]
            domains = profile.property_domains.get(mapping["iri"], ())
            if domains and not subject_ancestors.intersection(domains):
                continue
            selected_properties[mapping["iri"]] = mapping
            continue
        if name.startswith("atm:"):
            iri = (
                "https://data.nasa.gov/ontologies/atmonto/ATM#"
                + name.split(":", 1)[1]
            )
            if iri in atmonto.catalog.object_properties:
                record = atmonto.catalog.object_properties[iri]
            elif iri in atmonto.catalog.datatype_properties:
                record = atmonto.catalog.datatype_properties[iri]
            else:
                raise ValueError(f"unknown ATMONTO property: {name}")
            selected_properties[iri] = {
                "iri": iri,
                "label": record.label,
                "kind": "object" if record.kind == "ObjectProperty" else "datatype",
            }
            selected_classes.update(record.domain_iris)
            selected_classes.update(record.range_iris)
            continue
        raise ValueError(f"unknown FAA order ontology property: {name}")

    class_refs: list[OntologyClassRef] = []
    for iri in sorted(selected_classes):
        mapping = profile_classes.get(iri)
        if mapping is not None:
            class_refs.append(
                OntologyClassRef(
                    iri=iri,
                    local_name=_local_name(iri),
                    label=mapping.get("label", _local_name(iri)),
                    source_modules=("faa_jo_7210_3ee_ontology_profile_v2",),
                )
            )
            continue
        record = atmonto.catalog.classes.get(iri)
        if record is None:
            raise ValueError(f"class is outside the FAA order ontology slice: {iri}")
        class_refs.append(
            OntologyClassRef(
                iri=record.iri,
                local_name=record.local_name,
                label=record.label,
                comment=record.comment,
                source_modules=record.source_modules,
            )
        )

    property_refs: list[OntologyPropertyRef] = []
    for iri, mapping in sorted(selected_properties.items()):
        kind = "ObjectProperty" if mapping.get("kind") == "object" else "DataProperty"
        property_refs.append(
            OntologyPropertyRef(
                iri=iri,
                local_name=_local_name(iri),
                kind=kind,
                label=mapping.get("label", _local_name(iri)),
                domain_iris=profile.property_domains.get(
                    iri,
                    atmonto.catalog.object_properties.get(iri,
                        atmonto.catalog.datatype_properties.get(iri)
                    ).domain_iris if (
                        atmonto.catalog.object_properties.get(iri)
                        or atmonto.catalog.datatype_properties.get(iri)
                    ) else (),
                ),
                range_iris=profile.property_ranges.get(
                    iri,
                    atmonto.catalog.object_properties.get(iri).range_iris
                    if iri in atmonto.catalog.object_properties else (),
                ),
            )
        )

    hierarchy: list[OntologyHierarchyRef] = []
    for child in sorted(selected_classes):
        for parent in profile.class_ancestors.get(child, ()):
            if child != parent and parent in selected_classes:
                hierarchy.append(
                    OntologyHierarchyRef(
                        subclass_iri=child,
                        superclass_iri=parent,
                    )
                )
        for edge in atmonto.catalog.class_hierarchy:
            if edge.subclass_iri == child and edge.superclass_iri in selected_classes:
                hierarchy.append(
                    OntologyHierarchyRef(
                        subclass_iri=edge.subclass_iri,
                        superclass_iri=edge.superclass_iri,
                    )
                )
    unique_hierarchy = tuple(
        OntologyHierarchyRef(subclass_iri=child, superclass_iri=parent)
        for child, parent in sorted(
            {
                (edge.subclass_iri, edge.superclass_iri)
                for edge in hierarchy
            }
        )
    )
    catalog_checksum = hashlib.sha256(
        json.dumps(
            {
                "atmonto": atmonto.catalog_checksum,
                "profile": profile.ref.profile_checksum,
                "classes": sorted(selected_classes),
                "properties": sorted(selected_properties),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return OntologySlice(
        ontology_version=f"atmonto-plus-faa-order-{atmonto.ontology_version}",
        catalog_checksum=catalog_checksum,
        subject_class_iri=subject_class_iri,
        profile_id=profile.ref.profile_id,
        profile_checksum=profile.ref.profile_checksum,
        classes=tuple(class_refs),
        properties=tuple(property_refs),
        hierarchy=unique_hierarchy,
        constraints=tuple(
            OntologyConstraintRef(
                class_iri=constraint.class_iri,
                property_iri=constraint.property_iri,
                constraint_type=constraint.constraint_type,
                cardinality=constraint.cardinality,
                value_iris=constraint.value_iris,
                datatype_iris=constraint.datatype_iris,
            )
            for constraint in atmonto.catalog.cardinality_constraints
            if constraint.class_iri in selected_classes
            and constraint.property_iri in selected_properties
        ),
    )


__all__ = [
    "ATMONTO_GDP_CLASS",
    "ATMONTO_GROUND_STOP_CLASS",
    "ATMONTO_REROUTE_CLASS",
    "ATMONTO_TMI_CLASS",
    "FAA_ORDER_PROFILE_ID",
    "FAA_ORDER_NAMESPACE",
    "OPERATIONAL_ROLE_CLASS",
    "POLICY_PARAGRAPH_CLASS",
    "POLICY_RULE_CLASS",
    "PROCEDURE_REQUIREMENT_CLASS",
    "build_faa_order_entity_extraction_task",
    "build_faa_order_relation_extraction_task",
    "build_faa_order_ontology_slice",
    "compile_faa_order_extraction_schema",
    "normalize_faa_order_entities",
]
