import csv
import json
import os
from collections import defaultdict
from .simulator import POLICIES, make_episodes, run_episode


def run_experiment(episodes_per_seed, seeds, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    episode_rows, trace_rows = [], []
    for seed in seeds:
        episodes = make_episodes(episodes_per_seed, seed)
        for ep in episodes:
            for policy in POLICIES:
                # every policy sees the same world draws, so episodes are paired
                row, traces = run_episode(ep, policy)
                episode_rows.append(row)
                trace_rows.extend(traces)
    write_csv(os.path.join(out_dir, "episode_metrics.csv"), episode_rows)
    write_csv(os.path.join(out_dir, "step_traces.csv"), trace_rows)
    grouped = defaultdict(list)
    for row in episode_rows:
        grouped[row["policy"]].append(row)
    summary = {}
    for policy, rows in grouped.items():
        n = len(rows)
        summary[policy] = {
            "episodes": n,
            "episode_success_rate": round(sum(r["episode_success"] for r in rows) / n, 6),
            "wrong_steps_per_100": round(100 * sum(r["wrong_steps"] for r in rows) / sum(r["steps"] for r in rows), 6),
            "propagated_errors_per_episode": round(sum(r["propagated_errors"] for r in rows) / n, 6),
            "retrievals_per_episode": round(sum(r["retrievals"] for r in rows) / n, 6),
            "recoveries_per_episode": round(sum(r["recoveries"] for r in rows) / n, 6),
            "unnecessary_refreshes_per_episode": round(sum(r["unnecessary_refreshes"] for r in rows) / n, 6),
        }
    payload = {"benchmark": "DAR-RB", "version": "0.2.0", "episodes_per_seed": episodes_per_seed,
               "seeds": list(seeds), "policies": list(POLICIES),
               "warning": "Synthetic simulator outputs only; not real-world performance claims.",
               "results": summary}
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    return payload


def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
