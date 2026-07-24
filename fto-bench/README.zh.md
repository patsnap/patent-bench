# PatSnap FTO Bench

[English](./README.md) | **中文**

一个面向**发明专利 FTO（自由实施 / Freedom to Operate）检索系统**的评估 Bench。每条样本包含一份技术特征描述文档及其目标法域，标准答案为经真实诉讼判例确认或专业 FTO 报告识别的风险专利集合。

## 数据集概览

| 属性 | 取值 |
|----------|-------|
| **样本总数** | 30 |
| **数据来源** | 真实诉讼判例 + 专业 FTO 分析报告 |
| **法域** | CN / US / EP（各 10 条） |
| **语种** | CN / EN（与法域对应） |
| **IPC 覆盖** | A–H 全部 8 大类 |
| **真值** | 司法判决确认 + 资深专利工程师审核的风险专利 PN 列表 |
| **许可协议** | CC BY-NC 4.0 |

## 使用场景

本 Bench 用于评估发明专利 FTO 检索系统在以下环节的能力：

1. **检索能力**：给定一份技术特征描述文档与目标法域，从专利库中召回所有可能构成实施障碍的风险专利
2. **跨语言理解**：在中文与英文技术文档上保持稳定的语义理解能力，覆盖三大法域
3. **排序质量**：把风险专利集中排在结果列表前端，降低专利分析师的研判工作量

对应的标准检索指标为 **Hit Rate** 与 **PRES score**。

## 数据字段

| 字段 | 类型 | 说明 |
|-------|------|-------------|
| `id` | int | 样本标识 |
| `case_id` | string | 案例 UUID |
| `country` | string | 目标法域 `CN` / `US` / `EP` |
| `ipc_main` | string | IPC 主大类（A–H） |
| `type` | string | 样本来源类型：`litigation`（诉讼判例）或 `fto_professinal`（专业 FTO 报告） |
| `technical_text` | string | 技术特征描述文档（与法域同语种：CN 法域为中文，US/EP 为英文） |
| `target_pns` | list[str] | 真值：风险专利 PN 列表（PatSnap 标准化 PN） |
| `related_patent_detail` | list[object] | 真值专利的结构化详情，每项含 `country / lang / apno / ipc_main / pn` |
| `version` | string | 数据集版本 |

> **关于专利公开号（PN）：** 所有 PN 已统一为 PatSnap 标准化格式；同一专利的不同公开版本（如 A/B）按独立 PN 给出。

## 真值构建

每条样本的真值即 `target_pns` 列表 —— 对于 `type=litigation` 的样本，PN 来自法院最终判决确认的涉案专利；对于 `type=fto_professinal` 的样本，PN 来自资深 FTO 工程师在分析报告中识别的高风险专利。

**命中规则**：FTO 是典型的"查全驱动型"任务 —— 只要返回结果中出现 `target_pns` 中的**任意一件**专利，即视为该样本命中（hit=1），不论命中多少件；若一件都没有则 hit=0。命中率为样本级二值指标。

> ⚠️ **说明：** Hit Rate ≠ Recall。查全率衡量"找到了多少 GT"，命中率只问"是否至少找到一件 GT"。FTO 实务中，分析师只要能从精筛列表里发现任意一件风险专利，该方向上的初步预警就已建立，因此采用样本级二值口径更贴近真实业务价值。

## 评估指标

| 指标 | 说明 | 侧重 |
|--------|-------------|-------|
| **Hit Rate @ 100** | 精筛列表前 100 条中至少包含 1 件 `target_pns` 的样本比例 | 检出率（样本级二值） |
| **PRES @ 100** | Patent Retrieval Evaluation Score（Magdy & Jones 2010，含 miss-penalty 校正）：落在 `[0, 1]` 区间的综合分，同时刻画 top-N 内**命中多少** GT 专利以及它们**排得多靠前**。PRES = 1.0 表示所有 GT 都排在最前；PRES = 0 表示在 N 内无任何 GT 命中。默认 N = 100。 | 检索排序质量 |

> 主要评估范围为 **Top@100** —— 充分覆盖发明专利 FTO 检索的深度需求，同时不超出人工分析能力范围，符合自由实施检索的实际工作习惯。

### 评分等级（Hit Rate @ Top@100）

| 等级 | Hit Rate | 说明 |
|-------|----------|-------------|
| **A** | ≥ 60% | 优秀 —— 可直接辅助 FTO 分析师工作 |
| **B** | ≥ 40% | 良好 —— 可作为高效初筛工具 |
| **C** | ≥ 20% | 合格 —— 需人工大量补检 |
| **D** | < 20% | 未达标 —— 建议模型优化 |

## 数据分布

### 按法域

| 法域 | 数量 | 占比 |
|-------------|-------|------------|
| CN | 10 | 33.3% |
| US | 10 | 33.3% |
| EP | 10 | 33.3% |
| **合计** | **30** | **100%** |

### 按样本来源类型

| `type` | 数量 | 说明 |
|---|---|---|
| litigation | 26 | 诉讼判例：从诉讼文书中提取被控产品/技术方案描述，以法院判决确认的涉案专利作为标准答案 |
| fto_professinal | 4 | 专业 FTO 报告：从 FTO 技术规格说明书中提取技术方案，以报告中识别的风险专利作为标准答案 |

### 按 IPC 主大类

| IPC | 数量 |
|-----|------|
| A | 7 |
| G | 7 |
| F | 4 |
| H | 4 |
| B | 3 |
| C | 3 |
| D | 1 |
| E | 1 |

## 数据集构建

### 1. 基础数据层
从真实诉讼判例（原告胜诉，侵权成立）与专业 FTO 分析报告中筛选候选样本，覆盖 CN / US / EP 三大主要法域以及 IPC A–H 全部 8 大技术领域。

### 2. 技术文档层
从诉讼文书中提取被控侵权产品/技术方案的技术特征描述，整合为完整的技术规格说明文本；从 FTO 报告中提取产品技术方案的特征描述。两种来源的文本均以"实际可作为检索系统输入"为目标做了清洗与归一化。

### 3. 标注与质检层
- `litigation` 样本：以法院判决确认侵权成立的涉案专利为标准答案
- `fto_professinal` 样本：以 FTO 报告中识别的高风险专利为标准答案（资深专利工程师二次审核）
- 所有 PN 均已转为 PatSnap 标准化格式；同一专利的多个公开版本（A/B/U 等）均保留

## 评估示例

```python
import json, sys

# 复用 monorepo 中的共享检索指标
sys.path.insert(0, "../common/metrics")
from search_metrics import hit_rate_at_k, calc_pres  # noqa: E402

with open("data/test.jsonl", "r", encoding="utf-8") as f:
    dataset = [json.loads(line) for line in f]

print(f"Total samples: {len(dataset)}")

sample = dataset[0]
print(f"Case ID: {sample['case_id']}")
print(f"Country: {sample['country']}")
print(f"Type:    {sample['type']}")
print(f"GT PNs:  {sample['target_pns']}")
print(f"Technical text (preview): {sample['technical_text'][:80]}...")


def evaluate(dataset, results_dict, k=100, N=100):
    """
    计算 Hit Rate @ K 与 PRES @ N。
    results_dict: {sample_id: [按相关性排序的召回 PN 列表]}
    """
    hits, presses = [], []
    for s in dataset:
        ranked = results_dict.get(s["id"], [])
        hits.append(hit_rate_at_k(s["target_pns"], ranked, k=k))
        presses.append(calc_pres(s["target_pns"], ranked, N=N))
    n = len(dataset)
    return sum(hits) / n, sum(presses) / n
```

> 一行命令计算指标：`python ../common/metrics/search_metrics.py --dataset data/test.jsonl --results your_results.json --k 100 --N 100` —— 脚本本身不做检索，只对你提供的已排序结果文件计算分值。

## 基线结果

PatSnap FTO AI Agent 在完整 136 条内部 Bench 上的评估结果（2026 年 3 月）：

| AI 工具 | Hit Rate (Top@100) | PRES Score |
|---------|-------------------|------------|
| **PatSnap FTO AI Agent** | **57.00%** | **0.440** |
| Gemini 3.1 Pro（web search） | 25.62% | 0.140 |
| DeepSeek 3.2（web search） | 16.94% | 0.120 |
| ChatGPT 5.4（web search） | 9.23% | 0.290 |
| Perplexity Pro（web search） | 1.19% | 0.110 |

*说明：上述基线来自完整 136 条内部 Bench。本公开数据集为其中按法域均匀抽样的 30 条子集（CN / US / EP 各 10 条），可作为指标实现验证与方法对比的最小可复现集。*

## 局限性

- **公开子集规模**：本次公开仅为 30 条按法域均匀抽样的子集，并非完整 136 条内部 Bench。完整 Bench 计划在后续版本中分阶段扩展公开。
- **法域覆盖**：当前覆盖 CN / US / EP 三大主要法域；其他法域（JP、KR 等）暂未纳入。
- **数据来源比例**：30 条子集中 `litigation` : `fto_professinal` ≈ 26 : 4，与完整 Bench 110 : 26 的比例略有偏差（受按法域均匀抽样约束）。

## 引用

如果你使用了本数据集，请引用：

```bibtex
@dataset{patsnap_fto_bench_2026,
  title  = {PatSnap FTO Bench},
  author = {PatSnap},
  year   = {2026},
  note   = {A Bench for evaluating invention patent freedom-to-operate retrieval systems}
}
```

## 许可协议

本数据集依据 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 发布，可用于科研和非商业评测用途。

## 试用生产系统

体验 **PatSnap FTO AI Agent** —— 本 Bench 所评估的商业系统，提供端到端发明专利自由实施分析，支持技术特征文档输入、多法域风险专利检索与排序、PRES 优化的精筛报告输出。

🔗 **立即体验**：[PatSnap FTO on Eureka](https://eureka.patsnap.com/?from=benchmark_github)
