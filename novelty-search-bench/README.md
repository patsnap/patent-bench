# PatSnap Novelty Search Bench

**English** | [中文](./README.zh.md)

A Bench for evaluating **patent novelty search** (prior art search) systems. Each sample contains a query patent publication number (PN) along with ground truth **X-type** (novelty-destroying) prior art references identified by patent examiners.

The Bench is **deliberately designed as a 50% public release of an internal full evaluation set** that combines two complementary sample types — cross-jurisdiction family-expanded samples and single-jurisdiction non-expanded samples — so that retrieval systems can be probed on the most informative prior-art scenarios alongside a standard non-expanded baseline.

> 📄 **Companion paper:** *Research on Evaluation Methods for Patent Novelty Search Systems and Empirical Analysis* — Shu Zhang, LiSha Zhang, Kai Duan, XinKai Sun · arXiv [**2508.17782**](https://arxiv.org/abs/2508.17782) (Aug 2025). The paper details the dataset-construction methodology used to build this Bench (examiner citations + X-type citations from technically consistent family patents), the evaluation protocol (invention description as input, Top-k Detection Rate + Recall as core metrics), and a multi-dimensional analysis framework along language / IPC / filing-jurisdiction axes.
>
> ⚠️ **Note on the paper.** The dataset has been updated since the paper (arXiv, Aug 2025) was published; a revised paper is in preparation.

## Dataset Overview

| Property | Value |
|----------|-------|
| **Total samples (public release)** | **569** |
| **Family-expanded (`type=family`)** | 170 — 50% of internal full (340) |
| **Non-expanded (`type=public`)** | 399 — ~50% of internal full (≈800) |
| **Source** | Real patent examination records |
| **Jurisdictions** | CN / US / EP / WO (PCT) / AU |
| **Languages** | English (55.0%), Chinese (45.0%) |
| **IPC coverage** | All 8 sections (A–H), balanced |
| **Ground truth** | Examiner-cited X-type references; for family-expanded samples, also includes X references cited by examiners of the query patent's cross-jurisdiction family members |
| **License** | CC BY-NC 4.0 |

### Cross-jurisdiction family-expanded subset (170 samples)

The family-expanded subset is **the most informative slice for evaluating novelty search systems**: it captures the real-world scenario where a single invention has been examined by multiple patent offices, each citing different X-type prior art. A search system is tested not only against its query patent's direct X references, but also against the X references discovered across the patent's cross-jurisdiction family members — reflecting how a senior patent professional would treat the same invention from different angles.

This 170-sample slice is **50% of our internal full family-expanded set (340)**, retained at this ratio to keep the public release aligned with the structural distribution of the internal evaluation set.

### Single-jurisdiction non-expanded subset (399 samples)

The non-expanded subset provides a **standard, single-jurisdiction baseline** for assessing base retrieval ability. Each sample has only the X references directly cited by the examiner of that specific patent — no cross-family expansion. This subset (399) is **~50% of our internal full non-expanded set (≈800)**.

## Intended Use

This Bench evaluates the ability of patent novelty search systems to:

1. **Retrieve** examiner-cited X-type (novelty-destroying) prior art from a large patent corpus
2. **Match across jurisdictions** — for `type=family` samples, the query patent's cross-jurisdiction family members may have been examined by different offices citing different X references
3. **Rank** the most relevant prior art highly in the result list

It is designed for computing standard retrieval metrics: **top@K hit rate** (X-reference detection rate) and **Recall@K** (X-reference coverage rate).

## How to Use the Query

> ⚠️ **Query input is not bundled with this dataset.**
>
> Each sample exposes only the query patent's **publication number** (`pn`). The corresponding query input is the **technical solution text derived from the patent's specification**; it is **not** included in this repository because of file-size constraints.
>
> **To run a system against this Bench, first obtain the technical solution text of each `pn` yourself**, then feed that text into your retrieval system as the query.
>
> Recommended source: **[PatSnap Eureka](https://eureka.patsnap.com/?from=benchmark_github)** (free trial, provides the standardized technical solution text).
>
> The PNs used here are in **PatSnap standardized format** and are resolvable by all major public patent databases.

## Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Sample identifier (1–569) |
| `pn` | string | Publication number of the query patent (PatSnap standardized PN). **The query input is the technical solution text derived from this patent's specification.** |
| `apdt` | int | Application date (YYYYMMDD) |
| `ipc` | list[str] | IPC classification codes |
| `ipc_main` | string | Main IPC section (A–H) |
| `lang` | string | Language of the query patent (CN/EN) |
| `jurisdiction` | string | Filing jurisdiction (CN/WO/US/EP/AU) |
| `type` | string | Sample type: `family` (cross-jurisdiction family-expanded) or `public` (single-jurisdiction non-expanded) |
| `pn_x` | list[str] | X-type prior art reference PNs (directly cited by the examiner) |
| `pn_x_family` | list[str] | X-type references expanded to simple patent family member PNs (superset of `pn_x`). Used when the search system returns results collapsed by patent family |
| `pn_family_x` | list[str] | **Family-expanded subset only.** X-type reference PNs cited by examiners when examining the query patent's cross-jurisdiction family members. Must be merged into GT when evaluating `type=family` samples. **Empty list for `type=public` samples by definition.** |
| `pn_family_x_family` | list[str] | **Family-expanded subset only.** Simple patent family expansion of `pn_family_x`. **Empty list for `type=public` samples.** |

> **Note on Patent Numbers (PN):** All publication numbers in this dataset have been converted to PatSnap standardized PN format.

## Sample Types

### `type=family` — cross-jurisdiction family-expanded (170 samples)

Each query patent has cross-jurisdiction filings (CN, US, EP, etc.); these samples test whether the search system can find prior art across different patent offices and languages. The `pn_family_x` and `pn_family_x_family` fields capture additional X references discovered through cross-family examination. Family members are semantically equivalent (CC score = full match).

### `type=public` — single-jurisdiction non-expanded (399 samples)

Each query patent has only its direct examiner-cited X references; `pn_family_x` and `pn_family_x_family` are empty lists. These samples provide a non-expanded baseline reflecting standard single-jurisdiction retrieval scenarios.

## Ground Truth Construction

> ⚠️ **GT construction applies to X-type references only.**

### Why cross-family expansion matters (for `type=family`)

A single invention may be filed in multiple jurisdictions (e.g., CN and US). Examiners in different patent offices may independently cite different X references for what is essentially the same invention. The field `pn_family_x` captures these additional X references from other jurisdictions. When evaluating `type=family` samples, you **must merge** them into the GT.

**Example**: An invention is filed in both CN and US. The CN examiner cites `CN1234A` as X; the US examiner cites `US5678B1` as X.

- `pn_x = ["CN1234A"]`
- `pn_family_x = ["CN1234A", "US5678B1"]`
- GT = `["CN1234A", "US5678B1"]` — finding either one counts as a hit.

### GT by sample type and result format

| Result format | `type=family` | `type=public` |
|---------------|---------------|---------------|
| **Non-collapsed** (individual patents) | `pn_x` ∪ `pn_family_x` | `pn_x` (since `pn_family_x` is empty) |
| **Collapsed by family** (grouped by patent family) | `pn_x_family` ∪ `pn_family_x_family` | `pn_x_family` (since `pn_family_x_family` is empty) |

The same formula `pn_x ∪ pn_family_x` applies uniformly to both sample types — for `type=public`, the union with an empty set degenerates to `pn_x`. This keeps the metric script logic uniform regardless of sample type.

## Evaluation Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| **top@K** | % of samples with ≥1 GT hit in top K | X-reference detection rate at K = 1, 3, 5, 10, 20, 50, 100 |
| **Recall@K** | GT hits in top K / total GT refs | X-reference coverage rate at the same K cutoffs |

## Distribution

### By Sample Type

| Type | Count | Percentage |
|------|-------|------------|
| `family` (cross-jurisdiction family-expanded) | 170 | 29.9% |
| `public` (single-jurisdiction non-expanded) | 399 | 70.1% |
| **Total** | **569** | **100%** |

### By Jurisdiction

| Jurisdiction | Count | Percentage |
|-------------|-------|------------|
| CN | 223 | 39.2% |
| WO (PCT) | 179 | 31.5% |
| US | 89 | 15.6% |
| EP | 74 | 13.0% |
| AU | 4 | 0.7% |
| **Total** | **569** | **100%** |

### By Language

| Language | Count | Percentage |
|----------|-------|------------|
| English (EN) | 313 | 55.0% |
| Chinese (CN) | 256 | 45.0% |

### By IPC Section

| IPC | Description | Count |
|-----|-------------|-------|
| G | Physics | 75 |
| C | Chemistry; Metallurgy | 73 |
| A | Human Necessities | 72 |
| B | Operations; Transport | 72 |
| H | Electricity | 71 |
| F | Mechanical Engineering | 70 |
| D | Textiles; Paper | 68 |
| E | Fixed Constructions | 68 |
| **Total** | | **569** |

### Reference Statistics

| Field | Samples with refs | Total refs | Avg (all) | Avg (non-empty) | Max |
|-------|-------------------|------------|-----------|-----------------|-----|
| `pn_x` | 569 / 569 | 1,187 | 2.09 | 2.09 | 13 |
| `pn_x_family` | 569 / 569 | 9,154 | 16.09 | 16.09 | 269 |
| `pn_family_x` | 170 / 569 | 1,093 | 1.92 | 6.43 | 20 |
| `pn_family_x_family` | 170 / 569 | 10,971 | 19.28 | 64.54 | 541 |

### GT Size

| GT mode | All samples | `type=family` (170) | `type=public` (399) |
|---------|-------------|---------------------|---------------------|
| Non-collapsed (`pn_x ∪ pn_family_x`) | avg 3.36, median 2 | avg 6.43, median 5 | avg 2.05, median 2 |
| Collapsed (`pn_x_family ∪ pn_family_x_family`) | avg 26.94, median 12 | — | — |

## Dataset Construction

### 1. Base Data Layer

- Starting from the **full population of invention patents that have at least one examiner-cited X-type reference**, a sampling frame was built covering multiple IPC sections, jurisdictions, and recent application years
- Two sample tracks were prepared:
  - **Cross-jurisdiction family track** — patents with filings in at least two jurisdictions (CN, US, EP, etc.), where cross-family X references can be aggregated
  - **Single-jurisdiction track** — patents with examiner-cited X references in a single jurisdiction, providing a standard non-expanded baseline
- The internal full set is sampled at **50% per track** for the public release (170 of 340 family-expanded; 399 of ≈800 non-expanded)

### 2. Alignment & Processing Layer

- **Text comparability screening**: Initial filtering based on claims text
- **Semantic alignment**: Cross-language semantic mapping via proprietary claims consistency model
- **Technical similarity assessment** (`type=family` only): Ensuring cross-jurisdiction family members are technically identical (CC full score)
- **Noise reduction**: Second-round filtering to remove language-induced semantic noise

### 3. Bench & Quality Layer

- **Reference integration**: Based on examiner-cited X references
- **Normalization**: Per-source de-duplication (each citation source — direct examiner citations, family expansion of those citations, cross-jurisdiction family examiner citations, and family expansion of cross-jurisdiction citations — is de-duplicated independently), identifier unification (all PNs converted to PatSnap standardized format), citation caliber alignment. The four `pn_x*` / `pn_family_x*` fields are therefore individually de-duplicated but the union across fields is not, so some PNs may appear in more than one field; this is by design (see *Metric semantics* note below).
- **Quality assurance**: Minimum disclosure principle for data privacy; consistency checks for representativeness, stability, and fairness
- **Stratified sampling**: Public release was sampled per track stratified by IPC section × language, with random seed = 42 for reproducibility

> ℹ️ **Metric semantics on cross-field duplicates.** Because the reference scripts (`novelty_metrics.py`, `search_metrics.py`) build GT and score against a **set** (`pn_x ∪ pn_family_x`, etc.), any PN appearing in more than one field is counted once at scoring time. Cross-field duplicates therefore do not affect Hit Rate or Recall numerically. They are preserved in the JSONL so the per-field provenance of each reference is recoverable (which examiner / which jurisdiction).

## Evaluation Example

The shared metric library (`common/metrics/novelty_metrics.py`) provides `build_gt` and `compute_metrics`. Below is a complete snippet:

```python
import json, sys

# Reuse the shared retrieval metrics provided in the monorepo
sys.path.insert(0, "../common/metrics")
from novelty_metrics import build_gt, compute_metrics  # noqa: E402

# Load the JSONL file directly from this repository
with open("data/test.jsonl", "r", encoding="utf-8") as f:
    dataset = [json.loads(line) for line in f]

print(f"Total samples: {len(dataset)}")

# Example: evaluate a hypothetical search system
for sample in dataset:
    gt = build_gt(sample, collapsed=False)  # GT = pn_x ∪ pn_family_x
    # query_text = fetch_specification(sample["pn"])   # ← user-provided
    # result_list = your_search_system(query_text)
    # metrics = compute_metrics(gt, result_list, k_values=[1, 3, 5, 10, 20, 50, 100])
    # → {"top@1": 0/1, "top@5": 0/1, ..., "recall@100": 0.0-1.0, ...}
```

> For a one-command metric computation, run `python ../common/metrics/novelty_metrics.py --dataset data/test.jsonl --results your_results.json` — no retrieval is performed; the script only scores a ranked-results file you provide. Pass `--collapsed` if your results are grouped by patent family (uses `pn_x_family ∪ pn_family_x_family` as GT); omit for non-collapsed individual-patent results. By default the script runs in **strict / leaderboard mode** — any sample missing from your results is scored 0; pass `--allow-partial` only for local debugging.

## Baseline Results

The following baseline results are from PatSnap's internal novelty search system, evaluated in December 2025 **on the internal full cross-jurisdiction family-expanded subset (340 samples)** with family-collapsed GT.

| Metric | Value |
|--------|-------|
| top@1 | 12% |
| top@3 | 28% |
| top@5 | 36% |
| top@10 | 48% |
| top@20 | 62% |
| top@50 | 74% |
| top@100 | 84% |
| Recall@100 | 36% |

> ℹ️ **Baseline scope note.** These figures were measured on the **internal full family-expanded subset (340 samples)** — not on the present 569-sample public release. The current public release combines a 50% sample of that family-expanded subset (170 samples) with 399 single-jurisdiction non-expanded samples, so direct comparison to this baseline is not appropriate. Updated baselines for the public release will be published in a future iteration.

## Limitations

- **Retrieval-only Bench**: This dataset evaluates the search/retrieval step only. It does not cover patent analysis, invalidity determination, or freedom-to-operate assessments.
- **GT based on examiner citations**: Ground truth is based on references cited by patent examiners during prosecution. This does not represent an exhaustive set of all relevant prior art — examiners may not cite every pertinent document.
- **Temporal snapshot**: The dataset reflects examination outcomes up to its collection date. Newer prior art published after examination is not included.
- **Language bias**: Only Chinese and English patents are included. Performance on other languages (Japanese, Korean, German, etc.) cannot be inferred from this Bench.
- **Query text not bundled**: Users must obtain the specification text of each `pn` from public patent databases (see *How to Use the Query* above).
- **Public release is a 50% sample**: The internal full evaluation set is retained for internal validation; the public release deliberately preserves the per-track distribution at 50%.

## Citation

If you use this dataset, please cite both the dataset and the methodology paper:

```bibtex
@article{zhang2025novelty,
  title   = {Research on Evaluation Methods for Patent Novelty Search Systems and Empirical Analysis},
  author  = {Zhang, Shu and Zhang, LiSha and Duan, Kai and Sun, XinKai},
  journal = {arXiv preprint arXiv:2508.17782},
  year    = {2025},
  url     = {https://arxiv.org/abs/2508.17782}
}

@dataset{patsnap_novelty_search_bench_2026,
  title  = {PatSnap Novelty Search Bench},
  author = {PatSnap},
  year   = {2026},
  url    = {https://github.com/patsnap/patent-bench/tree/main/novelty-search-bench},
  note   = {Open dataset accompanying Zhang et al. 2025 (arXiv:2508.17782)}
}
```

## License

This dataset is released under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). It may be used for research and non-commercial evaluation purposes.

## Try the Production System

Experience the **PatSnap Novelty Search AI Agent** — the commercial system referenced in this Bench. It delivers end-to-end patent novelty search with cross-jurisdiction family expansion, multi-language semantic alignment, and examiner-grade X-reference retrieval.

🔗 **Try it now**: [PatSnap Novelty Search on Eureka](https://eureka.patsnap.com/ip/checking/?from=benchmark_github#/novelty-check-report)
