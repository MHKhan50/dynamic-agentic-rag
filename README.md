# Dynamic Agentic RAG Reliability Benchmark (DAR-RB) v0.1.0

**Researcher:** Muzammal Hussain  
**Organisation:** Masmatix Innovations  
**Status:** Initial runnable synthetic benchmark / research prototype. Not a production agent and not evidence of a validated research result.

## Research question
Can evidence-aware retrieval and step-level revalidation reduce cascading errors in long-horizon agentic RAG workflows, while controlling retrieval overhead?

## Why this problem?
Agentic workflows combine planning, retrieval, tools, memory and multi-step execution. A stale, incomplete or contradictory intermediate result can be reused downstream and become a cascading failure. Recent work identifies reliability/error recovery, trajectory-level failure attribution and multi-agent error propagation as open challenges. See `docs/references.md`.

## Proposed contribution (to be tested, not assumed)
A benchmark and a lightweight **Evidence-Gated Recovery (EGR)** policy that checks evidence freshness and contradiction signals at decision boundaries, then selectively refreshes and revalidates a step before its result is allowed to propagate.

## What v0.1.0 contains
- Deterministic synthetic scenario generator.
- Four baseline policies: static retrieval, refresh every step, confidence-triggered refresh, and evidence-gated recovery.
- Per-step CSV traces and episode-level summary metrics.
- Unit tests and reproducible CLI.
- Experimental protocol and limitations.

## Important limitations
- Scenarios are synthetic simulations, not real-world user queries or production agent traces.
- The benchmark does not call an LLM, web search, vector database, or external tool.
- Results measure this simulator's assumptions only. They cannot establish real-world effectiveness or scientific novelty.
- Evidence freshness and contradiction are simulated signals. A later version must validate them against real retrieval corpora and agent traces.

## Requirements
Python 3.9+; standard library only.

## Run

```bash
python3 -m dynamic_rag.cli run --episodes 2000 --seeds 17 29 43 71 101 --out results
python3 -m unittest discover -s tests -v
```

Outputs:
- `results/episode_metrics.csv`
- `results/step_traces.csv`
- `results/summary.json`

## Reproducibility
The same version, episode count and seed list produce identical CSV/JSON outputs. Record Python version and exact command in any paper or release.

## Repository plan
This v0.1.0 is the first executable baseline. Subsequent work should add external datasets / trace adapters only after licensing, privacy and schema audits; then compare against established agentic RAG and trajectory-analysis baselines.
