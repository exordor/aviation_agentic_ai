# Web Demo Final Smoke

- Ready: True
- Method: `fastapi_testclient_static_and_api_checks`

## Checks

| Check | Passed | Detail |
| --- | ---: | --- |
| `web_dependencies_importable` | True | FastAPI TestClient loaded. |
| `root_page_served` | True | HTTP 200 |
| `root_contains_question-list` | True | Token `question-list` present in static HTML. |
| `root_contains_toolbar-group` | True | Token `toolbar-group` present in static HTML. |
| `root_contains_demo_narrative` | True | Token `Demo Narrative` present in static HTML. |
| `root_contains_pipeline_explanation` | True | Token `Pipeline Explanation` present in static HTML. |
| `root_contains_why_this_result` | True | Token `Why This Result` present in static HTML. |
| `root_contains_kg_relationship_graph` | True | Token `KG Relationship Graph` present in static HTML. |
| `root_contains_retrieved_chunks` | True | Token `Retrieved Chunks` present in static HTML. |
| `root_contains_optional_live_query` | True | Token `Optional Live Query` present in static HTML. |
| `status_api_ok` | True | HTTP 200 |
| `status_default_strategy_structure_aware` | True | default_strategy=structure_aware |
| `status_live_query_disabled` | True | live_query_enabled=False |
| `status_advisory_boundary_present` | True | Advisory boundary returned by API. |
| `explanation_api_ok` | True | HTTP 200 |
| `explanation_has_pipeline` | True | Pipeline steps returned. |
| `explanation_recommends_structure_aware` | True | Strategy decision available. |
| `questions_api_ok` | True | HTTP 200 |
| `questions_count_10` | True | questions=10 |
| `questions_have_source_pages` | True | Every question summary exposes source_page. |
| `question_detail_api_ok` | True | HTTP 200 |
| `question_detail_has_structure_hybrid` | True | Structure-aware hybrid payload is present. |
| `question_detail_has_gold_label` | True | Gold label returned with question detail. |
| `kg_graph_api_ok` | True | HTTP 200 |
| `kg_graph_hybrid_has_edges` | True | hybrid_edges=8 |
| `kg_graph_vector_empty_state` | True | vector_edges=0 |
| `live_query_disabled_by_default` | True | HTTP 403 |
| `favicon_no_content` | True | HTTP 204 |

## Notes

- This smoke report verifies local static HTML and offline API behavior.
- It does not replace a visual browser screenshot or deployment test.
- Live query remains disabled by default for reproducible demonstrations.
