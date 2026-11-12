"""Synthetic multi-step agentic RAG workflow.

Every probability here is an assumption I chose, not a measurement. The point of
v0.2 is that no policy reads the hidden truth: each one only sees noisy signals
(a confidence score, a freshness check, a cross-source check, a consistency check).
"""
from dataclasses import dataclass
import random

POLICIES = ("static_retrieval", "refresh_every_step", "confidence_refresh", "evidence_gated_recovery")

CONFIDENCE_THRESHOLD = 0.75
FRESHNESS_RECALL, FRESHNESS_FALSE_ALARM = 0.80, 0.05      # timestamp check on retrieved evidence
CROSSCHECK_RECALL, CROSSCHECK_FALSE_ALARM = 0.70, 0.05    # second source disagrees
CONSISTENCY_RECALL = 0.60                                  # step output disagrees with earlier state
REFRESH_FIXES_SOURCE = 0.90
REFRESH_FIXES_CARRIED = 0.85


@dataclass
class Episode:
    episode_id: str
    seed: int
    steps: int
    stale_rate: float
    contradiction_rate: float
    propagation_rate: float


def make_episodes(n, seed, steps=8):
    rng = random.Random(seed)
    return [Episode(episode_id=f"s{seed}_e{i:05d}", seed=seed, steps=steps,
                    stale_rate=rng.choice((0.05, 0.10, 0.20, 0.30)),
                    contradiction_rate=rng.choice((0.02, 0.05, 0.10, 0.20)),
                    propagation_rate=rng.choice((0.25, 0.45, 0.65)))
            for i in range(n)]


def world_draws(ep, step):
    """All random numbers for one step, shared by every policy so comparisons are paired."""
    rng = random.Random(f"{ep.episode_id}|{step}")
    return [rng.random() for _ in range(9)]


def run_episode(ep, policy, rng=None):
    """`rng` is accepted for backward compatibility and ignored; draws come from world_draws."""
    if policy not in POLICIES:
        raise ValueError(f"Unknown policy: {policy}")
    carried_error = False
    wrong_steps = propagated_errors = retrievals = recoveries = unnecessary_refreshes = 0
    trace = []
    for step in range(ep.steps):
        u = world_draws(ep, step)
        stale = u[0] < ep.stale_rate
        contradiction = u[1] < ep.contradiction_rate
        bad = stale or contradiction
        # bad evidence often still looks confident, good evidence sometimes does not
        confidence = 0.40 + 0.50 * u[2] if bad else 0.60 + 0.40 * u[2]
        flagged_stale = u[3] < (FRESHNESS_RECALL if stale else FRESHNESS_FALSE_ALARM)
        flagged_conflict = u[4] < (CROSSCHECK_RECALL if contradiction else CROSSCHECK_FALSE_ALARM)
        flagged_carried = carried_error and u[5] < CONSISTENCY_RECALL

        if policy == "refresh_every_step":
            refresh = True
        elif policy == "confidence_refresh":
            refresh = confidence < CONFIDENCE_THRESHOLD
        elif policy == "evidence_gated_recovery":
            refresh = flagged_stale or flagged_conflict or flagged_carried
        else:
            refresh = False

        if refresh:
            retrievals += 1
            if not (bad or carried_error):
                unnecessary_refreshes += 1
            if bad and u[6] < REFRESH_FIXES_SOURCE:
                stale = contradiction = bad = False
                recoveries += 1
            if carried_error and u[7] < REFRESH_FIXES_CARRIED:
                carried_error = False
                recoveries += 1

        step_error = bad
        propagated_now = carried_error and u[8] < ep.propagation_rate
        if propagated_now:
            step_error = True
            propagated_errors += 1
        wrong_steps += step_error
        carried_error = step_error
        trace.append({
            "episode_id": ep.episode_id, "seed": ep.seed, "policy": policy, "step": step + 1,
            "stale_evidence": int(stale), "contradiction": int(contradiction),
            "confidence": round(confidence, 4), "refresh_triggered": int(refresh),
            "step_error": int(step_error), "error_propagated": int(propagated_now),
        })
    return {
        "episode_id": ep.episode_id, "seed": ep.seed, "policy": policy,
        "steps": ep.steps, "wrong_steps": wrong_steps, "episode_success": int(wrong_steps == 0),
        "propagated_errors": propagated_errors, "retrievals": retrievals,
        "recoveries": recoveries, "unnecessary_refreshes": unnecessary_refreshes,
    }, trace
