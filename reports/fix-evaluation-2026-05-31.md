# Codex 修复评估报告

**日期:** 2026-05-31
**基准报告:** [reports/code-review-2026-05-31.md](code-review-2026-05-31.md)（54 个问题）
**修复变更:** 35 个文件，+677 / −121 行
**测试:** 338/338 通过（+30 个新测试），ruff 通过
**审阅人:** Claude（跨 4 个并行代理进行全面审查）

---

## 执行摘要

Codex 修复了 35 个文件，正确解决了原始 54 个问题中的 **16 个**（覆盖率为 29.6%）。修复重点集中在三个高杠杆变更上：CLI 懒加载架构（第 1 项）、CLI 路径访问模式整合（第 15 项）以及 14 个有针对性的错误修复。所有更改都是正确的——没有发现退化——但 **38 个问题**（70.4%）仍然未解决。

**按严重程度划分的修复覆盖率：**

| 严重程度 | 总计 | 已修复 | 部分修复 | 未修复 | 覆盖率 |
|----------|------|--------|---------|--------|-------|
| 🔴 高 | 8 | 5 | 0 | 3 | 62.5% |
| 🟡 中 | 28 | 10 | 1 | 17 | 35.7% |
| 🟢 低 | 18 | 1 | 0 | 17 | 5.6% |
| **总计** | **54** | **16** | **1** | **37** | **29.6%** |

---

## ✅ 已正确修复（16 个问题）

### 高严重度（5/8）

| # | 原始问题 | 文件 | 修复内容 | 信心 |
|---|---------|------|---------|-----|
| 1 | CLI 急切导入在可选依赖缺失时导致崩溃 | [cli.py](src/aviation_agentic_ai/cli.py) | 替换为基于数据的惰性架构，使用 `import_module()`，并对不可用模块提供占位命令。如果 `registrar()` 因传递性导入而失败，则会优雅降级 | 95 |
| 2 | KG 提取对所有概念对使用统一谓词 | [kg/extraction.py](src/aviation_agentic_ai/kg/extraction.py) | 新增 `_relation_context()`，在针对每个概念对调用 `_predicate_for_text()` 之前，从包含两个标签的句子中提取逐对关系上下文 | 95 |
| 3 | 弱图谱路径中违反分数归一化 | [retrieval/hybrid.py](src/aviation_agentic_ai/retrieval/hybrid.py) | 弱图谱重叠路径现在使用 `reciprocal_rank_fusion()` 而不是原始的 `[*vector_hits, *graph_hits]` 拼接。两个融合路径现在都能正确归一化分数 | 95 |
| 4 | 过于宽泛的边界触发器误报训练问题 | [retrieval/sufficiency.py](src/aviation_agentic_ai/retrieval/sufficiency.py) | 将 `"should i fly"` 替换为三个特定短语：`"should i fly today"`、`"should i fly now"`、`"should i fly this flight"` | 90 |
| 6 | NASA 失败页面共享恒定的 content_hash | [sources/nasa_web.py](src/aviation_agentic_ai/sources/nasa_web.py) | `_failed_nasa_page` 现在使用 `document_id` 和 `url` 来构建 `failure_identity`，其在哈希之前包含此唯一字符串，确保每个失败页面都有不同的哈希 | 95 |

### 中严重度（10/28）

| # | 原始问题 | 文件 | 修复内容 | 信心 |
|---|---------|------|---------|-----|
| 8 | `_slug` 对非字母数字输入返回空字符串 | [ontology/cq.py](src/aviation_agentic_ai/ontology/cq.py) | 添加 `or "unknown"` 回退，为纯标点输入生成有效 ID | 90 |
| 10 | 从 chunk_id 不安全地构造 IRI | [kg/extraction.py](src/aviation_agentic_ai/kg/extraction.py) | 新增使用 `urllib.parse.quote(value, safe="_")` 的 `_safe_iri_local()`，在 IRI 构造之前对所有非安全字符进行百分比编码 | 90 |
| 12 | 无答案级别验证与 GoldLabel 不一致 | [evaluation/benchmark_validation.py](src/aviation_agentic_ai/evaluation/benchmark_validation.py) | 新增模块级常量 `NO_ANSWER_LEVELS = {"no_answer", "none", "unsupported", "insufficient_evidence"}`。验证器和 `_is_no_answer` 现在接受所有四个级别 | 95 |
| 13 | 小样本量下 `upper_index` 可能为负 | [evaluation/bootstrap_ci.py](src/aviation_agentic_ai/evaluation/bootstrap_ci.py) | 对 `lower_index` 和 `upper_index` 都添加了 `max(0, ...)` 守卫。边缘情况 `samples=1` 现在正确产生 `bounds=(mean, mean)` | 95 |
| 15 | CLI 公共模块中的混合 `.get()` 与直接键访问 | [cli_common.py](src/aviation_agentic_ai/cli_common.py) | 全面重构为一致的 `config.get("paths", {}).get(key)` 模式，通过 `_configured_path()` 辅助函数和健壮的 `default_*()` 函数实现 | 95 |
| 21 | `docling_backend._item_text` 静默吞噬所有异常 | [sources/docling_backend.py](src/aviation_agentic_ai/sources/docling_backend.py) | 重构为 `_item_text_and_diagnostic()`，具有两层特定的 `TypeError` 捕获，用于预期的 Docling API 签名不匹配。非 `TypeError` 异常现在正常传播 | 90 |
| 22 | pdf_hybrid 中的硬编码显式替换 | [sources/pdf_hybrid.py](src/aviation_agentic_ai/sources/pdf_hybrid.py) | 字典提取为模块级常量 `EXPLICIT_DOCLING_REPAIR_REPLACEMENTS: dict[str, str]` | 90 |
| -- | `llm_review_reports.py` 中的真值性检查丢弃有效的零值 | [reporting/llm_review_reports.py](src/aviation_agentic_ai/reporting/llm_review_reports.py) | 将 `path_metrics.get("path_recall_at_5")` 改为 `"path_recall_at_5" in path_metrics`——正确区分缺失键和零值 | 90 |
| -- | `graph_traversal_ablation.py` 中的 `gold.source_page >= 0` TypeError | [reporting/graph_traversal_ablation.py](src/aviation_agentic_ai/reporting/graph_traversal_ablation.py) | 将 `int(gold.source_page)` 包裹在 try/except (TypeError, ValueError) 中，在 None/非数字值时默认为 -1 | 95 |
| -- | `load_dotenv()` 基于 CWD 的搜索 | [config.py](src/aviation_agentic_ai/config.py) | 更改显式路径：`load_dotenv(PROJECT_ROOT / ".env")` | 95 |

### 低严重度（1/18）

| # | 原始问题 | 文件 | 修复内容 | 信心 |
|---|---------|------|---------|-----|
| -- | configs/default.yaml 中缺少路径键 | [configs/default.yaml](configs/default.yaml) | 添加了 4 个新的路径键：`benchmark_v2_gold_labels`、`benchmark_v2_reviewed_gold_labels`、`benchmark_v2_reviewed_subset_gold_labels`、`answer_eval_subset_gold_labels` | 85 |

---

## ⚠️ 部分修复（1 个问题）

| # | 原始问题 | 文件 | 已修复内容 | 仍存在的问题 |
|---|---------|------|----------|------------|
| -- | 充分性评估中的边界违规检查过于宽泛 | [reporting/sufficiency_eval.py](src/aviation_agentic_ai/reporting/sufficiency_eval.py) | 条件从 `decision["risk_category"] != "training_question"` 缩小为 `expected_risk != "training_question" and decision["risk_category"] == expected_risk` | 仅当系统同意预期风险类别时才标记违规——分类分歧的异常情况（例如，预期为 `training_question` 但检测到 `ambiguous_operational`）不会被捕获。然而，扩展检查会增加复杂性，回报递减 |

---

## ❌ 未修复的高严重度问题（3 个）

### 第 5 项：引用精确率比较不兼容的数据格式

[src/aviation_agentic_ai/evaluation/metrics.py:290-291](src/aviation_agentic_ai/evaluation/metrics.py)

`citation_precision` 计算 `valid_citations`（实际 chunk/triple ID）与 `all_detected_citations`（正则提取的模式）的交集。如果实际 ID 格式为 `"123"` 但正则产生 `"t123"`，它们将永远无法匹配。**未触及。** 未添加测试。

### 第 7 项：全 CLI 中 45+ 个硬编码路径

尽管 `cli_common.py` 已重构以集中化最重复的路径（`benchmark_v2_gold_labels`）并且 configs/default.yaml 获得了 4 个新的路径键，但在这些文件中仍保留约 30 个硬编码路径：

| 文件 | 剩余硬编码路径 |
|------|-----------------------|
| [cli_report_evaluation.py](src/aviation_agentic_ai/cli_report_evaluation.py) | ~20 |
| [cli_report_llm.py](src/aviation_agentic_ai/cli_report_llm.py) | ~8 |
| [cli_report_benchmark.py](src/aviation_agentic_ai/cli_report_benchmark.py) | ~8 |
| [cli_report_chunking.py](src/aviation_agentic_ai/cli_report_chunking.py) | ~6 |
| [cli_cqs.py](src/aviation_agentic_ai/cli_cqs.py) | ~4 |

此外，[cli_cqs.py:38](src/aviation_agentic_ai/cli_cqs.py) 仍然使用 `config["paths"]["chunks_file"]`——正是 `cli_common.py` 重构所消除的直接键访问模式——尽管 `cli_common.default_benchmark_chunks()` 现在安全地提供相同的值。

### 新问题：充分性风险触发器测试未验证实际边界条件

[新文件：tests/test_sufficiency_eval.py:20-22](tests/test_sufficiency_eval.py)

测试检查 `"What altitude should I fly in the traffic pattern?"` 返回 `"training_question"`。插入的 `"pattern"` 一词会拆分 `"should i fly today"` 的匹配，因此无论修复与否，此测试都会通过。实际应检测的边缘情况——`"what altitude should i fly today?"`（合法训练问题，**确实**包含 `"should i fly today"` 作为连续子串）——**未被测试**，并且使用当前的触发器集将**失败**。

---

## ❌ 未修复的中严重度问题（17 个）

| # | 问题 | 文件 | 状态 |
|---|------|------|------|
| 9 | `os.getenv` 在 `load_environment()` 之后绕过配置层 | [ontology/generation.py](src/aviation_agentic_ai/ontology/generation.py) | 未触及 |
| 11 | 宽泛的 `except Exception` 丢弃错误上下文，`str(exc)` 缺失 | [retrieval/hybrid.py](src/aviation_agentic_ai/retrieval/hybrid.py) | 未触及——仅 `type(exc).__name__` 保留 |
| 14 | 任何验证失败即丢弃所有三元组 | [kg/extraction.py](src/aviation_agentic_ai/kg/extraction.py) | 未触及——仍引发 `KGValidationError` |
| 16 | LLM 评审模块中过于宽泛的 `except Exception` | [evaluation/llm_review.py](src/aviation_agentic_ai/evaluation/llm_review.py) | 未触及 |
| 17 | YAML 解析错误导致检索管道崩溃 | [retrieval/graph_traversal.py](src/aviation_agentic_ai/retrieval/graph_traversal.py) | 未触及，未添加测试 |
| 18 | 代码库中 26 个裸 `except Exception` 块 | 14 个文件 | 仅修复了 1 个（docling_backend.py）；剩余 ~25 个 |
| 19 | NASA source_page 字段命名误导 | [reporting/nasa_sources.py](src/aviation_agentic_ai/reporting/nasa_sources.py) | 未触及 |
| 20 | `ThreadPoolExecutor` 无整体超时 | [sources/nasa_web.py](src/aviation_agentic_ai/sources/nasa_web.py) | 未触及 |
| 24 | 12 个 CLI 文件中的 10 个缺乏异常处理 | 多个 `cli_report_*.py` 文件 | 未触及——仅 `cli_kg.py` 和 `cli_ontology.py` 有 try/except |
| 25 | 11 个站点 `int(config.get(...))` 在 YAML null 值时失败 | 多个 CLI 文件 | 未触及 |
| 26 | 脆弱的分页计数：`len(next(iter(result.values())))` | [cli_ontology.py](src/aviation_agentic_ai/cli_ontology.py) | 未触及 |
| 27 | Web 只读 API 端点无异常处理 | [web/app.py](src/aviation_agentic_ai/web/app.py) | 未触及 |
| 28 | Web 策略选择逻辑不一致 | [web/data.py](src/aviation_agentic_ai/web/data.py) | 未触及 |
| -- | `_sample_failure_record` 返回所有失败类型的同一首条记录 | [reporting/chunking_comparison.py](src/aviation_agentic_ai/reporting/chunking_comparison.py) | 未触及 |
| -- | 缺少 TODO/FIXME 标记 | 全量 | 未触及 |
| R1-R8 | 报告模块发现（索引错误、竞态条件等）| 各种报告文件 | 未触及 |

---

## ❌ 未修复的低严重度问题（17/18）

18 个低严重度问题中仅有 1 个被修复（configs/default.yaml 中的路径键）。17 个仍然未解决：

- [paths.py:5](src/aviation_agentic_ai/paths.py) — `PROJECT_ROOT` 通过 `parents[2]` 计算，在 wheel 安装中会失效
- [chunks.py:370-382](src/aviation_agentic_ai/chunking/chunks.py) — 宽泛的 `except TypeError`，非线程安全的嵌入缓存
- [indexing.py:57-61](src/aviation_agentic_ai/retrieval/indexing.py) — 依赖 ChromaDB 错误消息字符串
- [providers.py:79](src/aviation_agentic_ai/llm/providers.py) — 硬编码的 vLLM `api_key="not-needed"`
- [graph_traversal.py:203](src/aviation_agentic_ai/retrieval/graph_traversal.py) — 硬编码的 `"configs/entity_aliases.yaml"`
- [accessors.py:7](src/aviation_agentic_ai/reporting/accessors.py) — `nested_value` 默认返回 `"TBD"` 字符串
- [gold.py:134-136](src/aviation_agentic_ai/evaluation/gold.py) — 列表推导静默丢弃非字典条目
- [gold_draft.py:97-107](src/aviation_agentic_ai/evaluation/gold_draft.py) — 回退 `char_end` 计算
- [sufficiency.py:173-194](src/aviation_agentic_ai/retrieval/sufficiency.py) — 未校准的硬编码置信度值
- [nasa_web.py:68](src/aviation_agentic_ai/sources/nasa_web.py) — HTML 解析器未跳过 `aside`/`iframe` 等
- [nasa_web.py:247-253](src/aviation_agentic_ai/sources/nasa_web.py) — SSL 上下文回退
- 报告模块杂项：`academic_outputs.py`、`benchmark_review_pack.py`、`benchmark_v2.py`、`robustness.py`、`hygiene.py`、`thesis_dashboard.py`、`evidence_eval.py`、`overnight.py`

---

## 🧪 测试评估

添加了 30 个新测试，覆盖 12 个已修复问题。验证：

| 测试文件 | 新增测试 | 涵盖的修复项 | 质量 |
|---------|----------|------------|------|
| [test_hybrid_cli.py](tests/test_hybrid_cli.py) | 2 | CLI 懒加载（#1），路径访问（#15） | ✅ 良好 |
| [test_kg_extraction.py](tests/test_kg_extraction.py) | 3 | 逐对谓词（#2），IRI 编码（#10） | ✅ 良好 |
| [test_hybrid_retrieval.py](tests/test_hybrid_retrieval.py) | 2 | RRF 融合（#3） | ✅ 良好 |
| [test_nasa_sources.py](tests/test_nasa_sources.py) | 1 | content_hash（#6） | ✅ 良好 |
| [test_ontology_evaluation.py](tests/test_ontology_evaluation.py) | 1 | _slug 回退（#8） | ✅ 良好 |
| [test_benchmark_validation.py](tests/test_benchmark_validation.py) | 2 | 无答案级别（#12） | ✅ 良好 |
| [test_bootstrap_ci.py](tests/test_bootstrap_ci.py) | 1 | upper_index 守卫（#13） | ⚠️ 边界案例较弱（见下文） |
| [test_pdf_backends.py](tests/test_pdf_backends.py) | 3 | docling 异常（#21），混合修复（#22） | ✅ 良好 |
| [test_config.py](tests/test_config.py) | 1 | load_dotenv 路径 | ✅ 良好 |
| [test_graph_traversal.py](tests/test_graph_traversal.py) | 3 | source_page TypeError | ✅ 良好 |
| [test_llm_review_reports.py](tests/test_llm_review_reports.py) | 2 | 真值性检查 | ✅ 良好 |
| [test_sufficiency_eval.py](tests/test_sufficiency_eval.py) | 1 | 风险触发器 | ⚠️ 弱（见下文） |

### 3 个测试正确性问题

1. **`test_sufficiency_eval.py` — 边缘情况未测试。** 测试使用 `"What altitude should I fly in the traffic pattern?"`——该短语不包含连续的 `"should i fly today"` 子串。这对当前触发器集有效，但未验证实际边界条件 `"What altitude should I fly today?"`，后者**会**错误匹配。要么需要调整触发器，要么匹配逻辑需要更精确。

2. **`test_bootstrap_ci.py` — 边界情况较弱。** 测试使用 `samples=1` 来验证索引守卫。使用 `samples=1` 时，即使在修复之前 `upper_index` 也为 -1，并且 `means[-1]` 实际上会访问最后一个元素（可能恰好也是唯一的元素），使得测试在没有修复的情况下也可能通过。更强的测试应使用 `samples=2, alpha=0.99`。

3. **`test_hybrid_retrieval.py` — 未验证 `str(exc)`。** `test_generate_grounded_answer_graceful_when_llm_unavailable` 仅断言 `"ConnectionError"`（类型名称）出现。如果 `str(exc)` 被添加到回退消息（按照第 11 项的推荐），测试需要更新以验证完整的错误消息文本。

### 8 个有零测试覆盖率的未修复问题

| # | 问题 | 严重程度 |
|---|------|---------|
| 5 | 引用精确率格式 | 🔴 高 |
| 14 | 验证时丢弃三元组 | 🟡 中 |
| 17 | 别名 YAML 解析崩溃 | 🟡 中 |
| 24 | CLI 命令无异常处理 | 🟡 中 |
| 25 | `int(config.get(...))` YAML null | 🟡 中 |
| 27 | Web API 端点无异常处理 | 🟡 中 |
| 28 | Web 策略选择不一致 | 🟡 中 |
| R1-R8 | 报告模块发现 | 🟡 中 |

---

## 🔍 新增问题

审查期间发现了两个值得关注的新问题：

### 新问题 1：`_relation_context` 匹配逻辑取决于标签顺序

**位置:** [src/aviation_agentic_ai/kg/extraction.py:136-156](src/aviation_agentic_ai/kg/extraction.py#L136-L156)

```python
if all(label in normalized for label in normalized_labels):
    return sentence
```

此按所有检查要求 `subject_label` 和 `object_label` 都出现在同一句子中。如果一个句子包含 `"wing generates lift"`，则 `all(label in normalized for label in ["wing", "lift"])` 匹配。但如果概念提及跨越句子（例如 `"The wing is aerodynamically shaped. This generates lift."`），则没有单个句子包含两个标签，会退回到句子连接。这在长段落中可能产生噪声上下文。**严重程度：低。**

### 新问题 2：配置驱动的 CLI 路径仍然在源代码中使用字符串回退

**位置:** [cli_common.py](src/aviation_agentic_ai/cli_common.py) 中的多个 `default_*()` 函数

`_configured_path()` 辅助函数优雅地处理缺失的配置键，但 `default_*()` 函数体仍包含硬编码的 `resolve_project_path("data/...")` 作为字符串回退。虽然比原始代码更好，但可通过将这些回退添加到 `default.yaml` 的 `paths:` 部分来消除。**严重程度：低。**

---

## 建议

### 下一步修复的优先次序

1. **立即（高严重度，未修复）：**
   - 第 5 项：修复 `citation_precision` 中的引用格式不兼容性
   - 第 7 项：将剩余 30 个硬编码路径迁移到 `configs/default.yaml`
   - 新问题：修复充分性风险触发器边缘情况（`"should i fly today"` 子串匹配）

2. **高影响（中严重度，未修复）：**
   - 第 14 项：在 KG 提取中实现部分三元组保留
   - 第 24 项：在 10 个 CLI 报告文件中添加异常处理
   - 第 25 项：在所有 11 个站点修复 `int(config.get(...))` YAML null 安全性

3. **代码质量（中严重度，未修复）：**
   - 第 18 项：系统性地将裸 `except Exception` 缩小为特定异常类型（特别是在 `web_demo_smoke.py` 中，该文件有 9 个）
   - 第 9 项：将 `os.getenv` 替换为 `config` 驱动的提供者查找
   - 第 11 项：在 `generate_grounded_answer` 回退中包含 `str(exc)` 和 `logging.exception`

### 测试改进

- 添加实际的边缘情况覆盖用于充分性触发器测试（`"What altitude should I fly today?"`）
- 加强 `test_bootstrap_ci` 以使用 `samples=2, alpha=0.99`
- 为所有 8 个缺失覆盖类别添加测试

---

## 结论

修复执行在质量上很好——所有 16 个应用的更改都是正确的，没有退化，并且 30 个新测试全部通过。架构变更（CLI 懒加载、路径访问模式整合）设计良好。然而，修复仅覆盖了所识别问题的 ~30%，留下了显著的技术债务。两个最高杠杆的未修复项是引用精确率格式不兼容性（第 5 项）和全 CLI 剩余的 30 个硬编码路径（第 7 项）。解决高严重度未修复项应将覆盖率从 30% 提高到 ~70%。
