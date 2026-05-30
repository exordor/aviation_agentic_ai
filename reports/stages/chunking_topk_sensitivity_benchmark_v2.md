# Chunking Top-K Sensitivity Benchmark V2

- Supported-label retrieval only; insufficient-evidence labels are not recall targets.
- Top-k comparisons also change context volume and must not be read as a universal chunking ranking.

## Top-3

| Rank | Strategy | Recall | MRR | Context Recall | Mean Context Chars |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | recursive_large | 0.79 | 0.6083 | 0.745 | 4252.35 |
| 2 | structure_aware_large | 0.78 | 0.6117 | 0.735 | 4297.31 |
| 3 | fixed_large | 0.76 | 0.595 | 0.72 | 4325.55 |
| 4 | recursive_medium | 0.64 | 0.48 | 0.615 | 2389.99 |
| 5 | embedding_semantic | 0.63 | 0.5117 | 0.595 | 1937.73 |
| 6 | structure_aware_medium | 0.62 | 0.4733 | 0.595 | 2390.62 |
| 7 | fixed_medium | 0.61 | 0.4867 | 0.585 | 2424.65 |
| 8 | hierarchical_parent_child | 0.6 | 0.4383 | 0.575 | 1063.86 |
| 9 | recursive_small | 0.6 | 0.4383 | 0.575 | 1063.86 |
| 10 | semantic_meta_like | 0.56 | 0.4217 | 0.535 | 1845.11 |
| 11 | fixed_small | 0.52 | 0.3867 | 0.5 | 1102.22 |
| 12 | structure_aware | 0.49 | 0.3733 | 0.465 | 1415.27 |
| 13 | proposition_like | 0.42 | 0.325 | 0.4 | 1198.03 |
| 14 | contextual_prefix | 0.34 | 0.2433 | 0.32 | 1079.49 |

## Top-5

| Rank | Strategy | Recall | MRR | Context Recall | Mean Context Chars |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | fixed_large | 0.86 | 0.617 | 0.83 | 7183.1 |
| 2 | structure_aware_large | 0.85 | 0.6262 | 0.82 | 7180.47 |
| 3 | recursive_large | 0.84 | 0.6198 | 0.81 | 7128.77 |
| 4 | recursive_medium | 0.83 | 0.5245 | 0.79 | 4045.84 |
| 5 | fixed_medium | 0.79 | 0.5287 | 0.75 | 4074.47 |
| 6 | structure_aware_medium | 0.79 | 0.5113 | 0.75 | 4034.42 |
| 7 | embedding_semantic | 0.73 | 0.5337 | 0.695 | 3203.35 |
| 8 | hierarchical_parent_child | 0.71 | 0.4628 | 0.68 | 1775.77 |
| 9 | recursive_small | 0.71 | 0.4628 | 0.68 | 1775.77 |
| 10 | semantic_meta_like | 0.68 | 0.4502 | 0.65 | 3059.09 |
| 11 | fixed_small | 0.64 | 0.4137 | 0.61 | 1828.28 |
| 12 | structure_aware | 0.57 | 0.3913 | 0.545 | 2191.64 |
| 13 | proposition_like | 0.56 | 0.356 | 0.53 | 2046.77 |
| 14 | contextual_prefix | 0.45 | 0.2693 | 0.42 | 1732.8 |

## Top-10

| Rank | Strategy | Recall | MRR | Context Recall | Mean Context Chars |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | structure_aware_large | 0.96 | 0.6412 | 0.945 | 14261.21 |
| 2 | recursive_large | 0.96 | 0.6372 | 0.945 | 14272.6 |
| 3 | fixed_large | 0.96 | 0.6303 | 0.945 | 14284.33 |
| 4 | recursive_medium | 0.91 | 0.5353 | 0.885 | 8084.29 |
| 5 | fixed_medium | 0.9 | 0.5448 | 0.875 | 8219.7 |
| 6 | structure_aware_medium | 0.89 | 0.5269 | 0.86 | 8050.6 |
| 7 | embedding_semantic | 0.85 | 0.5517 | 0.815 | 6415.1 |
| 8 | hierarchical_parent_child | 0.81 | 0.4782 | 0.78 | 3577.26 |
| 9 | recursive_small | 0.81 | 0.4782 | 0.78 | 3577.26 |
| 10 | fixed_small | 0.8 | 0.4328 | 0.76 | 3661.93 |
| 11 | semantic_meta_like | 0.79 | 0.4658 | 0.755 | 6041.71 |
| 12 | structure_aware | 0.68 | 0.4065 | 0.655 | 4191.55 |
| 13 | proposition_like | 0.62 | 0.3638 | 0.585 | 4081.91 |
| 14 | contextual_prefix | 0.51 | 0.2773 | 0.48 | 3125.98 |

## Top-20

| Rank | Strategy | Recall | MRR | Context Recall | Mean Context Chars |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | structure_aware_large | 0.99 | 0.6434 | 0.945 | 28457.46 |
| 2 | recursive_large | 0.99 | 0.6392 | 0.945 | 28489.87 |
| 3 | fixed_large | 0.99 | 0.6323 | 0.945 | 28596.46 |
| 4 | recursive_medium | 0.96 | 0.5389 | 0.885 | 16243.71 |
| 5 | embedding_semantic | 0.95 | 0.5593 | 0.815 | 12563.05 |
| 6 | fixed_medium | 0.95 | 0.5485 | 0.875 | 16429.13 |
| 7 | structure_aware_medium | 0.95 | 0.5312 | 0.86 | 16146.36 |
| 8 | hierarchical_parent_child | 0.92 | 0.4862 | 0.78 | 7192.65 |
| 9 | recursive_small | 0.92 | 0.4862 | 0.78 | 7192.65 |
| 10 | semantic_meta_like | 0.89 | 0.473 | 0.755 | 11985.3 |
| 11 | fixed_small | 0.86 | 0.4373 | 0.76 | 7316.71 |
| 12 | structure_aware | 0.82 | 0.4169 | 0.655 | 7968.81 |
| 13 | proposition_like | 0.71 | 0.3703 | 0.585 | 8159.64 |
| 14 | contextual_prefix | 0.57 | 0.2814 | 0.48 | 5471.75 |
