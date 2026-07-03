# Chunking Implementation Audit

- This audit records implemented behavior, not aspirational method labels.
- Partial methods remain explicitly marked partial until retrieval returns the claimed context unit.

| Strategy | Family | Retrieval unit | Returned context | Backend | Parent-child | Status | Name accuracy | Chunks | Avg chars | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| fixed_window | fixed_window | chunk_text | chunk_text | none | not_applicable | implemented | accurate | 35 | 1034.11 | May cut semantic or structural boundaries. |
| sentence_recursive | sentence_recursive | sentence_merged_chunk | sentence_merged_chunk | none | not_applicable | implemented | accurate | 35 | 1022.11 | Sentence-aware merging is deterministic, not learned. |
| structure_aware | structure_aware | section_line_merged_chunk | section_line_merged_chunk | none | not_applicable | implemented | accurate | 267 | 233.36 | Heading/list detection is heuristic and page-local. |
| semantic_meta_like | semantic_boundary_lexical | lexical_semantic_chunk | lexical_semantic_chunk | lexical_similarity | not_applicable | implemented | accurate | 56 | 580.55 | Semantic boundary decisions use lexical similarity, not embeddings. |
| fixed_small | fixed_window | chunk_text | chunk_text | none | not_applicable | implemented | accurate | 112 | 361.75 | May cut semantic or structural boundaries. |
| fixed_medium | fixed_window | chunk_text | chunk_text | none | not_applicable | implemented | accurate | 48 | 794.21 | May cut semantic or structural boundaries. |
| fixed_large | fixed_window | chunk_text | chunk_text | none | not_applicable | implemented | accurate | 27 | 1359.19 | May cut semantic or structural boundaries. |
| recursive_small | sentence_recursive | sentence_merged_chunk | sentence_merged_chunk | none | not_applicable | implemented | accurate | 107 | 358.78 | Sentence-aware merging is deterministic, not learned. |
| recursive_medium | sentence_recursive | sentence_merged_chunk | sentence_merged_chunk | none | not_applicable | implemented | accurate | 48 | 782.17 | Sentence-aware merging is deterministic, not learned. |
| recursive_large | sentence_recursive | sentence_merged_chunk | sentence_merged_chunk | none | not_applicable | implemented | accurate | 27 | 1355.26 | Sentence-aware merging is deterministic, not learned. |
| structure_aware_medium | structure_aware | section_line_merged_chunk | section_line_merged_chunk | none | not_applicable | implemented | accurate | 48 | 775.02 | Heading/list detection is heuristic and page-local. |
| structure_aware_large | structure_aware | section_line_merged_chunk | section_line_merged_chunk | none | not_applicable | implemented | accurate | 27 | 1349.63 | Heading/list detection is heuristic and page-local. |
| embedding_semantic | semantic_boundary_embedding | embedding_semantic_chunk | embedding_semantic_chunk | sentence_transformers | not_applicable | implemented_with_deterministic_fallback | conditional_on_backend | 53 | 613.47 | Only true semantic when the sentence-transformers backend loads. |
| proposition_like | proposition_like_heuristic | cue_sentence_or_merged_chunk | proposition_only | none | not_applicable | heuristic_partial | partial_should_not_be_called_llm_proposition_extraction | 85 | 383.33 | Cue-word segmentation is deterministic and not LLM proposition extraction.; Current retrieval returns proposition-like units, not parent paragraph context. |
| hierarchical_parent_child | hierarchical_parent_child | child_chunk | child_chunk_text | none | partial_child_index_parent_metadata | partial | partial_parent_metadata_only | 107 | 358.78 | Parent text is stored in chunk metadata but the retriever returns child text.; Do not claim full parent-return retrieval for this strategy. |
| contextual_prefix | contextual_prefix | prefix_plus_chunk_text | prefix_plus_chunk_text | none | not_applicable | implemented_no_llm_contextualization | accurate | 279 | 303.71 | Prefix is deterministic source metadata, not LLM contextual retrieval. |
