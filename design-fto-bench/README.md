# PatSnap Design FTO Bench

**English** | [中文](./README.zh.md)

A Bench for evaluating **design patent freedom-to-operate (FTO)** image retrieval systems. Each sample contains a query design patent image along with ground truth target patent images confirmed as infringing through real patent invalidation proceedings.

## Dataset Overview

| Property | Value |
|----------|-------|
| **Total samples** | 91 |
| **Source** | Real patent invalidation proceedings |
| **Image types** | Product photos ↔ Patent line drawings (cross-modal) |
| **LOC coverage** | 22 Locarno classification sections |
| **Ground truth** | Human-verified infringing patent image pairs |
| **License** | CC BY-NC 4.0 |

## Intended Use

This Bench evaluates the ability of design patent FTO systems to:
1. **Retrieve** visually similar design patents from a large patent image corpus given a query product/patent image
2. **Match** across image styles — product photos vs. patent line drawings (cross-modal retrieval)
3. **Rank** the most visually similar and legally relevant design patents highly in the result list

It is designed for computing standard retrieval metrics: **Hit Rate @ K** and **PRES score**.

## Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Sample identifier |
| `query_img_id` | string | Image ID of the query patent image |
| `query_pn` | string | Publication number of the query patent (PatSnap standardized PN) |
| `query_img_path` | string | Storage path of the query image |
| `target_pns` | list[str] | Ground truth infringing patent PNs (PatSnap standardized PN) |
| `target_img_ids` | list[str] | All image view IDs belonging to the target patents (e.g. S-0, S-1) |
| `pair_name` | string | Pair identifier linking query to its ground truth targets |
| `picture_type` | string | Image type: `无效` (patent invalidation proceedings) |
| `one_level_loc` | string | Locarno classification — first level code (dual classifications are joined with ` OR `, e.g. `02 OR 29`) |
| `two_level_loc` | string | Locarno classification — second level code (dual classifications are joined with ` OR `, e.g. `02-03 OR 29-02`) |
| `country` | list[str] | Target search jurisdiction (e.g. `["CN"]`) |
| `version` | string | Dataset version |

> **Note on Patent Numbers (PN):** All publication numbers have been converted to PatSnap standardized PN format.

## Ground Truth Construction

Each sample's ground truth is the `target_pns` list — patent publication numbers confirmed as infringing through real patent invalidation proceedings, verified by a human annotation team.

**Hit rule**: A retrieval system's result is considered a hit if any patent in `target_pns` appears in the returned results. Since one patent may have multiple image views (e.g. S-0, S-1), deduplication is performed at the `patent_id` level — any view of a target patent counts as a hit.

> ⚠️ **Note:** `target_img_ids` lists all image views of the target patents. When evaluating image-level retrieval systems, any `img_id` in this list counts as a hit for the corresponding patent.

## Evaluation Metrics

| Metric | Description | Focus |
|--------|-------------|-------|
| **Hit Rate @ K** | % of samples with ≥1 GT patent in top K results (K=10, 50, 100, 200) | Retrieval ranking precision |
| **PRES Score** | % of samples where the agent's final infringement report correctly identifies a GT patent | End-to-end judgment quality |

> The primary evaluation range is **Top@200**, which provides sufficient coverage for design patent visual similarity retrieval while remaining within practical human review capacity.

### Scoring Grades (Hit Rate @ Top@100)

| Grade | Hit Rate | Description |
|-------|----------|-------------|
| **A** | ≥ 90% | Excellent — suitable for direct professional use |
| **B** | ≥ 75% | Good — effective as a high-efficiency screening tool |
| **C** | ≥ 60% | Acceptable — requires human review of key results |
| **D** | < 60% | Below standard — model improvement needed |

## Distribution

### By Locarno (LOC) Classification

| LOC | Description | Count |
|-----|-------------|-------|
| 23 | Games, toys, sports equipment | 14 |
| 28 | Pharmaceutical & cosmetic articles | 10 |
| 08 | Tools & hardware | 9 |
| 15 | Machines | 9 |
| 09 | Packages & containers | 8 |
| 12 | Transport vehicles | 6 |
| 14 | Recording & communication equipment | 6 |
| 31 | Food products | 5 |
| 07 | Household goods | 5 |
| 26 | Lighting equipment | 3 |
| 16 | Photography & optics | 3 |
| Others | (11 additional sections) | 13 |
| **Total** | | **91** |

## Dataset Construction

### 1. Base Data Layer
Candidate pairs were selected from real patent invalidation proceedings across multiple LOC technical domains, covering cross-modal image pairs (product photos ↔ patent line drawings).

### 2. Visual Alignment Layer
Query patent images and target infringing patent images were extracted and validated for visual alignment. Cross-modal pairs (product photo vs. line drawing) were verified for structural and shape consistency.

### 3. Annotation & Quality Layer
- Human annotation team performed secondary confirmation of all infringement relationships
- De-duplication at `patent_id` level; all PNs converted to PatSnap standardized format
- Field completeness validation; records with incomplete query information were excluded

## Evaluation Example

```python
import json, sys

# Reuse the shared retrieval metrics provided in the monorepo
sys.path.insert(0, "../common/metrics")
from search_metrics import hit_rate_at_k, calc_pres  # noqa: E402

# Load the JSONL file directly from this repository
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
    Compute Hit Rate @ K.
    results_dict: {sample_id: [ranked list of retrieved PNs]}
    """
    hits = 0
    for sample in dataset:
        gt = set(sample["target_pns"])
        retrieved = results_dict.get(sample["id"], [])[:k]
        if any(pn in gt for pn in retrieved):
            hits += 1
    return hits / len(dataset)
```

> For a one-command metric computation, run `python ../common/metrics/search_metrics.py --dataset data/test.jsonl --results your_results.json` — no retrieval is performed; the script only scores a ranked-results file you provide.

## Baseline Results

Results from PatSnap Design FTO AI Agent evaluated on 261 samples (full internal dataset including e-commerce data), March 2026:

| AI Tool | Hit Rate (Top@200) | PRES Score |
|---------|-------------------|------------|
| **PatSnap Design FTO AI Agent** | **77.00%** | **0.700** |
| ChatGPT 5.4 (web search) | 0.93% | 0.015 |
| Gemini 3.1 Pro (web search) | 3.71% | 0.040 |

*Note: Baseline results are from the full 261-sample internal Bench (including e-commerce data). This public dataset contains only the 91-sample patent invalidation subset.*

## Limitations

- **Subset of invalidation data**: This public release contains only a curated subset of patent invalidation cases, not the full internal dataset. Future releases will expand to more comprehensive invalidation data covering additional patent offices.

## Citation

If you use this dataset, please cite:

```bibtex
@dataset{patsnap_design_fto_bench_2026,
  title={PatSnap Design FTO Bench},
  author={PatSnap},
  year={2026},
  note={A Bench for evaluating design patent freedom-to-operate image retrieval systems}
}
```

## License

This dataset is released under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). It may be used for research and non-commercial evaluation purposes.

## Try the Production System

Experience the **PatSnap Design FTO AI Agent** — the commercial system evaluated in this Bench. It delivers end-to-end design patent freedom-to-operate analysis, with cross-modal image retrieval (product photos ↔ patent line drawings), multi-jurisdiction coverage, and infringement risk assessment.

🔗 **Try it now**: [PatSnap Design FTO on Eureka](https://eureka.patsnap.com/ip/checking/?from=benchmark_github#/design-fto)
