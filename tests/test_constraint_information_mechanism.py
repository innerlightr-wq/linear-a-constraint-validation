"""
Tests for src/constraint_information_mechanism.py. Pure mathematics --
verifies exact finite constructions, not real corpus data.
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import constraint_information_mechanism as cim  # noqa: E402


# --------------------------------------------------------------------------- Task 1: core theorem
def test_theorem_balanced_elimination_preserves_p():
    r1, r0 = cim.elimination_rates(n1=50, n0=50, e1=20, e0=20)
    assert r1 == r0
    p_prime = cim.posterior_after_elimination(50, 50, 20, 20)
    assert abs(p_prime - 0.5) < 1e-12


def test_theorem_asymmetric_elimination_changes_p():
    p_prime = cim.posterior_after_elimination(50, 50, 30, 10)
    assert abs(p_prime - 0.5) > 1e-9


def test_theorem_iff_holds_across_a_grid():
    import itertools
    for n1, n0 in [(10, 10), (50, 30), (7, 13)]:
        for e1 in range(0, n1 + 1, max(1, n1 // 4)):
            for e0 in range(0, n0 + 1, max(1, n0 // 4)):
                if e1 == n1 and e0 == n0:
                    continue  # empty S', posterior undefined, skip
                assert cim.theorem_p_prime_equals_p(n1, n0, e1, e0)


def test_posterior_raises_on_invalid_counts():
    import pytest
    with pytest.raises(ValueError):
        cim.posterior_after_elimination(10, 10, 11, 0)


# --------------------------------------------------------------------------- Task 2: explicit examples
def test_example_A_huge_reduction_zero_information():
    r = cim.example_A_huge_reduction_zero_information()
    assert r["cardinality_reduction_fraction"] == 0.9
    assert r["information_gain"] is True  # "information_gain" flag means p_prime==p, i.e. NO real gain
    assert abs(r["p"] - r["p_prime"]) < 1e-12
    assert r["r1"] == r["r0"]


def test_example_B_tiny_reduction_large_information():
    r = cim.example_B_tiny_reduction_large_information()
    assert r["cardinality_reduction_fraction"] < 0.01
    assert r["p"] == 0.01
    assert abs(r["p_prime"] - (1 / 9901)) < 1e-9
    assert r["odds_ratio_p_to_pprime"] > 90  # roughly 100x odds shift


def test_example_C_progressive_no_accumulation():
    r = cim.example_C_progressive_no_accumulation()
    assert r["all_p_equal"] is True
    assert r["cardinality_shrunk_every_stage"] is True


def test_example_D_progressive_accumulation():
    r = cim.example_D_progressive_accumulation()
    assert r["strictly_increasing"] is True
    ps = [s["p"] for s in r["stages"]]
    assert ps[0] == 0.5
    assert ps[-1] > 0.8


# --------------------------------------------------------------------------- Task 3: I(C;X)>0, I(C;Y)=0
def test_mutual_information_zero_for_independent():
    joint = {(0, 0): 0.25, (0, 1): 0.25, (1, 0): 0.25, (1, 1): 0.25}
    assert abs(cim.mutual_information_binary(joint)) < 1e-12


def test_mutual_information_positive_for_deterministic_link():
    joint = {(0, 0): 0.5, (1, 1): 0.5}
    assert cim.mutual_information_binary(joint) > 0.99  # ~1 bit


def test_construction_IX_positive_IY_zero():
    r = cim.construction_IX_positive_IY_zero()
    assert r["C_independent_of_Y"] is True
    assert r["C_informative_about_X"] is True
    assert abs(r["I_C_X_bits"] - 1.0) < 1e-9
    assert r["(C,Y)_jointly_determine_X"] is True
    assert r["data_processing_inequality_satisfied"] is True


# --------------------------------------------------------------------------- Task 5/8: sequential + Simpson
def test_sequential_null_then_informative():
    r = cim.sequential_null_then_informative()
    assert r["stage1"]["informative"] is False
    assert r["stage2"]["informative"] is True
    assert r["null_step_did_not_block_later_information"] is True


def test_simpson_marginal_balanced_conditional_asymmetric():
    r = cim.simpson_marginal_balanced_conditional_asymmetric()
    assert r["marginal_appears_balanced"] is True
    assert r["within_strata_are_strongly_asymmetric_and_reversed"] is True
    # sanity: pooled p_before == p_after despite huge within-stratum shifts
    assert abs(r["pooled_marginal"]["p_before"] - r["pooled_marginal"]["p_after"]) < 1e-9


def test_confounded_proxy_marginal_asymmetric_conditionally_null():
    r = cim.confounded_proxy_marginal_asymmetric_conditionally_null()
    assert r["within_HT"]["asymmetric"] is False
    assert r["within_OTHER"]["asymmetric"] is False
    assert r["marginal_pooled"]["asymmetric"] is True
    assert r["confound_produces_spurious_marginal_asymmetry"] is True


# --------------------------------------------------------------------------- soft reweighting generalization
def test_soft_reweighting_equal_weights_preserves_p():
    r = cim.soft_reweighting_generalization(n1=40, n0=60, w1=0.5, w0=0.5)
    assert abs(r["p"] - r["p_prime"]) < 1e-12
    assert r["equal_weight_iff_p_unchanged"] is True


def test_soft_reweighting_unequal_weights_changes_p():
    r = cim.soft_reweighting_generalization(n1=40, n0=60, w1=1.0, w0=0.2)
    assert abs(r["p"] - r["p_prime"]) > 0.1
    assert r["equal_weight_iff_p_unchanged"] is True  # the IFF check itself still holds


# --------------------------------------------------------------------------- V1->V2 diagnostic (already-disclosed numbers only)
def test_v1_v2_elimination_diagnostic_matches_disclosed_figures():
    r = cim.v1_v2_elimination_diagnostic()
    assert r["V1_population"]["n1"] == 38
    assert r["V1_population"]["n0"] == 198
    assert abs(r["r1_r0"]["r1"] - 17 / 38) < 1e-9
    assert r["r1_r0"]["r0"] == 0.0
    assert r["extreme_asymmetry"] is True
    assert r["V2_population_implied"]["n1"] == 21
    assert r["V2_population_implied"]["n0"] == 198
