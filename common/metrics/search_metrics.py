"""
search_metrics.py — General-purpose retrieval evaluation metrics.

Provides two core metrics:
  - hit_rate_at_k : Top-K Hit Rate (whether any target is retrieved)
  - calc_pres     : PRES score (Magdy & Jones 2010)

Usage as a library:
    from search_metrics import hit_rate_at_k, calc_pres

Usage as a CLI (computes metrics over a Bench's JSONL dataset):
    python search_metrics.py \\
        --dataset ../../design-fto-bench/data/test.jsonl \\
        --results my_results.json \\
        --match-mode pn --k 200 --N 200

Where `my_results.json` is:
    {"<sample_id>": ["<ranked id 1>", "<ranked id 2>", ...], ...}

No third-party dependencies.
"""
import argparse
import json
from statistics import mean


def hit_rate_at_k(target_ids, ranked_ids, k=200, match_fn=None):
    """
    Top-K Hit Rate: whether any id in target_ids appears in the top K of ranked_ids.

    Args:
        target_ids  : list, ground truth ID list
        ranked_ids  : list, candidate ID list sorted by relevance
        k           : int, cutoff position, default 200
        match_fn    : callable(a, b) -> bool, custom match function; default is exact match

    Returns:
        1     hit
        0     miss
        None  target_ids is empty, skip
    """
    if not target_ids:
        return None
    if match_fn is None:
        match_fn = lambda a, b: a == b

    cutoff = ranked_ids[:k]
    for t_id in target_ids:
        for c_id in cutoff:
            if match_fn(t_id, c_id):
                return 1
    return 0


def calc_pres(target_ids, ranked_ids, N=200, match_fn=None):
    """
    PRES score (Magdy & Jones 2010, with miss-penalty correction).

    Formula: PRES = 1 - (Σr_i - n(n+1)/2) / (n × N)
      - n     : total number of target documents
      - r_i   : rank (1-based) of the i-th target in ranked_ids
      - For targets not found within the top N, use an imputed rank of
        N + (n + R + 1) / 2 as per Eq.4 of the paper
      - n(n+1)/2 : the sum of ranks in the ideal case (all targets ranked first)

    Args:
        target_ids  : list, ground truth ID list
        ranked_ids  : list, candidate ID list sorted by relevance
        N           : int, maximum retrieval depth, default 200
        match_fn    : callable(a, b) -> bool, custom match function; default is exact match

    Returns:
        float in [0, 1], or None (when target_ids is empty)
    """
    n = len(target_ids)
    if n == 0:
        return None
    if match_fn is None:
        match_fn = lambda a, b: a == b

    cutoff = ranked_ids[:N]
    found_ranks = []
    for t_id in target_ids:
        for i, c_id in enumerate(cutoff):
            if match_fn(t_id, c_id):
                found_ranks.append(i + 1)
                break

    R = len(found_ranks)
    sum_ranks = sum(found_ranks)

    # Penalty rank for missed targets (Eq.4 of the paper)
    if n > R:
        missing = n - R
        avg_missing_rank = N + (n + R + 1) / 2.0
        sum_ranks += missing * avg_missing_rank

    ideal_sum = n * (n + 1) / 2
    pres = 1 - (sum_ranks - ideal_sum) / (n * N)
    return max(0.0, pres)


# ── CLI ────────────────────────────────────────────────────────────────────

def _main():
    parser = argparse.ArgumentParser(
        description="Compute Hit Rate @ K and PRES @ N for a Bench.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dataset", required=True, help="Path to the Bench test.jsonl.")
    parser.add_argument("--results", required=True,
                        help='Ranked-results JSON: {"<sample_id>": ["<id1>", "<id2>", ...], ...}')
    parser.add_argument("--match-mode", choices=["pn", "img-id"], default="pn",
                        help="Match against target_pns (default) or target_img_ids.")
    parser.add_argument("--k", type=int, default=200, help="Hit Rate cutoff (default: 200).")
    parser.add_argument("--N", type=int, default=200, help="PRES retrieval depth (default: 200).")
    args = parser.parse_args()

    with open(args.dataset, "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]
    with open(args.results, "r", encoding="utf-8") as f:
        results = {str(k): list(v) for k, v in json.load(f).items()}

    hit_vals, pres_vals, missing = [], [], 0
    target_field = "target_pns" if args.match_mode == "pn" else "target_img_ids"
    for s in dataset:
        ranked = results.get(str(s["id"]))
        if ranked is None:
            missing += 1
            continue
        hr = hit_rate_at_k(s[target_field], ranked, k=args.k)
        pr = calc_pres(s[target_field], ranked, N=args.N)
        if hr is not None:
            hit_vals.append(hr)
        if pr is not None:
            pres_vals.append(pr)

    print(f"Dataset          : {args.dataset} ({len(dataset)} samples)")
    print(f"Results file     : {args.results}")
    print(f"Match mode       : {args.match_mode}")
    print(f"Samples scored   : {len(hit_vals)}")
    print(f"Missing in input : {missing}")
    print("-" * 48)
    print(f"Hit Rate @ {args.k:<3}  : {(mean(hit_vals) if hit_vals else 0)*100:.2f}%")
    print(f"PRES      @ {args.N:<3}  : {mean(pres_vals) if pres_vals else 0:.3f}")


if __name__ == "__main__":
    _main()
