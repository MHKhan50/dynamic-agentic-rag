# Research Proposal — DAR-RB

## Working title
**Evidence-Gated Recovery for Long-Horizon Agentic RAG: Reducing Cascading Errors under Stale and Contradictory Retrieval**

## Problem
Agentic RAG systems repeatedly retrieve information, transform it into intermediate state, and pass that state to later reasoning or tools. If an early retrieval is stale, incomplete or contradicted by newer evidence, downstream steps may treat the error as established fact. This can degrade task success and make failure attribution difficult.

## Research question
Across controlled long-horizon tasks, does selective evidence revalidation and recovery reduce cascading errors more efficiently than static retrieval, unconditional refresh, or confidence-only refresh?

## Hypotheses
- H1: Evidence-gated recovery will reduce wrong intermediate steps relative to static retrieval.
- H2: It will use fewer retrieval operations than refreshing at every step.
- H3: Confidence-only refresh will miss some stale/contradictory evidence when the confidence proxy is miscalibrated.
- H4: Gains will vary with workflow length, stale-evidence prevalence, contradiction rate and error-propagation probability.

These are hypotheses to test, not findings.

## Proposed method
At each critical decision boundary, maintain an evidence record with source identity, timestamp/freshness, claim support and contradiction status. Permit a result to propagate only if evidence checks pass. If checks fail, selectively retrieve again, compare evidence, revise the intermediate state, and record whether recovery succeeded. If evidence remains unresolved, abstain or request human review in a later implementation.

## Baselines
1. Static retrieval: retrieve once and reuse.
2. Refresh every step: unconditional retrieval.
3. Confidence refresh: refresh only below a confidence threshold.
4. Evidence-gated recovery: refresh when a freshness check, a cross-source check or a consistency check fires. In v0.2 these checks are imperfect (recall 0.8, 0.7 and 0.6) and no policy sees the hidden stale or contradiction state.

## Evaluation
Primary: episode success rate, wrong intermediate steps per 100 steps, propagated errors per episode.  
Efficiency: retrievals per episode, recoveries per episode, unnecessary refreshes.  
Later real-system evaluation should add wall-clock latency, token/API cost, task-quality grading, calibration, abstention quality and human-review burden.

## Experimental design
Use multiple seeds, controlled workflow lengths (e.g. 4, 8, 16, 32), and a factorial sweep over stale-evidence rate, contradiction rate and propagation probability. Keep scenario IDs and source documents disjoint across train/dev/test if any learned detector is introduced. Compare paired episodes and report confidence intervals and effect sizes. Include ablations for freshness-only, contradiction-only and combined gating.

## Novelty gate
Do not claim novelty until a systematic comparison is completed against agentic RAG, retrieval freshness, self-correction, trajectory analysis, process supervision, and agent recovery literature. A defensible contribution may be the specific combination of evidence provenance/freshness/contradiction checks with selective recovery, measured jointly for reliability and retrieval overhead, if prior-art review confirms it is not already established.
