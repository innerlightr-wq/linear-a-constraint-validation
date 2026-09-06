"""
Synthetic end-to-end tests for src/run_constraint_accumulation.py.

Every fixture here is hand-constructed, small, and synthetic. NONE of
these tests load or touch data/generated/lineara_extracted.json --
per docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md Phase 12 / this round's own
firewall, run_full_pipeline is exercised only against synthetic data in
this round. A few tests pass small keyword-only overrides
(min_total_n=..., n_splits_primary=...) to exercise rare edge paths
cheaply -- these override parameters default to the frozen protocol
constants and are never used by the module's own real-data entry point.

B is deliberately reduced (5-10) in these tests for runtime only -- the
frozen protocol's B=2000 is unchanged as the module's default.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import constraint_accumulation as ca  # noqa: E402
import run_constraint_accumulation as rca  # noqa: E402

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FREEZE_SHA = "2f58a7c80c173f538c758596ce94aa353d1ca07c"


def _row(tablet_id, site, support, position, commodity, numeric_value, numeric_bin, y):
    return ca.FeatureRow(
        tablet_id=tablet_id, index=0,
        site_block=site, support_block=support,
        position_bucket=position, commodity_class=commodity,
        numeric_value=numeric_value, numeric_bin=numeric_bin,
        fraction_present=y,
    )


def _rich_rows(n_tablets=30, numeric_bin_uniform=False):
    """60 rows / n_tablets tablets, varied across every block, both Y
    classes well represented. If numeric_bin_uniform, most rows share one
    numeric_bin category with a small (<10) minority in another -- forces
    M4's category-adequacy pre-check to fail by construction."""
    rows = []
    sites = ["Haghia Triada", "OTHER"]
    supports = ["Tablet", "OTHER"]
    positions = ["FIRST", "SECOND", "THIRD_OR_LATER"]
    commodities = ["LIQUID", "DRY"]
    idx = 0
    for t in range(n_tablets):
        tablet_id = f"T{t}"
        for k in range(2):
            if numeric_bin_uniform:
                nbin = "LARGE" if idx >= 55 else "MEDIUM"
            else:
                nbin = ["SMALL", "MEDIUM", "LARGE", "NO_INTEGER_VALUE"][idx % 4]
            rows.append(_row(
                tablet_id=tablet_id,
                site=sites[t % 2], support=supports[t % 2],
                position=positions[idx % 3],
                commodity=commodities[(t + k) % 2],
                numeric_value=float(1 + (idx * 7) % 200),
                numeric_bin=nbin,
                y=bool(idx % 2),
            ))
            idx += 1
    return rows


ADEQUACY_OVERRIDES = dict(min_total_n=50, min_tablets=20, min_positive=20, min_negative=20)


# --------------------------------------------------------------------------- 1. real runner path invokes frozen module
def test_runner_uses_frozen_accumulation_module_object():
    import constraint_accumulation as ca_direct
    assert rca.ca is ca_direct


# --------------------------------------------------------------------------- 2. no analysis logic duplicated in runner
def test_runner_source_calls_frozen_functions_not_reimplementations():
    src = open(os.path.join(REPO_ROOT, "src", "run_constraint_accumulation.py")).read()
    for fn in ("log_loss_bits", "delta_h", "holm_family", "step_permutation_pvalue",
               "conditional_permutation_delta", "fit_numeric_bin_cutoffs",
               "numeric_bin_fold", "encode_indicator", "fold_is_evaluable",
               "cardinality", "category_adequacy", "unique_tablets"):
        assert f"ca.{fn}(" in src, f"runner does not call frozen ca.{fn}"


# --------------------------------------------------------------------------- 3. 5-fold grouped CV path
def test_five_fold_path_chosen_when_evaluable():
    rows = _rich_rows()
    result = rca.run_full_pipeline(rows, seed=1, B=5, **ADEQUACY_OVERRIDES)
    assert result["status"] == "COMPLETE"
    assert result["chosen_n_splits"] == 5


# --------------------------------------------------------------------------- 4. 3-fold fallback path
def test_three_fold_fallback_when_five_infeasible():
    # only 4 tablets -> GroupKFold(5) cannot even construct 5 groups
    rows = []
    idx = 0
    for t in range(4):
        for k in range(4):
            rows.append(_row(f"T{t}", "Haghia Triada", "Tablet", "FIRST", "DRY",
                              float(1 + idx), "MEDIUM", bool(idx % 2)))
            idx += 1
    result = rca.run_full_pipeline(
        rows, seed=1, B=5,
        min_total_n=10, min_tablets=4, min_positive=5, min_negative=5,
        n_splits_primary=5, n_splits_fallback=3,
    )
    assert result["status"] == "COMPLETE"
    assert result["chosen_n_splits"] == 3


# --------------------------------------------------------------------------- 5. INCONCLUSIVE path
def test_inconclusive_when_adequacy_gate_fails():
    rows = [_row(f"T{i}", "Haghia Triada", "Tablet", "FIRST", "DRY", 1.0, "SMALL", i % 2 == 0)
            for i in range(5)]
    result = rca.run_full_pipeline(rows, seed=1, B=5)  # default (frozen) adequacy thresholds
    assert result["status"] == "INCONCLUSIVE"


# --------------------------------------------------------------------------- 6. M4 NOT_EVALUABLE under sparse conditional strata
def test_m4_not_evaluable_under_sparse_numeric_category():
    rows = _rich_rows(numeric_bin_uniform=True)
    result = rca.run_full_pipeline(rows, seed=1, B=5, **ADEQUACY_OVERRIDES)
    assert result["status"] == "COMPLETE"
    assert result["step_verdicts"]["M4"] == "NOT_EVALUABLE"
    assert result["raw_p"]["M4"] is None


# --------------------------------------------------------------------------- 7. all-evaluable Holm family
def test_all_evaluable_holm_family():
    rows = _rich_rows()
    result = rca.run_full_pipeline(rows, seed=1, B=5, **ADEQUACY_OVERRIDES)
    assert set(result["holm_adjusted_p"].keys()) == {"M2", "M3", "M4"}
    assert all(v != "NOT_EVALUABLE" for v in result["step_verdicts"].values())


# --------------------------------------------------------------------------- 8. partial-evaluable Holm family
def test_partial_evaluable_holm_family_excludes_not_evaluable_step():
    rows = _rich_rows(numeric_bin_uniform=True)
    result = rca.run_full_pipeline(rows, seed=1, B=5, **ADEQUACY_OVERRIDES)
    assert set(result["holm_adjusted_p"].keys()) == {"M2", "M3"}
    assert "M4" not in result["holm_adjusted_p"]


# --------------------------------------------------------------------------- 9. result serialization
def test_result_json_round_trips(tmp_path):
    rows = _rich_rows()
    result = rca.run_full_pipeline(rows, seed=1, B=5, **ADEQUACY_OVERRIDES)
    out_path = str(tmp_path / "result.json")
    rca.write_result_json(result, out_path)
    with open(out_path) as f:
        loaded = json.load(f)
    assert loaded["status"] == "COMPLETE"
    assert loaded["chosen_n_splits"] == result["chosen_n_splits"]


# --------------------------------------------------------------------------- 10. deterministic seed handling
def test_deterministic_seed_reproduces_identical_result():
    rows = _rich_rows()
    r1 = rca.run_full_pipeline(rows, seed=42, B=5, **ADEQUACY_OVERRIDES)
    r2 = rca.run_full_pipeline(rows, seed=42, B=5, **ADEQUACY_OVERRIDES)
    assert r1 == r2


# --------------------------------------------------------------------------- 11. result file generation
def test_result_file_generation_creates_file(tmp_path):
    rows = _rich_rows()
    result = rca.run_full_pipeline(rows, seed=1, B=5, **ADEQUACY_OVERRIDES)
    out_path = str(tmp_path / "generated_result.json")
    assert not os.path.exists(out_path)
    rca.write_result_json(result, out_path)
    assert os.path.exists(out_path)


# --------------------------------------------------------------------------- 12. no accidental modification of frozen files
def test_frozen_files_unchanged_after_synthetic_run():
    # exercise the full pipeline once more, then confirm the three files
    # frozen at CONSTRAINT_ACCUMULATION_PRE_RESULT_FREEZE are byte-identical
    # to that commit -- this test's own execution must not have touched them.
    _ = rca.run_full_pipeline(_rich_rows(), seed=1, B=5, **ADEQUACY_OVERRIDES)
    diff = subprocess.run(
        ["git", "diff", FREEZE_SHA, "--",
         "docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md",
         "src/constraint_accumulation.py",
         "tests/test_constraint_accumulation.py"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert diff.returncode == 0
    assert diff.stdout == ""


# --------------------------------------------------------------------------- provenance/adequacy (allowed-against-real-data path), synthetic only here
def test_compute_provenance_and_adequacy_marginal_only():
    rows = _rich_rows()
    result = rca.compute_provenance_and_adequacy(rows, freeze_sha=FREEZE_SHA, corpus_path=__file__)
    assert result["status"] == "PROVENANCE_AND_ADEQUACY_ONLY"
    assert result["n_total"] == len(rows)
    assert result["n_tablets"] == len(ca.unique_tablets(rows))
    assert result["freeze_sha"] == FREEZE_SHA
    # no inferential keys present
    for forbidden in ("delta_h", "h_hat", "raw_p", "holm_adjusted_p", "broad_program_update"):
        assert forbidden not in result
