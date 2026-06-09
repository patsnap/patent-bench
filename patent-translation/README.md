# PatSnap Patent Translation Bench

**English** | [中文](./README.zh.md)

A benchmark for evaluating **patent machine translation systems**, covering both Chinese-to-English (CN→EN) and English-to-Chinese (EN→CN) directions. It assesses translation quality across six dimensions: translation accuracy, terminology accuracy, terminology consistency, patent writing conventions, hallucination, and omission.

## Dataset Overview

| Attribute | Value |
|-----------|-------|
| **Total samples** | 2,498 |
| **Translation directions** | CN→EN / EN→CN |
| **CN→EN samples** | 2,498 |
| **EN→CN samples** | 1,428 |
| **IPC coverage** | All 8 sections: A / B / C / D / E / F / G / H |
| **Text granularity** | Word, character, sentence, paragraph, document |
| **License** | CC BY-NC 4.0 |

## Use Cases

This bench evaluates patent translation systems on the following capabilities:

1. **Translation accuracy**: Semantic alignment with the reference translation at word, character, sentence, paragraph, and document granularity
2. **Terminology accuracy**: Whether patent-specific terms are translated correctly
3. **Terminology consistency**: Whether the same term is translated consistently throughout the text
4. **Patent writing conventions**: Whether the translation conforms to patent document writing norms
5. **Hallucination detection**: Whether the translation introduces content not present in the source (e.g., source-language characters mixed in, abnormal length inflation)
6. **Omission detection**: Whether the translation is abnormally shorter than the source

## Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `pn` | string | Patent publication number (PatSnap normalized PN) |
| `ipc` | string | IPC top-level class (A–H; `Zero` if unclassified) |
| `content_cn` | string | Chinese source text |
| `content_en` | string | English source text (reference answer for CN→EN; `Zero` if unavailable) |
| `label_1` | string | Text granularity: `词` / `字` / `句` / `段` / `篇` (word / char / sentence / paragraph / document) |
| `label_2` | string | Evaluation dimension (see table below) |
| `label_3` | string | Text origin (special context marker): `摘要` / `权利要求` / `说明书`, etc.; `Zero` if not applicable |
| `special_cn` | string / list | Chinese special terms (used for professional metrics); `Zero` if none |
| `special_en` | string / list | English special terms (used for professional metrics); `Zero` if none |
| `domain` | string | Domain label; `Zero` if none |

### label_2 Values

| label_2 | Category | Description | Count |
|---------|----------|-------------|-------|
| terminology_accuracy | Professional | Whether patent terminology is accurately translated | 638 |
| terminology_consistency | Professional | Whether the same term is translated consistently | 377 |
| normal_sentence | General accuracy | Translation quality of regular sentences | 375 |
| normal_character | General accuracy | Translation quality of regular characters/words | 365 |
| paragraph_accuracy | General accuracy | Paragraph-level translation quality | 294 |
| special_character | Professional | Whether special symbols/characters are handled correctly | 235 |
| special_sentence | Professional | Whether special sentence structures are translated correctly | 151 |
| patent_writing_norm | Professional | Whether the translation conforms to patent writing norms | 55 |
| document_accuracy | General accuracy | Full-document translation quality | 8 |

## Data Distribution

### By Text Granularity (label_1)

| Granularity | Count | Ratio |
|-------------|-------|-------|
| Word (词) | 1,015 | 40.6% |
| Character (字) | 600 | 24.0% |
| Sentence (句) | 526 | 21.1% |
| Paragraph (段) | 294 | 11.8% |
| Document (篇) | 63 | 2.5% |

### By IPC Technical Domain

| IPC | Domain | Count |
|-----|--------|-------|
| H | Electricity | 235 |
| G | Physics | 200 |
| C | Chemistry; Metallurgy | 198 |
| B | Performing Operations; Transporting | 185 |
| A | Human Necessities | 160 |
| D | Textiles; Paper | 155 |
| F | Mechanical Engineering; Lighting; Heating; Weapons; Blasting | 150 |
| E | Fixed Constructions | 145 |
| — | No IPC label | 1,070 |

## Evaluation Metrics

### Accuracy Metrics (General translation quality — applies to label_2: normal_sentence / normal_character / paragraph_accuracy / special_sentence / document_accuracy)

#### BLEU (Bilingual Evaluation Understudy)

Measures translation accuracy and fluency by computing n-gram precision between the hypothesis and reference, with a brevity penalty. Scores range from 0 to 1; higher is better.

#### SacreBLEU

A standardized BLEU implementation using consistent tokenization and smoothing methods, ensuring reproducible and comparable results across different research groups.

#### METEOR (Metric for Evaluation of Translation with Explicit ORdering)

Considers stemming, synonyms, and word order; more sensitive to semantics than BLEU. Aligns tokens via exact match, stem match, and synonym match, then computes the harmonic mean of precision and recall with a fragmentation penalty.

#### ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

Evaluates semantic similarity via n-gram overlap. ROUGE-N measures n-gram overlap; ROUGE-L measures the longest common subsequence (LCS).

| Metric | Description | Direction |
|--------|-------------|-----------|
| **BLEU-1 / 2 / 4** | n-gram precision | CN→EN |
| **SacreBLEU** | Standardized corpus-level BLEU | CN→EN / EN→CN (document-level) |
| **METEOR** | n-gram metric with stemming and synonym matching | CN→EN / EN→CN |
| **ROUGE-1 / 2 / L** | Recall-oriented n-gram overlap | EN→CN |

Composite score calculation:

- Regular sentences / characters / paragraphs / special sentences: `score = (BLEU-1 + METEOR) / 2` (CN→EN); `score = (ROUGE-1 + METEOR) / 2` (EN→CN)
- Document accuracy: `score = SacreBLEU`

> Hallucination and omission metrics are computed only for entries whose `label_2` is: normal_sentence, normal_character, paragraph_accuracy, special_sentence, document_accuracy.

### Professional Metrics

#### Terminology Accuracy

Ensures professional terms are translated correctly, avoiding ambiguity.

| label_2 | Calculation | Description |
|---------|-------------|-------------|
| terminology_accuracy | Whether `special_en` (CN→EN) / `special_cn` (EN→CN) appears in the translation (0/1) | ACC: whether the terminology is correctly translated |

#### Terminology Consistency

The same term should be translated consistently throughout the document.

| label_2 | Calculation | Description |
|---------|-------------|-------------|
| terminology_consistency | Whether the term appears ≥ 2 times in the translation (0/1) | ACC: consistency of term translation across different parts (only counted when term is correctly translated) |

#### Special Characters

Whether the translation correctly preserves special symbols/characters from the source.

| label_2 | Calculation | Description |
|---------|-------------|-------------|
| special_character | Whether `special_en` (CN→EN) / `special_cn` (EN→CN) appears in the translation (0/1) | ACC: whether special symbols/characters are correctly preserved |

#### Patent Writing Conventions

Whether the translation meets USPTO patent writing requirements.

| label_2 | Calculation | Description |
|---------|-------------|-------------|
| patent_writing_norm | Ratio of matched convention phrases (0–1) | ACC: whether patent section names (abstract, claims, technical field, background, summary, detailed description, etc.) are correctly translated |

### Hallucination and Omission Metrics

All values are reported as **percentages (%)** — lower is better.

#### Omission

Whether the translation is complete. Computed only for entries whose `label_2` is normal_sentence, normal_character, paragraph_accuracy, special_sentence, or document_accuracy.

| Metric | Calculation |
|--------|-------------|
| **Omission rate (%)** | `count(translation length / reference length < 0.5) / total × 100` |

#### Hallucination

Whether the model output contains hallucinated content. Computed only for entries whose `label_2` is normal_sentence, normal_character, paragraph_accuracy, special_sentence, or document_accuracy.

| Metric | Calculation |
|--------|-------------|
| **Length hallucination rate (%)** | `count(translation length / reference length > 5) / total × 100` |
| **Source-language leakage rate — CN→EN (%)** | `count(translation contains Chinese characters) / total × 100` |
| **Source-language leakage rate — EN→CN (%)** | `count(translation contains English letters AND source has no English) / total × 100` |

> Length ratio for CN→EN is computed in words; for EN→CN in characters.

## Dataset Construction

### 1. Data Sources

Bilingual (CN/EN) patent text pairs were collected from the PatSnap patent database across all eight IPC sections (A–H). Text sources include patent abstracts, claims, and all description sections (background, summary, brief description of drawings, detailed description).

### 2. Stratified Annotation

Samples were annotated by text granularity (word / character / sentence / paragraph / document) and evaluation dimension (general accuracy / terminology accuracy / terminology consistency / patent writing conventions / special characters / special sentences) to ensure sufficient coverage of each dimension.

### 3. Professional Annotation

For samples containing patent-specific terms, special characters, or writing conventions, the `special_cn` / `special_en` fields were manually annotated for use in exact-match professional metrics.

### 4. Quality Control

- Entries with missing bilingual text or abnormal lengths were filtered out
- Reference answers were manually reviewed to ensure CN/EN alignment accuracy

## Evaluation Example

```python
import json, sys

sys.path.insert(0, "../common/metrics")
from translation_metrics import evaluate

# Add translation result field to each record in test_dataset.jsonl
# CN→EN: add content_cn_translate field
# EN→CN: add content_en_translate field

summary = evaluate("your_results.jsonl", direction="cn2en")
print(json.dumps(summary, ensure_ascii=False, indent=2))
```

Example output:

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

CLI usage:

```bash
python ../common/metrics/translation_metrics.py \
    --input your_results.jsonl \
    --direction cn2en \
    --output result_cn2en.json
```

## Score Grade Reference (composite score, as percentage)

| Grade | Score | Description |
|-------|-------|-------------|
| **A** | ≥ 80 | Excellent — ready for professional patent use |
| **B** | ≥ 65 | Good — suitable as a translation aid |
| **C** | ≥ 50 | Acceptable — key terms require manual review |
| **D** | < 50 | Below standard — model improvement recommended |

## Citation

If you use this dataset, please cite:

```bibtex
@dataset{patsnap_patent_translation_bench_2026,
  title={PatSnap Patent Translation Bench},
  author={PatSnap},
  year={2026},
  note={A benchmark for evaluating patent machine translation systems, covering CN↔EN bidirectional translation}
}
```

## License

This dataset is released under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) for research and non-commercial evaluation purposes.

## Try the Production System

Experience **PatSnap AI Translation** — the patent translation system evaluated by this bench, offering CN↔EN translation for patent documents from major patent offices worldwide.

**Try it now**: [PatSnap Eureka](https://eureka.patsnap.com)
