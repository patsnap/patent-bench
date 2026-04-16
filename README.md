# PatSnap Patent Bench

**English** | [中文](./README.zh.md)

> Open Patent Bench released by **PatSnap** for evaluating AI systems on patent-related tasks.

**Scope.** This repository provides:

1. **Evaluation datasets** — real-world, human-verified test cases from litigation, invalidation proceedings, or expert annotation.
2. **Reference metric implementations** — small, dependency-free Python scripts (Hit Rate, PRES, etc.).

It does **not** provide retrieval services, indexing pipelines, or an evaluation platform. Bring your own system, produce a ranked-results file, and use the metric scripts to score it.

## Available Bench

| Bench | Task | Samples | Status |
|---|---|:---:|---|
| [**design-fto-bench**](./design-fto-bench) | Cross-modal design-patent image retrieval | 91 | Released (v1.1) |
| *novelty-search-bench* | Prior-art retrieval for patent novelty search | — | Planned |
| *oar-bench* | Patent office action response (OAR) generation | — | Planned |
| *drafting-bench* | Patent application drafting | — | Planned |
| *…more patent Bench coming soon* | | | |

## Layout

```
patsnap/patent-bench
├── common/metrics/search_metrics.py   # Shared metric library + CLI
└── design-fto-bench/
    ├── README.md
    └── data/
        ├── test.jsonl
        └── image/
```

## Quick Start

```bash
git clone https://github.com/patsnap/patent-bench.git
cd patent-bench/design-fto-bench
# Read the sub-Bench README, run your system, then score:
python ../common/metrics/search_metrics.py \
    --dataset data/test.jsonl \
    --results your_results.json
```

## Try the Production Systems

Want to try the commercial systems referenced in the baselines? Visit **[PatSnap Eureka](https://eureka.patsnap.com/?from=benchmark_github)**.

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
