from pathlib import Path

from aviation_agentic_ai.ontology.stats import collect_stats


def test_collect_stats_on_baseline_ontology() -> None:
    path = Path("data/ontology/baseline/06_phak_ch4_0.ttl")
    stats = collect_stats(path)

    assert stats.triples > 0
    assert stats.classes > 0
    assert stats.object_properties > 0
    assert stats.datatype_properties >= 0
    assert stats.named_individuals == 0
