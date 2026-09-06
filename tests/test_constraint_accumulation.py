"""
Synthetic tests for src/constraint_accumulation.py.

Every fixture here is hand-constructed. NONE of these tests load or touch
data/generated/lineara_extracted.json -- this round is design/scaffold only
(docs/CONSTRAINT_ACCUMULATION_DESIGN.md), no real-data computation.
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from kuro_protocol import Token, Record  # noqa: E402
import constraint_accumulation as ca  # noqa: E402


def sg(sign_id):
    return Token(kind="signgroup", sign_ids=(sign_id,))


def num(value=None, fractions=None):
    return Token(kind="numeral", value=value, fractions=fractions)


def frac(value=1.0, n=1):
    return num(value=value, fractions=[{"value": 0.5, "confidence": None} for _ in range(n)])


# --------------------------------------------------------------------------- site_block / support_block
def test_site_block_dominant():
    assert ca.site_block("Haghia Triada") == "Haghia Triada"


def test_site_block_case_and_whitespace_insensitive():
    assert ca.site_block("  HAGHIA TRIADA ") == "Haghia Triada"


def test_site_block_other():
    assert ca.site_block("Zakros") == "OTHER"


def test_site_block_missing():
    assert ca.site_block(None) == "OTHER"


def test_support_block_dominant():
    assert ca.support_block("Tablet") == "Tablet"


def test_support_block_case_insensitive():
    assert ca.support_block("tablet") == "Tablet"


def test_support_block_other():
    assert ca.support_block("Roundel") == "OTHER"


def test_support_block_missing():
    assert ca.support_block(None) == "OTHER"


# --------------------------------------------------------------------------- position_bucket
def test_position_bucket_first():
    assert ca.position_bucket(1) == "FIRST"


def test_position_bucket_second():
    assert ca.position_bucket(2) == "SECOND"


def test_position_bucket_third():
    assert ca.position_bucket(3) == "THIRD_OR_LATER"


def test_position_bucket_later():
    assert ca.position_bucket(10) == "THIRD_OR_LATER"


# --------------------------------------------------------------------------- numeric_bin
def test_numeric_bin_none_is_no_integer_value():
    assert ca.numeric_bin(None) == "NO_INTEGER_VALUE"


def test_numeric_bin_small_boundary():
    assert ca.numeric_bin(3) == "SMALL"
    assert ca.numeric_bin(1) == "SMALL"


def test_numeric_bin_medium_boundary():
    assert ca.numeric_bin(4) == "MEDIUM"
    assert ca.numeric_bin(15) == "MEDIUM"


def test_numeric_bin_large_boundary():
    assert ca.numeric_bin(16) == "LARGE"
    assert ca.numeric_bin(976) == "LARGE"


# --------------------------------------------------------------------------- build_feature_rows
def test_build_feature_rows_basic_single_occurrence():
    rec = Record("T1", [sg("GRA"), num(value=2.0)])
    rows = ca.build_feature_rows(rec, site="Haghia Triada", support="Tablet")
    assert len(rows) == 1
    r = rows[0]
    assert r.tablet_id == "T1"
    assert r.commodity_class == "DRY"
    assert r.position_bucket == "FIRST"
    assert r.numeric_bin == "SMALL"
    assert r.fraction_present is False
    assert r.site_block == "Haghia Triada"
    assert r.support_block == "Tablet"


def test_build_feature_rows_ordinal_rank_across_occurrences():
    rec = Record("T1", [
        sg("GRA"), num(value=1.0),
        sg("VIN"), num(value=20.0),
        sg("OLIV"), frac(value=2.0),
    ])
    rows = ca.build_feature_rows(rec, site="Zakros", support="Sealing")
    assert [r.position_bucket for r in rows] == ["FIRST", "SECOND", "THIRD_OR_LATER"]
    assert rows[1].numeric_bin == "LARGE"
    assert rows[2].fraction_present is True


def test_build_feature_rows_excludes_out_of_scope_commodity():
    rec = Record("T1", [sg("CYP"), num(value=5.0)])
    rows = ca.build_feature_rows(rec, site="Haghia Triada", support="Tablet")
    assert rows == []


def test_build_feature_rows_excludes_no_quantity_occurrence():
    rec = Record("T1", [sg("GRA"), sg("VIN"), num(value=5.0)])
    rows = ca.build_feature_rows(rec, site="Haghia Triada", support="Tablet")
    # GRA is heading-like (no immediate quantity) -> excluded; VIN has one
    assert len(rows) == 1
    assert rows[0].commodity_class == "LIQUID"


def test_build_feature_rows_numeric_bin_fraction_only_numeral():
    rec = Record("T1", [sg("VIN"), frac(value=None)])
    rows = ca.build_feature_rows(rec, site="Khania", support="Tablet")
    assert rows[0].numeric_bin == "NO_INTEGER_VALUE"
    assert rows[0].fraction_present is True


def test_build_feature_rows_reuses_frozen_ligature_safety():
    # GRA+L4+L4 ligature must not leak into fraction_present, exactly as
    # already tested in constraint_candidate1 -- confirmed reused here.
    rec = Record("T1", [sg("GRA+L4+L4"), num(value=5.0)])
    rows = ca.build_feature_rows(rec, site="Haghia Triada", support="Tablet")
    assert rows[0].commodity_class == "DRY"
    assert rows[0].fraction_present is False


def test_build_feature_rows_empty_record():
    assert ca.build_feature_rows(Record("T1", []), site="X", support="Y") == []


# --------------------------------------------------------------------------- cardinality / missingness / unique_tablets
def test_cardinality_counts_distinct_values():
    rows = [
        ca.FeatureRow("T1", 0, "Haghia Triada", "Tablet", "FIRST", "DRY", 2.0, "SMALL", False),
        ca.FeatureRow("T1", 2, "Haghia Triada", "Tablet", "SECOND", "LIQUID", 20.0, "LARGE", True),
        ca.FeatureRow("T2", 0, "OTHER", "OTHER", "FIRST", "DRY", 2.0, "SMALL", False),
    ]
    c = ca.cardinality(rows, "commodity_class")
    assert c == {"DRY": 2, "LIQUID": 1}


def test_cardinality_site_block():
    rows = [
        ca.FeatureRow("T1", 0, "Haghia Triada", "Tablet", "FIRST", "DRY", 2.0, "SMALL", False),
        ca.FeatureRow("T2", 0, "OTHER", "OTHER", "FIRST", "DRY", 2.0, "SMALL", False),
    ]
    c = ca.cardinality(rows, "site_block")
    assert c == {"Haghia Triada": 1, "OTHER": 1}


def test_missingness_never_none_by_construction():
    rows = [ca.FeatureRow("T1", 0, "Haghia Triada", "Tablet", "FIRST", "DRY", 2.0, "SMALL", False)]
    assert ca.missingness(rows, "numeric_bin") == 0


def test_missingness_detects_none_field():
    rows = [ca.FeatureRow("T1", 0, None, "Tablet", "FIRST", "DRY", 2.0, "SMALL", False)]
    assert ca.missingness(rows, "site_block") == 1


def test_unique_tablets():
    rows = [
        ca.FeatureRow("T1", 0, "Haghia Triada", "Tablet", "FIRST", "DRY", 2.0, "SMALL", False),
        ca.FeatureRow("T1", 2, "Haghia Triada", "Tablet", "SECOND", "LIQUID", 20.0, "LARGE", True),
        ca.FeatureRow("T2", 0, "OTHER", "OTHER", "FIRST", "DRY", 2.0, "SMALL", False),
    ]
    assert ca.unique_tablets(rows) == {"T1", "T2"}


def test_unique_tablets_empty():
    assert ca.unique_tablets([]) == set()


# --------------------------------------------------------------------------- fit_numeric_bin_cutoffs / numeric_bin_fold (fold-only fitting)
def test_fit_numeric_bin_cutoffs_excludes_none():
    cutoffs = ca.fit_numeric_bin_cutoffs([1.0, 2.0, None, 3.0, 100.0])
    assert len(cutoffs) == 2
    assert cutoffs[0] <= cutoffs[1]


def test_fit_numeric_bin_cutoffs_too_few_values_raises():
    import pytest
    with pytest.raises(ValueError):
        ca.fit_numeric_bin_cutoffs([1.0, None])


def test_numeric_bin_fold_none_is_no_integer_value():
    assert ca.numeric_bin_fold(None, small_max=3, medium_max=15) == "NO_INTEGER_VALUE"


def test_numeric_bin_fold_uses_given_cutoffs_not_global():
    # cutoffs deliberately different from the fixed-global NUMERIC_SMALL_MAX/MEDIUM_MAX
    assert ca.numeric_bin_fold(50, small_max=100, medium_max=200) == "SMALL"
    assert ca.numeric_bin_fold(150, small_max=100, medium_max=200) == "MEDIUM"
    assert ca.numeric_bin_fold(250, small_max=100, medium_max=200) == "LARGE"


def test_numeric_bin_fold_applies_same_cutoffs_train_and_test():
    training_values = [1.0, 2.0, 3.0, 4.0, 5.0, 60.0, 70.0, 80.0, 90.0]
    small_max, medium_max = ca.fit_numeric_bin_cutoffs(training_values)
    # a test-fold value gets bucketed with the TRAINING fold's cutoffs, not its own
    test_value = 1000.0
    assert ca.numeric_bin_fold(test_value, small_max, medium_max) == "LARGE"


# --------------------------------------------------------------------------- fixed reference-level encoding
def test_encode_indicator_reference_level_is_empty():
    assert ca.encode_indicator("site_block", "OTHER") == {}


def test_encode_indicator_non_reference_level():
    assert ca.encode_indicator("site_block", "Haghia Triada") == {"site_block__Haghia Triada": 1.0}


def test_encode_indicator_position_three_levels():
    assert ca.encode_indicator("position_bucket", "FIRST") == {}
    assert ca.encode_indicator("position_bucket", "SECOND") == {"position_bucket__SECOND": 1.0}
    assert ca.encode_indicator("position_bucket", "THIRD_OR_LATER") == {"position_bucket__THIRD_OR_LATER": 1.0}


def test_encode_indicator_unknown_level_raises():
    import pytest
    with pytest.raises(ValueError):
        ca.encode_indicator("site_block", "Nowhere")


def test_encode_indicator_numeric_bin_four_levels():
    assert ca.encode_indicator("numeric_bin", "SMALL") == {}
    assert ca.encode_indicator("numeric_bin", "NO_INTEGER_VALUE") == {"numeric_bin__NO_INTEGER_VALUE": 1.0}


# --------------------------------------------------------------------------- log_loss_bits
def test_log_loss_bits_perfect_predictions_near_zero():
    loss = ca.log_loss_bits([1, 0, 1, 0], [1 - 1e-10, 1e-10, 1 - 1e-10, 1e-10])
    assert loss < 1e-6


def test_log_loss_bits_uninformative_half_is_one_bit():
    loss = ca.log_loss_bits([1, 0], [0.5, 0.5])
    assert abs(loss - 1.0) < 1e-9


def test_log_loss_bits_worst_case_predictions_large_but_finite():
    loss = ca.log_loss_bits([1, 0], [0.0, 1.0])
    assert loss > 10  # clipped, not infinite


def test_log_loss_bits_mismatched_lengths_raises():
    import pytest
    with pytest.raises(ValueError):
        ca.log_loss_bits([1, 0], [0.5])


def test_log_loss_bits_empty_raises():
    import pytest
    with pytest.raises(ValueError):
        ca.log_loss_bits([], [])


# --------------------------------------------------------------------------- delta_h / delta_h_label (sign convention)
def test_delta_h_sign_convention():
    assert abs(ca.delta_h(h_prev=1.0, h_curr=0.8) - 0.2) < 1e-9
    assert abs(ca.delta_h(h_prev=0.8, h_curr=1.0) - (-0.2)) < 1e-9


def test_delta_h_label_improves():
    assert ca.delta_h_label(0.05) == "IMPROVES"


def test_delta_h_label_harms():
    assert ca.delta_h_label(-0.05) == "HARMS"


def test_delta_h_label_no_information():
    assert ca.delta_h_label(0.0) == "NO_INFORMATION"


# --------------------------------------------------------------------------- conditional_permutation_delta
def test_conditional_permutation_preserves_stratum_composition():
    import random
    rows = [
        (("HT", "Tablet"), 1), (("HT", "Tablet"), 0), (("HT", "Tablet"), 1),
        (("OTHER", "Tablet"), 0), (("OTHER", "Tablet"), 0),
    ]
    rng = random.Random(1)
    permuted = ca.conditional_permutation_delta(rows, lambda preds: preds, rng)
    # stratum ("HT","Tablet") must still have exactly the same Y multiset {1,0,1}
    ht_ys = sorted(y for preds, y in permuted if preds == ("HT", "Tablet"))
    assert ht_ys == [0, 1, 1]
    other_ys = sorted(y for preds, y in permuted if preds == ("OTHER", "Tablet"))
    assert other_ys == [0, 0]


def test_conditional_permutation_predictors_unchanged():
    import random
    rows = [(("HT",), 1), (("HT",), 0), (("OTHER",), 1)]
    rng = random.Random(2)
    permuted = ca.conditional_permutation_delta(rows, lambda preds: preds, rng)
    assert [preds for preds, _ in permuted] == [("HT",), ("HT",), ("OTHER",)]


def test_conditional_permutation_can_shuffle_within_stratum():
    # with a stratum of size >=2, repeated draws should sometimes reorder
    import random
    rows = [(("HT",), 1), (("HT",), 0), (("HT",), 1), (("HT",), 0)]
    seen_orders = set()
    for seed in range(20):
        rng = random.Random(seed)
        permuted = ca.conditional_permutation_delta(rows, lambda preds: preds, rng)
        seen_orders.add(tuple(y for _, y in permuted))
    assert len(seen_orders) > 1


def test_permutable_strata_splits_by_size():
    rows = [(("HT",), 1), (("HT",), 0), (("OTHER",), 1)]
    permutable, not_permutable = ca.permutable_strata(rows, lambda preds: preds)
    assert permutable == {("HT",)}
    assert not_permutable == {("OTHER",)}


# --------------------------------------------------------------------------- finite_permutation_pvalue
def test_finite_permutation_pvalue_matches_candidate1_formula():
    import constraint_candidate1 as c1
    assert ca.finite_permutation_pvalue(0, 2000) == c1.finite_permutation_pvalue(0, 2000)
    assert ca.finite_permutation_pvalue(50, 2000) == c1.finite_permutation_pvalue(50, 2000)


# --------------------------------------------------------------------------- holm_correction
def test_holm_correction_single_pvalue_unchanged():
    assert ca.holm_correction([0.03]) == [0.03]


def test_holm_correction_order_independent_of_input_order():
    adj1 = ca.holm_correction([0.01, 0.02, 0.03])
    adj2 = ca.holm_correction([0.03, 0.01, 0.02])
    # same p-values, different input order -> same p gets same adjustment
    assert sorted(adj1) == sorted(adj2)


def test_holm_correction_monotone_nondecreasing_by_rank():
    adj = ca.holm_correction([0.01, 0.02, 0.03])
    order = sorted(range(3), key=lambda i: [0.01, 0.02, 0.03][i])
    sorted_adj = [adj[i] for i in order]
    assert sorted_adj == sorted(sorted_adj)


def test_holm_correction_clips_at_one():
    adj = ca.holm_correction([0.9, 0.95, 0.99])
    assert all(a <= 1.0 for a in adj)


def test_holm_correction_empty():
    assert ca.holm_correction([]) == []


def test_holm_correction_known_values():
    # m=3, p=(0.01, 0.02, 0.20) sorted ascending
    # adj_1 = 0.01*3=0.03; adj_2 = max(0.03, 0.02*2=0.04)=0.04; adj_3 = max(0.04, 0.20*1=0.20)=0.20
    adj = ca.holm_correction([0.01, 0.02, 0.20])
    assert abs(adj[0] - 0.03) < 1e-9
    assert abs(adj[1] - 0.04) < 1e-9
    assert abs(adj[2] - 0.20) < 1e-9


# --------------------------------------------------------------------------- fold_is_evaluable
def test_fold_is_evaluable_both_classes_present():
    assert ca.fold_is_evaluable([0, 1, 0, 1]) is True


def test_fold_is_evaluable_single_class_fails():
    assert ca.fold_is_evaluable([0, 0, 0]) is False
    assert ca.fold_is_evaluable([1, 1]) is False


def test_fold_is_evaluable_bool_values():
    assert ca.fold_is_evaluable([True, False, True]) is True


# --------------------------------------------------------------------------- adequacy gates
def test_primary_adequacy_gate_passes():
    assert ca.primary_adequacy_gate(n_total=236, n_tablets=133, n_positive=38, n_negative=198) is True


def test_primary_adequacy_gate_fails_low_n():
    assert ca.primary_adequacy_gate(n_total=100, n_tablets=133, n_positive=38, n_negative=198) is False


def test_primary_adequacy_gate_fails_low_positive():
    assert ca.primary_adequacy_gate(n_total=236, n_tablets=133, n_positive=10, n_negative=198) is False


def test_category_adequacy_marks_failing_categories():
    result = ca.category_adequacy({"FIRST": 100, "SECOND": 40, "THIRD_OR_LATER": 5}, min_count=10)
    assert result == {"FIRST": True, "SECOND": True, "THIRD_OR_LATER": False}


# --------------------------------------------------------------------------- step_permutation_pvalue (Phase 1 correction: unconditional on sign)
def test_step_permutation_pvalue_positive_delta_obs():
    # delta_obs is larger than all perm draws -> smallest possible p
    perm = [0.0] * 2000
    p = ca.step_permutation_pvalue(delta_obs=0.5, perm_deltas=perm, B=2000)
    assert abs(p - (0 + 1) / 2001) < 1e-12


def test_step_permutation_pvalue_zero_delta_obs_still_computed():
    perm = [0.0] * 1000 + [1.0] * 1000
    p = ca.step_permutation_pvalue(delta_obs=0.0, perm_deltas=perm, B=2000)
    # exactly the perm draws >= 0 (all 2000) count as extreme
    assert abs(p - (2000 + 1) / 2001) < 1e-12


def test_step_permutation_pvalue_negative_delta_obs_still_computed_not_skipped():
    # a very negative observed delta must still produce a valid (large) p,
    # not raise, not return None, not be silently skipped
    perm = [0.0] * 2000
    p = ca.step_permutation_pvalue(delta_obs=-5.0, perm_deltas=perm, B=2000)
    assert p is not None
    assert abs(p - (2000 + 1) / 2001) < 1e-12  # every perm draw (0.0) >= -5.0


def test_step_permutation_pvalue_wrong_length_raises():
    import pytest
    with pytest.raises(ValueError):
        ca.step_permutation_pvalue(delta_obs=0.1, perm_deltas=[0.0] * 5, B=2000)


# --------------------------------------------------------------------------- holm_family (Phase 1 correction)
def test_holm_family_negative_delta_step_remains_in_family():
    # step "M2" has a negative-ΔH-derived (large) p-value -- must still be
    # included and adjusted, not dropped for being non-supportive.
    step_pvalues = {"M2": 0.99, "M3": 0.02, "M4": 0.03}
    result = ca.holm_family(step_pvalues)
    assert "M2" in result
    assert len(result) == 3


def test_holm_family_zero_delta_step_remains_in_family():
    step_pvalues = {"M2": 0.5, "M3": 0.02}
    result = ca.holm_family(step_pvalues)
    assert "M2" in result
    assert len(result) == 2


def test_holm_family_positive_delta_step_remains_in_family():
    step_pvalues = {"M2": 0.01, "M3": 0.02, "M4": 0.03}
    result = ca.holm_family(step_pvalues)
    assert set(result.keys()) == {"M2", "M3", "M4"}


def test_holm_family_excludes_only_not_evaluable_steps():
    # M4 is NOT_EVALUABLE (None) -- excluded regardless of what its p might
    # have been; M2 and M3 (whatever their sign/p) remain.
    step_pvalues = {"M2": 0.99, "M3": 0.01, "M4": None}
    result = ca.holm_family(step_pvalues)
    assert set(result.keys()) == {"M2", "M3"}
    assert "M4" not in result


def test_holm_family_size_depends_on_evaluability_not_sign():
    # Same three p-values, only evaluability differs -> family size differs;
    # the SIGN/magnitude of the underlying ΔH is irrelevant to membership.
    all_evaluable = {"M2": 0.99, "M3": 0.5, "M4": 0.01}  # one very non-significant, one middling, one significant
    assert len(ca.holm_family(all_evaluable)) == 3

    one_not_evaluable = {"M2": 0.99, "M3": 0.5, "M4": None}
    assert len(ca.holm_family(one_not_evaluable)) == 2

    two_not_evaluable = {"M2": 0.99, "M3": None, "M4": None}
    assert len(ca.holm_family(two_not_evaluable)) == 1


def test_holm_family_all_not_evaluable_returns_empty():
    assert ca.holm_family({"M2": None, "M3": None, "M4": None}) == {}


def test_holm_family_adjusted_values_match_holm_correction():
    step_pvalues = {"M2": 0.01, "M3": 0.02, "M4": 0.20}
    result = ca.holm_family(step_pvalues)
    expected = ca.holm_correction([0.01, 0.02, 0.20])
    assert abs(result["M2"] - expected[0]) < 1e-9
    assert abs(result["M3"] - expected[1]) < 1e-9
    assert abs(result["M4"] - expected[2]) < 1e-9
