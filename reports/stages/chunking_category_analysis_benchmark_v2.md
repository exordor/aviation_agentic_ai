# Chunking Category Analysis Benchmark V2

- Supported question categories use retrieval metrics.
- Insufficient-evidence labels are diagnostic only and are not recall failures.

## Best By Category

| Category | Strategy | Recall@5 | MRR@5 | Context Recall | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| supported_factual | structure_aware_large | 0.825 | 0.6442 | 0.975 | benchmark-specific |
| concept_definition | fixed_large | 1.0 | 0.8222 | 1.0 | benchmark-specific |
| relation_causal | hierarchical_parent_child | 1.0 | 0.6911 | 1.0 | benchmark-specific |
| cross_page | recursive_large | 1.0 | 0.5833 | 0.85 | benchmark-specific |
| paraphrase | embedding_semantic | 0.7 | 0.5083 | 0.7 | benchmark-specific |
| terminology_variation | recursive_medium | 0.9 | 0.485 | 0.9 | benchmark-specific |
| insufficient_evidence | diagnostic_only | n/a | n/a | n/a | No-answer labels have no gold evidence target. |

## Full Category Table

| Category | Strategy | Labels | Recall@5 | Recall@10 | MRR@5 | Context Recall | Diagnostic only |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| supported_factual | fixed_small | 40 | 0.625 | 0.725 | 0.3642 | 0.725 | False |
| supported_factual | fixed_medium | 40 | 0.7 | 0.8 | 0.4558 | 0.8 | False |
| supported_factual | fixed_large | 40 | 0.825 | 0.95 | 0.5987 | 0.95 | False |
| supported_factual | recursive_small | 40 | 0.75 | 0.8 | 0.4537 | 0.8 | False |
| supported_factual | recursive_medium | 40 | 0.75 | 0.875 | 0.4425 | 0.875 | False |
| supported_factual | recursive_large | 40 | 0.775 | 0.975 | 0.6008 | 0.975 | False |
| supported_factual | structure_aware | 40 | 0.425 | 0.525 | 0.2683 | 0.525 | False |
| supported_factual | structure_aware_medium | 40 | 0.75 | 0.825 | 0.4212 | 0.825 | False |
| supported_factual | structure_aware_large | 40 | 0.825 | 0.975 | 0.6442 | 0.975 | False |
| supported_factual | semantic_meta_like | 40 | 0.625 | 0.775 | 0.4029 | 0.775 | False |
| supported_factual | embedding_semantic | 40 | 0.7 | 0.825 | 0.4279 | 0.825 | False |
| supported_factual | proposition_like | 40 | 0.575 | 0.6 | 0.3137 | 0.6 | False |
| supported_factual | hierarchical_parent_child | 40 | 0.75 | 0.8 | 0.4537 | 0.8 | False |
| supported_factual | contextual_prefix | 40 | 0.3 | 0.4 | 0.1537 | 0.4 | False |
| concept_definition | fixed_small | 15 | 0.6667 | 0.9333 | 0.5267 | 0.9333 | False |
| concept_definition | fixed_medium | 15 | 1.0 | 1.0 | 0.7333 | 1.0 | False |
| concept_definition | fixed_large | 15 | 1.0 | 1.0 | 0.8222 | 1.0 | False |
| concept_definition | recursive_small | 15 | 0.6667 | 0.9333 | 0.5189 | 0.9333 | False |
| concept_definition | recursive_medium | 15 | 1.0 | 1.0 | 0.6967 | 1.0 | False |
| concept_definition | recursive_large | 15 | 1.0 | 1.0 | 0.8222 | 1.0 | False |
| concept_definition | structure_aware | 15 | 0.8667 | 0.9333 | 0.6167 | 0.9333 | False |
| concept_definition | structure_aware_medium | 15 | 1.0 | 1.0 | 0.7267 | 1.0 | False |
| concept_definition | structure_aware_large | 15 | 1.0 | 1.0 | 0.8056 | 1.0 | False |
| concept_definition | semantic_meta_like | 15 | 0.8 | 0.8667 | 0.6 | 0.8667 | False |
| concept_definition | embedding_semantic | 15 | 0.9333 | 0.9333 | 0.7944 | 0.9333 | False |
| concept_definition | proposition_like | 15 | 0.5333 | 0.6 | 0.3967 | 0.6 | False |
| concept_definition | hierarchical_parent_child | 15 | 0.6667 | 0.9333 | 0.5189 | 0.9333 | False |
| concept_definition | contextual_prefix | 15 | 0.7333 | 0.8 | 0.4778 | 0.8 | False |
| relation_causal | fixed_small | 15 | 0.9333 | 0.9333 | 0.6244 | 0.9333 | False |
| relation_causal | fixed_medium | 15 | 0.9333 | 1.0 | 0.7 | 1.0 | False |
| relation_causal | fixed_large | 15 | 0.8 | 0.8667 | 0.5889 | 0.8667 | False |
| relation_causal | recursive_small | 15 | 1.0 | 1.0 | 0.6911 | 1.0 | False |
| relation_causal | recursive_medium | 15 | 0.9333 | 1.0 | 0.75 | 1.0 | False |
| relation_causal | recursive_large | 15 | 0.8667 | 0.8667 | 0.75 | 0.8667 | False |
| relation_causal | structure_aware | 15 | 0.9333 | 0.9333 | 0.5967 | 0.9333 | False |
| relation_causal | structure_aware_medium | 15 | 0.9333 | 1.0 | 0.75 | 1.0 | False |
| relation_causal | structure_aware_large | 15 | 0.8 | 0.8667 | 0.6467 | 0.8667 | False |
| relation_causal | semantic_meta_like | 15 | 0.9333 | 0.9333 | 0.5944 | 0.9333 | False |
| relation_causal | embedding_semantic | 15 | 0.7333 | 0.8667 | 0.6556 | 0.8667 | False |
| relation_causal | proposition_like | 15 | 0.7333 | 0.7333 | 0.5611 | 0.7333 | False |
| relation_causal | hierarchical_parent_child | 15 | 1.0 | 1.0 | 0.6911 | 1.0 | False |
| relation_causal | contextual_prefix | 15 | 0.8 | 0.8 | 0.5 | 0.8 | False |
| cross_page | fixed_small | 10 | 0.5 | 0.8 | 0.425 | 0.4 | False |
| cross_page | fixed_medium | 10 | 0.9 | 1.0 | 0.44 | 0.75 | False |
| cross_page | fixed_large | 10 | 1.0 | 1.0 | 0.5666 | 0.85 | False |
| cross_page | recursive_small | 10 | 0.6 | 0.7 | 0.325 | 0.4 | False |
| cross_page | recursive_medium | 10 | 0.9 | 1.0 | 0.4333 | 0.75 | False |
| cross_page | recursive_large | 10 | 1.0 | 1.0 | 0.5833 | 0.85 | False |
| cross_page | structure_aware | 10 | 0.5 | 0.6 | 0.4333 | 0.35 | False |
| cross_page | structure_aware_medium | 10 | 0.8 | 1.0 | 0.4533 | 0.7 | False |
| cross_page | structure_aware_large | 10 | 1.0 | 1.0 | 0.5833 | 0.85 | False |
| cross_page | semantic_meta_like | 10 | 0.6 | 0.8 | 0.3367 | 0.45 | False |
| cross_page | embedding_semantic | 10 | 0.7 | 0.9 | 0.5333 | 0.55 | False |
| cross_page | proposition_like | 10 | 0.6 | 0.8 | 0.345 | 0.4 | False |
| cross_page | hierarchical_parent_child | 10 | 0.6 | 0.7 | 0.325 | 0.4 | False |
| cross_page | contextual_prefix | 10 | 0.6 | 0.6 | 0.3117 | 0.3 | False |
| paraphrase | fixed_small | 10 | 0.5 | 0.6 | 0.3833 | 0.6 | False |
| paraphrase | fixed_medium | 10 | 0.6 | 0.8 | 0.425 | 0.8 | False |
| paraphrase | fixed_large | 10 | 0.7 | 0.9 | 0.4333 | 0.9 | False |
| paraphrase | recursive_small | 10 | 0.6 | 0.7 | 0.39 | 0.7 | False |
| paraphrase | recursive_medium | 10 | 0.6 | 0.7 | 0.3867 | 0.7 | False |
| paraphrase | recursive_large | 10 | 0.7 | 0.9 | 0.4167 | 0.9 | False |
| paraphrase | structure_aware | 10 | 0.4 | 0.7 | 0.3333 | 0.7 | False |
| paraphrase | structure_aware_medium | 10 | 0.5 | 0.8 | 0.4333 | 0.8 | False |
| paraphrase | structure_aware_large | 10 | 0.7 | 0.9 | 0.4833 | 0.9 | False |
| paraphrase | semantic_meta_like | 10 | 0.6 | 0.6 | 0.4033 | 0.6 | False |
| paraphrase | embedding_semantic | 10 | 0.7 | 0.7 | 0.5083 | 0.7 | False |
| paraphrase | proposition_like | 10 | 0.7 | 0.8 | 0.4783 | 0.8 | False |
| paraphrase | hierarchical_parent_child | 10 | 0.6 | 0.7 | 0.39 | 0.7 | False |
| paraphrase | contextual_prefix | 10 | 0.3 | 0.3 | 0.25 | 0.3 | False |
| terminology_variation | fixed_small | 10 | 0.5 | 0.6 | 0.295 | 0.6 | False |
| terminology_variation | fixed_medium | 10 | 0.7 | 0.8 | 0.36 | 0.8 | False |
| terminology_variation | fixed_large | 10 | 0.8 | 1.0 | 0.4233 | 1.0 | False |
| terminology_variation | recursive_small | 10 | 0.4 | 0.6 | 0.2833 | 0.6 | False |
| terminology_variation | recursive_medium | 10 | 0.9 | 0.9 | 0.485 | 0.9 | False |
| terminology_variation | recursive_large | 10 | 0.8 | 1.0 | 0.4367 | 1.0 | False |
| terminology_variation | structure_aware | 10 | 0.4 | 0.6 | 0.2533 | 0.6 | False |
| terminology_variation | structure_aware_medium | 10 | 0.7 | 0.8 | 0.3267 | 0.8 | False |
| terminology_variation | structure_aware_large | 10 | 0.8 | 1.0 | 0.44 | 1.0 | False |
| terminology_variation | semantic_meta_like | 10 | 0.5 | 0.7 | 0.3583 | 0.7 | False |
| terminology_variation | embedding_semantic | 10 | 0.6 | 0.9 | 0.4083 | 0.9 | False |
| terminology_variation | proposition_like | 10 | 0.1 | 0.3 | 0.05 | 0.3 | False |
| terminology_variation | hierarchical_parent_child | 10 | 0.4 | 0.6 | 0.2833 | 0.6 | False |
| terminology_variation | contextual_prefix | 10 | 0.1 | 0.2 | 0.05 | 0.2 | False |
| insufficient_evidence | fixed_small | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | fixed_medium | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | fixed_large | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | recursive_small | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | recursive_medium | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | recursive_large | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | structure_aware | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | structure_aware_medium | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | structure_aware_large | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | semantic_meta_like | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | embedding_semantic | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | proposition_like | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | hierarchical_parent_child | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
| insufficient_evidence | contextual_prefix | 20 | 0.0 | 0.0 | 0.0 | 1.0 | True |
