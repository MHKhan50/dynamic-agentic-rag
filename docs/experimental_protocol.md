# Experimental Protocol v0.1.0

1. Run tests before experiments: `python3 -m unittest discover -s tests -v`.
2. Smoke test: `python3 -m dynamic_rag.cli run --episodes 20 --seeds 17 29 --out results_smoke`.
3. Baseline run: `python3 -m dynamic_rag.cli run --episodes 2000 --seeds 17 29 43 71 101 --out results_v010`.
4. Preserve the exact command, Python version, Git commit and output files.
5. Do not tune thresholds on the final test set. v0.1.0 uses fixed simulator logic and is not a learned system.
6. Repeat with workflow lengths 4, 8, 16, 32 and parameter sweeps after the baseline implementation is audited.
7. Report all policies, all seeds, uncertainty intervals and negative results. Do not select only favourable runs.
8. Clearly label all outputs synthetic. No external corpus is included in v0.1.0.

## Current simulator assumptions
- Default workflow length: 8 steps.
- Stale evidence rate sampled from {0.05, 0.10, 0.20, 0.30} per episode.
- Contradiction rate sampled from {0.02, 0.05, 0.10, 0.20} per episode.
- Error propagation probability sampled from {0.25, 0.45, 0.65} per episode.
- Refresh resolves stale/contradictory evidence with probability 0.90.
- Recovery clears a latent upstream error with probability 0.85.

These are deliberately configurable synthetic assumptions, not estimates from production data. Sensitivity analysis is mandatory.
