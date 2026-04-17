# PatSnap Design FTO Bench

[English](./README.md) | **中文**

一个面向**外观设计专利 FTO（自由实施）图像检索系统**的评估 Bench。每个样本包含一张查询外观设计专利图像，以及通过真实无效宣告程序确认构成侵权的目标专利图像作为真值。

## 数据集概览

| 属性 | 取值 |
|----------|-------|
| **样本总数** | 91 |
| **数据来源** | 真实无效宣告程序 |
| **图像类型** | 产品实物图 ↔ 专利线稿图（跨模态） |
| **LOC 覆盖** | 22 个洛迦诺分类大类 |
| **真值** | 人工审核的侵权专利图像对 |
| **许可协议** | CC BY-NC 4.0 |

## 使用场景

本 Bench 用于评估外观设计专利 FTO 系统在以下环节的能力：
1. **检索**：给定一张查询产品/专利图像，从大规模专利图像库中召回视觉相似的外观设计专利
2. **跨模态匹配**：产品实物图 vs. 专利线稿图之间的风格转换下仍能保持识别准确性
3. **排序**：将视觉最相似、法律相关性最高的外观设计专利排在结果列表前列

对应的标准检索指标为 **Hit Rate @ K** 和 **PRES score**。

## 数据字段

| 字段 | 类型 | 说明 |
|-------|------|-------------|
| `id` | int | 样本标识 |
| `query_img_id` | string | 查询专利图像的图像 ID |
| `query_pn` | string | 查询专利公开号（PatSnap 标准化 PN） |
| `query_img_path` | string | 查询图像的存储路径 |
| `target_pns` | list[str] | 真值：侵权目标专利公开号列表（PatSnap 标准化 PN） |
| `target_img_ids` | list[str] | 目标专利的所有视图图像 ID（如 S-0、S-1） |
| `pair_name` | string | 查询-目标配对标识 |
| `picture_type` | string | 图像类型：`无效`（来自无效宣告程序） |
| `one_level_loc` | string | 洛迦诺分类一级码（双重分类用 ` OR ` 连接，如 `02 OR 29`） |
| `two_level_loc` | string | 洛迦诺分类二级码（双重分类用 ` OR ` 连接，如 `02-03 OR 29-02`） |
| `country` | list[str] | 目标法域 (例如. `["CN"]`) |
| `version` | string | 数据集版本 |

> **关于专利公开号（PN）：** 所有公开号已统一转为 PatSnap 标准化 PN 格式。

## 真值构建

每条样本的真值即 `target_pns` 列表 —— 这些专利公开号是通过真实无效宣告程序确认构成侵权关系的，并经过人工标注团队二次审核。

**命中规则**：只要返回结果中出现 `target_pns` 中的任何一个专利，即视为命中。由于同一专利可能有多张视图（如 S-0、S-1），去重在 `patent_id` 层进行 —— 命中任意一张视图即计入命中。

> ⚠️ **说明：** `target_img_ids` 列出了目标专利的所有视图图像。对于图像粒度的检索系统，返回结果中出现该列表里任意 `img_id` 即计入对应专利命中。

## 评估指标

| 指标 | 说明 | 侧重 |
|--------|-------------|-------|
| **Hit Rate @ K** | 前 K 个结果中至少有 1 个真值专利的样本比例（K = 10, 50, 100, 200） | 检索排序精度 |
| **PRES Score** | Agent 最终侵权报告正确识别出真值专利的样本比例 | 端到端判断质量 |

> 主要评估范围为 **Top@200** —— 对外观设计视觉相似度检索有足够覆盖，同时保留在可人工复核的范围内。

### 评分等级（Hit Rate @ Top@100）

| 等级 | Hit Rate | 说明 |
|-------|----------|-------------|
| **A** | ≥ 90% | 优秀 —— 可直接用于专业场景 |
| **B** | ≥ 75% | 良好 —— 可作为高效初筛工具 |
| **C** | ≥ 60% | 合格 —— 需人工复核关键结果 |
| **D** | < 60% | 未达标 —— 建议模型优化 |

## 数据分布

### 按洛迦诺（LOC）分类

| LOC | 说明 | 数量 |
|-----|-------------|-------|
| 23 | 游戏、玩具、体育器材 | 14 |
| 28 | 医药与化妆品用品 | 10 |
| 08 | 工具与五金 | 9 |
| 15 | 机械 | 9 |
| 09 | 包装与容器 | 8 |
| 12 | 交通工具 | 6 |
| 14 | 录音与通信设备 | 6 |
| 31 | 食品 | 5 |
| 07 | 家居用品 | 5 |
| 26 | 照明设备 | 3 |
| 16 | 摄影与光学 | 3 |
| 其他 | （11 个其他分类） | 13 |
| **合计** | | **91** |

## 数据集构建

### 1. 基础数据层
从多个 LOC 技术领域的真实无效宣告程序中筛选候选配对，覆盖跨模态图像组合（产品实物图 ↔ 专利线稿图）。

### 2. 视觉对齐层
提取查询专利图像与目标侵权专利图像，并校验视觉对齐；跨模态配对（产品图 vs. 线稿）在结构和轮廓一致性上做复核。

### 3. 标注与质检层
- 人工标注团队对所有侵权关系进行二次确认
- 在 `patent_id` 层去重；所有 PN 转为 PatSnap 标准化格式
- 字段完备性校验；查询信息不完整的记录已剔除

## 评估示例

```python
import json, sys

# 复用 monorepo 中的共享检索指标
sys.path.insert(0, "../common/metrics")
from search_metrics import hit_rate_at_k, calc_pres  # noqa: E402

# 直接读取仓库内的 JSONL 文件
with open("data/test.jsonl", "r", encoding="utf-8") as f:
    dataset = [json.loads(line) for line in f]

print(f"Total samples: {len(dataset)}")

sample = dataset[0]
print(f"Query image ID: {sample['query_img_id']}")
print(f"Query PN: {sample['query_pn']}")
print(f"Target PNs (GT): {sample['target_pns']}")
print(f"LOC: {sample['one_level_loc']} / {sample['two_level_loc']}")
print(f"Country: {sample['country']}")


def compute_hit_rate(dataset, results_dict, k=100):
    """
    计算 Hit Rate @ K。
    results_dict: {sample_id: [按相关性排序的召回 PN 列表]}
    """
    hits = 0
    for sample in dataset:
        gt = set(sample["target_pns"])
        retrieved = results_dict.get(sample["id"], [])[:k]
        if any(pn in gt for pn in retrieved):
            hits += 1
    return hits / len(dataset)
```

> 一行命令计算指标：`python ../common/metrics/search_metrics.py --dataset data/test.jsonl --results your_results.json` —— 脚本本身不做检索，只对你提供的已排序结果文件计算分值。

## 基线结果

PatSnap Design FTO AI Agent 在 261 条完整内部数据（含电商数据）上的评估结果（2026 年 3 月）：

| AI 工具 | Hit Rate (Top@200) | PRES Score |
|---------|-------------------|------------|
| **PatSnap Design FTO AI Agent** | **77.00%** | **0.700** |
| ChatGPT 5.4（web search） | 0.93% | 0.015 |
| Gemini 3.1 Pro（web search） | 3.71% | 0.040 |

*说明：上述基线来自完整 261 条内部 Bench（含电商数据）。本公开数据集仅包含其中的 91 条无效宣告程序子集。*

## 局限性

- **仅公开无效数据子集**：本次公开仅为经筛选的无效宣告程序子集，并非完整的内部数据集。后续会扩展到覆盖更多受理局的更全面的无效数据。

## 许可协议

本数据集依据 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 发布，可用于科研和非商业评测用途。

## 试用生产系统

体验 **PatSnap Design FTO AI Agent** —— 本 Bench 所评估的商业系统，提供端到端外观设计专利自由实施分析，支持跨模态图像检索（产品实物图 ↔ 专利线稿图）、多辖区覆盖以及侵权风险评估。

🔗 **立即体验**：[PatSnap Design FTO on Eureka](https://eureka.patsnap.com/ip/checking/?from=benchmark_github#/design-fto)
