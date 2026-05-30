from aviation_agentic_ai.retrieval.hybrid import tokenize
from aviation_agentic_ai.utils.text import GRAPH_TRAVERSAL_STOPWORDS, normalize_text, tokenize_terms


def test_tokenize_terms_uses_shared_stopwords_and_normalization() -> None:
    assert normalize_text("What’s  Angle   of Attack?") == "what's angle of attack?"
    assert tokenize_terms("What is angle of attack and lift?") == {"angle", "attack", "lift"}
    assert tokenize_terms("What’s angle?") == {"angle"}
    assert tokenize_terms("What’s angle?", normalize_apostrophes=True) == {"what's", "angle"}


def test_retrieval_tokenize_delegates_to_shared_terms() -> None:
    text = "When should angle-of-attack affect lift?"
    assert tokenize(text) == tokenize_terms(text)
    assert "when" in tokenize(text)
    assert "when" not in tokenize_terms(text, stopwords=GRAPH_TRAVERSAL_STOPWORDS)
