# Dynamic Agentic RAG Reliability Benchmark (DAR-RB)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24167525.svg)](https://doi.org/10.5281/zenodo.24167525)

An agent that retrieves, reasons and passes its result to the next step can carry one stale or contradicted fact all the way to the end. This simulator asks a narrow question: if you can only afford to re-retrieve sometimes, when should you do it?

Everything is synthetic. Each episode is an 8-step workflow where retrieved evidence can be stale or contradicted, and an error at one step can carry into the next. No LLM, vector store or web search is called.

## What I found (v0.2.0)

5 seeds × 2,000 episodes; all four policies face the same evidence at every step.

| Policy | Episodes with no wrong step | Wrong steps per 100 | Retrievals per episode | Unneeded retrievals |
|---|---|---|---|---|
| static_retrieval | 17.2% | 34.3 | 0.00 | 0.00 |
| confidence_refresh | 49.7% | 11.3 | 3.63 | 2.06 |
| evidence_gated_recovery | 57.4% | 8.0 | 2.34 | 0.55 |
| refresh_every_step | 82.8% | 2.5 | 8.00 | 5.94 |

- Checking the evidence beat checking the confidence score: 7.6 points more clean episodes (paired 95% interval 6.6 to 8.7) with 1.29 fewer retrievals per episode.
- Re-retrieving every step was still the most accurate by a wide margin, at 3.4 times the retrievals of the gated policy. If retrieval is cheap, just refresh.
- The gated policy's lead depends on how good its checks are. With freshness recall at 0.8 it wins; at 0.7 it ties confidence refresh (48.9% against 49.7%); at 0.6 it loses (41.7%).

That last point is the real result: a gate is only worth having if its detectors are good, and in this simulator "good" means catching at least about 70 to 80% of stale evidence.

## How it works

- Each episode draws a stale rate (5 to 30%), a contradiction rate (2 to 20%) and a chance that an error carries into the next step (25 to 65%).
- Policies never see whether evidence is really stale. They see:
  - a confidence score that overlaps between good and bad evidence,
  - a freshness check (catches 80% of stale evidence, 5% false alarms),
  - a cross-source check (catches 70% of contradictions, 5% false alarms),
  - a consistency check (catches 60% of carried errors).
- A refresh fixes bad evidence 90% of the time and a carried error 85% of the time.

All of these numbers sit at the top of `dynamic_rag/simulator.py`.

## Run it

Python 3.9 or newer, standard library only.

```bash
python3 -m unittest discover -s tests -v
python3 -m dynamic_rag.cli run --episodes 2000 --seeds 17 29 43 71 101 --out results
python3 scripts/analysis.py
```

Results go to `results/episode_metrics.csv`, `results/step_traces.csv` and `results/summary.json`. The step traces file is large and not committed; the other two are this exact run.

## Limits

- The detector accuracies, fix rates and propagation rule are my assumptions.
- One workflow length (8 steps). Retrieval cost is a count, not time or tokens.
- Nothing here has been checked against real agent traces. That is the next step before any claim about real systems.

Background and references are in `docs/`.

## Citation

See `CITATION.cff`. MIT licence.
