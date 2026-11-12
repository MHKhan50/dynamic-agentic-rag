"""Paired differences and detector-quality sensitivity behind the README numbers.

    python3 scripts/analysis.py --metrics results/episode_metrics.csv
"""
import argparse
import csv
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dynamic_rag.simulator as sim  # noqa: E402


def paired(rows, a, b, metric):
    by = {(r["episode_id"], r["policy"]): float(r[metric]) for r in rows}
    ids = sorted({r["episode_id"] for r in rows})
    diffs = [by[(i, a)] - by[(i, b)] for i in ids]
    mean = statistics.mean(diffs)
    half = 1.96 * statistics.stdev(diffs) / math.sqrt(len(diffs))
    return mean, mean - half, mean + half


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default="results/episode_metrics.csv")
    parser.add_argument("--seeds", type=int, nargs="+", default=[17, 29, 43, 71, 101])
    parser.add_argument("--episodes", type=int, default=2000)
    args = parser.parse_args()

    rows = list(csv.DictReader(open(args.metrics, encoding="utf-8")))
    for other in ("confidence_refresh", "refresh_every_step", "static_retrieval"):
        for metric in ("episode_success", "retrievals"):
            m, lo, hi = paired(rows, "evidence_gated_recovery", other, metric)
            print("gated - %-20s %-16s %+.4f  [%+.4f, %+.4f]" % (other, metric, m, lo, hi))

    # How good do the checks have to be? Lower all three recalls together.
    episodes = [e for s in args.seeds for e in sim.make_episodes(args.episodes, s)]
    print("\nfreshness recall | gated success | gated retrievals | confidence success")
    conf = statistics.mean(sim.run_episode(e, "confidence_refresh")[0]["episode_success"] for e in episodes)
    for recall in (0.8, 0.7, 0.6, 0.4):
        sim.FRESHNESS_RECALL, sim.CROSSCHECK_RECALL, sim.CONSISTENCY_RECALL = recall, recall - 0.1, recall - 0.2
        out = [sim.run_episode(e, "evidence_gated_recovery")[0] for e in episodes]
        print("%.1f              | %.3f         | %.2f             | %.3f" % (
            recall, statistics.mean(r["episode_success"] for r in out),
            statistics.mean(r["retrievals"] for r in out), conf))


if __name__ == "__main__":
    main()
