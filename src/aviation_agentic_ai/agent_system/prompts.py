"""Frozen prompt-catalog loader and fixed message assembler (design §16).

The normative role prompts live in ``configs/prompts/decision_case_agents_v1.yaml``.
Runtime code LOADS that catalog; it must not rewrite, extend, or silently
replace the prompt text, and must not add a hidden system prefix or rewrite
the examples.

Runtime message assembly is fixed (design §16):

    SystemMessage(role.system)
    HumanMessage(role.few_shot[0].user)
    AIMessage(role.few_shot[0].assistant)
    HumanMessage(role.few_shot[1].user)
    AIMessage(role.few_shot[1].assistant)
    HumanMessage(render(role.user_template, current_input))

The catalog is loaded once and cached. Callers ask for a :class:`RolePrompt`
by role key and render the final user turn from a variables dict; the
assembler returns the ordered message list plus the prompt-set/version metadata
the run trace must record.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import yaml

from aviation_agentic_ai.config import resolve_project_path

# Frozen catalog path (design §16). The single source of truth for role prompts.
DEFAULT_PROMPT_CATALOG = "configs/prompts/decision_case_agents_v1.yaml"

# The frozen role keys the system exercises.
ROLE_KEYS: tuple[str, ...] = (
    "semantic_resolution",
    "decision_case_assembly",
    "query",
)

# Backwards-compatible alias kept for legacy callers/tests that imported the
# module-level version string. The authoritative version is the catalog's
# prompt_set_id.
PROMPT_VERSION = "agent-system-v1"


@dataclass(frozen=True)
class RolePrompt:
    """One loaded role prompt from the frozen catalog (design §16)."""

    role: str
    prompt_set_id: str
    prompt_version: str
    system: str
    user_template: str
    few_shot: tuple[tuple[str, str], ...]  # (user, assistant) pairs
    max_output_tokens: int
    invocation_policy: str
    temperature: float
    thinking: str
    max_retries: int
    timeout_seconds: float

    def render_user(self, variables: dict[str, Any]) -> str:
        """Render the role's ``user_template`` with the supplied variables.

        Unknown ``${var}`` placeholders are left in place (they surface a
        missing input loudly in the model output rather than silently). Extra
        variables not referenced by the template are ignored.
        """

        return _render_template(self.user_template, variables)


@dataclass(frozen=True)
class PromptCatalog:
    """The loaded frozen prompt catalog."""

    prompt_set_id: str
    status: str
    language_policy: str
    roles: dict[str, RolePrompt]

    def role(self, key: str) -> RolePrompt:
        if key not in self.roles:
            raise KeyError(f"role {key!r} not in catalog (have: {sorted(self.roles)})")
        return self.roles[key]


@dataclass(frozen=True)
class AssembledPrompt:
    """The fixed 6-message prompt for one model call + its trace metadata."""

    role: str
    prompt_set_id: str
    prompt_version: str
    messages: tuple[tuple[str, str], ...]  # (role, content) in call order
    rendered_user: str
    max_output_tokens: int


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_prompt_catalog(catalog_path: str = DEFAULT_PROMPT_CATALOG) -> PromptCatalog:
    """Load and validate the frozen prompt catalog (design §16).

    Validation (no provider call): every role in :data:`ROLE_KEYS` exists,
    carries a prompt version, a non-empty system prompt, a user template,
    exactly two few-shot pairs, and model defaults consistent with §16.
    """

    path = resolve_project_path(catalog_path)
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"prompt catalog {path} is not a mapping")
    prompt_set_id = str(payload.get("prompt_set_id", ""))
    if not prompt_set_id:
        raise ValueError("prompt catalog missing prompt_set_id")
    if str(payload.get("status", "")) != "frozen":
        raise ValueError(f"prompt catalog status is not 'frozen': {payload.get('status')!r}")

    defaults = payload.get("model_defaults", {}) or {}
    temperature = float(defaults.get("temperature", 0))
    thinking = str(defaults.get("thinking", "disabled"))
    max_retries = int(defaults.get("max_retries", 0))
    timeout_seconds = float(defaults.get("timeout_seconds", 120))

    roles: dict[str, RolePrompt] = {}
    raw_roles = payload.get("roles", {}) or {}
    missing = [k for k in ROLE_KEYS if k not in raw_roles]
    if missing:
        raise ValueError(f"prompt catalog missing roles: {missing}")
    extra = [k for k in raw_roles if k not in ROLE_KEYS]
    if extra:
        raise ValueError(f"prompt catalog has unexpected roles: {extra}")
    for key in ROLE_KEYS:
        roles[key] = _build_role(
            key, raw_roles[key], prompt_set_id, temperature, thinking, max_retries, timeout_seconds
        )

    return PromptCatalog(
        prompt_set_id=prompt_set_id,
        status=str(payload.get("status", "")),
        language_policy=str(payload.get("language_policy", "")),
        roles=roles,
    )


def _build_role(
    key: str,
    raw: dict[str, Any],
    prompt_set_id: str,
    temperature: float,
    thinking: str,
    max_retries: int,
    timeout_seconds: float,
) -> RolePrompt:
    system = str(raw.get("system", "")).rstrip()
    user_template = str(raw.get("user_template", ""))
    if not system:
        raise ValueError(f"role {key!r} has empty system prompt")
    if not user_template:
        raise ValueError(f"role {key!r} has empty user_template")
    few_shot_raw = raw.get("few_shot") or []
    if not isinstance(few_shot_raw, list) or len(few_shot_raw) != 2:
        raise ValueError(
            f"role {key!r} must have exactly two few-shot pairs (got {len(few_shot_raw)})"
        )
    few_shot: list[tuple[str, str]] = []
    for pair in few_shot_raw:
        if not isinstance(pair, dict) or "user" not in pair or "assistant" not in pair:
            raise ValueError(f"role {key!r} few-shot pair missing user/assistant")
        few_shot.append((str(pair["user"]).rstrip(), str(pair["assistant"]).rstrip()))
    return RolePrompt(
        role=key,
        prompt_set_id=prompt_set_id,
        prompt_version=str(raw.get("prompt_version", "")),
        system=system,
        user_template=user_template,
        few_shot=tuple(few_shot),
        max_output_tokens=int(raw.get("max_output_tokens", 512)),
        invocation_policy=str(raw.get("invocation_policy", "")),
        temperature=temperature,
        thinking=thinking,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
    )


@lru_cache(maxsize=4)
def _cached_catalog(catalog_path: str) -> PromptCatalog:
    return load_prompt_catalog(catalog_path)


def get_prompt_catalog(catalog_path: str = DEFAULT_PROMPT_CATALOG) -> PromptCatalog:
    """Return the cached frozen catalog (loaded once per process)."""

    return _cached_catalog(catalog_path)


# ---------------------------------------------------------------------------
# Fixed 6-message assembler (design §16)
# ---------------------------------------------------------------------------


def assemble_prompt(
    role: str,
    variables: dict[str, Any],
    *,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> AssembledPrompt:
    """Assemble the fixed 6-message prompt for one role (design §16).

    Message order is exactly: system, few-shot[0].user, few-shot[0].assistant,
    few-shot[1].user, few-shot[1].assistant, rendered(user_template, variables).
    """

    catalog = get_prompt_catalog(catalog_path)
    rp = catalog.role(role)
    rendered = rp.render_user(variables)
    messages: list[tuple[str, str]] = [("system", rp.system)]
    for user, assistant in rp.few_shot:
        messages.append(("user", user))
        messages.append(("assistant", assistant))
    messages.append(("user", rendered))
    return AssembledPrompt(
        role=role,
        prompt_set_id=catalog.prompt_set_id,
        prompt_version=rp.prompt_version,
        messages=tuple(messages),
        rendered_user=rendered,
        max_output_tokens=rp.max_output_tokens,
    )


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------


_VAR_RE = re.compile(r"\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def _render_template(template: str, variables: dict[str, Any]) -> str:
    """Render ``${var}`` placeholders from ``variables``.

    Missing variables are left as-is so an incomplete input is visible in the
    rendered prompt rather than silently dropped. Values are stringified.
    """

    def _sub(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in variables:
            return match.group(0)
        return _stringify(variables[name])

    return _VAR_RE.sub(_sub, template)


def _stringify(value: Any) -> str:
    """Render a template variable value as plain text (never JSON)."""

    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return "\n".join(_stringify(v) for v in value)
    if isinstance(value, dict):
        lines = []
        for key, val in value.items():
            lines.append(f"{key}={_stringify(val)}")
        return "\n".join(lines)
    return str(value)
