"""
Synthetic end-to-end tests for src/run_constraint_accumulation_v2.py.

Every fixture here is hand-constructed and synthetic. NONE of these tests
load or touch data/generated/lineara_extracted.json.

Scope note: every broad-verdict combination (M2-only, M3-only, M4-only,
M2+M3, M3+M4, M2+M4, all three, none) is already exhaustively unit-tested
against constraint_accumulation_v2.classify_broad_verdict directly in
tests/test_constraint_accumulation_v2.py -- that logic is not duplicated
here. This file instead proves the HARNESS correctly wires real (small,
synthetic) pipeline output through that already-tested logic -- via a
representative set of end-to-end scenarios (adequate/inadequate paths,
one clean single-block-significant case, one clean null case, one
NOT_EVALUABLE case) -- plus orchestration concerns (fold construction,
Holm family, serialization, provenance, determinism) that only exist at
the harness level.

B is deliberately reduced from the frozen 2000 for test runtime only.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import constraint_accumulation as ca  # noqa: E402
import constraint_accumulation_v2 as v2  # noqa: E402
import run_constraint_accumulation_v2 as rca2  # noqa: E402

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FREEZE_SHA = "931fd5905ec3c67f526b108452ec9c355c1b0048"

ADEQUACY_OVERRIDES = dict(min_total_n=50, min_tablets=20)


def _v2row(tablet_id, site, support, position, commodity, numeric_value, y):
    return v2.V2Row(
        tablet_id=tablet_id, site_block=site, support_block=support,
        position_bucket=position, commodity_class=commodity,
        whole_component_magnitude=v2.log2_magnitude(numeric_value),
        fraction_present=y,
    )


def _null_rows(n_tablets=60, rows_per_tablet=2, seed=1, base_rate=0.3):
    """No predictor carries any real signal -- Y assigned independently."""
    rng = random.Random(seed)
    sites = ["Haghia Triada", "OTHER"]
    supports = ["Tablet", "OTHER"]
    positions = ["FIRST", "SECOND", "THIRD_OR_LATER"]
    commodities = ["LIQUID", "DRY"]
    rows = []
    for t in range(n_tablets):
        tid = f"T{t}"
        for _ in range(rows_per_tablet):
            rows.append(_v2row(
                tid, rng.choice(sites), rng.choice(supports),
                rng.choice(positions), rng.choice(commodities),
                float(rng.randint(1, 300)), rng.random() < base_rate,
            ))
    return rows


def _magnitude_signal_rows(n_tablets=60, rows_per_tablet=2, seed=1):
    """Y strongly (near-deterministically) determined by magnitude
    (large integer_value -> Y=1), independent of every other predictor --
    isolates M4 as the only genuinely informative block."""
    rng = random.Random(seed)
    sites = ["Haghia Triada", "OTHER"]
    supports = ["Tablet", "OTHER"]
    positions = ["FIRST", "SECOND", "THIRD_OR_LATER"]
    commodities = ["LIQUID", "DRY"]
    rows = []
    for t in range(n_tablets):
        tid = f"T{t}"
        for _ in range(rows_per_tablet):
            val = rng.randint(1, 300)
            true_signal = val >= 150
            y = true_signal if rng.random() < 0.9 else (not true_signal)
            rows.append(_v2row(
                tid, rng.choice(sites), rng.choice(supports),
                rng.choice(positions), rng.choice(commodities),
                float(val), y,
            ))
    return rows


# --------------------------------------------------------------------------- adequacy / INCONCLUSIVE paths
def test_inconclusive_when_coarse_screen_fails():
    rows = _null_rows(n_tablets=5, rows_per_tablet=1)
    result = rca2.run_full_pipeline_v2(rows, seed=1, B=10)  # default (frozen) thresholds
    assert result["status"] == "INCONCLUSIVE"
    assert "feasibility" in result["reason"]


def test_inconclusive_when_not_enough_tablets_for_five_folds():
    rows = _null_rows(n_tablets=4, rows_per_tablet=5, seed=2)
    result = rca2.run_full_pipeline_v2(rows, seed=1, B=10, min_total_n=10, min_tablets=4)
    assert result["status"] == "INCONCLUSIVE"
    assert "grouped folds" in result["reason"]


def test_inconclusive_when_training_fold_lacks_a_class():
    # all Y=0 -- criterion A must fail
    rows = [_v2row(f"T{i}", "Haghia Triada", "Tablet", "FIRST", "DRY", 5.0, False)
            for i in range(60)]
    result = rca2.run_full_pipeline_v2(rows, seed=1, B=10, min_total_n=50, min_tablets=20)
    assert result["status"] == "INCONCLUSIVE"
    assert "criterion A" in result["reason"]


def test_inconclusive_when_minority_per_fold_too_thin():
    # exactly 2 positives total, spread thin -- criterion B should fail
    rng = random.Random(9)
    rows = []
    for t in range(60):
        y = t < 2   # only tablets 0 and 1 are positive
        rows.append(_v2row(f"T{t}", "Haghia Triada", "Tablet",
                            rng.choice(["FIRST", "SECOND"]), rng.choice(["LIQUID", "DRY"]),
                            float(rng.randint(1, 300)), y))
    result = rca2.run_full_pipeline_v2(rows, seed=1, B=10, min_total_n=50, min_tablets=20)
    assert result["status"] == "INCONCLUSIVE"
    assert "criterion" in result["reason"]


# --------------------------------------------------------------------------- adequate full execution
def test_adequate_execution_reaches_complete():
    rows = _null_rows(n_tablets=60, rows_per_tablet=2, seed=3, base_rate=0.3)
    result = rca2.run_full_pipeline_v2(rows, seed=1, B=30, **ADEQUACY_OVERRIDES)
    assert result["status"] == "COMPLETE"
    assert result["n_splits"] == 5
    assert set(result["h_hat"].keys()) == {"M0", "M1", "M2", "M3", "M4"}
    assert set(result["delta_h"].keys()) == {"M1", "M2", "M3", "M4"}


def test_null_data_tends_toward_negative_update_or_inconclusive():
    # pure noise: no block should spuriously reach SUPPORTED under Holm
    rows = _null_rows(n_tablets=60, rows_per_tablet=2, seed=4, base_rate=0.3)
    result = rca2.run_full_pipeline_v2(rows, seed=1, B=100, **ADEQUACY_OVERRIDES)
    assert result["status"] == "COMPLETE"
    assert result["broad_program_update"] in ("NEGATIVE UPDATE",)
    assert all(v != "SUPPORTED" for v in result["step_verdicts"].values())


# --------------------------------------------------------------------------- one clean single-block-significant scenario (M4 only)
def test_strong_magnitude_signal_supports_m4_and_not_others():
    rows = _magnitude_signal_rows(n_tablets=70, rows_per_tablet=2, seed=5)
    result = rca2.run_full_pipeline_v2(rows, seed=1, B=150, **ADEQUACY_OVERRIDES)
    assert result["status"] == "COMPLETE"
    assert result["step_verdicts"]["M4"] == "SUPPORTED"
    assert result["step_verdicts"]["M2"] != "SUPPORTED"
    assert result["step_verdicts"]["M3"] != "SUPPORTED"
    assert result["broad_program_update"] == "LIMITED POSITIVE"


# --------------------------------------------------------------------------- Holm family / NOT_EVALUABLE wiring
def test_holm_family_excludes_not_evaluable_step_in_real_pipeline():
    # commodity constant across the whole corpus -> M3's own conditioning
    # strata degenerate; still must produce a well-formed result with M3
    # excluded from holm_adjusted_p if genuinely NOT_EVALUABLE, without
    # crashing the pipeline.
    rng = random.Random(6)
    rows = []
    for t in range(60):
        for k in range(2):
            rows.append(_v2row(f"T{t}", rng.choice(["Haghia Triada", "OTHER"]),
                                rng.choice(["Tablet", "OTHER"]),
                                rng.choice(["FIRST", "SECOND", "THIRD_OR_LATER"]),
                                "DRY",  # constant commodity -> degenerate M3 stratification
                                float(rng.randint(1, 300)), rng.random() < 0.3))
    result = rca2.run_full_pipeline_v2(rows, seed=1, B=30, **ADEQUACY_OVERRIDES)
    if result["status"] == "COMPLETE":
        for step, p in result["raw_p"].items():
            if p is None:
                assert step not in result["holm_adjusted_p"]
                assert result["step_verdicts"][step] == "NOT_EVALUABLE"


# --------------------------------------------------------------------------- result serialization / provenance / determinism
def test_result_json_round_trips(tmp_path):
    rows = _null_rows(n_tablets=60, rows_per_tablet=2, seed=7)
    result = rca2.run_full_pipeline_v2(rows, seed=1, B=10, **ADEQUACY_OVERRIDES)
    out_path = str(tmp_path / "v2_result.json")
    rca2.write_result_json(result, out_path)
    with open(out_path) as f:
        loaded = json.load(f)
    assert loaded["status"] == result["status"]


def test_compute_provenance_and_adequacy_v2_marginal_only():
    rows = _null_rows(n_tablets=10, rows_per_tablet=2, seed=8)
    result = rca2.compute_provenance_and_adequacy_v2(rows, freeze_sha=FREEZE_SHA, corpus_path=__file__)
    assert result["status"] == "PROVENANCE_AND_ADEQUACY_ONLY"
    assert result["n_total"] == len(rows)
    assert result["freeze_sha"] == FREEZE_SHA
    for forbidden in ("delta_h", "h_hat", "raw_p", "holm_adjusted_p", "broad_program_update", "step_verdicts"):
        assert forbidden not in result


def test_deterministic_seed_reproduces_identical_result():
    rows = _null_rows(n_tablets=60, rows_per_tablet=2, seed=9)
    r1 = rca2.run_full_pipeline_v2(rows, seed=42, B=10, **ADEQUACY_OVERRIDES)
    r2 = rca2.run_full_pipeline_v2(rows, seed=42, B=10, **ADEQUACY_OVERRIDES)
    assert r1 == r2


# --------------------------------------------------------------------------- no accidental modification of frozen files
def test_frozen_v2_files_unchanged_after_synthetic_run():
    import subprocess
    _ = rca2.run_full_pipeline_v2(_null_rows(n_tablets=60, seed=10), seed=1, B=10, **ADEQUACY_OVERRIDES)
    diff = subprocess.run(
        ["git", "diff", FREEZE_SHA, "--",
         "docs/CONSTRAINT_ACCUMULATION_V2_PROTOCOL.md",
         "src/constraint_accumulation_v2.py",
         "tests/test_constraint_accumulation_v2.py"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert diff.returncode == 0
    assert diff.stdout == ""
