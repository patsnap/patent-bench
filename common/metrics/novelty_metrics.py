"""
novelty_metrics.py — Retrieval evaluation metrics for the Novelty Search Bench.

Each sample has two pairs of X-reference fields:
    pn_x                 — examiner-cited X references
    pn_x_family          — patent-family expansion of pn_x
    pn_family_x          — X references cited for the query patent's cross-jurisdiction family members
    pn_family_x_family   — patent-family expansion of pn_family_x

Ground truth is built as:
    collapsed=False  →  pn_x ∪ pn_family_x                  (system returns individual patents)
    collapsed=True   →  pn_x_family ∪ pn_family_x_family    (system returns family-collapsed results)

Provides two helpers used by the bench README:
    build_gt        — build the GT set for a sample
    compute_metrics — compute top@K and recall@K at multiple K cutoffs

Usage as a library:
    from novelty_metrics import build_gt, compute_metrics
    gt      = build_gt(sample, collapsed=False)
    metrics = compute_metrics(gt, ranked_list, k_values=[1, 3, 5, 10, 20, 50, 100])

Usage as a CLI (computes metrics over the bench JSONL):
    python novelty_metrics.py \\
        --dataset ../../novelty-search-bench/data/test.jsonl \\
        --results my_results.json \\
        [--collapsed]                        # use family-expanded GT
        [--k 1 3 5 10 20 50 100]             # cutoffs to report

Where `my_results.json` is:
    {"<sample_id>": ["<ranked PN 1>", "<ranked PN 2>", ...], ...}

No third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
from statistics import mean
from typing import Iterable


DEFAULT_K_VALUES = (1, 3, 5, 10, 20, 50, 100)


def _canonicalize_pn(pn) -> str:
    """Canonicalize a publication number for matching.

    Rules: strip whitespace, uppercase, drop empty strings.
    This is the canonical form used for GT construction and ranked-list dedup,
    so submissions that vary only in casing or surrounding whitespace match.
    """
    if pn is None:
        return ""
    return str(pn).strip().upper()


def _canonical_unique(seq: Iterable) -> list:
    """Canonicalize a sequence of PNs and drop duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for item in seq:
        c = _canonicalize_pn(item)
        if not c or c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out


def build_gt(sample: dict, collapsed: bool = False) -> set:
    """Build the Ground Truth set for one sample.

    Args:
        sample    : one record loaded from data/test.jsonl
        collapsed : if True, GT is the patent-family-expanded set
                    (use when your retrieval system returns results collapsed by patent family).
                    If False (default), GT is the per-patent set.

    Returns:
        set of canonicalized PN strings. Empty set if the sample has no X references.
    """
    if collapsed:
        raw = list(sample.get("pn_x_family", []) or []) + list(sample.get("pn_family_x_family", []) or [])
    else:
        raw = list(sample.get("pn_x", []) or []) + list(sample.get("pn_family_x", []) or [])
    return {_canonicalize_pn(pn) for pn in raw if _canonicalize_pn(pn)}


def compute_metrics(
    gt: set,
    ranked_list: Iterable,
    k_values: Iterable[int] = DEFAULT_K_VALUES,
) -> dict:
    """Compute top@K (hit indicator) and recall@K for a single sample.

    The ranked list is canonicalized + deduplicated before scoring, so duplicate
    PNs in the submission cannot inflate recall above 1.0.

    Args:
        gt          : Ground Truth set built via build_gt().
        ranked_list : ranked PNs returned by the retrieval system, most relevant first.
        k_values    : K cutoffs to report.

    Returns:
        dict of {"top@K": 0|1, "recall@K": float in [0,1]} for each K.
        Empty dict if GT is empty (sample is skipped).
    """
    if not gt:
        return {}
    ranked = _canonical_unique(ranked_list)
    out = {}
    for k in k_values:
        top_k_set = set(ranked[:k])
        hits = len(top_k_set & gt)  # set intersection — recall capped at 1.0 by construction
        out[f"top@{k}"] = 1 if hits > 0 else 0
        out[f"recall@{k}"] = hits / len(gt)
    return out


# ── CLI ────────────────────────────────────────────────────────────────────

def _aggregate(per_sample: list[dict], k_values: Iterable[int]) -> dict:
    """Aggregate per-sample metrics into corpus-level averages."""
    agg = {}
    for k in k_values:
        top_vals = [m[f"top@{k}"] for m in per_sample if f"top@{k}" in m]
        rec_vals = [m[f"recall@{k}"] for m in per_sample if f"recall@{k}" in m]
        agg[f"top@{k}"] = mean(top_vals) if top_vals else 0.0
        agg[f"recall@{k}"] = mean(rec_vals) if rec_vals else 0.0
    return agg


def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute top@K and recall@K for the Novelty Search Bench.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dataset", required=True, help="Path to novelty-search-bench/data/test.jsonl.")
    parser.add_argument("--results", required=True,
                        help='Ranked-results JSON: {"<sample_id>": ["<PN1>", "<PN2>", ...], ...}')
    parser.add_argument("--collapsed", action="store_true",
                        help="Use family-expanded GT (pn_x_family ∪ pn_family_x_family). "
                             "Pass this flag if your results are collapsed by patent family.")
    parser.add_argument("--k", type=int, nargs="+", default=list(DEFAULT_K_VALUES),
                        help=f"K cutoffs to report (default: {' '.join(map(str, DEFAULT_K_VALUES))}).")
    parser.add_argument("--allow-partial", action="store_true",
                        help="Debug flag: average only over samples that have a ranked list. "
                             "By default (strict / leaderboard mode) missing samples are scored 0, "
                             "so the denominator is the full set of samples with GT. NEVER pass "
                             "this flag when reporting numbers on a leaderboard.")
    args = parser.parse_args()

    with open(args.dataset, "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]
    with open(args.results, "r", encoding="utf-8") as f:
        raw_results = json.load(f)
    if not isinstance(raw_results, dict):
        raise SystemExit(
            f"Results file must be a JSON object mapping sample id → ranked list of PNs, "
            f"but the top-level value is {type(raw_results).__name__}."
        )
    # Schema fail-fast: each value must be a list of str/int. Without this check,
    # a stray string value would be silently iterated character-by-character and
    # the run would report 0.00% with no error — a silent failure that's lethal
    # for leaderboard reporting.
    results = {}
    for sid, ranked in raw_results.items():
        if not isinstance(ranked, list):
            raise SystemExit(
                f"Result for id={sid!r} must be a list of PN strings, got "
                f"{type(ranked).__name__}. Did you write a single string instead "
                f"of a one-element list? (e.g. \"id\": \"CN1234A\" → "
                f"\"id\": [\"CN1234A\"])"
            )
        bad = [(i, item) for i, item in enumerate(ranked) if not isinstance(item, (str, int))]
        if bad:
            i, item = bad[0]
            raise SystemExit(
                f"Result for id={sid!r}[{i}] must be str or int, got "
                f"{type(item).__name__} ({item!r}). All elements in a ranked list "
                f"must be PN strings (or ints)."
            )
        results[str(sid)] = list(ranked)

    per_sample, skipped_no_gt, missing_results = [], 0, 0
    for s in dataset:
        gt = build_gt(s, collapsed=args.collapsed)
        if not gt:
            skipped_no_gt += 1
            continue
        ranked = results.get(str(s["id"]))
        if ranked is None:
            missing_results += 1
            if args.allow_partial:
                continue
            # Strict mode: missing submission counts as 0 across all K cutoffs.
            ranked = []
        per_sample.append(compute_metrics(gt, ranked, k_values=args.k))

    agg = _aggregate(per_sample, args.k)

    mode = "PARTIAL (debug)" if args.allow_partial else "STRICT (leaderboard)"
    gt_mode = "collapsed (pn_x_family ∪ pn_family_x_family)" if args.collapsed else "non-collapsed (pn_x ∪ pn_family_x)"
    print(f"Dataset          : {args.dataset} ({len(dataset)} samples)")
    print(f"Results file     : {args.results}")
    print(f"GT mode          : {gt_mode}")
    print(f"Scoring mode     : {mode}")
    print(f"Samples scored   : {len(per_sample)}")
    print(f"Skipped (no GT)  : {skipped_no_gt}")
    print(f"Missing results  : {missing_results}" + ("  (scored 0)" if not args.allow_partial else "  (skipped)"))
    print("-" * 56)
    for k in args.k:
        print(f"top@{k:<4}        : {agg[f'top@{k}']*100:6.2f}%       recall@{k:<4}: {agg[f'recall@{k}']*100:6.2f}%")


if __name__ == "__main__":
    _main()
