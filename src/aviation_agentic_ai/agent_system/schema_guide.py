"""SchemaGuide: read-only access to the existing NASA ATMONTO ATCSCC schema slice.

The system mainline inherits the schema-guided KG construction work already on
``main``. This module does NOT create a new ontology, does NOT regenerate any
schema, and does NOT add an Ontology Agent. It loads the frozen ATCSCC schema
slice and exposes the classes / properties / constraints Decision Case
Assembly and the deterministic materializer need.

The ontology is a shared knowledge-representation contract for all Agents, not
a new LLM role. Only a compact slice relevant to the current event class is
available to Assembly; the full OWL is never dumped into a prompt.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.agent_system.tmi_profiles import active_tmi_profiles

DEFAULT_SCHEMA_SLICE = "data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json"

# Authority-term abbreviation -> exact ATMONTO event class (prefixed name).
# The active event-family profile is the single policy source for this map.
TERM_TO_EVENT_CLASS: dict[str, str] = {
    profile.authority_term: event_class
    for profile in active_tmi_profiles()
    if (event_class := profile.prefixed_ontology_class) is not None
}

# Predicate allowed for source traceability. prov:wasDerivedFrom is a W3C PROV
# predicate, not an atm: property; it is permitted in the Graph Patch for source
# traceability only and is recorded as a non-ontology trace predicate.
TRACE_PREDICATES: frozenset[str] = frozenset({"prov:wasDerivedFrom"})


@dataclass(frozen=True)
class OwlClass:
    iri: str
    prefixed_name: str
    local_name: str
    label: str
    comment: str
    superclasses: tuple[str, ...]


@dataclass(frozen=True)
class OwlObjectProperty:
    iri: str
    prefixed_name: str
    local_name: str
    label: str
    comment: str
    domain: frozenset[str]  # prefixed class names
    range: frozenset[str]


@dataclass(frozen=True)
class OwlDatatypeProperty:
    iri: str
    prefixed_name: str
    local_name: str
    label: str
    comment: str
    domain: frozenset[str]
    datatype: frozenset[str]  # e.g. xsd:dateTime


@dataclass(frozen=True)
class OwlConstraint:
    class_iri: str
    property_iri: str
    constraint_type: str
    cardinality: str | None
    class_set: frozenset[str]
    datatype_set: frozenset[str]
    # Enumerated allowed values (plan §5.4 check 7). Empty when the property
    # has no closed value set in the active profile.
    allowed_values: frozenset[str] = frozenset()
    # Prefixed names for the constrained class/property (populated from the
    # slice's convenience fields); empty when the slice did not carry them.
    class_prefixed: str = ""
    property_prefixed: str = ""


@dataclass(frozen=True)
class SchemaGuide:
    """Read-only view over the frozen ATCSCC schema slice."""

    schema_slice_id: str
    checksum: str
    classes: dict[str, OwlClass]  # prefixed_name -> OwlClass
    object_properties: dict[str, OwlObjectProperty]
    datatype_properties: dict[str, OwlDatatypeProperty]
    constraints: tuple[OwlConstraint, ...]
    direct_parents: dict[str, frozenset[str]]  # prefixed -> direct superclasses

    # ---- lookups ----------------------------------------------------------

    def has_class(self, prefixed_name: str) -> bool:
        return prefixed_name in self.classes

    def has_property(self, prefixed_name: str) -> bool:
        return prefixed_name in self.object_properties or prefixed_name in self.datatype_properties

    def is_object_property(self, prefixed_name: str) -> bool:
        return prefixed_name in self.object_properties

    def is_datatype_property(self, prefixed_name: str) -> bool:
        return prefixed_name in self.datatype_properties

    def superclasses(self, prefixed_name: str) -> frozenset[str]:
        """All transitive superclasses of a class (reflexive: includes itself)."""

        prefixed_name = next(
            (
                candidate.prefixed_name
                for candidate in self.classes.values()
                if candidate.iri == prefixed_name
            ),
            prefixed_name,
        )
        seen: set[str] = set()
        stack = [prefixed_name]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            for parent in self.direct_parents.get(current, frozenset()):
                if parent not in seen:
                    stack.append(parent)
        return frozenset(seen)

    def event_class_for_term(self, abbreviation: str) -> str | None:
        return TERM_TO_EVENT_CLASS.get(abbreviation.upper())

    def object_property_domain_ok(self, prop: str, subject_class: str) -> bool:
        op = self.object_properties.get(prop)
        if op is None:
            return False
        if not op.domain:
            return True  # unconstrained domain
        subject_supers = self.superclasses(subject_class)
        return bool(op.domain & subject_supers)

    def object_property_range_ok(self, prop: str, object_class: str) -> bool:
        op = self.object_properties.get(prop)
        if op is None:
            return False
        if not op.range:
            return True
        object_supers = self.superclasses(object_class)
        return bool(op.range & object_supers)

    def datatype_property_ok(self, prop: str, subject_class: str) -> bool:
        dp = self.datatype_properties.get(prop)
        if dp is None:
            return False
        if not dp.domain:
            return True
        return bool(dp.domain & self.superclasses(subject_class))

    def datatype_for(self, prop: str) -> frozenset[str]:
        dp = self.datatype_properties.get(prop)
        return dp.datatype if dp is not None else frozenset()

    # ---- constraint lookups (plan §5.4 checks 6, 7, 10) -------------------

    def constraints_for(self, class_prefixed: str, property_prefixed: str) -> tuple[OwlConstraint, ...]:
        """All constraints declared on (class, property) in the active slice.

        Plan §5.4 checks 6/7/10 require the Formal Graph Kernel to consult
        datatype, enumerated-value, and cardinality constraints. This lookup
        matches by the prefixed class/property names the slice carries.
        """

        return tuple(
            c for c in self.constraints
            if c.class_prefixed == class_prefixed and c.property_prefixed == property_prefixed
        )

    def exact_cardinality(self, class_prefixed: str, property_prefixed: str) -> int | None:
        """The required exact cardinality for (class, property), or None.

        Returns the integer cardinality when an ``objectExactCardinality`` or
        ``dataExactCardinality`` constraint is declared, otherwise ``None``
        (no exact-cardinality requirement in the active profile).
        """

        for c in self.constraints_for(class_prefixed, property_prefixed):
            if c.constraint_type in ("objectExactCardinality", "dataExactCardinality") and c.cardinality:
                try:
                    return int(c.cardinality)
                except ValueError:
                    return None
        return None

    def allowed_values(self, class_prefixed: str, property_prefixed: str) -> frozenset[str]:
        """The closed allowed-value set for (class, property), or empty."""

        for c in self.constraints_for(class_prefixed, property_prefixed):
            if c.constraint_type in ("data_all_values_from", "object_all_values_from") and c.allowed_values:
                return c.allowed_values
        return frozenset()

    # ---- compact context for Event Evidence Integration ------------------------

    def compact_context_for_event(self, event_class: str) -> str:
        """A compact, prompt-sized schema slice for one event class.

        Includes only the event class, its superclasses, and the properties
        whose domain covers it. Never dumps the full OWL.
        """

        if event_class not in self.classes:
            return f"# event class {event_class} is not in the schema slice\n"
        cls = self.classes[event_class]
        lines = [
            f"# Schema slice: {self.schema_slice_id}",
            f"# Event class: {cls.prefixed_name} ({cls.label}) — {cls.comment}",
        ]
        supers = self.superclasses(event_class) - {event_class}
        if supers:
            lines.append(f"# Superclasses: {', '.join(sorted(supers))}")
        for prop in sorted(self.object_properties):
            op = self.object_properties[prop]
            if self.object_property_domain_ok(prop, event_class):
                rng = ", ".join(sorted(op.range)) if op.range else "any"
                lines.append(f"#   {op.prefixed_name} ({op.label}) -> [{rng}] — {op.comment}")
        for prop in sorted(self.datatype_properties):
            dp = self.datatype_properties[prop]
            if self.datatype_property_ok(prop, event_class):
                dt = ", ".join(sorted(dp.datatype)) if dp.datatype else "any"
                lines.append(f"#   {dp.prefixed_name} ({dp.label}) ^^^ {dt} — {dp.comment}")
        lines.append(
            "# Output ONLY Graph Patch lines: subject | predicate | object | source_ids"
        )
        lines.append("# Use atm:* / nas:* predicates above; prov:wasDerivedFrom for source trace.")
        return "\n".join(lines) + "\n"


def _checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_schema_guide(slice_path: str = DEFAULT_SCHEMA_SLICE) -> SchemaGuide:
    """Load the frozen ATCSCC schema slice into a :class:`SchemaGuide`."""

    path = resolve_project_path(slice_path)
    payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    checksum = _checksum(path)

    classes: dict[str, OwlClass] = {}
    for c in payload.get("classes", []):
        prefixed = c["prefixed_name"]
        classes[prefixed] = OwlClass(
            iri=c["iri"],
            prefixed_name=prefixed,
            local_name=c["local_name"],
            label=c.get("label", prefixed),
            comment=c.get("comment", ""),
            superclasses=tuple(c.get("superclasses", [])),
        )

    object_properties: dict[str, OwlObjectProperty] = {}
    for op in payload.get("object_properties", []):
        prefixed = op["prefixed_name"]
        object_properties[prefixed] = OwlObjectProperty(
            iri=op["iri"],
            prefixed_name=prefixed,
            local_name=op["local_name"],
            label=op.get("label", prefixed),
            comment=op.get("comment", ""),
            domain=frozenset(op.get("domain_set", [])),
            range=frozenset(op.get("range_set", [])),
        )

    datatype_properties: dict[str, OwlDatatypeProperty] = {}
    for dp in payload.get("datatype_properties", []):
        prefixed = dp["prefixed_name"]
        datatype_properties[prefixed] = OwlDatatypeProperty(
            iri=dp["iri"],
            prefixed_name=prefixed,
            local_name=dp["local_name"],
            label=dp.get("label", prefixed),
            comment=dp.get("comment", ""),
            domain=frozenset(dp.get("domain_set", [])),
            datatype=frozenset(dp.get("datatype_set", [])),
        )

    constraints = tuple(
        OwlConstraint(
            class_iri=c.get("class_iri", ""),
            property_iri=c.get("property_iri", ""),
            constraint_type=c.get("constraint_type", ""),
            cardinality=c.get("cardinality"),
            class_set=frozenset(c.get("class_set", [])),
            datatype_set=frozenset(c.get("datatype_set", [])),
            allowed_values=frozenset(c.get("allowed_values", []) or []),
            class_prefixed=c.get("class", "") or "",
            property_prefixed=c.get("property", "") or "",
        )
        for c in payload.get("class_property_constraints", [])
    )

    direct_parents: dict[str, frozenset[str]] = {}
    for ax in payload.get("class_hierarchy", []):
        sub = ax.get("subclass")
        sup = ax.get("superclass")
        if sub and sup and not sup.startswith("urn:absolute:icarus"):
            direct_parents.setdefault(sub, set()).add(sup)
    direct_parents = {k: frozenset(v) for k, v in direct_parents.items()}

    return SchemaGuide(
        schema_slice_id=payload["schema_slice_id"],
        checksum=checksum,
        classes=classes,
        object_properties=object_properties,
        datatype_properties=datatype_properties,
        constraints=constraints,
        direct_parents=direct_parents,
    )


# Re-export for callers that want the dataclass shapes.
_ = field  # referenced for downstream typing
