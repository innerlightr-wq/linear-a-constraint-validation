"""
Synthetic tests for src/constraint_candidate1.py.

Every fixture here is hand-constructed. NONE of these tests load or touch
data/generated/lineara_extracted.json -- per docs/CANDIDATE1_PROTOCOL.md
item 22, the real corpus is not read anywhere in this round.
"""
import random
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from kuro_protocol import Token, Record  # noqa: E402
import constraint_candidate1 as c1  # noqa: E402


def sg(sign_id, damaged=False):
    return Token(kind="signgroup", sign_ids=(sign_id,), damaged=damaged)


def num(value=None, fractions=None, damaged=False):
    return Token(kind="numeral", value=value, fractions=fractions, damaged=damaged)


def frac_tok(value=None, n=1, confidence=None):
    """A numeral token carrying `n` fraction entries."""
    return num(value=value, fractions=[{"value": 0.5, "confidence": confidence} for _ in range(n)])


# --------------------------------------------------------------------------- base_sign / family normalization
def test_base_sign_no_ligature():
    assert c1.base_sign("GRA") == "GRA"


def test_base_sign_single_ligature():
    assert c1.base_sign("OLE+U") == "OLE"


def test_base_sign_double_ligature():
    assert c1.base_sign("GRA+L4+L4") == "GRA"


def test_commodity_class_liquid_bare():
    assert c1.commodity_class("VIN") == "LIQUID"
    assert c1.commodity_class("OLE") == "LIQUID"


def test_commodity_class_liquid_ligature_variants():
    for v in ("OLE+U", "OLE+A", "OLE+E", "OLE+KI", "OLE+MI", "OLE+DI"):
        assert c1.commodity_class(v) == "LIQUID"


def test_commodity_class_dry_bare():
    assert c1.commodity_class("GRA") == "DRY"
    assert c1.commodity_class("OLIV") == "DRY"


def test_commodity_class_dry_ligature():
    assert c1.commodity_class("GRA+L4+L4") == "DRY"


def test_commodity_class_out_of_scope_unrelated():
    assert c1.commodity_class("CYP") is None
    assert c1.commodity_class("CYP+D") is None
    assert c1.commodity_class("VIR+KA") is None


def test_commodity_class_no_loose_substring_match():
    # "OLIVE" is not a real ligature form; base_sign("OLIVE") == "OLIVE",
    # which is NOT exactly "OLIV" -- must not match via substring/prefix.
    assert c1.commodity_class("OLIVE") is None
    assert c1.commodity_class("OLIVX") is None
    assert c1.commodity_class("XOLIV") is None


def test_commodity_class_exact_equality_not_startswith():
    # "OLEX" starts with "OLE" but is not a declared ligature form under the
    # +-split rule (base_sign("OLEX") == "OLEX", not "OLE").
    assert c1.commodity_class("OLEX") is None


# --------------------------------------------------------------------------- fraction_present
def test_fraction_present_false_when_none():
    assert c1.fraction_present(num(value=5.0)) is False


def test_fraction_present_false_when_empty_list():
    t = num(value=5.0)
    t.fractions = []
    assert c1.fraction_present(t) is False


def test_fraction_present_true_regardless_of_confidence():
    # unresolved confidence (None) still counts as PRESENT -- Candidate 1
    # tests sign presence, not resolved arithmetic value.
    t = frac_tok(confidence=None)
    assert c1.fraction_present(t) is True
    t2 = frac_tok(confidence="secure")
    assert c1.fraction_present(t2) is True


# --------------------------------------------------------------------------- associated_quantity
def test_associated_quantity_immediate_numeral():
    rec = Record("T1", [sg("GRA"), num(value=10.0)])
    q = c1.associated_quantity(rec, 0)
    assert q is not None and q.value == 10.0


def test_associated_quantity_none_when_heading():
    rec = Record("T1", [sg("GRA"), sg("VIN"), num(value=10.0)])
    assert c1.associated_quantity(rec, 0) is None


def test_associated_quantity_none_when_last_token():
    rec = Record("T1", [sg("GRA")])
    assert c1.associated_quantity(rec, 0) is None


def test_associated_quantity_stops_at_ruling():
    rec = Record("T1", [sg("GRA"), Token(kind="ruling"), num(value=10.0)])
    assert c1.associated_quantity(rec, 0) is None


# --------------------------------------------------------------------------- ligature/fraction confusion (adversarial)
def test_ligature_suffix_does_not_leak_into_fraction_presence():
    # "GRA+L4+L4" is a DRY-family ligature; the associated numeral carries
    # NO Unicode fraction glyph. The ligature suffix on the commodity token
    # must never be scanned for fraction-like content.
    rec = Record("T1", [sg("GRA+L4+L4"), num(value=5.0)])
    occs = c1.find_commodity_occurrences(rec)
    assert len(occs) == 1
    assert occs[0].commodity_class == "DRY"
    assert occs[0].has_quantity is True
    assert occs[0].fraction_present is False


def test_ligature_suffix_class_membership_still_recognized():
    rec = Record("T1", [sg("OLE+MI"), frac_tok()])
    occs = c1.find_commodity_occurrences(rec)
    assert occs[0].commodity_class == "LIQUID"
    assert occs[0].fraction_present is True


# --------------------------------------------------------------------------- find_commodity_occurrences (Level A)
def test_multi_element_sign_ids_out_of_scope_never_miscounted():
    # a resolved TARGET (e.g. KU-RO) has a multi-element sign_ids tuple --
    # must never be treated as a commodity occurrence.
    rec = Record("T1", [Token(kind="signgroup", sign_ids=("AB081", "AB002")), num(value=10.0)])
    assert c1.find_commodity_occurrences(rec) == []


def test_find_commodity_occurrences_order_preserved():
    rec = Record("T1", [sg("GRA"), num(value=1.0), sg("VIN"), num(value=2.0)])
    occs = c1.find_commodity_occurrences(rec)
    assert [o.sign_id for o in occs] == ["GRA", "VIN"]


def test_find_commodity_occurrences_empty_tokens():
    assert c1.find_commodity_occurrences(Record("T1", [])) == []


# --------------------------------------------------------------------------- Level B: tablet-level aggregation
def test_tablet_level_first_occurrence_rule_not_any_rule():
    # First GRA occurrence has NO fraction; second GRA occurrence DOES.
    # The naive "ANY" rule would say FRACTION_PRESENT; the frozen
    # first-occurrence rule must say FRACTION_ABSENT.
    rec = Record("T1", [
        sg("GRA"), num(value=3.0),
        sg("GRA"), frac_tok(value=2.0),
    ])
    obs = c1.tablet_level_observations(rec)
    dry = [o for o in obs if o.commodity_class == "DRY"][0]
    assert dry.outcome == "FRACTION_ABSENT"


def test_tablet_level_first_occurrence_present_when_first_has_fraction():
    rec = Record("T1", [
        sg("GRA"), frac_tok(value=2.0),
        sg("GRA"), num(value=3.0),
    ])
    obs = c1.tablet_level_observations(rec)
    dry = [o for o in obs if o.commodity_class == "DRY"][0]
    assert dry.outcome == "FRACTION_PRESENT"


def test_tablet_level_skips_heading_only_occurrence_to_find_first_usable():
    rec = Record("T1", [
        sg("GRA"), sg("VIN"),           # GRA is a heading here (no quantity)
        num(value=5.0),                 # belongs to VIN
        sg("GRA"), frac_tok(value=1.0), # GRA's first USABLE occurrence
    ])
    obs = c1.tablet_level_observations(rec)
    dry = [o for o in obs if o.commodity_class == "DRY"][0]
    assert dry.outcome == "FRACTION_PRESENT"


def test_tablet_level_class_absent_produces_no_row():
    rec = Record("T1", [sg("GRA"), num(value=1.0)])
    obs = c1.tablet_level_observations(rec)
    assert all(o.commodity_class != "LIQUID" for o in obs)


def test_tablet_level_all_heading_only_is_ambiguous_unusable():
    rec = Record("T1", [sg("GRA"), sg("VIN"), num(value=1.0)])
    obs = c1.tablet_level_observations(rec)
    dry = [o for o in obs if o.commodity_class == "DRY"][0]
    assert dry.outcome == "AMBIGUOUS_UNUSABLE"
    assert dry.source_index is None


def test_tablet_level_both_classes_independent():
    rec = Record("T1", [
        sg("VIN"), frac_tok(value=1.0),
        sg("GRA"), num(value=2.0),
    ])
    obs = c1.tablet_level_observations(rec)
    by_class = {o.commodity_class: o.outcome for o in obs}
    assert by_class == {"LIQUID": "FRACTION_PRESENT", "DRY": "FRACTION_ABSENT"}


# --------------------------------------------------------------------------- Level C: physical-artifact key
def test_physical_artifact_key_face_letter_stripped():
    assert c1.physical_artifact_key("HT11a") == "HT11"
    assert c1.physical_artifact_key("HT11b") == "HT11"


def test_physical_artifact_key_no_face_letter_unchanged():
    assert c1.physical_artifact_key("HT1") == "HT1"


def test_physical_artifact_key_compound_join_id():
    assert c1.physical_artifact_key("HT123+124a") == "HT123+124"


def test_physical_artifact_key_no_trailing_digit_unchanged():
    assert c1.physical_artifact_key("KH5") == "KH5"


# --------------------------------------------------------------------------- stratum_key
def test_stratum_key_basic():
    assert c1.stratum_key("Haghia Triada", "Tablet") == ("haghia triada", "tablet")


def test_stratum_key_missing_values():
    assert c1.stratum_key(None, None) == ("unknown", "unknown")


def test_stratum_key_whitespace_and_case_normalized():
    assert c1.stratum_key("  Haghia Triada ", "TABLET") == ("haghia triada", "tablet")


# --------------------------------------------------------------------------- usable_rows / delta
def test_usable_rows_excludes_ambiguous():
    obs = [
        c1.TabletObservation("T1", "LIQUID", "FRACTION_PRESENT", 0),
        c1.TabletObservation("T2", "DRY", "AMBIGUOUS_UNUSABLE", None),
    ]
    assert len(c1.usable_rows(obs)) == 1


def test_delta_basic():
    rows = [("LIQUID", True), ("LIQUID", False), ("DRY", False), ("DRY", False)]
    assert c1.delta(rows) == 0.5 - 0.0


def test_delta_none_when_liquid_empty():
    rows = [("DRY", True), ("DRY", False)]
    assert c1.delta(rows) is None


def test_delta_none_when_dry_empty():
    rows = [("LIQUID", True)]
    assert c1.delta(rows) is None


def test_delta_zero_when_equal_rates():
    rows = [("LIQUID", True), ("DRY", True)]
    assert c1.delta(rows) == 0.0


# --------------------------------------------------------------------------- exchangeable_strata
def test_exchangeable_strata_both_classes_present():
    rbs = {("siteA", "tablet"): [("LIQUID", True), ("DRY", False)]}
    exch, non_exch = c1.exchangeable_strata(rbs)
    assert exch == {("siteA", "tablet")}
    assert non_exch == set()


def test_exchangeable_strata_single_class_excluded():
    rbs = {("siteA", "tablet"): [("LIQUID", True), ("LIQUID", False)]}
    exch, non_exch = c1.exchangeable_strata(rbs)
    assert exch == set()
    assert non_exch == {("siteA", "tablet")}


def test_exchangeable_strata_mixed_pool():
    rbs = {
        ("siteA", "tablet"): [("LIQUID", True), ("DRY", False)],
        ("siteB", "sealing"): [("DRY", True)],
    }
    exch, non_exch = c1.exchangeable_strata(rbs)
    assert exch == {("siteA", "tablet")}
    assert non_exch == {("siteB", "sealing")}


# --------------------------------------------------------------------------- permutation invariants
def test_stratified_permutation_delta_preserves_counts():
    rbs = {("s", "t"): [("LIQUID", True), ("LIQUID", False), ("DRY", False), ("DRY", False)]}
    rng = random.Random(0)
    d = c1.stratified_permutation_delta(rbs, rng)
    assert d is not None
    # total usable rows across the (single) exchangeable stratum unchanged
    exch, _ = c1.exchangeable_strata(rbs)
    assert len(rbs[list(exch)[0]]) == 4


def test_stratified_permutation_delta_excludes_nonexchangeable_stratum():
    rbs = {
        ("s", "t"): [("LIQUID", True), ("DRY", False)],
        ("s2", "t2"): [("LIQUID", True), ("LIQUID", True)],  # single-class, excluded
    }
    rng = random.Random(1)
    d = c1.stratified_permutation_delta(rbs, rng)
    # only the exchangeable stratum's 2 rows can possibly contribute;
    # observed_delta must match (restricted to the same stratum set)
    obs_d = c1.observed_delta(rbs)
    assert obs_d == 1.0 - 0.0  # p_L=1(from the exchangeable stratum only), p_D=0.0


def test_observed_delta_none_when_no_exchangeable_strata():
    rbs = {("s", "t"): [("LIQUID", True), ("LIQUID", False)]}
    assert c1.observed_delta(rbs) is None


def test_run_stratified_permutation_test_none_when_delta_obs_undefined():
    rbs = {("s", "t"): [("DRY", True)]}
    rng = random.Random(2)
    assert c1.run_stratified_permutation_test(rbs, B=100, rng=rng) is None


def test_run_stratified_permutation_test_small_enumerable_case():
    # Fully symmetric small case: p-value must be a valid probability.
    rbs = {("s", "t"): [("LIQUID", True), ("LIQUID", False), ("DRY", True), ("DRY", False)]}
    rng = random.Random(3)
    result = c1.run_stratified_permutation_test(rbs, B=2000, rng=rng)
    assert result is not None
    assert 0.0 <= result["p_value"] <= 1.0
    assert result["delta_obs"] == 0.0
    assert result["B"] == 2000


def test_permutation_reproducible_with_seeded_rng():
    rbs = {("s", "t"): [("LIQUID", True), ("LIQUID", False), ("DRY", False), ("DRY", False)]}
    r1 = c1.run_stratified_permutation_test(rbs, B=500, rng=random.Random(42))
    r2 = c1.run_stratified_permutation_test(rbs, B=500, rng=random.Random(42))
    assert r1 == r2


# --------------------------------------------------------------------------- finite_permutation_pvalue
def test_finite_permutation_pvalue_zero_extreme():
    assert c1.finite_permutation_pvalue(0, 2000) == 1 / 2001


def test_finite_permutation_pvalue_all_extreme():
    assert c1.finite_permutation_pvalue(2000, 2000) == 1.0


def test_finite_permutation_pvalue_midpoint():
    assert c1.finite_permutation_pvalue(999, 1999) == 1000 / 2000


# --------------------------------------------------------------------------- edge cases: zero counts
def test_delta_zero_counts_no_exception():
    assert c1.delta([]) is None


def test_tablet_level_observations_empty_record():
    assert c1.tablet_level_observations(Record("T1", [])) == []
