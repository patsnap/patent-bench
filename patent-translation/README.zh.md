# PatSnap Patent Translation Bench

[English](./README.md) | **中文**

一个面向**专利文本机器翻译系统**的评估 Bench，覆盖中翻英（CN→EN）与英翻中（EN→CN）两个方向，从翻译准确性、术语准确性、术语一致性、专利书写规范、幻觉、漏译六个维度对翻译质量进行系统评估。

## 数据集概览

| 属性 | 取值 |
|----------|-------|
| **样本总数** | 2,498 |
| **翻译方向** | 中翻英（CN→EN）/ 英翻中（EN→CN） |
| **中翻英可用条数** | 2,498 |
| **英翻中可用条数** | 1,428 |
| **IPC 覆盖** | A / B / C / D / E / F / G / H 八大技术领域 |
| **文本粒度** | 词、字、句、段、篇 |
| **许可协议** | CC BY-NC 4.0 |

## 使用场景

本 Bench 用于评估专利翻译系统在以下能力上的表现：

1. **翻译准确性**：在词、字、句、段、篇各粒度上与标准答案的语义吻合程度
2. **术语准确性**：专利专业术语是否被准确翻译
3. **术语一致性**：同一术语在同一文本中是否保持一致的译法
4. **专利书写规范**：译文是否符合专利文件的书写范式
5. **幻觉检测**：译文是否出现原文中没有的内容（如混入源语言字符、篇幅异常膨胀）
6. **漏译检测**：译文篇幅相较原文是否出现异常压缩

## 数据字段

| 字段 | 类型 | 说明                                                |
|-------|------|---------------------------------------------------|
| `pn` | string | 专利公开号（PatSnap 标准化 PN）                             |
| `ipc` | string | IPC 一级分类（A–H，无分类记为 `Zero`）                        |
| `content_cn` | string | 中文原文                                              |
| `content_en` | string | 英文原文（中翻英的标准答案；`Zero` 表示该条无英文）                     |
| `label_1` | string | 文本粒度：`词` / `字` / `句` / `段` / `篇`                  |
| `label_2` | string | 评测维度（见下表）                                         |
| `label_3` | string | 文本来源（特殊场景标记）：`摘要` / `权利要求` / `说明书` 等，无来源记为 `Zero` |
| `special_cn` | string / list | 中文特殊词/术语（用于专业性指标），无则为 `Zero`                      |
| `special_en` | string / list | 英文特殊词/术语（用于专业性指标），无则为 `Zero`                      |
| `domain` | string | 领域标签，无则为 `Zero`                                   |

### label_2 取值说明

| label_2 | 类别 | 说明 | 条数 |
|---------|------|------|------|
| terminology_accuracy | 专业性 | 专利术语翻译是否准确 | 638 |
| terminology_consistency | 专业性 | 同一术语在文中译法是否一致 | 377 |
| normal_sentence | 普通准确性 | 常规句子翻译质量 | 375 |
| normal_character | 普通准确性 | 常规字符/词汇翻译质量 | 365 |
| paragraph_accuracy | 普通准确性 | 段落级翻译质量 | 294 |
| special_character | 专业性 | 特殊符号/字符是否正确处理 | 235 |
| special_sentence | 专业性 | 特殊句式是否正确翻译 | 151 |
| patent_writing_norm | 专业性 | 译文是否符合专利文书规范 | 55 |
| document_accuracy | 普通准确性 | 全文篇章级翻译质量 | 8 |

## 数据分布

### 按文本粒度（label_1）

| 粒度 | 条数 | 占比 |
|------|------|------|
| word | 1,015 | 40.6% |
| character | 600 | 24.0% |
| sentence | 526 | 21.1% |
| paragraph | 294 | 11.8% |
| document | 63 | 2.5% |

### 按 IPC 技术领域

| IPC | 技术领域 | 条数 |
|-----|---------|------|
| H | 电学 | 235 |
| G | 物理 | 200 |
| C | 化学；冶金 | 198 |
| B | 作业；运输 | 185 |
| A | 人类生活必需 | 160 |
| D | 纺织；造纸 | 155 |
| F | 机械工程；照明；加热；武器；爆破 | 150 |
| E | 固定建筑物 | 145 |
| 无 | 无 IPC 标注 | 1,070 |

## 评估指标

### 准确性指标（普通翻译质量，针对 label_2 为 normal_sentence / normal_character / paragraph_accuracy / special_sentence / document_accuracy）

#### BLEU（Bilingual Evaluation Understudy）

通过计算候选翻译与参考翻译之间的 n-gram 匹配度评估翻译的准确性和流畅性，分数在 0–1 之间，越接近 1 表示质量越好。统计 n-gram 匹配情况并引入长度惩罚因子。

#### SacreBLEU

标准化的 BLEU 实现，使用统一的 tokenization 和 smoothing 方法，确保不同研究者之间的结果可比。

#### METEOR（Metric for Evaluation of Translation with Explicit ORdering）

综合考虑词形变化、同义词和词序的评估指标，对语义和词序更加敏感。通过词汇匹配、词干匹配和同义词匹配进行词语对齐，计算准确率和召回率的调和平均，并引入长度惩罚因子。

#### ROUGE（Recall-Oriented Understudy for Gisting Evaluation）

主要通过计算候选翻译与参考翻译之间的 n-gram 重叠度评估语义相似度。ROUGE-N 衡量 n-gram 重叠，ROUGE-L 衡量最长公共子序列（LCS）长度。

| 指标 | 说明 | 适用方向 |
|------|------|---------|
| **BLEU-1 / 2 / 4** | n-gram 精确匹配率 | CN→EN / EN→CN |
| **SacreBLEU** | 标准化 corpus-level BLEU | CN→EN / EN→CN |
| **METEOR** | 含词形还原与同义词匹配的 n-gram 指标 | CN→EN / EN→CN |
| **ROUGE-1 / 2 / L** | 召回导向的 n-gram 重叠 | CN→EN / EN→CN |

综合得分（score）计算规则：
- 普通语句/字符/段落/特殊语句：`score = (BLEU-1 + METEOR) / 2`（CN→EN）；`score = (ROUGE-1 + METEOR) / 2`（EN→CN）
- document_accuracy：`score = SacreBLEU`

> 幻觉与漏译指标仅针对 `label_2` 为以下类别的条目计算：normal_sentence、normal_character、paragraph_accuracy、special_sentence、document_accuracy。

### 专业性指标

#### 术语准确性

确保专业术语的翻译与原文保持一致，避免歧义。

| label_2 | 计算方式 | 说明 |
|---------|---------|------|
| terminology_accuracy | `special_en`（CN→EN）/ `special_cn`（EN→CN）是否出现在译文中（0/1） | ACC：专业术语的翻译是否正确 |

#### 术语一致性

同一术语在全文中的使用应保持一致。

| label_2 | 计算方式 | 说明 |
|---------|---------|------|
| terminology_consistency | 术语在译文中出现次数 ≥ 2（0/1） | ACC：同一术语在不同部分的翻译是否一致（仅统计术语翻译准确的条目） |

#### 特殊字符

译文是否正确保留了原文中的特殊符号/字符。

| label_2 | 计算方式 | 说明 |
|---------|---------|------|
| special_character | `special_en`（CN→EN）/ `special_cn`（EN→CN）是否出现在译文中（0/1） | ACC：特殊符号/字符是否正确保留 |

#### 专利书写规范性

译文是否符合 USPTO 专利撰写要求。

| label_2 | 计算方式 | 说明 |
|---------|---------|------|
| patent_writing_norm | 规范短语命中比例（0–1） | ACC：摘要、权利要求、技术领域、背景技术、概述、具体实施方式等专业名词翻译是否准确 |

### 幻觉与漏译指标

#### 漏译

翻译是否完整。以下指标仅针对 `label_2` 为 normal_sentence、normal_character、paragraph_accuracy、special_sentence、document_accuracy 的条目计算，结果为触发百分比（%），越低越好。

| 指标 | 计算方式 |
|------|---------|
| **漏译率** | `count(模型返回结果长度 / 标注答案长度 < 0.5) / 总量` |

#### 幻觉

模型回答是否存在幻觉。以下指标仅针对 `label_2` 为 normal_sentence、normal_character、paragraph_accuracy、special_sentence、document_accuracy 的条目计算，结果为触发百分比（%），越低越好。

| 指标 | 计算方式 |
|------|---------|
| **篇幅幻觉率** | `count(模型返回结果长度 / 标注答案长度 > 5) / 总量` |
| **源语言混入率（CN→EN）** | `count(翻译结果存在中文字符) / 总量` |
| **源语言混入率（EN→CN）** | `count(翻译结果存在英文字符 且 原文不含英文) / 总量` |

> CN→EN 以单词数计算长度比；EN→CN 以字符数计算长度比。

## 数据集构建

### 1. 数据来源

从 PatSnap 专利数据库中采集覆盖 A–H 八大 IPC 领域的中英双语专利文本对，文本来源涵盖专利摘要、权利要求、说明书各章节（背景技术、发明内容、附图说明、具体实施方式）。

### 2. 评测维度分层

按照文本粒度（word/character/sentence/paragraph/document）和评测维度（普通准确性/terminology_accuracy/terminology_consistency/patent_writing_norm/special_character/special_sentence）对样本进行分层标注，确保各维度均有充足的评测覆盖。

### 3. 专业性标注

对包含专利专用术语、特殊字符和书写规范的样本，人工标注 `special_cn` / `special_en` 字段，用于专业性指标的精确匹配评测。

### 4. 质检与过滤

- 剔除双语文本缺失或长度异常的条目
- 对标准答案进行人工复核，确保中英对照的准确性

## 评估示例

```python
import json, sys

sys.path.insert(0, "../common/metrics")
from translation_metrics import evaluate

# 在 test_dataset.jsonl 基础上，为每条记录添加翻译结果字段
# 中翻英：添加 content_cn_translate 字段
# 英翻中：添加 content_en_translate 字段

summary = evaluate("your_results.jsonl", direction="cn2en")
print(json.dumps(summary, ensure_ascii=False, indent=2))
```

输出示例：

```json
{
  "direction": "cn2en",
  "total": 1469,
  "accuracy_by_label": {
    "normal_sentence": 72.34,
    "terminology_accuracy": 85.10,
    "...": "..."
  },
  "hallucination_pct_by_label": {
    "normal_sentence": 1.20,
    "...": "..."
  },
  "miss_translation_pct_by_label": {
    "normal_sentence": 0.80,
    "...": "..."
  }
}
```

命令行方式：

```bash
python ../common/metrics/translation_metrics.py \
    --input your_results.jsonl \
    --direction cn2en \
    --output result_cn2en.json
```

## 评分等级参考（综合 score，以百分制计）

| 等级 | score | 说明 |
|------|-------|------|
| **A** | ≥ 80 | 优秀 —— 可直接用于专利专业场景 |
| **B** | ≥ 65 | 良好 —— 可作为辅助翻译工具 |
| **C** | ≥ 50 | 合格 —— 需人工校对关键术语 |
| **D** | < 50 | 未达标 —— 建议模型优化 |

## 引用

如果你使用了本数据集，请引用：

```bibtex
@dataset{patsnap_patent_translation_bench_2026,
  title={PatSnap Patent Translation Bench},
  author={PatSnap},
  year={2026},
  note={A benchmark for evaluating patent machine translation systems, covering CN↔EN bidirectional translation}
}
```

## 许可协议

本数据集依据 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 发布，可用于科研和非商业评测用途。

## 试用生产系统

体验 **PatSnap AI Translation** —— 本 Bench 所评估的专利翻译系统，提供专利文本中英互译服务，覆盖全球主要受理局专利文件。

🔗 **立即体验**：[PatSnap Eureka](https://eureka.patsnap.com)
