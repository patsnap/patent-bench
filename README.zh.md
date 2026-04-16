# PatSnap Patent Bench

[English](./README.md) | **中文**

> 由 **PatSnap** 发布的开放式 Patent Bench，用于评估 AI 系统在专利相关任务上的能力。

**范围说明。** 本仓库提供：

1. **评估数据集** —— 来自真实诉讼、无效宣告程序或专家标注的、经人工审核的测试样本。
2. **参考指标实现** —— 小巧、零依赖的 Python 脚本（Hit Rate、PRES 等）。

本仓库 **不** 提供检索服务、索引管道或评估平台。请自行运行你的系统，产出已排序的结果文件，再用仓库提供的指标脚本打分。

## Available Bench

| Bench | 任务 | 样本数 | 状态 |
|---|---|:---:|---|
| [**design-fto-bench**](./design-fto-bench) | 外观设计专利跨模态图像检索 | 91 | 已发布 (v1.1) |
| *novelty-search-bench* | 专利新颖性检索（Prior-art retrieval） | — | 规划中 |
| *oar-bench* | 专利审查意见答复（OAR）生成 | — | 规划中 |
| *drafting-bench* | 专利申请文件撰写 | — | 规划中 |
| *…更多 patent Bench 陆续推出* | | | |

## 目录结构

```
patsnap/patent-bench
├── common/metrics/search_metrics.py   # 共享指标库 + CLI
└── design-fto-bench/
    ├── README.md
    └── data/
        ├── test.jsonl
        └── image/
```

## 快速开始

```bash
git clone https://github.com/patsnap/patent-bench.git
cd patent-bench/design-fto-bench
# 阅读子 Bench 的 README，运行你的系统，然后打分：
python ../common/metrics/search_metrics.py \
    --dataset data/test.jsonl \
    --results your_results.json
```

## 试用生产系统

想体验基线中引用的商业系统？访问 **[PatSnap Eureka](https://eureka.patsnap.com/?from=benchmark_github)**。

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
