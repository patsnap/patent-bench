# PatSnap FTO Bench

**English** | [中文](./README.zh.md)

A Bench for evaluating **invention patent freedom-to-operate (FTO) retrieval systems**. Each sample contains a technical feature description document and a target jurisdiction, with ground truth being a set of risk patents confirmed through real litigation rulings or identified in professional FTO analysis reports.

## Dataset Overview

| Property | Value |
|----------|-------|
| **Total samples** | 30 |
| **Source** | Real litigation cases + professional FTO analysis reports |
| **Jurisdictions** | CN / US / EP (10 each) |
| **Languages** | CN / EN (aligned with jurisdiction) |
| **IPC coverage** | All eight sections A–H |
| **Ground truth** | Risk patent PN list confirmed by court rulings + reviewed by senior patent engineers |
| **License** | CC BY-NC 4.0 |

## Intended Use

This Bench evaluates the ability of invention patent FTO retrieval systems to:

1. **Retrieve** all potentially blocking risk patents from a large patent corpus given a technical feature description document and a target jurisdiction
2. **Cross-lingual understanding** — maintain stable semantic understanding across Chinese and English technical documents covering three major jurisdictions
3. **Ranking quality** — concentrate risk patents at the top of the result list to reduce the patent analyst's review workload

It is designed for computing the standard retrieval metrics **Hit Rate** and **PRES score**.

## Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Sample identifier |
| `case_id` | string | Case UUID |
| `country` | string | Target jurisdiction: `CN` / `US` / `EP` |
| `ipc_main` | string | IPC section (A–H) |
| `type` | string | Sample source: `litigation` (court rulings) or `fto_professinal` (professional FTO reports) |
| `technical_text` | string | Technical feature description (same language as jurisdiction: CN→Chinese, US/EP→English) |
| `target_pns` | list[str] | Ground truth: risk patent PNs (PatSnap standardized format) |
| `related_patent_detail` | list[object] | Structured detail for each GT patent, fields: `country / lang / apno / ipc_main / pn` |
| `version` | string | Dataset version |

> **Note on Patent Numbers (PN):** All PNs are converted to PatSnap standardized format; different publication versions of the same patent (e.g. A / B) are listed as separate PNs.

## Ground Truth Construction

Each sample's ground truth is the `target_pns` list. For `type=litigation` samples, the PNs come from court-confirmed infringing patents in final judgments; for `type=fto_professinal` samples, the PNs come from high-risk patents identified by senior FTO engineers in analysis reports.

**Hit rule**: FTO is a typical "recall-driven" task — a sample is considered hit (hit=1) if **any** patent from `target_pns` appears in the returned results, regardless of how many GT patents are found; otherwise hit=0. Hit Rate is a sample-level binary metric.

> ⚠️ **Note:** Hit Rate ≠ Recall. Recall measures "how many GT patents were found", while Hit Rate only asks "whether at least one GT was found". In FTO practice, as soon as the analyst can locate any risk patent from the shortlist, initial risk alert in that direction is established — making sample-level binary the more business-relevant measurement.

## Evaluation Metrics

| Metric | Description | Focus |
|--------|-------------|-------|
| **Hit Rate @ 100** | % of samples with ≥1 patent from `target_pns` in the top 100 results | Detection rate (sample-level binary) |
| **PRES @ 100** | Patent Retrieval Evaluation Score (Magdy & Jones 2010, with miss-penalty correction): a single score in `[0, 1]` that jointly captures **how many** GT patents are retrieved within top-N and **how highly** they are ranked. PRES = 1.0 means every GT patent appears at the very top; PRES = 0 means none are found within N. Default N = 100. | Retrieval ranking quality |

> The primary evaluation range is **Top@100** — provides sufficient coverage for invention patent FTO retrieval depth, while staying within practical human analysis capacity, matching real-world FTO workflows.

### Scoring Grades (Hit Rate @ Top@100)

| Grade | Hit Rate | Description |
|-------|----------|-------------|
| **A** | ≥ 60% | Excellent — suitable to directly assist FTO analysts |
| **B** | ≥ 40% | Good — effective as a high-efficiency screening tool |
| **C** | ≥ 20% | Acceptable — significant human supplementation required |
| **D** | < 20% | Below standard — model improvement needed |

## Distribution

### By Jurisdiction

| Jurisdiction | Count | Share |
|-------------|-------|------------|
| CN | 10 | 33.3% |
| US | 10 | 33.3% |
| EP | 10 | 33.3% |
| **Total** | **30** | **100%** |

### By Sample Source Type

| `type` | Count | Description |
|---|---|---|
| litigation | 26 | Court rulings: extracted from litigation documents (accused product/technical scheme description); ground truth = court-confirmed infringing patents |
| fto_professinal | 4 | Professional FTO reports: extracted from FTO technical specification documents; ground truth = high-risk patents identified in the reports |

### By IPC Section

| IPC | Count |
|-----|------|
| A | 7 |
| G | 7 |
| F | 4 |
| H | 4 |
| B | 3 |
| C | 3 |
| D | 1 |
| E | 1 |

## Dataset Construction

### 1. Foundation Layer
Candidate samples selected from real litigation cases (plaintiff prevailed; infringement established) and professional FTO analysis reports, covering CN / US / EP three major jurisdictions and all 8 IPC sections (A–H).

### 2. Technical Document Layer
Technical feature descriptions of the accused infringing product/technical scheme are extracted from litigation documents and integrated into complete technical specification text; for FTO reports, product technical scheme descriptions are extracted directly. Text from both sources is cleaned and normalized with the goal of being directly usable as input to a retrieval system.

### 3. Annotation & QA Layer
- `litigation` samples: court-confirmed infringing patents as ground truth
- `fto_professinal` samples: high-risk patents identified in FTO reports as ground truth (re-reviewed by senior patent engineers)
- All PNs converted to PatSnap standardized format; multiple publication versions of the same patent (A / B / U, etc.) are all retained

## Evaluation Example

```python
import json, sys

# Reuse the shared retrieval metrics from the monorepo
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
    Compute Hit Rate @ K and PRES @ N.
    results_dict: {sample_id: [ranked PN list]}
    """
    hits, presses = [], []
    for s in dataset:
        ranked = results_dict.get(s["id"], [])
        hits.append(hit_rate_at_k(s["target_pns"], ranked, k=k))
        presses.append(calc_pres(s["target_pns"], ranked, N=N))
    n = len(dataset)
    return sum(hits) / n, sum(presses) / n
```

> One-line CLI: `python ../common/metrics/search_metrics.py --dataset data/test.jsonl --results your_results.json --k 100 --N 100` — the script itself performs no retrieval; it computes scores from a ranked-results file you provide.

## Baseline Results

PatSnap FTO AI Agent on the full 136-sample internal Bench (March 2026):

| AI Tool | Hit Rate (Top@100) | PRES Score |
|---------|-------------------|------------|
| **PatSnap FTO AI Agent** | **57.00%** | **0.440** |
| Gemini 3.1 Pro (web search) | 25.62% | 0.140 |
| DeepSeek 3.2 (web search) | 16.94% | 0.120 |
| ChatGPT 5.4 (web search) | 9.23% | 0.290 |
| Perplexity Pro (web search) | 1.19% | 0.110 |

*Note: The baseline above is computed on the full 136-sample internal Bench. This public release is a 30-sample subset stratified evenly by jurisdiction (10 per CN / US / EP), intended as a minimal reproducible set for metric implementation validation and method comparison.*

## Limitations

- **Public subset size**: This release contains only the 30-sample subset stratified evenly by jurisdiction, not the complete 136-sample internal Bench. The full Bench is planned for staged release in subsequent versions.
- **Jurisdiction coverage**: Currently covers CN / US / EP three major jurisdictions; others (JP, KR, etc.) are not yet included.
- **Source type ratio**: In the 30-sample subset, `litigation` : `fto_professinal` ≈ 26 : 4, slightly different from the full Bench ratio of 110 : 26 (due to the stratified-by-jurisdiction constraint).

## Citation

If you use this dataset, please cite:

```bibtex
@dataset{patsnap_fto_bench_2026,
  title  = {PatSnap FTO Bench},
  author = {PatSnap},
  year   = {2026},
  note   = {A Bench for evaluating invention patent freedom-to-operate retrieval systems}
}
```

## License

This dataset is released under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) for research and non-commercial evaluation purposes.

## Try the Production System

Experience **PatSnap FTO AI Agent** — the commercial system evaluated in this Bench, offering end-to-end invention patent freedom-to-operate analysis: technical feature document input, multi-jurisdiction risk patent retrieval and ranking, and PRES-optimized shortlist reports.

🔗 **Try it now**: [PatSnap FTO on Eureka](https://eureka.patsnap.com/?from=benchmark_github)
