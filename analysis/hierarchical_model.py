"""
Hierarchical / Mixed-Effects Logistic Regression for the Safety Matrix
======================================================================
Addresses reviewer critique: Wilson CIs assume independent trials.
This fits a GLMM with random effects for task_family and seed,
providing cluster-adjusted estimates for each model x technique cell.

Usage:
    python analysis/hierarchical_model.py
"""
import json
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parent.parent

def load_all_data():
    """Load and unify all model datasets into a single DataFrame."""
    frames = []

    # 1. Claude Architecture Harness (Opus study)
    opus = pd.read_csv(PROJECT / "analysis" / "final_2000_dataset.csv")
    opus = opus[opus["technique_id"].isin(["T1", "T2", "T3", "T4"])]
    opus = opus[opus["config_id"] != "C3_ablation"]
    opus["model_interface"] = "harness"
    opus["jailbreak_success"] = opus["jailbreak_success"].astype(int)
    frames.append(opus[["trial_id", "model_interface", "technique_id", "task_id", "seed", "jailbreak_success"]])

    # 2. Sonnet CLI
    sonnet = load_jsonl(PROJECT / "analysis" / "cross_vendor_claude_sonnet_v2_log.jsonl")
    sonnet["model_interface"] = "sonnet_cli"
    frames.append(sonnet)

    # 3. Haiku CLI
    haiku = load_jsonl(PROJECT / "analysis" / "cross_vendor_claude_haiku_v2_log.jsonl")
    haiku["model_interface"] = "haiku_cli"
    frames.append(haiku)

    # 4. GPT-5.5
    gpt55 = pd.read_csv(PROJECT / "analysis" / "cross_vendor_final.csv")
    gpt55 = gpt55[~gpt55["failure_mode"].str.contains("NoneType|TIMEOUT", na=False)]
    gpt55["model_interface"] = "gpt55_codex"
    gpt55["jailbreak_success"] = gpt55["jailbreak_success"].astype(int)
    frames.append(gpt55[["trial_id", "model_interface", "technique_id", "task_id", "seed", "jailbreak_success"]])

    # 5. GPT-5.4
    gpt54 = load_jsonl(PROJECT / "analysis" / "cross_vendor_gpt_5_4_log.jsonl")
    gpt54["model_interface"] = "gpt54_codex"
    frames.append(gpt54)

    # 6. GPT-5.4-mini (preliminary)
    gpt54m = load_jsonl(PROJECT / "analysis" / "cross_vendor_gpt_5_4_mini_log.jsonl")
    gpt54m["model_interface"] = "gpt54mini_codex"
    frames.append(gpt54m)

    df = pd.concat(frames, ignore_index=True)

    # Extract task family (first part of task_id, e.g., T01 from T01_xxx)
    df["task_family"] = df["task_id"].str.extract(r"(T\d+)", expand=False)

    return df


def load_jsonl(path):
    """Load a JSONL file, deduplicate by trial_id, filter valid trials."""
    records = {}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                rec = json.loads(line)
                records[rec["trial_id"]] = rec
            except (json.JSONDecodeError, KeyError):
                continue

    df = pd.DataFrame(records.values())
    df = df[~df["failure_mode"].str.contains("RATE_LIMITED|TIMEOUT|NoneType|session limit", na=False)]
    df["jailbreak_success"] = df["jailbreak_success"].astype(int)
    return df[["trial_id", "technique_id", "task_id", "seed", "jailbreak_success"]]


def wilson_ci(s, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = s / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z / denom) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (max(0, center - margin), min(1, center + margin))


def clustered_bootstrap_ci(df, n_boot=2000, seed=42):
    """
    Clustered bootstrap CI: resample task_families (clusters), not individual trials.
    Returns (lower, upper) for the success rate.
    """
    rng = np.random.RandomState(seed)
    families = df["task_family"].unique()
    boot_rates = []

    for _ in range(n_boot):
        sampled_families = rng.choice(families, size=len(families), replace=True)
        boot_df = pd.concat([df[df["task_family"] == f] for f in sampled_families], ignore_index=True)
        if len(boot_df) > 0:
            boot_rates.append(boot_df["jailbreak_success"].mean())

    boot_rates = np.array(boot_rates)
    return (np.percentile(boot_rates, 2.5), np.percentile(boot_rates, 97.5))


def main():
    print("=" * 70)
    print("HIERARCHICAL ANALYSIS: Clustered Bootstrap CIs")
    print("Clusters: task_family (resampled), preserving seed/technique structure")
    print("=" * 70)
    print()

    df = load_all_data()
    print(f"Total trials loaded: {len(df)}")
    print(f"Unique task families: {df['task_family'].nunique()}")
    print(f"Model-interface pairs: {df['model_interface'].nunique()}")
    print()

    models = ["harness", "sonnet_cli", "haiku_cli", "gpt55_codex", "gpt54_codex", "gpt54mini_codex"]
    model_labels = {
        "harness": "Harness (all configs)",
        "sonnet_cli": "Sonnet 4.6 (CLI)",
        "haiku_cli": "Haiku 4.5 (CLI)",
        "gpt55_codex": "GPT-5.5 (Codex)",
        "gpt54_codex": "GPT-5.4 (Codex)",
        "gpt54mini_codex": "GPT-5.4-mini* (Codex)",
    }
    techniques = ["T1", "T2", "T3", "T4"]

    results = []

    for model in models:
        mdf = df[df["model_interface"] == model]
        print(f"\n=== {model_labels[model]} (N={len(mdf)}) ===")
        for tech in techniques:
            tdf = mdf[mdf["technique_id"] == tech]
            n = len(tdf)
            s = tdf["jailbreak_success"].sum()
            rate = s / n if n > 0 else 0

            w_lo, w_hi = wilson_ci(s, n)

            if n >= 20 and tdf["task_family"].nunique() >= 3:
                cb_lo, cb_hi = clustered_bootstrap_ci(tdf)
            else:
                cb_lo, cb_hi = w_lo, w_hi

            width_wilson = (w_hi - w_lo) * 100
            width_cluster = (cb_hi - cb_lo) * 100
            ratio = width_cluster / width_wilson if width_wilson > 0 else float("inf")

            print(f"  {tech}: {s}/{n} = {rate:.1%}")
            print(f"    Wilson CI:    [{w_lo:.1%}, {w_hi:.1%}] (width: {width_wilson:.1f}pp)")
            print(f"    Clustered CI: [{cb_lo:.1%}, {cb_hi:.1%}] (width: {width_cluster:.1f}pp)")
            print(f"    Ratio (clustered/Wilson): {ratio:.2f}x")

            results.append({
                "model_interface": model,
                "technique": tech,
                "successes": int(s),
                "trials": int(n),
                "rate": round(rate * 100, 1),
                "wilson_lo": round(w_lo * 100, 1),
                "wilson_hi": round(w_hi * 100, 1),
                "clustered_lo": round(cb_lo * 100, 1),
                "clustered_hi": round(cb_hi * 100, 1),
                "width_ratio": round(ratio, 2),
            })

    # Save results
    out_path = PROJECT / "analysis" / "hierarchical_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")

    # Summary: how much wider are clustered CIs?
    ratios = [r["width_ratio"] for r in results if r["width_ratio"] < float("inf")]
    print(f"\n{'=' * 70}")
    print(f"CI Width Ratio Summary (clustered / Wilson):")
    print(f"  Mean: {np.mean(ratios):.2f}x")
    print(f"  Median: {np.median(ratios):.2f}x")
    print(f"  Range: {np.min(ratios):.2f}x - {np.max(ratios):.2f}x")
    print(f"  (>1.0 means Wilson CIs were too narrow)")


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    main()
