# 项目弱点审阅 — 审稿人视角

**日期:** 2026-06-01
**审阅人角色:** 博士论文外部审阅人
**项目:** aviation_agentic_ai — 面向 KG/ABox 构建和 GraphRAG 检索的航空本体论生成
**方法:** 4 个并行代理，涵盖架构、方法论、代码质量和可重复性
**分支:** codex/nasa-atmonto-minimal-loop

---

## 执行摘要

该项目展示了在 AI 驱动的航空本体论构建和基于证据的 KG 提取方面的大量工作量。CLI 架构经过深思熟虑，测试套件全面（395 项测试），代码库结构在宏观层面合理。然而，作为论文提交，该项目存在**四个重大弱点**，在最终确定之前需要关注：

1. **NASA ATMONTO 实验存在方法论缺陷**，削弱了其假设检验和主张——特别是，`manual_semantic_correctness` 是精确率的同义反复，黄金标注通过 LLM 引入循环评估，且关键假设阈值看起来是任意的/事后的。

2. **一个 8,759 行的单体巨石**（`atmonto_experiment.py`）包含 227 个函数，使用自己的 `argparse` CLI 绕过项目的 Click 架构，并与其他两个 1,700+ 行的脚本耦合——占代码库的 24%，但零分解。

3. **在 11 个 CLI 报告文件中的 70+ 个命令函数中，约 2,200 行相同的样板代码重复。** 每个更改都需要编辑 11+ 个文件——代码生成或提取的注册器模式将消除这种重复。

4. **再现性文档记录不完整。** `.env.example` 有一个虚构的模型名称，缺少 5 个环境变量。`THIRD_PARTY.md` 缺少 4 篇论文 PDF 和 ATMONTO/AIRM-O 参考文献。`data/` 缺少统一的 README。没有可用的端到端重现脚本。`Makefile` 的 `thesis-all` 在没有与手动分步构建绑定才能生成的前提条件文件的情况下会失败。

---

## 架构与结构弱点

### 1. 单体巨石模块（关键）

十个文件超过 1,000 行。最大的 `atmonto_experiment.py`（8,759 行，227 个函数）本身就是一个完整的应用程序——它在第 8735 行使用 `argparse` 而不是项目的 Click CLI，并在第 8754 行有自己的 `if __name__ == "__main__"`。

| 文件 | 行数 | 问题 |
|------|-------|------|
| `ontology/atmonto_experiment.py` | 8,759 | 并行 CLI，227 个函数，60+ 个硬编码路径 |
| `reporting/chunking_comparison.py` | 1,867 | 多策略比较单体巨石 |
| `ontology/atmonto_minimal_loop.py` | 1,772 | 具有自己 argparse CLI 的独立脚本 |
| `reporting/project_report.py` | 1,640 | 55+ 个来源的大规模报告组装 |
| `reporting/thesis_dashboard.py` | 1,504 | 混合了数据加载、计算和渲染 |
| `chunking/chunks.py` | 1,500 | 55 个函数，混合了分块策略、嵌入、相似度 |
| `ontology/evaluation.py` | 1,445 | 在一个模块中评估了 14+ 个质量门槛 |
| `reporting/academic_outputs.py` | 1,396 | 学术论文 + 答辩笔记 + 演讲大纲 + 视觉资料 |
| `reporting/nasa_sources.py` | 1,167 | NASA 来源报告单体巨石 |
| `reporting/llm_review_reports.py` | 1,115 | LLM 评审报告单体巨石 |

### 2. 并行 CLI 入口点

`atmonto_experiment.py` 和 `atmonto_minimal_loop.py` 都使用 `argparse` 和他们自己的 `main()` 函数——完全绕过了 `cli.py` 中的 Click 架构。这造成了混乱：审阅人无法仅通过运行 `aviation-ai --help` 发现 ATMONTO 命令。

### 3. CLI 报告样板文件重复（~2,200 行）

所有 11 个 `cli_report_*.py` 文件在 70+ 个命令函数中重复相同的 `@report.command` / `@click.option` / `try: load_config(); write_*(); click.echo(); except: ClickException` 模式。每个添加新默认路径或更改错误处理模式的更改都需要编辑 11 个文件。

### 4. Web 层与 CLAUDE.md 矛盾

`web/app.py`、`web/data.py` 和 FastAPI 依赖项存在且功能齐全，但 CLAUDE.md 明确指出："Keep FastAPI or other service layers out of the first implementation." 要么更新 CLAUDE.md，要么提取 Web 层。

### 5. 缺少公共 API 边界

大多数 `__init__.py` 文件是空的（0-2 行）。`reporting/` 中的 33 个模块没有分组为子包。消费者使用深度文件路径导入（`from aviation_agentic_ai.reporting.chunking_comparison import write_chunking_comparison_v2`），而不是稳定的包级导入。

---

## 研究方法论弱点

### 6. 关键：`manual_semantic_correctness` 是精确率的同义反复

**位置:** `ontology/atmonto_experiment.py`，第 439 行

```python
"manual_semantic_correctness": precision,
```

实验协议将 "Manual Semantic Correctness" 定义为需要通过人工对照源证据审查来衡量的质量保证指标。实现将其设置得与精确率相同，使该指标成为精确率的同义反复，并虚假暗示人工验证。在评分报告中，对于每个系统，S0–S4，`manual_semantic_correctness == precision`。

### 7. 黄金标注数据存在循环评估

黄金标注工作流程使用与 S1–S3 预测相同模型家族的 LLM 或前沿模型来提议哪些事实应为黄金标注。相同的 LLM 通过黄金标签进行评估。尽管有 "对抗性审计" 角色，但单一审阅人无法独立验证模型建议的黄金事实是否不是模型幻觉产物。

### 8. 无注释者间一致性（IAA）

所有 100 条记录均由一名人员（或 LLM 辅助的单人）使用四角色工作流程进行审查。未计算科恩 kappa、Krippendorff alpha 或任何 IAA 指标。对抗性审查将其列为 "nice_to_have" ——对于正式实验来说，它应该是必须的。

### 9. 无训练/开发/测试拆分

相同的 100 条记录用于模式切片设计、验证器测试、规范化桥接调优、S4 合并规则设计、假设阈值选择和最终评分。所有超参数和设计决策可能都已针对评估数据进行了优化。

### 10. 假设阈值显得任意

- **H1:** 模式违规率降低 10 个百分点 —— 刚好勉强满足（0.1024 > 0.10）
- **H2:** 修复成功率 15% 且语义损失 <5pp
- **H3:** F1 改进 >5% 且确定性字段损失 <2%

所有四个假设都报告为 "supported" ——这对于初步研究来说是可疑的。H1 阈值通过 1 个不同标记的事实以 0.0024 的差值勉强达到。

### 11. S1 基线在结构上无法评分

S1_llm_only 产生 1,211 个候选事实，但被验证器拒绝了所有 1,211 个（模式违规率 = 1.0）。H3 比较在 S4 不可用时将 S3 与 S1 进行比较——任何具有有效事实的系统都 "supports" H3，因为 S1 的全零基线使 `s3_precision > 0` 在平凡情况下为真。

### 12. 小且时间上狭窄的样本

100 条记录覆盖来自单个操作背景的 7 天窗口。几个语义组的大小危险地小：3 条、2 条、2 条、1 条记录。对于这些组，F1 分数在统计学上毫无意义，但在评分报告中作为等权行报告。

### 13. 仅 200 次引导迭代

`SEMANTIC_BOOTSTRAP_ITERATIONS = 200`（atmonto_experiment.py，第 102 行）。标准实践使用 1,000–10,000。使用 200，第 2.5 个百分位数仅从 5 个顺序统计量估计。通用 `bootstrap_ci.py` 模块使用 1,000。

### 14. 系统间无正式统计检验

报告了点估计和引导区间，但未进行配对差异检验、麦克尼马尔检验或威尔科克森符号秩检验以确定系统差异是否具有统计显著性。

### 15. 无本体论特定指标

实验仅使用事实的精确率/召回率/F1。在 `docs/evaluation_protocol.md` 中列出的本体论度量（逻辑可满足性、冗余检测、SHACL 约束符合性、覆盖率差距）均未计算。

### 16. 无快速敏感性消融实验

每个 LLM 系统仅使用了 1 个提示批次。没有对变化的措辞、少量示例数量或模式表示格式进行消融研究。

### 17. 精确字符串匹配忽略语义等价性

`canonical_fact_key` 使用精确字符串比较（经过小写 + 空白符压缩）。语义等价但具有不同命名空间前缀或表示的事实将不匹配，从而遗漏了真正的正例。

### 18. S4 显示可疑的 100% 结构化接受率

S4 报告了 686 个候选事实中的 686 个被接受（接受率 = 1.0），而 S0 拒绝了 48 个（7.8%）。如果在 S4 合并逻辑中存在未正确应用验证器或选择性合并过滤的 bug，这是可疑的。

### 19. 双重项目架构造成了混乱的转变

该项目有两个冲突的实验设计：PHAK 第 4 章航空训练 QA 和 NASA ATMONTO KG 提取。两者都保持活跃，具有独立的评估框架、独立的黄金标注和独立的报告。两者都未完全完成。

### 20. 黄金标注匹配使用精确字符串比较

两个语义等价但字符串表示不同的事实（例如，"GroundStopTMI" vs "atm:GroundStopTMI"）不会匹配，即使两者都是正确的。

---

## 代码质量弱点

### 21. 87 个裸 `except Exception` 块

分布在所有 CLI 报告文件、核心模块（`generation.py`、`extraction.py`、`hybrid.py`）和外部脚本中。最集中的是 `cli_report_evaluation.py`（12 个）、`cli_report_nasa.py`（8 个）、`cli_report_thesis.py`（8 个）和 `web/app.py`（7 个）。在长时间运行的 LLM 生成循环中捕获 `Exception` ——`generation.py` 第 484 和 529 行 ——也会捕获 `KeyboardInterrupt`，使得无法干净地取消操作。

### 22. 稀疏的类型注解

1,327 个函数中，约 450 个（34%）缺少返回类型注解。受影响最严重的：`cli_report_evaluation.py`（13 个函数中 12 个缺少注解）、`reporting/evaluation_protocol.py`（5 个中 4 个）。

### 23. 不完整的文档字符串覆盖

许多函数，特别是 CLI 报告命令回调和 `_private` 辅助函数，缺乏文档字符串。在作为博士论文提交的研究代码库中，这对可重复性至关重要。

### 24. 测试：源代码比率为 30%

13,100 测试行 / 44,100 源代码行 = 0.30。低于研究代码的典型 50–80% 目标。许多大型报告模块（11 个文件 >300 行）没有对应的测试文件。

### 25. 测试导入私有符号

测试如 `test_kg_extraction.py` 直接导入 `_deterministic_triples_for_chunk`，将测试与实现细节耦合。

---

## 可重复性与提交就绪性

### 26. `.env.example` 不完整且具有虚构值

- `MODEL_NAME` 默认 = `gpt-5.4-mini`（不是真实的 OpenAI 模型；代码默认使用 `gpt-4o-mini`）
- 缺少：`VLLM_API_KEY`、`AVIATION_AI_PROJECT_ROOT` 以及 3 个工作区同步变量
- 没有解释必须将 `.env` 放在项目根目录

### 27. THIRD_PARTY.md 不完整

缺少：`data/papers/` 中的 4 个 PDF 文件、ATMONTO/AIRM-O 参考文献、NASA BGA 来​​源材料、演示运行时归属。`data/papers/README.md` 记录了 5 个 PDF 中仅 1 个。

### 28. 无统一的 data/README.md

`data/` 目录缺少解释每个子目录内容的概述文档，什么是策划的 vs 生成的，以及审阅人在克隆后应期望看到什么。

### 29. 无端到端重现脚本

`make thesis-all` 在没有 `data/chunks/` 和 `data/indexes/` 的情况下失败，这些文件被 gitignore 且未提供。没有目标从零生成这些前提条件。审阅人必须阅读文档并拼凑正确的命令序列。

### 30. 归档文件中硬编码的作者特定路径

`workspace_sync.py` 包含 `wjl@desktop-g9260uj`、`C:\Users\wjl\...` 和 `wsl -d Ubuntu-22.04` ——作者的个人工作站详细信息。这些应被移除或替换为占位符。

### 31. 论文 PDF 政策矛盾

`.gitignore` 排除了 `data/papers/*.pdf`，但 CLAUDE.md 说提交论文，`data/papers/README.md` 说 PDF 有意保持本地化，但 README.md 将一篇论文 PDF 列为基线资产。存在 4 个未记录的 PDF。

### 32. 未记录 LLM 成本和令牌使用量

审阅人不知道哪些命令需要 API 密钥，哪些是确定性的，或者运行所有依赖 LLM 的报告的成本。`make reports-review` 目标包括 10 个需要 LLM 的命令，但没有成本估算。

### 33. `uv.lock` 是特定于平台的

锁定文件在 macOS 上生成，包含 darwin 特定的依赖轮子。README 没有说明项目是否预期在 Linux 上工作，或者 `uv sync` 是否在其他平台上需要重新生成锁定文件。

### 34. 无提交生成的数据的策略

`data/processed/`、`data/evaluation/` 和 `data/experiments/` 包含生成/提取的产物（LLM 预测、评分报告、审查批次）。CLAUDE.md 的产物政策未明确授权提交这些内容，但它们存在于仓库中。如果它们是经过筛选的证据，则需要文档记录；如果它们是生成的且不应提交，则需要 `.gitignore`。

---

## 优先级摘要

### 提交前必须修复

| # | 项目 | 严重程度 | 工作量 |
|---|------|--------|--------|
| 6 | `manual_semantic_correctness = precision` 同义反复 | 关键 | 小 — 实现或移除指标 |
| 7 | 通过 LLM 辅助的黄金标注造成的循环评估 | 关键 | 大 — 需要独立标注 |
| 25 | `.env.example` 有虚构的模型名称 | 高 | 小 — 1 行修复 |
| 1 | 8,759 行单体巨石无分解 | 高 | 非常大 — 跨模块的多周重构 |
| 28 | 无端到端重现脚本 | 高 | 中 — 新 Makefile 目标 |

### 强烈推荐

| # | 项目 | 严重程度 | 工作量 |
|---|------|--------|--------|
| 3 | 11 个文件中的 2,200 行 CLI 样板重复 | 中 | 大 — 提取注册器模式 |
| 8 | 无注释者间一致性指标 | 中 | 大 — 需要第二名标注者 |
| 9 | 无训练/开发/测试拆分 | 中 | 大 — 需要新的拆分和重新评分 |
| 10 | 假设阈值显得任意 | 中 | 中 — 需要统计验证或预注册 |
| 11 | S1 基线在结构上无法评分 | 中 | 小 — 排除比较或记录限制 |
| 26 | THIRD_PARTY.md 不完整 | 中 | 小 — 文档更新 |
| 27 | 无统一的 data/README.md | 中 | 小 — 新文档 |

### 考虑

| # | 项目 | 严重程度 |
|---|------|--------|
| 2 | 并行 CLI 入口点（argparse + Click） | 低 |
| 4 | Web 层与 CLAUDE.md 矛盾 | 低 |
| 12–20 | 方法论细微差别（样本量、引导迭代、消融实验） | 低–中 |
| 21–25 | 代码质量问题（裸异常、注解、文档字符串） | 低 |
| 29–33 | 提交细节（平台、策略、成本） | 低 |

---

## 审阅人将问的问题

1. **"我如何重现你完整的实验管道？"** — 目前，答案需要跨文档拼凑 5+ 个步骤。需要一个单一的 `make reproduce-all` 目标。

2. **"你如何知道你的黄金标注是正确的？"** — 没有 IAA，没有独立的第二名标注者，并且黄金标注建议使用了与评估相同的 LLM 模型。这是一个循环。

3. **"为什么 `manual_semantic_correctness` 与精确率相同？"** — 这是一个实现错误，使质量保证指标变得毫无意义。需要人工审查或移除。

4. **"你的假设阈值来自哪里？"** — 这些阈值（10pp、15%、5pp、2pp）没有统计验证或方法论文献支持。

5. **"ATMonto 实验如何与 PHAK 本体论工作相关联？"** — 该项目改变了重点，但两项工作都保持在部分完成状态。

6. **"为什么实验模块是一个 8,759 行的文件？"** — 审阅人将对单体巨石的维护性和正确性缺乏信心。

7. **"引用的本体论特定评估指标在哪里？"** — 协议承诺了本体论指标（一致性、连贯性、SHACL 符合性），但未计算。

---

*由 4 个并行审阅代理生成，每个专注于不同的分析维度。*
