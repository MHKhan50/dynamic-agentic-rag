"""Synthetic long-horizon agentic-RAG workflow simulator.

All probabilities are explicit simulator assumptions, not empirical estimates.
"""
from dataclasses import dataclass
import random

POLICIES = ("static_retrieval", "refresh_every_step", "confidence_refresh", "evidence_gated_recovery")

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
    episodes = []
    for i in range(n):
        episodes.append(Episode(
            episode_id=f"s{seed}_e{i:05d}", seed=seed, steps=steps,
            stale_rate=rng.choice((0.05, 0.10, 0.20, 0.30)),
            contradiction_rate=rng.choice((0.02, 0.05, 0.10, 0.20)),
            propagation_rate=rng.choice((0.25, 0.45, 0.65)),
        ))
    return episodes


def run_episode(ep, policy, rng):
    if policy not in POLICIES:
        raise ValueError(f"Unknown policy: {policy}")
    latent_error = False
    wrong_steps = propagated_errors = retrievals = recoveries = unnecessary_refreshes = 0
    trace = []
    for step in range(ep.steps):
        stale = rng.random() < ep.stale_rate
        contradiction = rng.random() < ep.contradiction_rate
        # Confidence is an imperfect proxy; stale evidence can look confident.
        confidence = 0.55 if (stale or contradiction) else 0.90
        refresh = False
        if policy == "refresh_every_step":
            refresh = True
        elif policy == "confidence_refresh":
            refresh = confidence < 0.75
        elif policy == "evidence_gated_recovery":
            refresh = stale or contradiction or latent_error

        if refresh:
            retrievals += 1
            if not (stale or contradiction or latent_error):
                unnecessary_refreshes += 1
            # A refresh resolves a stale/contradictory source with high but imperfect probability.
            if stale or contradiction:
                resolved = rng.random() < 0.90
                if resolved:
                    stale = contradiction = False
                    recoveries += 1
            if latent_error and rng.random() < 0.85:
                latent_error = False
                recoveries += 1

        local_error = stale or contradiction
        propagated_now = False
        if latent_error and rng.random() < ep.propagation_rate:
            local_error = True
            propagated_errors += 1
            propagated_now = True
        if local_error:
            wrong_steps += 1
        # A local error can poison later state. Recovery policy can detect it only at a later gate.
        latent_error = local_error
        trace.append({
            "episode_id": ep.episode_id, "seed": ep.seed, "policy": policy,
            "step": step + 1, "stale_evidence": int(stale),
            "contradiction": int(contradiction), "confidence": round(confidence, 4),
            "refresh_triggered": int(refresh), "step_error": int(local_error),
            "error_propagated": int(propagated_now),
        })
    return {
        "episode_id": ep.episode_id, "seed": ep.seed, "policy": policy,
        "steps": ep.steps, "wrong_steps": wrong_steps,
        "episode_success": int(wrong_steps == 0),
        "propagated_errors": propagated_errors, "retrievals": retrievals,
        "recoveries": recoveries, "unnecessary_refreshes": unnecessary_refreshes,
    }, trace
