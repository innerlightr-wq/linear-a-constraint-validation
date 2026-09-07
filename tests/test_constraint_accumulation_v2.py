"""
Synthetic tests for src/constraint_accumulation_v2.py.

Every fixture here is hand-constructed. NONE of these tests load or touch
data/generated/lineara_extracted.json -- this round is design/scaffold
only (docs/CONSTRAINT_ACCUMULATION_V2_DESIGN.md), no real-data
computation, no model fitting, no CV, no permutation.
"""
import math
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import constraint_accumulation as ca  # noqa: E402
import constraint_accumulation_v2 as v2  # noqa: E402


def _fr(tablet_id, numeric_value, fraction_present, site="Haghia Triada",
        support="Tablet", position="FIRST", commodity="DRY"):
    return ca.FeatureRow(
        tablet_id=tablet_id, index=0,
        site_block=site, support_block=support,
        position_bucket=position, commodity_class=commodity,
        numeric_value=numeric_value, numeric_bin="SMALL",
        fraction_present=fraction_present,
    )


# --------------------------------------------------------------------------- is_integer_resolvable
def test_is_integer_resolvable_true_for_value():
    assert v2.is_integer_resolvable(5.0) is True


def test_is_integer_resolvable_false_for_none():
    assert v2.is_integer_resolvable(None) is False


def test_is_integer_resolvable_true_for_zero():
    # 0.0 is falsy but not None -- must still be treated as resolvable
    assert v2.is_integer_resolvable(0.0) is True


def test_is_integer_resolvable_independent_of_fraction_present():
    # PROOF, not just intent: identical numeric_value, opposite Y, must
    # give identical inclusion decisions -- the function signature itself
    # takes no fraction_present argument, so this is definitionally true,
    # but we assert it via the two call sites' behavior too.
    row_true = _fr("T1", 5.0, fraction_present=True)
    row_false = _fr("T2", 5.0, fraction_present=False)
    assert v2.is_integer_resolvable(row_true.numeric_value) == v2.is_integer_resolvable(row_false.numeric_value)


# --------------------------------------------------------------------------- log2_magnitude
def test_log2_magnitude_zero():
    assert v2.log2_magnitude(0) == 0.0


def test_log2_magnitude_one():
    assert abs(v2.log2_magnitude(1) - 1.0) < 1e-9


def test_log2_magnitude_monotonic():
    values = [0, 1, 2, 5, 10, 100, 976]
    transformed = [v2.log2_magnitude(v) for v in values]
    assert transformed == sorted(transformed)


def test_log2_magnitude_negative_raises():
    import pytest
    with pytest.raises(ValueError):
        v2.log2_magnitude(-1)


def test_log2_magnitude_matches_formula():
    assert abs(v2.log2_magnitude(15) - math.log2(16)) < 1e-9


# --------------------------------------------------------------------------- build_v2_rows
def test_build_v2_rows_excludes_no_integer_value():
    rows = [
        _fr("T1", 5.0, fraction_present=False),
        _fr("T2", None, fraction_present=True),  # NO_INTEGER_VALUE -- excluded from V2
    ]
    v2_rows = v2.build_v2_rows(rows)
    assert len(v2_rows) == 1
    assert v2_rows[0].tablet_id == "T1"


def test_build_v2_rows_preserves_other_fields_unchanged():
    rows = [_fr("T1", 8.0, fraction_present=True, site="OTHER", support="OTHER",
                 position="SECOND", commodity="LIQUID")]
    v2_rows = v2.build_v2_rows(rows)
    r = v2_rows[0]
    assert r.site_block == "OTHER"
    assert r.support_block == "OTHER"
    assert r.position_bucket == "SECOND"
    assert r.commodity_class == "LIQUID"
    assert r.fraction_present is True


def test_build_v2_rows_computes_magnitude_correctly():
    rows = [_fr("T1", 15.0, fraction_present=False)]
    v2_rows = v2.build_v2_rows(rows)
    assert abs(v2_rows[0].whole_component_magnitude - math.log2(16)) < 1e-9


def test_build_v2_rows_empty_input():
    assert v2.build_v2_rows([]) == []


def test_build_v2_rows_all_excluded():
    rows = [_fr("T1", None, fraction_present=True), _fr("T2", None, fraction_present=True)]
    assert v2.build_v2_rows(rows) == []


def test_build_v2_rows_never_uses_fraction_present_to_decide_inclusion():
    # Two rows, same numeric_value, opposite Y -- both must be included
    # (or both excluded) identically; inclusion cannot depend on Y.
    rows = [
        _fr("T1", 10.0, fraction_present=True),
        _fr("T2", 10.0, fraction_present=False),
    ]
    v2_rows = v2.build_v2_rows(rows)
    assert len(v2_rows) == 2
    assert {r.tablet_id for r in v2_rows} == {"T1", "T2"}


# --------------------------------------------------------------------------- population_cardinality / unique_tablets
def test_population_cardinality_marginal_only():
    rows = [
        _fr("T1", 5.0, False, commodity="DRY"),
        _fr("T2", 6.0, True, commodity="LIQUID"),
        _fr("T3", 7.0, False, commodity="DRY"),
    ]
    v2_rows = v2.build_v2_rows(rows)
    c = v2.population_cardinality(v2_rows, "commodity_class")
    assert c == {"DRY": 2, "LIQUID": 1}


def test_unique_tablets_v2():
    rows = [
        _fr("T1", 5.0, False),
        _fr("T1", 6.0, True),
        _fr("T2", 7.0, False),
    ]
    v2_rows = v2.build_v2_rows(rows)
    assert v2.unique_tablets(v2_rows) == {"T1", "T2"}


def test_unique_tablets_v2_empty():
    assert v2.unique_tablets([]) == set()


# --------------------------------------------------------------------------- reuse of frozen V1 blocks, unchanged
def test_v2_reuses_frozen_site_block_function_unchanged():
    assert v2.ca.site_block is ca.site_block


def test_v2_reuses_frozen_commodity_class_function_via_constraint_candidate1():
    import constraint_candidate1 as c1
    assert v2.ca.c1.commodity_class is c1.commodity_class


def test_v2_row_has_no_magnitude_field_only_whole_component_magnitude():
    rows = [_fr("T1", 8.0, fraction_present=True)]
    v2_rows = v2.build_v2_rows(rows)
    assert hasattr(v2_rows[0], "whole_component_magnitude")
    assert not hasattr(v2_rows[0], "magnitude")


# --------------------------------------------------------------------------- model nesting (protocol §4)
def test_model_blocks_v2_nesting_is_cumulative():
    assert v2.MODEL_BLOCKS_V2["M0"] == []
    assert v2.MODEL_BLOCKS_V2["M1"] == ["site_support"]
    assert v2.MODEL_BLOCKS_V2["M2"] == ["site_support", "position"]
    assert v2.MODEL_BLOCKS_V2["M3"] == ["site_support", "position", "commodity"]
    assert v2.MODEL_BLOCKS_V2["M4"] == ["site_support", "position", "commodity", "magnitude"]


def test_step_prev_model_v2_mapping():
    assert v2.STEP_PREV_MODEL_V2 == {"M2": "M1", "M3": "M2", "M4": "M3"}


def test_step_stratum_fields_v2_grows_by_one_each_step():
    assert v2.STEP_STRATUM_FIELDS_V2["M2"] == ("site_block", "support_block")
    assert v2.STEP_STRATUM_FIELDS_V2["M3"] == ("site_block", "support_block", "position_bucket")
    assert v2.STEP_STRATUM_FIELDS_V2["M4"] == ("site_block", "support_block", "position_bucket", "commodity_class")


# --------------------------------------------------------------------------- information-type classification
def test_information_types_v2_classification():
    assert v2.INFORMATION_TYPES_V2["site_support"] == "INDEPENDENT STRUCTURAL INFORMATION"
    assert v2.INFORMATION_TYPES_V2["position"] == "DERIVED STRUCTURAL INFORMATION"
    assert v2.INFORMATION_TYPES_V2["commodity"] == "EXTERNAL MODEL INFORMATION"
    assert "magnitude" in v2.INFORMATION_TYPES_V2


# --------------------------------------------------------------------------- adequacy gates (protocol §7)
def test_training_fold_minority_adequate_passes_at_threshold():
    assert v2.training_fold_minority_adequate([1, 1, 1, 1, 1, 0, 0, 0]) is True  # exactly 5


def test_training_fold_minority_adequate_fails_below_threshold():
    assert v2.training_fold_minority_adequate([1, 1, 1, 0, 0, 0]) is False  # only 3


def test_training_fold_minority_adequate_zero_minority():
    assert v2.training_fold_minority_adequate([0, 0, 0]) is False


def test_mixed_strata_fraction_basic():
    rbs = {
        "s1": [1, 0, 1],   # mixed
        "s2": [0, 0, 0],   # not mixed
        "s3": [1, 1],      # not mixed (all positive)
        "s4": [1, 0],      # mixed
    }
    assert v2.mixed_strata_fraction(rbs) == 0.5


def test_mixed_strata_fraction_empty():
    assert v2.mixed_strata_fraction({}) == 0.0


def test_strata_mixed_adequate_at_threshold():
    rbs = {"s1": [1, 0], "s2": [1, 0], "s3": [0, 0]}  # 2/3 = 0.667 >= 0.5
    assert v2.strata_mixed_adequate(rbs) is True


def test_strata_mixed_adequate_below_threshold():
    rbs = {"s1": [1, 0], "s2": [0, 0], "s3": [0, 0], "s4": [0, 0]}  # 1/4 = 0.25 < 0.5
    assert v2.strata_mixed_adequate(rbs) is False


# --------------------------------------------------------------------------- step verdict classification (ΔH sign handling)
def test_classify_step_verdict_positive_significant_is_supported():
    assert v2.classify_step_verdict(holm_p=0.01, delta_obs=0.1) == "SUPPORTED"


def test_classify_step_verdict_positive_not_significant_is_not_supported():
    assert v2.classify_step_verdict(holm_p=0.5, delta_obs=0.1) == "NOT SUPPORTED"


def test_classify_step_verdict_negative_delta_is_not_supported_not_undefined():
    # even a "significant" p-value with a negative delta must never be SUPPORTED
    assert v2.classify_step_verdict(holm_p=0.01, delta_obs=-0.1) == "NOT SUPPORTED"


def test_classify_step_verdict_zero_delta_is_not_supported():
    assert v2.classify_step_verdict(holm_p=0.01, delta_obs=0.0) == "NOT SUPPORTED"


def test_classify_step_verdict_not_evaluable_when_none():
    assert v2.classify_step_verdict(holm_p=None, delta_obs=None) == "NOT_EVALUABLE"
    assert v2.classify_step_verdict(holm_p=None, delta_obs=0.1) == "NOT_EVALUABLE"


# --------------------------------------------------------------------------- broad verdict: every edge case (protocol §11)
def test_broad_verdict_m2_only():
    v = v2.classify_broad_verdict({"M2": "SUPPORTED", "M3": "NOT SUPPORTED", "M4": "NOT SUPPORTED"})
    assert v == "LIMITED POSITIVE"


def test_broad_verdict_m3_only():
    v = v2.classify_broad_verdict({"M2": "NOT SUPPORTED", "M3": "SUPPORTED", "M4": "NOT SUPPORTED"})
    assert v == "LIMITED POSITIVE (EXTERNAL-MODEL-ONLY)"


def test_broad_verdict_m4_only():
    v = v2.classify_broad_verdict({"M2": "NOT SUPPORTED", "M3": "NOT SUPPORTED", "M4": "SUPPORTED"})
    assert v == "LIMITED POSITIVE"


def test_broad_verdict_m2_and_m3_not_m4():
    v = v2.classify_broad_verdict({"M2": "SUPPORTED", "M3": "SUPPORTED", "M4": "NOT SUPPORTED"})
    assert v == "LIMITED POSITIVE"   # only M2 counts; M3 doesn't upgrade or add a second qualifier


def test_broad_verdict_m3_and_m4_not_m2():
    v = v2.classify_broad_verdict({"M2": "NOT SUPPORTED", "M3": "SUPPORTED", "M4": "SUPPORTED"})
    assert v == "LIMITED POSITIVE"   # only M4 counts


def test_broad_verdict_m2_and_m4():
    v = v2.classify_broad_verdict({"M2": "SUPPORTED", "M3": "NOT SUPPORTED", "M4": "SUPPORTED"})
    assert v == "ACCUMULATION EVIDENCE"


def test_broad_verdict_all_three_supported():
    v = v2.classify_broad_verdict({"M2": "SUPPORTED", "M3": "SUPPORTED", "M4": "SUPPORTED"})
    assert v == "ACCUMULATION EVIDENCE"   # M3's extra support does not change the label


def test_broad_verdict_none_supported():
    v = v2.classify_broad_verdict({"M2": "NOT SUPPORTED", "M3": "NOT SUPPORTED", "M4": "NOT SUPPORTED"})
    assert v == "NEGATIVE UPDATE"


def test_broad_verdict_one_not_evaluable_others_not_supported():
    v = v2.classify_broad_verdict({"M2": "NOT SUPPORTED", "M3": "NOT SUPPORTED", "M4": "NOT_EVALUABLE"})
    assert v == "NEGATIVE UPDATE"   # M2/M3 still evaluable, neither supported


def test_broad_verdict_m4_not_evaluable_m2_supported():
    v = v2.classify_broad_verdict({"M2": "SUPPORTED", "M3": "NOT SUPPORTED", "M4": "NOT_EVALUABLE"})
    assert v == "LIMITED POSITIVE"


def test_broad_verdict_all_not_evaluable_is_inconclusive():
    v = v2.classify_broad_verdict({"M2": "NOT_EVALUABLE", "M3": "NOT_EVALUABLE", "M4": "NOT_EVALUABLE"})
    assert v == "INCONCLUSIVE"


def test_broad_verdict_missing_keys_default_not_evaluable():
    assert v2.classify_broad_verdict({}) == "INCONCLUSIVE"


def test_v2_module_imports_no_modeling_dependency_used_for_real_computation():
    # This round's firewall: no model-fitting/CV/permutation function is
    # DEFINED (not merely mentioned in prose) in this module -- only
    # population construction + transform. Checks actual call/definition
    # patterns, not the module's own disclaimer text.
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                             "src", "constraint_accumulation_v2.py")).read()
    for forbidden in ("LogisticRegression(", "GroupKFold(", "def holm", "log_loss_bits(",
                       "conditional_permutation_delta(", "step_permutation_pvalue("):
        assert forbidden not in src, f"V2 scaffold unexpectedly calls/defines '{forbidden}' -- real inference must not be implemented this round"
