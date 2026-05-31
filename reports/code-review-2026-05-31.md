# 代码审阅报告（第二轮）

**日期:** 2026-05-31
**审阅范围:** `aviation_agentic_ai` 全量代码（commit `58c0180`）
**覆盖:** 94 个 Python 源文件，48 个测试文件
**验证状态:** `ruff check` 通过，`pytest` 308/308 通过
**审阅轮次:** 第 1 轮（核心模块）+ 第 2 轮（web/sources/CLI 报告/配置/测试）

---

## 统计概览

| 严重度 | 数量 |
|--------|------|
| 🔴 高 | 8 |
| 🟡 中 | 28 |
| 🟢 低 | 18 |
| **合计** | **54** |

系统性发现：
- **26 个**裸 `except Exception` 块
- **45+ 个**硬编码文件路径（违反 CLAUDE.md "Keep paths config-driven"）
- **12 个** CLI 命令文件中有 **10 个**缺乏异常处理
- **11 处** `int(config.get(...))` / `float(config.get(...))` 在 YAML null 值时失败
- **8 个**文件定义了各自不同语义的 `_load_json` / `_read_json` 帮助函数

---

## 🔴 高严重度（6 个问题）

### 1. CLI 启动时急切导入 17 个子命令模块，可选依赖缺失时整个 CLI 崩溃

**位置:** [src/aviation_agentic_ai/cli.py:5-21](src/aviation_agentic_ai/cli.py#L5-L21)

`cli.py` 在模块顶层导入 17 个子命令模块。任何传递性导入链拉入未安装的可选包（`chromadb`、`fastapi`、`langchain`、`sentence-transformers`、`docling` 等），所有命令都会因 `ImportError` 而崩溃——包括 `--help`。

**复现:**
```bash
pip install aviation-agentic-ai          # 不安装 optional-dependencies
aviation-ai ontology validate            # 崩溃
aviation-ai --help                       # 甚至这个也崩溃
```

**修复方向:** 将子命令导入包裹在 `try/except ImportError` 中，延迟到命令调用时失败；或将注册逻辑移到在组被调用时触发的懒加载函数中。

---

### 2. 确定性 KG 提取对所有概念对使用统一谓词

**位置:** [src/aviation_agentic_ai/kg/extraction.py:127-135](src/aviation_agentic_ai/kg/extraction.py#L127-L135)

`_deterministic_triples_for_chunk` 对整个 chunk 调用一次 `_predicate_for_text(chunk.text)`，然后将其应用于该 chunk 中所有相邻概念对。对于同时包含 "wing"、"airfoil"、"boundary layer" 和 "lift" 的 chunk，`airfoil hasComponent boundary_layer` 和 `boundary_layer hasComponent lift` 会得到相同的 `hasComponent` 谓词，尽管这些关系的语义不同。

**后果:** 确定性 KG 提取路径产生的三元组在结构上错误，使其在可解释性分析中不可靠。

---

### 3. 违反分数归一化要求：原始向量分数与原始图谱分数直接拼接

**位置:** [src/aviation_agentic_ai/retrieval/hybrid.py:195](src/aviation_agentic_ai/retrieval/hybrid.py#L195)

`vector_first_guarded_fusion` 在弱图谱重叠时执行 `[*vector_hits, *graph_hits]`。向量命中使用从余弦距离转换而来的 `1.0/(1.0+d)` 分数（范围约 0.33–1.0），而图谱命中使用整数词项重叠计数（范围 1, 2, 3, …）。然后 `_merge_duplicate_hit` 通过原始数值比较对这些命中进行去重（[hybrid.py:140](src/aviation_agentic_ai/retrieval/hybrid.py#L140)）。

**这直接违反了 CLAUDE.md 中的规定:**
> "Hybrid retrieval must normalize or rank-fuse scores. Do not add raw graph scores and raw vector cosine scores directly."

强重叠路径正确使用了 `reciprocal_rank_fusion`（[hybrid.py:193](src/aviation_agentic_ai/retrieval/hybrid.py#L193)）。弱重叠路径也应使用 RRF。

---

### 4. 过于宽泛的边界触发器导致训练问题被错误拒绝

**位置:** [src/aviation_agentic_ai/retrieval/sufficiency.py:57](src/aviation_agentic_ai/retrieval/sufficiency.py#L57)

`RISK_TRIGGERS["go_no_go_decision"]` 包含触发器 `"should i fly"`。此文本是如 `"what altitude should i fly at today?"`（一个合法的训练问题）的子串。由于 `detect_risk_category` 在首次匹配时即返回，边界闸在证据充分性被评估之前就抢占了。

**后果:** 即使证据完美充分，系统也会静默拒绝合法训练问题。

---

### 5. 引用精确率比较不兼容的数据格式

**位置:** [src/aviation_agentic_ai/evaluation/metrics.py:290-291](src/aviation_agentic_ai/evaluation/metrics.py#L290-L291)

`citation_precision` 计算 `set(valid_citations)` 和 `all_detected_citations` 的交集。但 `valid_citations` 包含来自数据的实际 chunk/triple ID，而 `all_detected_citations` 还混合了正则提取的模式。如果实际三元组 ID 格式为 `"123"` 而正则模式产生 `"t123"`，它们将永远无法匹配。

---

### 6. 🆕 NASA 失败页面的 content_hash 恒为常量

**位置:** [src/aviation_agentic_ai/sources/nasa_web.py:903-905](src/aviation_agentic_ai/sources/nasa_web.py#L903-L905)

`_failed_nasa_page` 设置 `cleaned_text = ""` 然后计算其 SHA-256，总是产生 `e3b0c44...`（空字符串的哈希）。多个不同的失败页面将共享相同的 `content_hash`，使去重和完整性校验失效。

**修复:** 使用 `record["url"]` 或 `record["document_id"]` 作为哈希输入，确保失败页面有唯一的标识。

---

### 7. 🆕 全 CLI 45+ 处硬编码文件路径，违反 CLAUDE.md 约束

**位置:** 12 个 CLI 文件中分散存在

CLAUDE.md 明确要求 "Keep paths config-driven. Avoid hardcoded absolute paths in code." 然而同一字符串 `"data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"` 在 CLI 文件中出现了 **10 次**，总计 45+ 个硬编码路径。每次的出现形式都是 `or resolve_project_path("data/...")`——这些全部应该通过 `load_default_config()` 从 `configs/default.yaml` 中的 `paths:` 键获取。

**受影响文件:**
| 文件 | 硬编码路径数 |
|------|------------|
| `cli_report_evaluation.py` | ~20 |
| `cli_report_llm.py` | ~8 |
| `cli_report_benchmark.py` | ~8 |
| `cli_report_chunking.py` | ~6 |
| `cli_report_thesis.py` | ~4 |
| `cli_cqs.py`、`cli_ontology.py`、`cli_kg.py`、`cli_report_stage.py` 等 | ~10 |

**风险:** 路径重构需要跨多个文件进行手动、易出错的编辑。配置重命名一处即可解决。

---

## 🟡 中严重度（22 个问题）

### 7. `load_dotenv()` 使用基于 CWD 的搜索，可能找不到 .env

**位置:** [src/aviation_agentic_ai/config.py:50](src/aviation_agentic_ai/config.py#L50)

`load_dotenv()` 调用时没有 `dotenv_path` 参数。`python-dotenv` 默认从 CWD 向上搜索 `.env`。如果从项目树之外的目录调用 CLI，将永远找不到 `.env` 文件。

**修复:** 改为 `load_dotenv(PROJECT_ROOT / ".env")`。

---

### 8. `_slug` 对非字母数字输入返回空字符串

**位置:** [src/aviation_agentic_ai/ontology/cq.py:82-83](src/aviation_agentic_ai/ontology/cq.py#L82-L83)

列表推导为每个非字母数字字符产生 `"-"`。若输入完全没有字母数字字符（例如 `"---"`），`_slug` 返回 `""`。这在 `stable_cq_id` 中传播，产生格式错误的 ID。

**修复:** 对空结果添加回退值 `or "unknown"`。

---

### 9. 在 `load_environment()` 之后使用原始 `os.getenv`

**位置:** [src/aviation_agentic_ai/ontology/generation.py:185-198](src/aviation_agentic_ai/ontology/generation.py#L185-L198)

`_llm_manifest_metadata` 调用 `load_environment()` 但随后直接使用 `os.getenv` 读取 `DEEPSEEK_BASE_URL`、`VLLM_PORT`、`OPENAI_BASE_URL`。应使用与 `configured_llm_provider()` 相同的配置机制。

**修复:** 使用 [providers.py](src/aviation_agentic_ai/llm/providers.py) 中的 `configured_llm_provider()` 和 `configured_llm_model()` 等函数。

---

### 10. 从未经净化的 chunk_id 进行不安全的 IRI 构建

**位置:** [src/aviation_agentic_ai/kg/extraction.py:389,392](src/aviation_agentic_ai/kg/extraction.py#L389)

`ns[f"KGTriple_{triple.triple_id.replace('-', '_')}"]` 使用 `triple_id` 作为 Turtle IRI 本地名称。`triple_id` 源自 `chunk_id`，可能包含对 Turtle IRI 本地名称无效的字符。唯一应用的净化是将 `-` 替换为 `_`。

**修复:** 在构造 IRI 之前对 `triple_id` 进行 URL 编码。

---

### 11. 宽泛的 `except Exception` 丢弃错误上下文

**位置:** [src/aviation_agentic_ai/retrieval/hybrid.py:279-285](src/aviation_agentic_ai/retrieval/hybrid.py#L279-L285)

`generate_grounded_answer` 捕获 `Exception` 但仅在回退消息中保留 `type(exc).__name__`。实际的错误消息和根因被静默丢弃。

**修复:** 在回退消息中包含 `str(exc)`；考虑添加 `logging.exception`。

---

### 12. 无答案级别验证与 GoldLabel 数据模型不一致

**位置:**
- [src/aviation_agentic_ai/evaluation/benchmark_validation.py:175-176](src/aviation_agentic_ai/evaluation/benchmark_validation.py#L175-L176)
- [src/aviation_agentic_ai/evaluation/gold.py:81](src/aviation_agentic_ai/evaluation/gold.py#L81)

验证器仅接受 `gold_level == "no_answer"`，但 `GoldLabel.from_dict` 将四个级别视为有效的无答案标签。

**修复:** 要么让验证器接受全部四个级别，要么让 `GoldLabel.from_dict` 在存储前规范化。

---

### 13. 极小样本量时 `upper_index` 可能为负

**位置:** [src/aviation_agentic_ai/evaluation/bootstrap_ci.py:38](src/aviation_agentic_ai/evaluation/bootstrap_ci.py#L38)

`upper_index` 仅通过 `min(samples - 1, ...)` 设置上限，没有 `max(0, ...)` 下限守卫。当 `samples=1` 时产生 `-1`。

**修复:** `max(0, min(samples - 1, int((1.0 - alpha / 2.0) * samples) - 1))`

---

### 14. 任何验证失败即丢弃所有三元组

**位置:** [src/aviation_agentic_ai/kg/extraction.py:715-716](src/aviation_agentic_ai/kg/extraction.py#L715-L716)

如果 `report["valid"]` 为`False`，则引发 `KGValidationError`。意味着如果 99 个三元组有效且 1 个失败，全部 100 个都被丢弃。

**修复:** 写入有效三元组子集并提供包含跳过原因的部分报告。

---

### 15. CLI 公共模块中混合安全的 `.get()` 与直接键访问

**位置:**
- [src/aviation_agentic_ai/cli_common.py:11](src/aviation_agentic_ai/cli_common.py#L11) — `.get("curated_ontology")` ✅
- [src/aviation_agentic_ai/cli_common.py:16](src/aviation_agentic_ai/cli_common.py#L16) — `config["paths"]["baseline_ontology"]` ❌
- [src/aviation_agentic_ai/cli_common.py:21](src/aviation_agentic_ai/cli_common.py#L21) — `config["paths"]["chunks_file"]` ❌

同样模式出现在多个 CLI 报告文件中（`cli_report_nasa.py`、`cli_report_pdf.py` 等）。

---

### 16. LLM 评审模块中过于宽泛的 `except Exception`

**位置:** [src/aviation_agentic_ai/evaluation/llm_review.py:379](src/aviation_agentic_ai/evaluation/llm_review.py#L379)

捕获所有 `Exception` 子类，包括 `json.JSONDecodeError`、`ValueError`、`KeyError` 和 `AttributeError`（全部静默处理）。

**修复:** 分别捕获预期的异常类型；让意外异常传播或记录完整回溯。

---

### 17. YAML 解析错误导致检索管道崩溃

**位置:** [src/aviation_agentic_ai/retrieval/graph_traversal.py:206](src/aviation_agentic_ai/retrieval/graph_traversal.py#L206)

`load_entity_aliases` 调用 `load_yaml(alias_path)` 且无 try/except。如果别名 YAML 文件损坏，`ValueError` 会传播到 `graph_search_traversal`。

**修复:** 包裹在 try/except 中，返回空别名字典并记录警告。

---

### 18. 🆕 全代码库 26 个裸 `except Exception` 块

**系统性代码质量问题。** 分布在 14 个文件中：

| 文件 | 数量 |
|------|------|
| `reporting/web_demo_smoke.py` | 9 |
| `chunking/chunks.py` | 2 |
| `sources/docling_backend.py` | 3 |
| `sources/nasa_web.py` | 1 |
| `ontology/validation.py` | 2 |
| `ontology/generation.py` | 2 |
| `ontology/evaluation.py` | 1 |
| `kg/extraction.py` | 1 |
| `retrieval/hybrid.py` | 1 |
| `retrieval/indexing.py` | 1 |
| `evaluation/llm_review.py` | 1 |
| `web/app.py` | 1 |
| `reporting/llm_review_reports.py` | 1 |

其中 `web_demo_smoke.py` 单个文件包含 9 个裸 `except Exception` 块。多项捕获在丢弃异常时只保存了 `type(exc).__name__`，丢失了诊断信息。

---

### 19. 🆕 NASA 来源 `source_page` 字段命名误导

**位置:** [src/aviation_agentic_ai/reporting/nasa_sources.py:610-611](src/aviation_agentic_ai/reporting/nasa_sources.py#L610-L611)

`_label()` 中 `source_page` 被设为 `section_order`（section 顺序编号，来自 `_page_snippet`），而非实际文档页码。字段名称暗示存储的是页码，在依赖 `source_page` 为页码的下游指标中会造成混淆。

---

### 20. 🆕 `ThreadPoolExecutor` 无整体超时

**位置:** [src/aviation_agentic_ai/sources/nasa_web.py:986-996](src/aviation_agentic_ai/sources/nasa_web.py#L986-L996)

`ingest_nasa_sources` 使用 `ThreadPoolExecutor.map` 并行获取数据。虽然 `fetch_nasa_page` 的单次 HTTP 请求有 30s 超时，但如果多个 worker 同时运行或网络极慢，累计等待时间无上限。

**修复:** 使用 `concurrent.futures.as_completed` 并设置整体超时，或使用 `ThreadPoolExecutor` 的超时参数。

---

### 21. 🆕 `docling_backend._item_text` 静默吞噬所有异常

**位置:** [src/aviation_agentic_ai/sources/docling_backend.py:68](src/aviation_agentic_ai/sources/docling_backend.py#L68)

```python
except Exception:
    return ""
```

这吞噬了 `export_to_markdown()` 引发的所有异常——包括由代码 bug 引起的 `AttributeError`。应区分预期的故障模式（API 兼容性问题）和未预期的错误。

---

### 22. 🆕 `pdf_hybrid.py` 中硬编码的显式替换

**位置:** [src/aviation_agentic_ai/sources/pdf_hybrid.py:99](src/aviation_agentic_ai/sources/pdf_hybrid.py#L99)

```python
explicit_replacements = {"ORESSURE": "PRESSURE"}
```

已知 Docling OCR 产物的列表硬编码在函数内部。应移至数据文件或配置驱动字典中，以便维护和扩展。

---

### 23. 🆕 代码库中无 TODO/FIXME 标记

全源树中 `grep -rn "TODO\|FIXME\|HACK\|XXX\|BUG" src/` 返回零结果。这意味着已知修复项没有被追踪，可能积累为技术债务。

---

### 24. 🆕 12 个 CLI 文件中的 10 个缺乏异常处理

**位置:** 所有 `cli_report_*.py` 和部分 `cli_*.py` 文件

仅有 `cli_kg.py` 和 `cli_ontology.py` 包含 `try:` 语句。所有其他命令直接调用写入/计算函数（`write_benchmark_v2_summary()`、`write_chunking_comparison_v2()`、`write_evidence_cards()` 等）而不包裹 try/except。如果这些函数抛出任何异常（IOError、PermissionError、LLM 调用错误），用户会看到原始 Python traceback 而非清晰的 `ClickException`。

**修复:** 将每个命令函数体包裹在 `try: ... except Exception as exc: raise click.ClickException(str(exc)) from exc` 中。

---

### 25. 🆕 11 处 `int(config.get(...))` / `float(config.get(...))` 在 YAML null 值时失败

**位置:**
- `cli_report_chunking.py:63`
- `cli_report_evaluation.py:65-67, 292-293`
- `cli_query.py:49, 51, 52`
- `cli_kg.py:79, 82`
- `cli_ontology.py:252-265`

Python 的 `dict.get(key, default)` 在键**存在但值为 `None`**（YAML `null`）时返回 `None` 而非 default。然后 `int(None)` 引发 `TypeError`。

**修复:** 使用 `int(config.get("key") or 5)` 或 `int(config.get("key", 5) or 5)`。

---

### 26. 🆕 脆弱的分页计数：`len(next(iter(result.values())))`

**位置:** [src/aviation_agentic_ai/cli_ontology.py:196](src/aviation_agentic_ai/cli_ontology.py#L196)

```python
pages = len(next(iter(result.values()))) if result else 0
```

这通过获取结果字典中第一个值并调用其 `len()` 来计算页数。如果结果的内部结构改变（例如第一个值不是集合），可能返回字符串长度、引发 TypeError，或给出完全错误的数值。

---

### 27. 🆕 Web: 只读 API 端点缺少异常处理

**位置:** [src/aviation_agentic_ai/web/app.py:157-195](src/aviation_agentic_ai/web/app.py#L157-L195)

`/api/status`、`/api/demo/explanation`、`/api/questions`、`/api/experiments/summary` 端点直接调用 build 函数而没有 try/except。如果底层 JSON 数据文件损坏，`WebDataReadError` 会传播到 FastAPI，返回通用 HTTP 500——与 `/api/query`（正确返回结构化 502/503）不一致。

---

### 28. 🆕 Web: 选择策略逻辑不一致

**位置:**
- [src/aviation_agentic_ai/web/data.py:603-605](src/aviation_agentic_ai/web/data.py#L603-L605) — 使用解析后的 JSON 真值性
- [src/aviation_agentic_ai/web/data.py:213](src/aviation_agentic_ai/web/data.py#L213) — 使用文件存在性

`selected_default_strategy` 可以因 JSON 文件存在但包含空对象而在两次调用中取不同值。对该值的检查必须一致。

---

## 🟢 低严重度 / 设计问题（16 个问题）

| # | 位置 | 问题 |
|---|------|------|
| 24 | [paths.py:5](src/aviation_agentic_ai/paths.py#L5) | `PROJECT_ROOT` 通过 `Path(__file__).resolve().parents[2]` 计算——在非可编辑安装（wheel 打包）中会指向 `site-packages/` 而非项目根目录 |
| 25 | [chunks.py:370-375](src/aviation_agentic_ai/chunking/chunks.py#L370-L375) | 宽泛的 `except TypeError` 捕获了 SentenceTransformer 构造中**所有** TypeError，不仅仅是 `local_files_only` 参数缺失的情况 |
| 26 | [chunks.py:378-382](src/aviation_agentic_ai/chunking/chunks.py#L378-L382) | 嵌入缓存字典在并发读/写下不是线程安全的 |
| 27 | [indexing.py:57-61](src/aviation_agentic_ai/retrieval/indexing.py#L57-L61) | 依赖 ChromaDB 精确错误消息字符串——可能因库版本变更而失效 |
| 28 | [providers.py:79](src/aviation_agentic_ai/llm/providers.py#L79) | vLLM 的 `api_key="not-needed"` 硬编码——若 vLLM 实例配置要求 API 密钥验证则会失败 |
| 29 | [graph_traversal.py:203](src/aviation_agentic_ai/retrieval/graph_traversal.py#L203) | `"configs/entity_aliases.yaml"` 硬编码为字符串——应来自配置层 |
| 30 | [accessors.py:7](src/aviation_agentic_ai/reporting/accessors.py#L7) | `nested_value` 通用工具函数默认返回 `"TBD"` 字符串——数值调用者对比 `"TBD"` 检测缺失值时可能出 bug |
| 31 | [gold.py:134,136](src/aviation_agentic_ai/evaluation/gold.py#L134-L136) | 列表推导静默丢弃非字典条目且无警告 |
| 32 | [gold_draft.py:97-107](src/aviation_agentic_ai/evaluation/gold_draft.py#L97-L107) | 回退 `char_end` 使用空白符折叠文本长度对标原始文本位置——可能指向错误字符边界 |
| 33 | [sufficiency.py:173-194](src/aviation_agentic_ai/retrieval/sufficiency.py#L173-L194) | 硬编码的置信度值（0.9、0.85、0.7 等）无经验校准 |
| 34 | [nasa_web.py:68](src/aviation_agentic_ai/sources/nasa_web.py#L68) | `MainContentParser.handle_starttag` 未跳过 `aside`、`noscript`、`template`、`iframe`、`object` 元素——可能注入意外内容 |
| 35 | [nasa_web.py:247-253](src/aviation_agentic_ai/sources/nasa_web.py#L247-L253) | `certifi` 不可用时回退到 `ssl.create_default_context()`——某些系统可能缺乏必要的根证书 |

---

## 已确认无误项

- **`config.py:10`** — `_ENVIRONMENT_LOADED` 哨兵正确工作；测试正确使用 monkeypatching 重置。
- **`config.py:23`** — 对空 YAML 文件的 `yaml.safe_load(stream) or {}` 防御性处理正确。
- **`hybrid.py:93`** — RRF 实现本身正确；违反归一化规定仅影响弱图谱重叠路径。
- **`kg/extraction.py:112-115`** — SHA1 40 位截断哈希碰撞风险可忽略不计。
- **`ontology/evaluation.py:1031`** — 混合类型排序键在实践中不会触发（所有页面键均为数字字符串）。
- **`.gitignore`** — 正确排除了 `.env`、`.venv/`、`data/indexes/`、`data/chunks/`、`*.faiss`、`*.index`、`*.sqlite3` 等。

---

## 快速修复项

以下是可立即、各自独立修复的项目：

1. **[config.py:50](src/aviation_agentic_ai/config.py#L50)** — 将 `load_dotenv()` 改为 `load_dotenv(PROJECT_ROOT / ".env")`
2. **[bootstrap_ci.py:38](src/aviation_agentic_ai/evaluation/bootstrap_ci.py#L38)** — 添加 `max(0, ...)` 守卫
3. **[benchmark_validation.py:175](src/aviation_agentic_ai/evaluation/benchmark_validation.py#L175)** — 接受全部四个无答案级别或规范化到 `"no_answer"`
4. **[cli_common.py:16,21](src/aviation_agentic_ai/cli_common.py#L16-L21)** — 将所有 `config["key"]` 替换为 `config.get("key")`
5. **[cq.py:82](src/aviation_agentic_ai/ontology/cq.py#L82)** — 对空 `_slug` 结果添加回退处理
6. **[hybrid.py:279](src/aviation_agentic_ai/retrieval/hybrid.py#L279)** — 在回退消息中包含 `str(exc)`，添加 `logging.exception`
7. **[nasa_web.py:903-905](src/aviation_agentic_ai/sources/nasa_web.py#L903-L905)** — 使失败页面的 content_hash 基于 URL/document_id
8. **[pdf_hybrid.py:99](src/aviation_agentic_ai/sources/pdf_hybrid.py#L99)** — 将 `explicit_replacements` 字典提取为模块级常量
9. **[sufficiency_eval.py:84-90](src/aviation_agentic_ai/reporting/sufficiency_eval.py#L84-L90)** — `boundary_violation` 检查将所有非训练问题的回答都标记为违规
10. **[graph_traversal_ablation.py:156](src/aviation_agentic_ai/reporting/graph_traversal_ablation.py#L156)** — `gold.source_page >= 0` 当 source_page 为 None 时引发 TypeError
11. **[chunking_comparison.py:1213-1230](src/aviation_agentic_ai/reporting/chunking_comparison.py#L1213-L1230)** — `_sample_failure_record` 对所有失败类型返回相同的首条记录
12. **[llm_review_reports.py:544](src/aviation_agentic_ai/reporting/llm_review_reports.py#L544)** — 真值性检查丢弃零值 `path_recall_at_5`（误将 0.0 视为缺失）

---

## 📋 报告模块中的其他发现

| # | 位置 | 严重度 | 问题 |
|---|------|--------|------|
| R1 | [academic_outputs.py:112](src/aviation_agentic_ai/reporting/academic_outputs.py#L112) | 🟡 | `chunking.get("ranking", [])` 若 chunking 为非 dict 则引发 AttributeError |
| R2 | [benchmark_review_pack.py:70](src/aviation_agentic_ai/reporting/benchmark_review_pack.py#L70) | 🟡 | `detect_risk_category(question)[0]` 在返回空序列时引发 IndexError |
| R3 | [benchmark_v2.py:62](src/aviation_agentic_ai/reporting/benchmark_v2.py#L62) | 🟡 | 直接键访问 `metadata["evidence_span_validation"]` 无守卫 |
| R4 | [robustness.py:23-42](src/aviation_agentic_ai/reporting/robustness.py#L23-L42) | 🟡 | `_run_retrieval_with_deterministic_answer` 无异常处理 |
| R5 | [hygiene.py:196](src/aviation_agentic_ai/reporting/hygiene.py#L196) | 🟡 | `shutil.move` 异常未捕获，终止整个清理操作 |
| R6 | [thesis_dashboard.py:358-389](src/aviation_agentic_ai/reporting/thesis_dashboard.py#L358-L389) | 🟡 | 对含有非 dict 元素的列表元素调用 `.get()` |
| R7 | [evidence_eval.py:22](src/aviation_agentic_ai/reporting/evidence_eval.py#L22) | 🟡 | `int(chunk.get("page", -1))` 在非数字字符串上失败 |
| R8 | [overnight.py:49](src/aviation_agentic_ai/reporting/overnight.py#L49) | 🟢 | `path.stat().st_mtime` 在 glob 和 stat 之间存在竞态条件 |
