from __future__ import annotations

import json
import re
from collections.abc import Callable

from aviation_agentic_ai.cross_source.contracts import (
    AlignmentCandidate,
    AlignmentMethod,
    Mention,
)


ContextInvoker = Callable[[list[dict[str, str]]], str]


class ContextAlignmentAgent:
    """Ranks registry-supplied candidates without creating new targets."""

    def rank(
        self,
        *,
        mention: Mention,
        candidates: list[AlignmentCandidate],
        invoker: ContextInvoker | None = None,
    ) -> list[AlignmentCandidate]:
        if len(candidates) < 2:
            return candidates
        if invoker is None:
            return self._rank_locally(mention=mention, candidates=candidates)
        allowed = {item.target_id for item in candidates}
        messages = [
            {
                "role": "system",
                "content": (
                    "You align one ambiguous FAA abbreviation to one supplied candidate. "
                    "Do not create a new target. Return JSON with target_id, score from 0 to 1, "
                    "and rationale."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "surface_form": mention.surface_form,
                        "evidence_text": mention.evidence_text,
                        "candidates": [
                            {
                                "target_id": item.target_id,
                                "label": item.target_label,
                                "type": item.target_type,
                            }
                            for item in candidates
                        ],
                    },
                    sort_keys=True,
                ),
            },
        ]
        payload = json.loads(invoker(messages))
        target_id = str(payload.get("target_id") or "")
        if target_id not in allowed:
            raise ValueError("Context Alignment Agent proposed a target outside the registry candidates")
        score = float(payload.get("score", 0.0))
        if not 0 <= score <= 1:
            raise ValueError("Context Alignment Agent score must be between 0 and 1")
        rationale = str(payload.get("rationale") or "contextual ranking")
        ranked: list[AlignmentCandidate] = []
        for item in candidates:
            item_score = score if item.target_id == target_id else max(0.0, 1.0 - score)
            ranked.append(
                item.model_copy(
                    update={
                        "method": AlignmentMethod.CONTEXT_AGENT,
                        "gate_score": item_score,
                        "rationale": rationale if item.target_id == target_id else "not selected",
                    }
                )
            )
        return sorted(ranked, key=lambda item: (-item.gate_score, item.target_id))

    def _rank_locally(
        self,
        *,
        mention: Mention,
        candidates: list[AlignmentCandidate],
    ) -> list[AlignmentCandidate]:
        """Deterministically rank known ambiguous terms from advisory context."""
        text = mention.evidence_text.upper()
        labels = {item.target_label.lower(): item for item in candidates}
        scores = {item.target_id: 0.5 for item in candidates}
        rationales = {item.target_id: "No discriminating context cue matched." for item in candidates}

        ground_stop = labels.get("ground stop")
        glide_slope = labels.get("glide slope")
        if ground_stop and glide_slope and mention.normalized_form == "GS":
            ground_patterns = (
                (r"\bGROUND\s+STOP\b", "explicit GROUND STOP"),
                (r"\bGS\s+(?:CNX|CX|CANCEL(?:LED|LATION)?)\b", "GS cancellation syntax"),
                (r"\b(?:CDM|ATCSCC)\s+GS\b", "traffic-management GS syntax"),
                (r"\b(?:CTL ELEMENT|DEP FACILITIES|GROUND DELAY)\b", "TMI control field"),
            )
            glide_patterns = (
                (r"\bGLIDE\s+SLOPE\b", "explicit GLIDE SLOPE"),
                (r"\b(?:ILS|LOCALIZER|INSTRUMENT APPROACH)\b", "instrument-approach context"),
            )
            ground_cues = [label for pattern, label in ground_patterns if re.search(pattern, text)]
            glide_cues = [label for pattern, label in glide_patterns if re.search(pattern, text)]
            if ground_cues and not glide_cues:
                scores[ground_stop.target_id] = 0.98
                scores[glide_slope.target_id] = 0.02
                rationales[ground_stop.target_id] = "Matched: " + ", ".join(ground_cues)
                rationales[glide_slope.target_id] = "No glide-slope cue matched."
            elif glide_cues and not ground_cues:
                scores[glide_slope.target_id] = 0.98
                scores[ground_stop.target_id] = 0.02
                rationales[glide_slope.target_id] = "Matched: " + ", ".join(glide_cues)
                rationales[ground_stop.target_id] = "No traffic-management cue matched."

        ranked = [
            item.model_copy(
                update={
                    "method": AlignmentMethod.CONTEXT_AGENT,
                    "gate_score": scores[item.target_id],
                    "rationale": rationales[item.target_id],
                }
            )
            for item in candidates
        ]
        return sorted(ranked, key=lambda item: (-item.gate_score, item.target_id))
