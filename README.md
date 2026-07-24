# PatSnap Patent Bench

**English** | [中文](./README.zh.md)

> Open Patent Bench released by **PatSnap** for evaluating AI systems on patent-related tasks.

PatSnap Patent Bench is a growing portfolio of **task-specific evaluation datasets and reference metric implementations** for the patent domain. Each sub-Bench targets one real-world patent workflow — prior-art search, FTO, drafting, examination response, translation, claim charting — with human-verified samples drawn from real examinations, litigations, invalidation proceedings, or expert annotation.

## What's Inside

1. **Evaluation datasets** — real-world, human-verified test cases. Each sub-Bench ships a JSONL file with a stable, documented schema.
2. **Reference metric implementations** — small, dependency-free Python scripts (Hit Rate, PRES, MRR, etc.).
3. **A shared evaluation flow** — run your own system to produce results (a ranked list of candidate IDs for retrieval, a model output for generation), save them as JSON, then score them with the scripts under `common/metrics/`.

This repository does **not** provide retrieval services, indexing pipelines, generation backends, or an evaluation platform. It is system-agnostic by design.

## Bench Portfolio

PatSnap Patent Bench covers **8 capabilities across 4 directions**.

### Retrieval & Risk Analysis

| Bench | Task | Samples | Status |
|---|---|:---:|---|
| [**design-fto-bench**](./design-fto-bench) | Cross-modal design-patent image retrieval (product photo ↔ patent drawing) | 91 | **Released v1.1** · also on [🤗 HF](https://huggingface.co/datasets/PatSnap/design-fto-bench) |
| [**novelty-search-bench**](./novelty-search-bench) | Prior-art retrieval for patent novelty search (examiner-cited X references, with cross-jurisdiction family-expanded + single-jurisdiction non-expanded tracks) | 569 | **Released v1.0** · also on [🤗 HF](https://huggingface.co/datasets/PatSnap/novelty-search-bench) |
| *fto-bench* | Patent freedom-to-operate retrieval (derived from real litigation + FTO reports) | — | Coming Soon (Aug 2026) |

> 💡 The **Hugging Face mirrors** ship a self-contained version: `novelty-search-bench` bundles every query patent's full `description` text, and `design-fto-bench` embeds all 91 query images as decoded PIL Image objects — `load_dataset(...)` gives you everything you need to run an end-to-end evaluation, no external lookup required.

### Drafting & Examination Response

| Bench | Task | Samples | Status |
|---|---|:---:|---|
| *oar-bench* | Office-action response (OAR) generation | — | Coming Soon (Aug 2026) |
| *drafting-bench* | Full patent application drafting | — | Coming Soon (Sep 2026) |
| *invention-disclosure-bench* | Invention-disclosure drafting from user-supplied technical material | — | Coming Soon (Oct 2026) |

### Translation

| Bench | Task | Samples | Status |
|---|---|:---:|---|
| [**patent-translation**](./patent-translation) | Patent translation quality (CN↔EN), covering terminology accuracy/consistency, patent writing conventions, hallucination, and omission | 2,498 | **Released v1.0** |

### Feature Comparison

| Bench | Task | Samples | Status |
|---|---|:---:|---|
| *claim-charting-bench* | Claim-feature alignment across patent pairs and invention disclosures | — | Coming Soon (Aug 2026) |

> ℹ️ Sample counts and scope for **Coming Soon** Benches are intentionally omitted — the final dataset composition may change before release. Each Bench will document its definitive sample count, GT format, and scoring protocol in its own `README.md` at release time.

All sub-Benches cover at least **CN / US / EP** jurisdictions and **CN / EN** languages where applicable, with IPC distribution spanning sections A–H.

## Roadmap

| Window | New Releases |
|---|---|
| **Jun 2026** | `novelty-search-bench` |
| **Jul 2026** | `patent-translation` |
| **Aug 2026** | `fto-bench`, `oar-bench`, `claim-charting-bench` |
| **Sep 2026** | `drafting-bench` |
| **Oct 2026** | `invention-disclosure-bench` |

Dates above are intended monthly release windows. Check the [GitHub Releases page](https://github.com/patsnap/patent-bench/releases) for actuals, and [`CHANGELOG.md`](./CHANGELOG.md) for the full per-release diff.

## Layout

```
patsnap/patent-bench
├── common/metrics/search_metrics.py      # Shared metric library + CLI
├── design-fto-bench/                     # Released v1.1
│   ├── README.md
│   └── data/{test.jsonl, image/}
├── novelty-search-bench/                 # Released v1.0
│   ├── README.md
│   └── data/test.jsonl
├── patent-translation/                   # Released v1.0
│   ├── README.md
│   └── data/test_dataset.jsonl
└── <other-bench>/                        # Coming Soon, per Roadmap
    ├── README.md
    └── data/...
```

Every sub-Bench follows the same skeleton: a self-contained `README.md` describing the dataset schema and scoring protocol, plus a `data/` directory.

## Quick Start

```bash
git clone https://github.com/patsnap/patent-bench.git

# Design FTO — cross-modal image retrieval
cd patent-bench/design-fto-bench
python ../common/metrics/search_metrics.py \
    --dataset data/test.jsonl \
    --results your_results.json

# Novelty Search — prior-art retrieval
# Uses novelty_metrics.py (NOT search_metrics.py) because the Novelty schema
# carries pn_x / pn_x_family / pn_family_x / pn_family_x_family rather than
# a single target_pns field. novelty_metrics.py builds the GT union for you
# and handles cross-jurisdiction family expansion via the --collapsed flag.
cd ../novelty-search-bench
python ../common/metrics/novelty_metrics.py \
    --dataset data/test.jsonl \
    --results your_results.json
    # add --collapsed if your retrieval results are grouped by patent family

# Patent Translation — CN<->EN generation quality
cd ../patent-translation
python ../common/metrics/translation_metrics.py \
    --input your_results.jsonl \
    --direction cn2en \
    --output result_cn2en.json
```

> ⚠️ **Strict scoring is the default.** Both metric scripts score any
> sample missing from your results file as 0, so the denominator is always
> the full dataset size — submitting only a subset can't inflate your
> numbers. Use `--allow-partial` only when debugging locally; any number
> you put on a leaderboard must come from the default strict mode.

Read each sub-Bench's `README.md` for its evaluation protocol, GT semantics, and supported metrics before running.

## Evaluation Paradigm

All retrieval-style sub-Benches share a uniform four-step interface:

1. **Iterate** the sub-Bench's `data/test.jsonl`, pulling the query (PN, image, or text) from each record.
2. **Run** your retrieval / generation system on the query and produce either a ranked list of candidate IDs (retrieval) or a model output (generation).
3. **Serialize** the output to a JSON file keyed by sample `id`.
4. **Score** with the metric script in `common/metrics/` (or the sub-Bench's own metrics) to obtain Hit Rate @ K, Recall @ K, PRES, MRR, or task-specific scores.

This keeps every Bench reproducible and system-agnostic — swap in any retrieval engine, LLM, or hybrid stack without touching the data or the metric logic.

## Try the Production Systems

Want to compare against the commercial systems referenced in the baselines? Visit **[PatSnap Eureka](https://eureka.patsnap.com/?from=benchmark_github)**.

## Contributing

We welcome:

- **Result submissions** — open a GitHub issue with your scoring run on any released Bench; notable results may be added to the sub-Bench README.
- **Methodology feedback** — issues / PRs that critique the protocol, surface data-quality problems, or propose extensions.
- **Cross-listings** — if you maintain a public patent-domain evaluation dataset and would like it cross-referenced from here, open an issue.

We do **not** currently accept PRs that add proprietary data, internal scoring pipelines, or vendor-specific baselines.

## License

- **Data**: [CC BY-NC 4.0](./LICENSE)
- **Code**: Apache-2.0 (see source headers)

## Citation

```bibtex
@misc{patsnap_patent_bench,
  title  = {PatSnap Patent Bench: Open Evaluations for Patent AI Systems},
  author = {PatSnap},
  year   = {2026},
  url    = {https://github.com/patsnap/patent-bench}
}
```

### Companion Papers

Sub-Benches accompanied by a published methodology paper — please also cite the paper when using the corresponding dataset:

| Sub-Bench | Paper | arXiv |
|---|---|---|
| `novelty-search-bench` | Zhang et al. 2025 — *Research on Evaluation Methods for Patent Novelty Search Systems and Empirical Analysis* | [2508.17782](https://arxiv.org/abs/2508.17782) |

> ⚠️ **`novelty-search-bench` paper note.** The dataset has been updated since the paper (arXiv, Aug 2025) was published; a revised paper is in preparation.
