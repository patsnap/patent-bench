# Changelog

All notable changes to **PatSnap Patent Bench** will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows the release windows announced in the top-level [README](./README.md#roadmap).

## [Unreleased]

## [2026-06] — `novelty-search-bench` v1.0

### Added
- **`novelty-search-bench/`** — new sub-Bench for patent novelty (prior-art) search
  - **569 samples**, deliberately released at 50% of the internal full evaluation set
    - **170 cross-jurisdiction family-expanded samples (`type=family`)** — 50% of internal full (340)
    - **399 single-jurisdiction non-expanded samples (`type=public`)** — ~50% of internal full (≈800)
  - Cross-jurisdiction coverage: CN / US / EP / WO (PCT) / AU
  - Languages: English (55.0%), Chinese (45.0%)
  - IPC: all 8 sections (A–H), balanced
  - Ground truth: examiner-cited X-type references; for `type=family`, also includes X references cited by examiners of the query patent's cross-jurisdiction family members
  - Schema preserves four GT fields (`pn_x` / `pn_x_family` / `pn_family_x` / `pn_family_x_family`) so the same `build_gt` formula applies uniformly to both sample types
  - Bilingual README (`README.md` + `README.zh.md`)
  - Companion methodology paper: Zhang, Zhang, Duan, Sun — *Research on Evaluation Methods for Patent Novelty Search Systems and Empirical Analysis*, arXiv [2508.17782](https://arxiv.org/abs/2508.17782) (Aug 2025). The paper experiments on an early internal evaluation set of about 1,000 patents; that internal set has since been substantially expanded and cleaned up, and the present public release (569) is sampled from the latest internal version. A revised paper based on the current internal set is being prepared.
- **`common/metrics/novelty_metrics.py`** — new metric library for novelty retrieval
  - `build_gt(sample, collapsed=False)` builds the per-sample GT union (`pn_x ∪ pn_family_x`) or family-expanded GT (`pn_x_family ∪ pn_family_x_family`)
  - `compute_metrics(gt, ranked_list)` reports `top@K` and `recall@K` for K ∈ {1, 3, 5, 10, 20, 50, 100}
  - Standalone CLI: `python common/metrics/novelty_metrics.py --dataset ... --results ... [--collapsed]`
- **`CHANGELOG.md`** — this file

### Changed
- **Top-level `README.md` + `README.zh.md`** — portfolio expanded to **8 capabilities × 4 directions** with a published Roadmap. Coming-Soon Benches now show only task descriptions; sample counts and scope details are intentionally omitted until release.
- **`design-fto-bench/README.md` + `README.zh.md`** — added jurisdiction breakdown table and BibTeX citation block.

### Fixed
- **`common/metrics/search_metrics.py` — P0 partial-submission gaming vulnerability.**
  Previously, samples missing from a results file were silently skipped, so submitting 1 of 91 samples could report `Hit Rate @ 200 = 100%`. The script now defaults to **strict / leaderboard mode**: any missing sample is scored 0 and the denominator stays the full dataset size. Pass `--allow-partial` only for local debugging — never on a leaderboard.
- **`common/metrics/novelty_metrics.py` — P0 recall could exceed 100%.**
  Without ranked-list deduplication, GT = {A, B} with ranked = [A, A, A] returned `recall@3 = 1.5`. The script now canonicalizes (`str.strip().upper()`) and deduplicates the ranked list before scoring, then computes hits as a set intersection — recall is mathematically capped at 1.0.

### Added (CLI flags)
- `common/metrics/search_metrics.py` — `--target-field <name>` makes the same script reusable across Benches that ship their own GT field name (instead of the hard-coded `target_pns` / `target_img_ids`).
- `common/metrics/search_metrics.py` + `common/metrics/novelty_metrics.py` — `--allow-partial` debug flag (opt-in only).

## [2025-12] — `design-fto-bench` v1.1

### Added
- Initial public release of `design-fto-bench`: 91 cross-modal design-patent samples, 91 jurisdiction-stratified image directories under `data/image/`, English + Chinese READMEs, and `common/metrics/search_metrics.py` for Hit Rate @ K and PRES @ N.
- Top-level `README.md` + `README.zh.md`, `LICENSE` (CC BY-NC 4.0), and `.gitignore`.
