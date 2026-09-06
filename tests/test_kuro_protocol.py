"""
Synthetic tests for src/kuro_protocol.py.

ALL data here is invented. Nothing in this file is a real Linear A tablet
transcription -- per this project's own policy (no real corpus snippets in
committed tests while licensing of the source corpus is unresolved), and
because the point of this phase is to verify the protocol's *logic*, not to
look at any real result.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

import kuro_protocol as kp
from kuro_protocol import Token, Record


def sg(ids, damaged=False, uncertain=False):
    return Token(kind="signgroup", sign_ids=tuple(ids), damaged=damaged,
                 sign_identity_uncertain=uncertain)


def num(value=None, fractions=None, damaged=False):
    return Token(kind="numeral", value=value, fractions=fractions, damaged=damaged)


def rule():
    return Token(kind="ruling")


# --------------------------------------------------------------------- occurrence extraction
class TestOccurrenceExtraction:
    def test_finds_kuro(self):
        r = Record("SYN1", [sg(["A100"]), num(5), sg(kp.KURO_IDS), num(5)])
        assert kp.find_occurrences(r, "KU-RO") == [2]

    def test_does_not_confuse_kiro_with_kuro(self):
        r = Record("SYN2", [sg(kp.KIRO_IDS), num(3)])
        assert kp.find_occurrences(r, "KU-RO") == []
        assert kp.find_occurrences(r, "KI-RO") == [0]

    def test_finds_multiple_kuro_in_one_tablet(self):
        r = Record("SYN3", [
            sg(["A1"]), num(2), sg(kp.KURO_IDS), num(2),
            sg(["A2"]), num(3), sg(kp.KURO_IDS), num(3),
        ])
        assert kp.find_occurrences(r, "KU-RO") == [2, 6]

    def test_no_occurrence_in_tablet_without_totals(self):
        r = Record("SYN4", [sg(["A1"]), num(5), sg(["A2"]), num(2)])
        assert kp.find_occurrences(r, "KU-RO") == []


# --------------------------------------------------------------------- terminal classification
class TestTerminalClassification:
    def test_terminal_when_last_signgroup(self):
        r = Record("SYN5", [sg(["A1"]), num(2), sg(kp.KURO_IDS), num(2)])
        assert kp.classify_position(r, 2) == "TERMINAL"

    def test_terminal_ignores_trailing_ruling(self):
        r = Record("SYN6", [sg(["A1"]), num(2), sg(kp.KURO_IDS), num(2), rule()])
        assert kp.classify_position(r, 2) == "TERMINAL"

    def test_near_terminal_at_threshold(self):
        # exactly 2 following signgroups -> NEAR_TERMINAL (declared threshold)
        r = Record("SYN7", [sg(kp.KURO_IDS), num(2), sg(["B1"]), sg(["B2"])])
        assert kp.classify_position(r, 0) == "NEAR_TERMINAL"

    def test_non_terminal_beyond_threshold(self):
        r = Record("SYN8", [sg(kp.KURO_IDS), num(2), sg(["B1"]), sg(["B2"]), sg(["B3"])])
        assert kp.classify_position(r, 0) == "NON_TERMINAL"

    def test_one_following_signgroup_is_near_terminal(self):
        r = Record("SYN9", [sg(kp.KURO_IDS), num(2), sg(["B1"])])
        assert kp.classify_position(r, 0) == "NEAR_TERMINAL"


# --------------------------------------------------------------------- numeral association
class TestNumeralAssociation:
    def test_associates_immediately_following_numeral(self):
        r = Record("SYN10", [sg(kp.KURO_IDS), num(7)])
        t = kp.associated_numeral(r, 0)
        assert t is not None and kp.numeral_value(t) == 7.0

    def test_no_numeral_if_next_token_is_signgroup(self):
        r = Record("SYN11", [sg(kp.KURO_IDS), sg(["B1"]), num(7)])
        assert kp.associated_numeral(r, 0) is None

    def test_no_numeral_if_next_token_is_ruling(self):
        r = Record("SYN12", [sg(kp.KURO_IDS), rule(), num(7)])
        assert kp.associated_numeral(r, 0) is None

    def test_no_numeral_at_end_of_record(self):
        r = Record("SYN13", [sg(kp.KURO_IDS)])
        assert kp.associated_numeral(r, 0) is None


# --------------------------------------------------------------------- fractions
class TestFractions:
    def test_fraction_value_sums_admitted_confidence_only(self):
        t = num(fractions=[{"value": 0.5, "confidence": "secure"},
                            {"value": 0.25, "confidence": "derived"},
                            {"value": 0.125, "confidence": "open"}])
        assert kp.numeral_value(t) == pytest.approx(0.75)

    def test_fraction_all_unadmitted_confidence_is_unresolved(self):
        t = num(fractions=[{"value": 0.5, "confidence": "open"}])
        assert kp.numeral_value(t) is None

    def test_whole_number_label_takes_precedence_over_fractions(self):
        t = num(value=10, fractions=[{"value": 0.5, "confidence": "secure"}])
        assert kp.numeral_value(t) == 10.0

    def test_direct_and_fraction_can_combine_when_recorded_as_one_token_sum(self):
        # HT104-style composite value, entered here as a synthetic single
        # fraction-sum token (whole-number component modeled as its own
        # 'secure' fraction entry of integer value, per this project's own
        # token schema -- not a real tablet).
        t = num(fractions=[{"value": 45.0, "confidence": "secure"},
                            {"value": 0.5, "confidence": "secure"}])
        assert kp.numeral_value(t) == pytest.approx(45.5)


# --------------------------------------------------------------------- summation / residual
class TestSummationAndResidual:
    def test_exact_closure(self):
        r, r_rel = kp.residual(10.0, [4.0, 6.0])
        assert r == 0.0
        assert kp.classify_arithmetic(r, r_rel, damaged=False) == "EXACT_CLOSURE"

    def test_rounding_compatible_absolute(self):
        r, r_rel = kp.residual(26.0, [25.83])
        assert kp.classify_arithmetic(r, r_rel, damaged=False) == "ROUNDING_COMPATIBLE"

    def test_rounding_compatible_relative(self):
        # 4% off, exceeds absolute-1.0 rule at this scale but within 5% relative
        r, r_rel = kp.residual(100.0, [96.0])
        assert kp.classify_arithmetic(r, r_rel, damaged=False) == "ROUNDING_COMPATIBLE"

    def test_unexplained_mismatch(self):
        r, r_rel = kp.residual(100.0, [50.0])
        assert kp.classify_arithmetic(r, r_rel, damaged=False) == "UNEXPLAINED_MISMATCH"

    def test_residual_sign_convention(self):
        r, _ = kp.residual(10.0, [12.0])
        assert r == -2.0

    def test_r_rel_undefined_when_total_zero(self):
        r, r_rel = kp.residual(0.0, [0.0])
        assert r_rel is None


# --------------------------------------------------------------------- damage / uncertainty
class TestDamageExclusion:
    def test_damage_on_total_token_overrides_small_residual(self):
        r, r_rel = kp.residual(10.0, [10.0])
        assert kp.classify_arithmetic(r, r_rel, damaged=True) == "DAMAGED_OR_UNCERTAIN"

    def test_classify_exclusion_ambiguous_sign_identity(self):
        occ = sg(kp.KURO_IDS, uncertain=True)
        total = num(10)
        block = [num(10)]
        assert kp.classify_exclusion(occ, total, block) == "AMBIGUOUS"

    def test_classify_exclusion_missing_no_total(self):
        occ = sg(kp.KURO_IDS)
        block = [num(10)]
        assert kp.classify_exclusion(occ, None, block) == "MISSING"

    def test_classify_exclusion_missing_empty_block(self):
        occ = sg(kp.KURO_IDS)
        total = num(10)
        assert kp.classify_exclusion(occ, total, []) == "MISSING"

    def test_classify_exclusion_damaged_block_numeral(self):
        occ = sg(kp.KURO_IDS)
        total = num(10)
        block = [num(4), num(6, damaged=True)]
        assert kp.classify_exclusion(occ, total, block) == "DAMAGED"

    def test_classify_exclusion_none_when_clean(self):
        occ = sg(kp.KURO_IDS)
        total = num(10)
        block = [num(4), num(6)]
        assert kp.classify_exclusion(occ, total, block) is None


# --------------------------------------------------------------------- preceding block / sectioning
class TestPrecedingBlock:
    def test_block_bounded_by_ruling(self):
        r = Record("SYN14", [num(99), rule(), sg(["A1"]), num(4), sg(["A2"]), num(6),
                              sg(kp.KURO_IDS), num(10)])
        block = kp.preceding_block(r, 6, rule="A")
        assert [kp.numeral_value(t) for t in block] == [4.0, 6.0]

    def test_block_bounded_by_prior_total(self):
        r = Record("SYN15", [sg(["A1"]), num(1), sg(kp.KURO_IDS), num(1),
                              sg(["A2"]), num(2), sg(["A3"]), num(3),
                              sg(kp.KURO_IDS), num(5)])
        block = kp.preceding_block(r, 8, rule="A")
        assert [kp.numeral_value(t) for t in block] == [2.0, 3.0]

    def test_block_from_start_of_record_if_no_boundary(self):
        r = Record("SYN16", [sg(["A1"]), num(2), sg(["A2"]), num(3), sg(kp.KURO_IDS), num(5)])
        block = kp.preceding_block(r, 4, rule="A")
        assert [kp.numeral_value(t) for t in block] == [2.0, 3.0]

    def test_rule_b_commodity_heading_bounds_block(self):
        commodities = {"VIN"}
        r = Record("SYN17", [
            sg(["VIN"]),               # heading: commodity NOT followed by numeral
            sg(["A1"]), num(4),
            sg(["A2"]), num(6),
            sg(kp.KURO_IDS), num(10),
        ])
        block_a = kp.preceding_block(r, 5, rule="A")
        block_b = kp.preceding_block(r, 5, rule="B", commodity_ids=commodities)
        assert [kp.numeral_value(t) for t in block_a] == [4.0, 6.0]
        assert [kp.numeral_value(t) for t in block_b] == [4.0, 6.0]  # heading is at index 0, block starts at 1 either way here

    def test_rule_b_inline_commodity_is_not_a_heading(self):
        commodities = {"VIN"}
        r = Record("SYN18", [
            sg(["VIN"]), num(1),   # inline entry, not a heading
            sg(["A2"]), num(6),
            sg(kp.KURO_IDS), num(7),
        ])
        block_b = kp.preceding_block(r, 4, rule="B", commodity_ids=commodities)
        assert [kp.numeral_value(t) for t in block_b] == [1.0, 6.0]


# --------------------------------------------------------------------- duplicates / multiple entries
class TestDuplicatesAndMultipleEntries:
    def test_duplicate_kuro_occurrences_indexed_separately(self):
        r = Record("SYN19", [
            sg(["A1"]), num(2), sg(kp.KURO_IDS), num(2),
            sg(["B1"]), num(3), sg(kp.KURO_IDS), num(3),
        ])
        occs = kp.find_occurrences(r, "KU-RO")
        assert len(occs) == 2
        block0 = kp.preceding_block(r, occs[0], rule="A")
        block1 = kp.preceding_block(r, occs[1], rule="A")
        assert [kp.numeral_value(t) for t in block0] == [2.0]
        assert [kp.numeral_value(t) for t in block1] == [3.0]

    def test_potokuro_distinct_from_kuro(self):
        r = Record("SYN20", [sg(kp.KURO_IDS), num(4), sg(kp.POTOKURO_IDS), num(4)])
        assert kp.find_occurrences(r, "KU-RO") == [0]
        assert kp.find_occurrences(r, "PO-TO-KU-RO") == [2]


# --------------------------------------------------------------------- missing / malformed
class TestMissingAndMalformed:
    def test_empty_record_yields_no_occurrences(self):
        r = Record("SYN21", [])
        assert kp.find_occurrences(r, "KU-RO") == []

    def test_signgroup_with_no_sign_ids_is_not_a_match(self):
        t = Token(kind="signgroup", sign_ids=None)
        r = Record("SYN22", [t])
        assert kp.find_occurrences(r, "KU-RO") == []

    def test_numeral_with_no_value_and_no_fractions_is_unresolved(self):
        t = num()
        assert kp.numeral_value(t) is None

    def test_non_comparable_when_rules_disagree_on_classification(self):
        commodities = {"VIN"}
        r = Record("SYN23", [
            sg(["VIN"]), num(1),          # inline under Rule A scope, heading-adjacent under B
            sg(["A2"]), num(100),
            sg(kp.KURO_IDS), num(101),
        ])
        idx = 4
        occ = r.tokens[idx]
        total = kp.associated_numeral(r, idx)
        block_a = kp.preceding_block(r, idx, rule="A")
        block_b = kp.preceding_block(r, idx, rule="B", commodity_ids=commodities)
        result = kp.classify_exclusion(occ, total, block_a, block_b)
        # Rule A includes the inline VIN=1 (sum 101, exact); Rule B does not
        # change anything here since VIN is inline (not a heading) either
        # way -- included as a negative control: rules agree, so this must
        # NOT be flagged NON_COMPARABLE.
        assert result is None


# --------------------------------------------------------------------- verdict
class TestVerdict:
    def test_support(self):
        assert kp.verdict(0.05, 0.05, n_arithmetically_testable=20,
                           not_testable_or_damaged_fraction=0.1) == "SUPPORT"

    def test_weakening_on_arithmetic_only(self):
        assert kp.verdict(0.05, 0.15, n_arithmetically_testable=20,
                           not_testable_or_damaged_fraction=0.1) == "WEAKENING"

    def test_failure_on_positional(self):
        assert kp.verdict(0.15, 0.05, n_arithmetically_testable=20,
                           not_testable_or_damaged_fraction=0.1) == "FAILURE"

    def test_inconclusive_small_sample(self):
        assert kp.verdict(0.05, 0.05, n_arithmetically_testable=5,
                           not_testable_or_damaged_fraction=0.1) == "INCONCLUSIVE"

    def test_inconclusive_corpus_inadequate(self):
        assert kp.verdict(0.05, 0.05, n_arithmetically_testable=20,
                           not_testable_or_damaged_fraction=0.6) == "INCONCLUSIVE"

    def test_positional_falsified_dominates_even_with_good_arithmetic(self):
        assert kp.verdict(0.25, 0.0, n_arithmetically_testable=50,
                           not_testable_or_damaged_fraction=0.0) == "FAILURE"
