from aviation_agentic_ai.config import load_default_config, load_yaml, resolve_project_path


def test_load_default_config() -> None:
    config = load_default_config()

    assert config["project"]["name"] == "aviation_agentic_ai"
    assert "curated_ontology" in config["paths"]
    assert "baseline_ontology" in config["paths"]
    assert config["kg_extraction"]["max_tokens"] == 4096


def test_resolve_project_path() -> None:
    path = resolve_project_path("configs/default.yaml")

    assert path.name == "default.yaml"
    assert path.exists()


def test_ontology_generation_config_uses_larger_token_budget() -> None:
    config = load_yaml("configs/ontology_generation.yaml")

    assert config["max_tokens"] == 8192
