from __future__ import annotations

import re

RETRIEVAL_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "be",
        "by",
        "for",
        "from",
        "how",
        "in",
        "is",
        "of",
        "on",
        "or",
        "should",
        "that",
        "the",
        "to",
        "what",
        "with",
    }
)

GRAPH_TRAVERSAL_STOPWORDS = RETRIEVAL_STOPWORDS | frozenset({"when", "where", "which"})

SOURCE_SCOPE_STOPWORDS = RETRIEVAL_STOPWORDS | frozenset({"at", "it"})

DEFAULT_STOPWORDS = RETRIEVAL_STOPWORDS

TOKEN_RE = re.compile(r"[a-z0-9']+")


def normalize_text(value: str) -> str:
    """Normalize text for lightweight lexical scoring."""
    return " ".join(value.replace("’", "'").lower().split())


def tokenize_terms(
    text: str,
    *,
    stopwords: set[str] | frozenset[str] | None = DEFAULT_STOPWORDS,
    min_length: int = 3,
    normalize_apostrophes: bool = False,
) -> set[str]:
    """Return stable lowercase lexical terms for retrieval/report diagnostics."""
    normalized = normalize_text(text) if normalize_apostrophes else " ".join(text.lower().split())
    return {
        token
        for token in TOKEN_RE.findall(normalized)
        if len(token) >= min_length and (stopwords is None or token not in stopwords)
    }
