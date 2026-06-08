# PatSnap Patent Bench

[English](./README.md) | **中文**

> 由 **PatSnap** 发布的开放式 Patent Bench，用于评估 AI 系统在专利相关任务上的能力。

PatSnap Patent Bench 是面向专利领域的**任务级评估数据集与参考指标实现合集**。每个子 Bench 对准一种真实的专利工作流 —— 查新检索、防侵权检索、专利申请撰写、审查意见答复、专利翻译、专利特征对比 —— 样本均来自真实的审查记录、诉讼、无效宣告程序或专家标注，经人工核验。

## 仓库提供的内容

1. **评估数据集** —— 真实业务场景、经人工核验的测试样本。每个子 Bench 提供一份 JSONL 文件，并附带稳定且文档化的字段约定。
2. **参考指标实现** —— 小巧、零依赖的 Python 脚本（Hit Rate、PRES、MRR 等）。
3. **统一的评估流程** —— 你用自己的系统跑出结果（检索任务给一个排好序的候选 ID 列表，生成任务给模型输出），存成 JSON 文件，再用 `common/metrics/` 下的脚本打分。

本仓库 **不** 提供检索服务、索引管道、生成后端或评估平台 —— 它在设计上对实现方式无侵入。

## 子 Bench 矩阵

PatSnap Patent Bench 目前覆盖 **4 个方向、8 项能力**。

### 检索与风险分析

| Bench | 任务 | 样本数 | 状态 |
|---|---|:---:|---|
| [**design-fto-bench**](./design-fto-bench) | 外观设计专利跨模态图像检索（产品图 ↔ 专利图） | 91 | **已发布 v1.1** |
| [**novelty-search-bench**](./novelty-search-bench) | 专利查新检索（审查员引用的 X 类对比文献，含跨受理局同族扩展与单受理局非扩展两类样本） | 569 | **已发布 v1.0** |
| *fto-bench* | FTO 防侵权检索（基于真实诉讼与 FTO 报告） | — | 即将发布（2026-06） |

### 撰写与审查答复

| Bench | 任务 | 样本数 | 状态 |
|---|---|:---:|---|
| *oar-bench* | 审查意见答复（OAR）生成 | — | 即将发布（2026-07） |
| *drafting-bench* | 专利申请文件全文撰写 | — | 即将发布（2026-08） |
| *invention-disclosure-bench* | 基于用户提供的技术资料生成交底书 | — | 即将发布（2026-09） |

### 专利翻译

| Bench | 任务 | 样本数 | 状态 |
|---|---|:---:|---|
| *translation-bench* | 专利翻译；含长上下文、术语一致性、跨段一致性等专项检测 | — | 即将发布（2026-08） |

### 特征对比

| Bench | 任务 | 样本数 | 状态 |
|---|---|:---:|---|
| *claim-charting-bench* | 权利要求特征对齐；覆盖专利对与交底书 | — | 即将发布（2026-08） |

> ℹ️ **即将发布** 的 Bench 暂不提供样本数与具体细节 — 数据集组成在正式发布前仍可能调整。每个 Bench 的最终样本数、GT 形态与评分协议会在发布时以其 `README.md` 为准。

所有子 Bench 至少覆盖 **CN / US / EP** 受理局以及 **CN / EN** 语种（视任务而定），IPC 覆盖 A–H 全部 8 大类。

## 发布节奏

| 发布窗口 | 新增子 Bench |
|---|---|
| **2026-06** | `novelty-search-bench`、`fto-bench` |
| **2026-07** | `oar-bench` |
| **2026-08** | `drafting-bench`、`translation-bench`、`claim-charting-bench` |
| **2026-09** | `invention-disclosure-bench` |

表中为计划月度发布窗口。实际版本以 [GitHub Releases](https://github.com/patsnap/patent-bench/releases) 为准；完整版本变更详见 [`CHANGELOG.md`](./CHANGELOG.md)。

## 目录结构

```
patsnap/patent-bench
├── common/metrics/search_metrics.py      # 共享指标库 + CLI
├── design-fto-bench/                     # 已发布 v1.1
│   ├── README.md
│   └── data/{test.jsonl, image/}
├── novelty-search-bench/                 # 已发布 v1.0
│   ├── README.md
│   └── data/test.jsonl
└── <其他-bench>/                          # 即将发布，详见上方节奏表
    ├── README.md
    └── data/...
```

每个子 Bench 共用一套骨架：一份描述数据 schema 与打分协议的 `README.md`，加一个 `data/` 目录。

## 快速开始

```bash
git clone https://github.com/patsnap/patent-bench.git

# Design FTO —— 外观跨模态图像检索
cd patent-bench/design-fto-bench
python ../common/metrics/search_metrics.py \
    --dataset data/test.jsonl \
    --results your_results.json

# Novelty Search —— 查新检索
# 使用 novelty_metrics.py（不是 search_metrics.py）—— Novelty schema 字段是
# pn_x / pn_x_family / pn_family_x / pn_family_x_family，而非单一的 target_pns。
# novelty_metrics.py 会自动构造 GT 并支持跨同族扩展（通过 --collapsed 开关）。
cd ../novelty-search-bench
python ../common/metrics/novelty_metrics.py \
    --dataset data/test.jsonl \
    --results your_results.json
    # 若你的检索结果按家族折叠返回，加 --collapsed
```

> ⚠️ **默认按 leaderboard 严格口径打分。** 两个指标脚本默认把 results 里没出现的样本当作 0 分计算，分母始终是数据集的全量大小 —— 所以只交一部分样本是刷不出虚高分数的。本地调试时可以加 `--allow-partial` 跳过缺失样本；但要上 leaderboard 的数字必须用默认严格口径跑出来。

运行前请阅读每个子 Bench 的 `README.md`，了解其评估协议、GT 口径与支持的指标。

## 评估范式

所有检索类子 Bench 共享同一套四步流程：

1. **遍历** 子 Bench 的 `data/test.jsonl`，从每条记录里取出 query（PN、图像或文本）。
2. **运行** 你的检索 / 生成系统：检索任务产出按相关性排序的候选 ID 列表，生成任务产出模型输出。
3. **序列化** 输出为以样本 `id` 为键的 JSON 文件。
4. **打分** 用 `common/metrics/` 下的指标脚本（或子 Bench 自带的指标）计算 Hit Rate @ K、Recall @ K、PRES、MRR 或任务专用指标。

这样的解耦保证了 Bench 的可复现性与系统中立性 —— 任何检索引擎、LLM 或混合方案都能直接接入，无需改动数据或指标逻辑。

## 试用生产系统

想体验基线中引用的商业系统？访问 **[PatSnap Eureka](https://eureka.patsnap.com/?from=benchmark_github)**。

## 参与贡献

欢迎以下形式的贡献：

- **结果提交** —— 在已发布的任一子 Bench 上跑出打分结果，提 Issue 即可；具有代表性的结果会被列入对应子 Bench 的 README。
- **方法学反馈** —— 提 Issue / PR 评议评估协议、指出数据质量问题或提出扩展方案。
- **数据集互链** —— 如果你维护公开的专利领域评估数据集，希望被本仓库交叉引用，请提 Issue。

我们 **不** 接受以下 PR：携带专有数据、内部评分管道，或绑定单一厂商的基线。

## 许可协议

- **数据**：[CC BY-NC 4.0](./LICENSE)
- **代码**：Apache-2.0（详见源文件头部声明）

## 引用

```bibtex
@misc{patsnap_patent_bench,
  title  = {PatSnap Patent Bench: Open Evaluations for Patent AI Systems},
  author = {PatSnap},
  year   = {2026},
  url    = {https://github.com/patsnap/patent-bench}
}
```

### 配套论文

部分子 Bench 配有公开发表的方法学论文，使用对应数据集时请同时引用对应论文：

| 子 Bench | 论文 | arXiv |
|---|---|---|
| `novelty-search-bench` | Zhang et al. 2025 — *Research on Evaluation Methods for Patent Novelty Search Systems and Empirical Analysis* | [2508.17782](https://arxiv.org/abs/2508.17782) |

> ⚠️ **`novelty-search-bench` 论文样本数说明。** arXiv 论文（2025-08）的实验是在约 1,000 篇专利的早期内部评测集上做的；该评测集发表后已做过一次重要扩展和清洗，当前公开版（569 条）抽样自最新的内部版本。**我们正在用最新的内部数据集重新跑实验，新版论文即将提交。** 新版论文上线前，论文里的数字应作为方法学参考，不应直接当作本公开数据集的 baseline。
