"""
Tests for src/v2_adequacy_audit.py. SYNTHETIC DATA ONLY -- confirms the
grid-based stability check runs and behaves sanely; does not assert
anything about real V2 data.
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import v2_adequacy_audit as vaa  # noqa: E402


def test_make_synthetic_dataset_has_exact_positive_count():
    rows = vaa.make_synthetic_dataset(n_positive=15, seed=1, n_total=50, n_tablets=20)
    assert sum(1 for r in rows if r.fraction_present) == 15
    assert len(rows) == 50


def test_make_synthetic_dataset_deterministic_with_seed():
    r1 = vaa.make_synthetic_dataset(n_positive=10, seed=42, n_total=40, n_tablets=15)
    r2 = vaa.make_synthetic_dataset(n_positive=10, seed=42, n_total=40, n_tablets=15)
    assert [(r.tablet_id, r.fraction_present) for r in r1] == [(r.tablet_id, r.fraction_present) for r in r2]


def test_stability_check_completes_at_low_minority_count():
    result = vaa.stability_check(n_positive=10, seed=999, B=10)
    assert result["status"] == "COMPLETE"


def test_stability_check_completes_at_higher_minority_count():
    result = vaa.stability_check(n_positive=40, seed=999, B=10)
    assert result["status"] == "COMPLETE"


def test_stability_check_produces_valid_pvalues_when_evaluable():
    result = vaa.stability_check(n_positive=20, seed=5, B=10)
    for step, p in result["raw_p"].items():
        if p is not None:
            assert 0.0 <= p <= 1.0


def test_run_grid_covers_predeclared_grid_exactly():
    # small B via direct stability_check calls to keep this test fast;
    # confirm run_grid's grid matches the predeclared, non-21-centered set
    assert vaa.MINORITY_GRID == (10, 15, 20, 25, 30, 40)
    assert 21 not in vaa.MINORITY_GRID
