"""
V2 adequacy stress test: SYNTHETIC DATA ONLY.

Per docs/CONSTRAINT_ACCUMULATION_V2_BLOCKER_AUDIT.md Phase 5. Tests
whether the already-frozen/reused machinery (GroupKFold construction,
logistic regression fitting, log-loss computation, conditional
permutation, Holm correction) remains MECHANICALLY STABLE across a
predeclared grid of minority-class (positive) counts -- NOT an estimate of
whether V2 will find a real effect. Predictor-outcome relationships in
every synthetic dataset are independently/randomly generated -- this
module NEVER uses real corpus predictor/outcome relationships, and NEVER
loads data/generated/lineara_extracted.json.

The minority-count grid (10, 15, 20, 25, 30, 40) was fixed before checking
any result -- it is not centered on or optimized around the real V2
count (21).
"""
from __future__ import annotations

import random
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import constraint_accumulation as ca  # noqa: E402
import run_constraint_accumulation as rca  # noqa: E402

MINORITY_GRID = (10, 15, 20, 25, 30, 40)   # predeclared, not centered on 21
SYNTHETIC_N = 219        # matches V2's real population size, structure only
SYNTHETIC_TABLETS = 89   # matches V2's real tablet count, structure only


def make_synthetic_dataset(n_positive: int, seed: int,
                            n_total: int = SYNTHETIC_N,
                            n_tablets: int = SYNTHETIC_TABLETS) -> list:
    """Independently-generated synthetic FeatureRow-like objects. Every
    predictor value and the Y label are drawn independently at random --
    NO real predictor-outcome relationship is encoded. `numeric_value` is
    drawn from a log-uniform-ish spread so log2_magnitude is well-defined
    and varied."""
    rng = random.Random(seed)
    sites = ["Haghia Triada", "OTHER"]
    supports = ["Tablet", "OTHER"]
    positions = ["FIRST", "SECOND", "THIRD_OR_LATER"]
    commodities = ["LIQUID", "DRY"]

    tablet_ids = [f"T{i}" for i in range(n_tablets)]
    # assign each row to a tablet round-robin-ish, independent of Y
    row_tablets = [tablet_ids[i % n_tablets] for i in range(n_total)]
    rng.shuffle(row_tablets)

    y = [1] * n_positive + [0] * (n_total - n_positive)
    rng.shuffle(y)

    rows = []
    for i in range(n_total):
        rows.append(ca.FeatureRow(
            tablet_id=row_tablets[i], index=0,
            site_block=rng.choice(sites), support_block=rng.choice(supports),
            position_bucket=rng.choice(positions), commodity_class=rng.choice(commodities),
            numeric_value=float(rng.randint(1, 300)), numeric_bin="SMALL",
            fraction_present=bool(y[i]),
        ))
    return rows


def stability_check(n_positive: int, seed: int, B: int = 50) -> dict:
    """Runs the full frozen pipeline (reused unchanged from
    run_constraint_accumulation.run_full_pipeline) on one synthetic
    dataset at reduced B (engineering speed only), with adequacy
    thresholds relaxed via the harness's own test-only override
    parameters (never used against real data) so the stress test isn't
    blocked by the very thresholds under audit."""
    rows = make_synthetic_dataset(n_positive, seed)
    result = rca.run_full_pipeline(
        rows, seed=seed, B=B,
        min_total_n=50, min_tablets=20, min_positive=5, min_negative=5,
    )
    return result


def run_grid(seed_base: int = 1) -> dict:
    """Runs stability_check across MINORITY_GRID, one seed per grid point
    (seed = seed_base + n_positive, deterministic and reproducible)."""
    out = {}
    for m in MINORITY_GRID:
        out[m] = stability_check(m, seed=seed_base + m)
    return out


if __name__ == "__main__":
    results = run_grid()
    for m, r in results.items():
        print(m, "->", r.get("status"), "| step_verdicts:", r.get("step_verdicts"))
