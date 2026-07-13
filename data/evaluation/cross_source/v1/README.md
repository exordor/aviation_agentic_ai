# Cross-source automated regression set V1

`automated_regression_v1.jsonl` is the active 24-case matched evaluation suite
for the frozen 68-advisory cohort. `hard_ambiguity_v1.jsonl` is the active
20-case Ground Stop / Glide Slope / neutral / conflicting challenge. The
mainline evaluator reports source-only, linked-text, and KG-layered component
metrics plus an independent deterministic answer audit. Passing is bounded
internal evidence conformance, not external aviation-expert certification.

The active evaluator scores rows marked `evaluation_status=automated_regression`,
runs the hard challenge, and writes
`reports/stages/cross_source_mainline_evaluation.{json,md}`. Unscored rows remain
available for exploratory cases without being treated as expectations.
