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

    # For other benches, override the GT field name explicitly:
    python search_metrics.py \\
        --dataset ../../<other-bench>/data/test.jsonl \\
        --results my_results.json \\
        --target-field <gt_field_name> --k 100 --N 100

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
                        help="Match against target_pns (default) or target_img_ids. "
                             "Ignored when --target-field is supplied.")
    parser.add_argument("--target-field",
                        help="Explicit name of the GT field in each sample (e.g. 'pn_x'). "
                             "Overrides --match-mode; lets the same script serve any bench whose "
                             "JSONL uses a different GT field name.")
    parser.add_argument("--k", type=int, default=200, help="Hit Rate cutoff (default: 200).")
    parser.add_argument("--N", type=int, default=200, help="PRES retrieval depth (default: 200).")
    parser.add_argument("--allow-partial", action="store_true",
                        help="Debug flag: average only over samples that have a ranked list. "
                             "By default (strict / leaderboard mode) missing samples are scored 0, "
                             "so the denominator is the full dataset size. NEVER pass this flag "
                             "when reporting numbers on a leaderboard.")
    args = parser.parse_args()

    with open(args.dataset, "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]
    with open(args.results, "r", encoding="utf-8") as f:
        raw_results = json.load(f)
    if not isinstance(raw_results, dict):
        raise SystemExit(
            f"Results file must be a JSON object mapping sample id → ranked list of IDs, "
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
                f"Result for id={sid!r} must be a list of ID strings, got "
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
                f"must be ID strings (or ints)."
            )
        results[str(sid)] = list(ranked)

    hit_vals, pres_vals, missing, no_gt = [], [], 0, 0
    if args.target_field:
        target_field = args.target_field
    else:
        target_field = "target_pns" if args.match_mode == "pn" else "target_img_ids"
    for s in dataset:
        ranked = results.get(str(s["id"]))
        if ranked is None:
            missing += 1
            if args.allow_partial:
                continue
            # Strict mode: missing submission counts as 0 — denominator stays len(dataset)
            ranked = []
        hr = hit_rate_at_k(s[target_field], ranked, k=args.k)
        pr = calc_pres(s[target_field], ranked, N=args.N)
        if hr is None:
            no_gt += 1
            continue
        hit_vals.append(hr)
        if pr is not None:
            pres_vals.append(pr)

    mode = "PARTIAL (debug)" if args.allow_partial else "STRICT (leaderboard)"
    print(f"Dataset          : {args.dataset} ({len(dataset)} samples)")
    print(f"Results file     : {args.results}")
    print(f"Match mode       : {args.match_mode}")
    print(f"Scoring mode     : {mode}")
    print(f"Samples scored   : {len(hit_vals)}")
    print(f"Skipped (no GT)  : {no_gt}")
    print(f"Missing in input : {missing}" + ("  (scored 0)" if not args.allow_partial else "  (skipped)"))
    print("-" * 48)
    print(f"Hit Rate @ {args.k:<3}  : {(mean(hit_vals) if hit_vals else 0)*100:.2f}%")
    print(f"PRES      @ {args.N:<3}  : {mean(pres_vals) if pres_vals else 0:.3f}")


if __name__ == "__main__":
    _main()
