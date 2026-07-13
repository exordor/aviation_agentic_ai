from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from aviation_agentic_ai.cross_source.contracts import (
    AlignmentCandidate,
    AlignmentMethod,
    CanonicalEntity,
    Mention,
    MentionType,
    TermConcept,
)
from aviation_agentic_ai.cross_source.identifiers import normalize_code


class AlignmentRegistry:
    def __init__(
        self,
        facilities: Iterable[CanonicalEntity],
        terms: Iterable[TermConcept],
    ) -> None:
        self.facilities = list(facilities)
        self.terms = list(terms)
        self._facility_codes: dict[str, list[CanonicalEntity]] = defaultdict(list)
        self._facility_aliases: dict[str, list[CanonicalEntity]] = defaultdict(list)
        self._term_abbreviations: dict[str, list[TermConcept]] = defaultdict(list)
        self._term_aliases: dict[str, list[TermConcept]] = defaultdict(list)
        for entity in self.facilities:
            for code in entity.codes:
                self._facility_codes[normalize_code(code.value)].append(entity)
            for alias in entity.aliases:
                self._facility_aliases[normalize_code(alias)].append(entity)
        for term in self.terms:
            self._term_abbreviations[normalize_code(term.abbreviation)].append(term)
            for alias in term.aliases:
                self._term_aliases[normalize_code(alias)].append(term)

    def candidates(self, mention: Mention) -> list[AlignmentCandidate]:
        token = normalize_code(mention.normalized_form)
        if mention.mention_type is MentionType.FACILITY_CODE:
            exact = self._facility_codes.get(token, [])
            method = AlignmentMethod.AUTHORITY_EXACT_CODE
            matches = exact or self._facility_aliases.get(token, [])
            if not exact:
                method = AlignmentMethod.AUTHORITY_EXACT_ALIAS
            unique_matches = {item.entity_id: item for item in matches}
            return [
                AlignmentCandidate(
                    mention_id=mention.mention_id,
                    target_id=item.entity_id,
                    target_label=item.preferred_label,
                    target_type=item.entity_type.value,
                    method=method,
                    authority_sources=item.source_refs,
                    gate_score=1.0 if method is AlignmentMethod.AUTHORITY_EXACT_CODE else 0.98,
                    rationale=f"{token} matched an authoritative facility {method.value}.",
                )
                for item in unique_matches.values()
            ]

        exact_terms = self._term_abbreviations.get(token, [])
        method = AlignmentMethod.AUTHORITY_EXACT_CODE
        matches = exact_terms or self._term_aliases.get(token, [])
        if not exact_terms:
            method = AlignmentMethod.AUTHORITY_EXACT_ALIAS
        score = 1.0 if method is AlignmentMethod.AUTHORITY_EXACT_CODE else 0.98
        unique_terms = {item.term_id: item for item in matches}
        return [
            AlignmentCandidate(
                mention_id=mention.mention_id,
                target_id=item.term_id,
                target_label=item.preferred_label,
                target_type=item.term_category.value,
                method=method,
                authority_sources=item.source_refs,
                gate_score=score,
                rationale=f"{token} matched an authoritative term {method.value}.",
            )
            for item in unique_terms.values()
        ]
