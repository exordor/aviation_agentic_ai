# 代码审阅报告 — NASA ATMONTO 正式实验

**日期:** 2026-06-01
**审阅范围:** 最近提交（`ad52bb4`、`b422322`、`d8aa17e`、`bd11e0d`、`3cd04c1`）
**覆盖:** `src/aviation_agentic_ai/ontology/atmonto_experiment.py`（~8738 行）、测试（~1917 行）、数据/报告文件
**验证状态:** 338 项测试通过，ruff 检查通过
**审阅方法:** 4 个并行代理审查不同模块部分

---

## 统计概览

| 严重程度 | 数量 |
|--------|------|
| 🔴 严重 | 2 |
| 🟠 高 | 12 |
| 🟡 中 | 10 |
| 🟢 低 | 6 |
| **总计** | **30** |

---

## 🔴 严重（2 项发现）

### C1. `datetime.UTC` 需要 Python 3.11+ — 违反项目 `>=3.10` 目标

**位置:** [src/aviation_agentic_ai/ontology/atmonto_experiment.py:7](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L7)

`pyproject.toml` 声明 `requires-python = ">=3.10"` 且 `ruff` 目标为 `py310`。然而，`datetime.UTC` 是在 Python 3.11 中引入的。在 Python 3.10 上，`from datetime import UTC` 在导入时引发 `ImportError`，使整个模块无法加载。

```python
from datetime import UTC, datetime   # line 7 -- ImportError on Python 3.10
```

唯一的使用点是 `utc_timestamp()`（第 5305 行）中的 `datetime.now(UTC)`。

**修复：** 使用 `datetime.timezone.utc`，这在 Python 3.10+ 上有效：

```python
from datetime import datetime, timezone

def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
```

---

### C2. 拒绝完整性门控中硬编码的幻数 `288`（4 处）

**位置:** [atmonto_experiment.py:7351, 7353, 7363, 7620](src/aviation_agentic_ai/ontology/atmonto_experiment.py)

值 `288`（试点被拒绝的事实的硬编码总数）出现在四处。实际计数通过 `rejection_analysis.get("rejected_fact_count", 0)` 动态读取。如果被拒绝的事实计数在运行之间发生变化，代码会静默返回 `"incomplete_rejection_accounting"`，即使所有预期的拒绝都已处理。第 7363 行的字符串字面量也嵌入了相同的幻数。

**修复：** 从数据本身派生预期计数，从验证的黄金标注中提取，或从拒绝分析中计算。至少，将其提取到模块级常量中。

---

## 🟠 高（12 项发现）

### H1. LLM 调用缺乏重试/错误处理 — 瞬态 API 故障导致整个批处理崩溃

**位置:** 流水线阶段 S1–S4（第 2001–5000 行）

`run_llm_prediction_system` 及其调用的阶段函数通过 `get_llm(...).invoke(...)` 进行 LLM 调用，但没有 try/except、没有重试逻辑、没有超时配置。任何瞬态 API 故障（速率限制、网络错误、5xx）都会导致整个批处理运行崩溃，丢失所有未处理的记录。对于可能需要数小时且成本高昂的实验运行，单个瞬态故障不应使整个过程无效。

**修复：** 使用指数退避添加重试包装器。至少，捕获 `Exception`，记录失败的记录 ID，并继续处理剩余项目。

---

### H2. 非原子文件写入，约 30 处 — 存在部分/损坏产物的风险

**位置:** [write_json:234-236](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L234-L236), [write_jsonl:239-242](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L239-L242)，以及 `run_formal_experiment_readiness` 中的所有调用点

`write_json` 和 `write_jsonl` 通过 `Path.write_text()` 直接写入目标路径，没有临时文件后重命名的模式。在 `run_formal_experiment_readiness`（第 8438–8707 行）中，大约 30 个文件被顺序写入。如果进程被中断（磁盘满、OOM、SIGKILL），部分写入的文件会保留在预期路径上，没有损坏指示。这违反了 CLAUDE.md："Keep CLI commands deterministic and scriptable"。

**修复：** 使用写入临时文件后重命名模式：

```python
def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)  # atomic on same filesystem
```

---

### H3. `build_gold_semantic_groups` 中未处理的 KeyError

**位置:** [atmonto_experiment.py:1994](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L1994)

```python
source_record = source_records[sample_id]   # KeyError if mismatch
```

如果工作量计划中的任何 `sample_id` 在黄金模板中缺失（例如，由于陈旧的工作量计划或数据一致性错误），这会引发未处理的 `KeyError`，且没有关于哪个 `sample_id` 失败的上下文。

**修复：**

```python
source_record = source_records.get(sample_id)
if source_record is None:
    raise ValueError(f"sample_id {sample_id!r} found in workload plan but not in gold template")
```

---

### H4. `markdown_report` 中使用负索引的列表插入 — 重构风险

**位置:** [atmonto_experiment.py:8367-8381](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L8367-L8381)

该函数使用 `lines.insert(-3, ...)` 三次来在 `"### Next Commands"` 部分标题之前插入信息。正确的插入点取决于前面 `lines.extend([...])` 块中元素的确切数量（12 个）。如果开发人员修改了 extend 块，`-3` 索引会静默地指向错误位置，产生格式错误的 markdown，且没有运行时错误。

**修复：** 显式构建 "Next Commands" 部分，然后一次性扩展：

```python
next_section = ["", "### Next Commands", ""]
if next_session:
    next_section[:0] = [f"- Next session sample: ...", f"- Next review session: ..."]
else:
    next_section[:0] = ["- Next review session: `none`; gold review is complete."]
for command in kickoff["next_commands"]:
    next_section.append(f"- `{command}`")
lines.extend(next_section)
```

---

### H5. 评分有效性检查中的精确浮点相等性

**位置:** [atmonto_experiment.py:6733](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L6733)

```python
and structural.get("schema_violation_rate") == 1.0
```

虽然 `n/n == 1.0` 在 IEEE 754 中对典型大小的整数比率精确成立，但未来的重构可能通过中间计算或平均来计算 `schema_violation_rate`，产生 `0.9999999999999999`。这会静默地破坏 S1 的 scoring-validity 检测逻辑。

**修复：** 使用 epsilon 比较：

```python
and float(structural.get("schema_violation_rate") or 0.0) >= 0.999
```

---

### H6. 测试写入真实工作目录（破坏性副作用）

**位置:** [test_nasa_atmonto_formal_experiment.py:302, 788, 1119, 1153](tests/test_nasa_atmonto_formal_experiment.py)

四个测试调用 `prepare_formal_experiment_inputs(Path("."))`，将文件写入仓库树内的 `data/experiments/nasa_atmonto/formal/`。这些测试是破坏性的：它们覆盖已提交的产物，可能留下脏的工作副本，并干扰其他依赖于这些文件处于已知状态的测试。

**修复：** 使用 `tmp_path` 并仅复制所需的最小数据文件。

---

### H7. 20+ 个测试从文件系统读取并带有硬编码的数值断言

**位置:** 两个测试文件中约 25 个测试函数

大约三分之二的测试函数通过从 `Path(".")` 读取已提交文件来构造测试输入，然后针对特定的具体数字进行断言（例如 `== 100`、`== 643`、`== 462`、`== 48`、`== 288`、`== 275`、`== 13`、`== 9`、`== 615`）。任何对策划的黄金数据、评估模板或生成报告的更改都会静默地破坏这些测试——即使底层逻辑仍然正确。

**修复：** 用从数据文件在测试时派生的参数化值替换，或转换为基于快照的测试。

---

### H8. 关键转换函数缺乏单元测试

**置信度:** 85

`canonicalize_s1_fact`（第 4582 行）、`build_s1b_prediction_record`（第 4735 行）和 `build_s4_prediction_record`（第 4814 行）执行将 LLM 输出规范化为 ATMONTO 配置文件的核心工作。它们有**零**个直接单元测试。它们仅通过集成级测试间接测试。

**修复：** 为这些函数添加专注的单元测试，覆盖已知的转换情况。

---

### H9. `claim_and_hypothesis_statuses` 为 310 行，嵌套条件深达 4 层

**位置:** [atmonto_experiment.py:7180-7490](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L7180-L7490)

评估四个假设（H1–H4）和四个声明（C1–C4）。仅 H1 分支就有 7 条条件路径（第 7240–7283 行），嵌套最深达 4 层。这违反了 CLAUDE.md 的原则："Keep modules small and purpose-specific."

**修复：** 将每个假设评估提取到自己的函数中。

---

### H10. `run_formal_experiment_readiness` 为 269 行，编排了太多副作用

**位置:** [atmonto_experiment.py:8438-8707](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L8438-L8707)

单个函数构建 8+ 个报告，写入 30+ 个文件，并有条件地跳过决策模板的重新生成。与非原子写入问题（H2）结合，中途失败会在磁盘上产生不一致的产物状态。

**修复：** 拆分为多个阶段：(a) 在内存中计算所有报告，(b) 写入所有文件，(c) 返回摘要。

---

### H11. `score_report_markdown` 为 321 行，包含整体式 markdown 生成

**位置:** [atmonto_experiment.py:7772-8093](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L7772-L8093)

在一个函数中包含系统指标表、置信区间表、语义组表、拒绝裁定、声明/假设状态和完成审计渲染。

**修复：** 提取子渲染器。

---

### H12. S4 记录构建中潜在的共享引用错误

**置信度:** 80

在 `build_s4_prediction_record` 中，如果相同的字典引用在记录之间被重用（而不是使用 `dict()` 或 `{**item}` 进行深拷贝），修改一个记录可能会静默地破坏另一个。需要审查以确保结构正确。

---

## 🟡 中（10 项发现）

| # | 位置 | 问题 |
|---|------|------|
| M1 | [第 31–117 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L31-L117) | 30+ 个模块级路径常量硬编码 — 违反 CLAUDE.md "config-driven paths" |
| M2 | [第 221–243 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L221-L243) | 严格 I/O 辅助函数缺乏异常处理 — `FileNotFoundError` 导致原始回溯 |
| M3 | [第 1009 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L1009) | `build_gold_freeze_status` 使用深度列表字典相等性 — JSON 往返键顺序差异可能导致错误报告 |
| M4 | [第 5776 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L5776) | `prediction_record_counts` 是死代码 — 在文件中无调用者 |
| M5 | [第 7153 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L7153) | `metric_interval_text(None)` 和 `metric_interval_text({})` 都返回 `"n/a"` — 混淆了不同的缺失状态 |
| M6 | 测试 | `run_llm_prediction_system` 中的三个 `ValueError` 守卫子句无测试 |
| M7 | [test 第 1522 行](tests/test_nasa_atmonto_formal_experiment.py) | 空泛通过的否定断言（`assert "ID" not in markdown`）— 如果 markdown 生成完全不包含 ID，仍然通过 |
| M8 | 多个测试 | 弱 `> 0` 断言 — 规范化为 1 个事实时仍然通过（预期为数百个） |
| M9 | [test 第 87 行](tests/test_nasa_atmonto_formal_experiment.py) | `structural_metrics` 测试中缺失空列表边缘情况 — 除以零守卫分支未经测试 |
| M10 | [第 428 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L428) | 使用 `groups.setdefault(key[0], set()).add(key)` 时，`set()` 被急切求值 — 应使用 `defaultdict(set)` |

---

## 🟢 低（6 项发现）

| # | 位置 | 问题 |
|---|------|------|
| L1 | [第 5305, 6222, 6305 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py) | `utc_timestamp`、`read_jsonl_lenient`、`valid_prediction_records` 的前向引用 — 在首次使用之后定义，影响可读性 |
| L2 | [第 428, 2003–2005 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py) | `setdefault` 在每次调用时都急切求值默认值 — `defaultdict(set)` 更符合惯例 |
| L3 | [test 第 8–9 行](tests/test_nasa_atmonto_experiment_protocol.py) | 协议测试因缺失文件而崩溃，且无 `pytest.skip` — 应优雅跳过 |
| L4 | [test 第 941 行](tests/test_nasa_atmonto_formal_experiment.py) | `formal_scoring_gold_source` 回退路径未经测试 — 仅测试了 "frozen_reviewed_gold" 源 |
| L5 | [docs/experiment_protocol.md](docs/experiment_protocol.md) | 文档不一致风险 — 测试读取实时文件以进行协议一致性，但若文档被重命名则崩溃 |
| L6 | 多个位置 | 文件大小 — 8738 行是一个非常大的单模块。考虑拆分为 `atmonto_experiment/` 包，包含 `config.py`、`scoring.py`、`reporting.py`、`pipeline.py`、`gold.py` |

---

## 已确认正确的方面

- **无 `os.getenv` 调用** — 模块正确使用 LLM 提供者层进行配置
- **所有导入的符号均已使用** — 无未使用的导入
- **评分数学是正确的** — 精确率/召回率/F1、Bootstrap CI、属性级指标。所有除法点均存在除以零守卫。
- **排序/批处理构造中无差一错误**
- **无提示注入向量** — 系统提示与用户输入是分开的
- **全面的黄金标注管道** — 模板、审查工作流程、决策模板和进度跟踪结构设计良好
- **338/338 项测试通过** — 回合通过率为 100%
- **ruff 检查通过** — 无 lint 违规

---

## 快速修复项

1. **[第 7 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L7)** — `from datetime import UTC, datetime` → `from datetime import datetime, timezone`；将 `datetime.now(UTC)` 替换为 `datetime.now(timezone.utc)`
2. **[第 7351 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L7351)** — 从数据中派生预期的拒绝计数，而不是硬编码 `288`
3. **[第 234 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L234)** — 在 `write_json` 和 `write_jsonl` 中添加原子写入（临时文件后重命名）
4. **[第 1994 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L1994)** — 添加 `source_records.get(sample_id)` 守卫，并附有描述性错误
5. **[第 6733 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L6733)** — 将 `== 1.0` 改为 `>= 0.999`
6. **[第 8367 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L8367)** — 将 `lines.insert(-3, ...)` 替换为显式部分构建
7. **[测试第 302 行](tests/test_nasa_atmonto_formal_experiment.py)** — 在四个破坏性测试中使用 `tmp_path` 而非 `Path(".")`
8. **[第 5776 行](src/aviation_agentic_ai/ontology/atmonto_experiment.py#L5776)** — 移除死代码 `prediction_record_counts`

---

## 总结

NASA ATMONTO 正式实验模块是对该项目的实质性、设计良好的新增功能。黄金标注管道、多系统评分和假设评估框架展示了良好的实验设计。主要关注点围绕**弹性**（LLM 重试、原子文件 I/O）、**Python 版本兼容性**（`datetime.UTC` 仅适用于 3.11+）以及**可维护性**（过长的函数、过多的硬编码数值、脆弱的测试）。关键路径上的 2 项严重发现和 12 项高严重度问题应在将实验提交作为最终结果之前予以解决。
