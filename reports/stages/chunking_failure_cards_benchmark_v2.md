# Chunking Failure Cards Benchmark V2

- These cards are deterministic qualitative diagnostics, not human-review results.
- Each card stores the first matching sample per strategy and failure type when one exists.

| Strategy | Failure type | Samples | Example CQ | Notes |
| --- | --- | ---: | --- | --- |
| fixed_small | missed_gold_evidence_at_5 | 1 | bv2-sf-002 | sample found |
| fixed_small | chunk_too_small_lost_context | 1 | bv2-sf-002 | sample found |
| fixed_small | chunk_too_large_low_precision | 0 |  | no matching sample in this run |
| fixed_small | section_boundary_split | 1 | bv2-sf-002 | sample found |
| fixed_small | semantic_boundary_error | 0 |  | no matching sample in this run |
| fixed_small | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| fixed_small | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| fixed_small | proposition_context_loss | 0 |  | no matching sample in this run |
| fixed_small | parent_child_not_used | 0 |  | no matching sample in this run |
| fixed_medium | missed_gold_evidence_at_5 | 1 | bv2-sf-006 | sample found |
| fixed_medium | chunk_too_small_lost_context | 0 |  | no matching sample in this run |
| fixed_medium | chunk_too_large_low_precision | 0 |  | no matching sample in this run |
| fixed_medium | section_boundary_split | 1 | bv2-sf-006 | sample found |
| fixed_medium | semantic_boundary_error | 0 |  | no matching sample in this run |
| fixed_medium | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| fixed_medium | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| fixed_medium | proposition_context_loss | 0 |  | no matching sample in this run |
| fixed_medium | parent_child_not_used | 0 |  | no matching sample in this run |
| fixed_large | missed_gold_evidence_at_5 | 1 | bv2-sf-004 | sample found |
| fixed_large | chunk_too_small_lost_context | 0 |  | no matching sample in this run |
| fixed_large | chunk_too_large_low_precision | 1 | bv2-sf-001 | sample found |
| fixed_large | section_boundary_split | 1 | bv2-sf-004 | sample found |
| fixed_large | semantic_boundary_error | 0 |  | no matching sample in this run |
| fixed_large | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| fixed_large | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| fixed_large | proposition_context_loss | 0 |  | no matching sample in this run |
| fixed_large | parent_child_not_used | 0 |  | no matching sample in this run |
| recursive_small | missed_gold_evidence_at_5 | 1 | bv2-sf-006 | sample found |
| recursive_small | chunk_too_small_lost_context | 1 | bv2-sf-006 | sample found |
| recursive_small | chunk_too_large_low_precision | 0 |  | no matching sample in this run |
| recursive_small | section_boundary_split | 1 | bv2-sf-006 | sample found |
| recursive_small | semantic_boundary_error | 0 |  | no matching sample in this run |
| recursive_small | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| recursive_small | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| recursive_small | proposition_context_loss | 0 |  | no matching sample in this run |
| recursive_small | parent_child_not_used | 0 |  | no matching sample in this run |
| recursive_medium | missed_gold_evidence_at_5 | 1 | bv2-sf-006 | sample found |
| recursive_medium | chunk_too_small_lost_context | 0 |  | no matching sample in this run |
| recursive_medium | chunk_too_large_low_precision | 0 |  | no matching sample in this run |
| recursive_medium | section_boundary_split | 1 | bv2-sf-006 | sample found |
| recursive_medium | semantic_boundary_error | 0 |  | no matching sample in this run |
| recursive_medium | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| recursive_medium | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| recursive_medium | proposition_context_loss | 0 |  | no matching sample in this run |
| recursive_medium | parent_child_not_used | 0 |  | no matching sample in this run |
| recursive_large | missed_gold_evidence_at_5 | 1 | bv2-sf-001 | sample found |
| recursive_large | chunk_too_small_lost_context | 0 |  | no matching sample in this run |
| recursive_large | chunk_too_large_low_precision | 1 | bv2-sf-001 | sample found |
| recursive_large | section_boundary_split | 1 | bv2-sf-001 | sample found |
| recursive_large | semantic_boundary_error | 0 |  | no matching sample in this run |
| recursive_large | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| recursive_large | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| recursive_large | proposition_context_loss | 0 |  | no matching sample in this run |
| recursive_large | parent_child_not_used | 0 |  | no matching sample in this run |
| structure_aware | missed_gold_evidence_at_5 | 1 | bv2-sf-001 | sample found |
| structure_aware | chunk_too_small_lost_context | 1 | bv2-sf-001 | sample found |
| structure_aware | chunk_too_large_low_precision | 0 |  | no matching sample in this run |
| structure_aware | section_boundary_split | 0 |  | no matching sample in this run |
| structure_aware | semantic_boundary_error | 0 |  | no matching sample in this run |
| structure_aware | cross_page_evidence_split | 1 | bv2-xp-002 | sample found |
| structure_aware | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| structure_aware | proposition_context_loss | 0 |  | no matching sample in this run |
| structure_aware | parent_child_not_used | 0 |  | no matching sample in this run |
| structure_aware_medium | missed_gold_evidence_at_5 | 1 | bv2-sf-006 | sample found |
| structure_aware_medium | chunk_too_small_lost_context | 0 |  | no matching sample in this run |
| structure_aware_medium | chunk_too_large_low_precision | 0 |  | no matching sample in this run |
| structure_aware_medium | section_boundary_split | 0 |  | no matching sample in this run |
| structure_aware_medium | semantic_boundary_error | 0 |  | no matching sample in this run |
| structure_aware_medium | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| structure_aware_medium | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| structure_aware_medium | proposition_context_loss | 0 |  | no matching sample in this run |
| structure_aware_medium | parent_child_not_used | 0 |  | no matching sample in this run |
| structure_aware_large | missed_gold_evidence_at_5 | 1 | bv2-sf-004 | sample found |
| structure_aware_large | chunk_too_small_lost_context | 0 |  | no matching sample in this run |
| structure_aware_large | chunk_too_large_low_precision | 1 | bv2-sf-001 | sample found |
| structure_aware_large | section_boundary_split | 0 |  | no matching sample in this run |
| structure_aware_large | semantic_boundary_error | 0 |  | no matching sample in this run |
| structure_aware_large | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| structure_aware_large | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| structure_aware_large | proposition_context_loss | 0 |  | no matching sample in this run |
| structure_aware_large | parent_child_not_used | 0 |  | no matching sample in this run |
| semantic_meta_like | missed_gold_evidence_at_5 | 1 | bv2-sf-006 | sample found |
| semantic_meta_like | chunk_too_small_lost_context | 1 | bv2-sf-006 | sample found |
| semantic_meta_like | chunk_too_large_low_precision | 0 |  | no matching sample in this run |
| semantic_meta_like | section_boundary_split | 0 |  | no matching sample in this run |
| semantic_meta_like | semantic_boundary_error | 1 | bv2-sf-006 | sample found |
| semantic_meta_like | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| semantic_meta_like | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| semantic_meta_like | proposition_context_loss | 0 |  | no matching sample in this run |
| semantic_meta_like | parent_child_not_used | 0 |  | no matching sample in this run |
| embedding_semantic | missed_gold_evidence_at_5 | 1 | bv2-sf-006 | sample found |
| embedding_semantic | chunk_too_small_lost_context | 1 | bv2-sf-006 | sample found |
| embedding_semantic | chunk_too_large_low_precision | 0 |  | no matching sample in this run |
| embedding_semantic | section_boundary_split | 0 |  | no matching sample in this run |
| embedding_semantic | semantic_boundary_error | 1 | bv2-sf-006 | sample found |
| embedding_semantic | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| embedding_semantic | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| embedding_semantic | proposition_context_loss | 0 |  | no matching sample in this run |
| embedding_semantic | parent_child_not_used | 0 |  | no matching sample in this run |
| proposition_like | missed_gold_evidence_at_5 | 1 | bv2-sf-006 | sample found |
| proposition_like | chunk_too_small_lost_context | 1 | bv2-sf-006 | sample found |
| proposition_like | chunk_too_large_low_precision | 0 |  | no matching sample in this run |
| proposition_like | section_boundary_split | 0 |  | no matching sample in this run |
| proposition_like | semantic_boundary_error | 0 |  | no matching sample in this run |
| proposition_like | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| proposition_like | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| proposition_like | proposition_context_loss | 1 | bv2-sf-006 | sample found |
| proposition_like | parent_child_not_used | 0 |  | no matching sample in this run |
| hierarchical_parent_child | missed_gold_evidence_at_5 | 1 | bv2-sf-006 | sample found |
| hierarchical_parent_child | chunk_too_small_lost_context | 1 | bv2-sf-006 | sample found |
| hierarchical_parent_child | chunk_too_large_low_precision | 0 |  | no matching sample in this run |
| hierarchical_parent_child | section_boundary_split | 0 |  | no matching sample in this run |
| hierarchical_parent_child | semantic_boundary_error | 0 |  | no matching sample in this run |
| hierarchical_parent_child | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| hierarchical_parent_child | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| hierarchical_parent_child | proposition_context_loss | 0 |  | no matching sample in this run |
| hierarchical_parent_child | parent_child_not_used | 1 | bv2-sf-006 | sample found |
| contextual_prefix | missed_gold_evidence_at_5 | 1 | bv2-sf-001 | sample found |
| contextual_prefix | chunk_too_small_lost_context | 1 | bv2-sf-001 | sample found |
| contextual_prefix | chunk_too_large_low_precision | 0 |  | no matching sample in this run |
| contextual_prefix | section_boundary_split | 0 |  | no matching sample in this run |
| contextual_prefix | semantic_boundary_error | 0 |  | no matching sample in this run |
| contextual_prefix | cross_page_evidence_split | 1 | bv2-xp-001 | sample found |
| contextual_prefix | no_answer_retrieved_misleading_context | 1 | bv2-ie-011-runway-performance | sample found |
| contextual_prefix | proposition_context_loss | 0 |  | no matching sample in this run |
| contextual_prefix | parent_child_not_used | 0 |  | no matching sample in this run |
