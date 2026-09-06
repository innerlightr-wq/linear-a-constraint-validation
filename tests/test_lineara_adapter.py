"""
Synthetic schema-level tests for src/lineara_adapter.py.

ALL raw dicts here are invented, shaped to match the schema documented in
docs/SCHEMA_MAPPING.md -- NOT copied from any real tablet's transcription.
`KU-RO`/`KI-RO`/`PO-TO-KU-RO` are the canonical scholarly transliteration
labels (already cited throughout kuro_protocol.py); the surrounding filler
words (agent/commodity placeholders) are invented, not real corpus content.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

import lineara_adapter as la
from kuro_protocol import KURO_IDS, KIRO_IDS, POTOKURO_IDS


def raw(name="SYN-A1", words=None, **extra):
    d = {"name": name, "site": "Synthetic Site", "findspot": "Synthetic Findspot",
         "scribe": None, "context": None, "support": "Tablet",
         "transliteratedWords": words or []}
    d.update(extra)
    return d


class TestTabletIdExtraction:
    def test_tablet_id_from_name_field(self):
        r = la.raw_tablet_to_record(raw(name="SYN-XYZ", words=["KU-RO", "10"]))
        assert r.tablet_id == "SYN-XYZ"

    def test_missing_metadata_does_not_crash(self):
        d = {"name": "SYN-NOMETA", "transliteratedWords": ["KU-RO", "5"]}
        r = la.raw_tablet_to_record(d)
        assert r.tablet_id == "SYN-NOMETA"
        assert len(r.tokens) == 2

    def test_missing_transliterated_words_yields_empty_record(self):
        d = {"name": "SYN-EMPTY"}
        r = la.raw_tablet_to_record(d)
        assert r.tablet_id == "SYN-EMPTY"
        assert r.tokens == []


class TestTokenOrderPreservation:
    def test_order_preserved(self):
        # "\n" is dropped (N1 correction, see TestRulingBoundaries) -- order
        # of the remaining, non-dropped tokens must still be preserved.
        words = ["AGENT-ONE", "\n", "AGENT-TWO", "4", "\n", "KU-RO", "4"]
        r = la.raw_tablet_to_record(raw(words=words))
        kinds = [t.kind for t in r.tokens]
        assert kinds == ["signgroup", "signgroup", "numeral",
                          "signgroup", "numeral"]


class TestTargetNormalization:
    def test_kuro_gets_canonical_ids(self):
        r = la.raw_tablet_to_record(raw(words=["KU-RO", "5"]))
        assert r.tokens[0].kind == "signgroup"
        assert r.tokens[0].sign_ids == KURO_IDS

    def test_kiro_gets_canonical_ids(self):
        r = la.raw_tablet_to_record(raw(words=["KI-RO", "5"]))
        assert r.tokens[0].sign_ids == KIRO_IDS

    def test_potokuro_gets_canonical_ids(self):
        r = la.raw_tablet_to_record(raw(words=["PO-TO-KU-RO", "5"]))
        assert r.tokens[0].sign_ids == POTOKURO_IDS

    def test_non_target_word_keeps_raw_string_as_placeholder_id(self):
        r = la.raw_tablet_to_record(raw(words=["ZU-SU-MA-NE", "5"]))
        assert r.tokens[0].sign_ids == ("ZU-SU-MA-NE",)

    def test_fallback_log_records_every_tablet(self):
        log = []
        la.raw_tablet_to_record(raw(name="SYN-LOG1", words=["KU-RO", "5"]), fallback_log=log)
        la.raw_tablet_to_record(raw(name="SYN-LOG2", words=["KI-RO", "5"]), fallback_log=log)
        assert [e["tablet_id"] for e in log] == ["SYN-LOG1", "SYN-LOG2"]


class TestNumeralDecoding:
    def test_plain_integer_numeral(self):
        r = la.raw_tablet_to_record(raw(words=["KU-RO", "42"]))
        assert r.tokens[1].kind == "numeral"
        assert r.tokens[1].value == 42.0

    def test_zero_is_a_valid_numeral(self):
        r = la.raw_tablet_to_record(raw(words=["KU-RO", "0"]))
        assert r.tokens[1].value == 0.0


class TestFractionDecoding:
    def test_fraction_merges_into_preceding_numeral(self):
        r = la.raw_tablet_to_record(raw(words=["KU-RO", "45", "¹⁄₂"]))
        total_tok = r.tokens[1]
        assert total_tok.kind == "numeral"
        assert total_tok.value == 45.0
        assert total_tok.fractions == [{"value": 0.5, "confidence": None}]

    def test_fraction_confidence_is_absent_not_invented(self):
        r = la.raw_tablet_to_record(raw(words=["KU-RO", "10", "¹⁄₄"]))
        frac = r.tokens[1].fractions[0]
        assert frac["confidence"] is None

    def test_fraction_alone_without_preceding_numeral_becomes_its_own_numeral(self):
        r = la.raw_tablet_to_record(raw(words=["KU-RO", "¹⁄₈"]))
        assert r.tokens[1].kind == "numeral"
        assert r.tokens[1].value is None
        assert r.tokens[1].fractions == [{"value": 0.125, "confidence": None}]

    def test_multiple_fraction_glyphs_accumulate(self):
        r = la.raw_tablet_to_record(raw(words=["KU-RO", "1", "¹⁄₂", "¹⁄₄"]))
        assert [f["value"] for f in r.tokens[1].fractions] == [0.5, 0.25]


class TestDamagePropagation:
    def test_bracket_in_signgroup_marks_damaged(self):
        r = la.raw_tablet_to_record(raw(words=["TE+RO[", "20"]))
        assert r.tokens[0].damaged is True

    def test_bracket_strips_from_sign_id(self):
        r = la.raw_tablet_to_record(raw(words=["TE+RO[", "20"]))
        assert r.tokens[0].sign_ids == ("TE+RO",)

    def test_question_mark_in_numeral_marks_damaged(self):
        r = la.raw_tablet_to_record(raw(words=["KU-RO", "5?"]))
        assert r.tokens[1].damaged is True

    def test_clean_word_is_not_damaged(self):
        r = la.raw_tablet_to_record(raw(words=["KU-RO", "5"]))
        assert r.tokens[0].damaged is False
        assert r.tokens[1].damaged is False

    def test_damaged_target_word_still_recognized(self):
        # A damaged KU-RO reading e.g. "KU-RO[" should still resolve to the
        # canonical target ids (with damage flagged), not fall through to
        # the generic placeholder branch.
        r = la.raw_tablet_to_record(raw(words=["KU-RO[", "5"]))
        assert r.tokens[0].sign_ids == KURO_IDS
        assert r.tokens[0].damaged is True


class TestRulingBoundaries:
    """N1 correction (see src/lineara_adapter.py module docstring): "\\n" is
    dropped, not mapped to Token(kind="ruling") -- found wrong via the first
    real-corpus run (every occurrence's preceding block was emptied, since
    this source places "\\n" between every entry, not only at true section
    boundaries). Fixed at the adapter level; the frozen protocol's Rule A
    definition (ruling / prior-total / start-of-tablet) is unchanged -- this
    source simply supplies no reliable ruling signal, so Rule A reduces to
    its other two conditions for this source."""

    def test_newline_is_dropped_not_a_ruling_token(self):
        r = la.raw_tablet_to_record(raw(words=["A", "\n", "B"]))
        kinds = [t.kind for t in r.tokens]
        assert kinds == ["signgroup", "signgroup"]

    def test_word_separator_is_also_dropped(self):
        r = la.raw_tablet_to_record(raw(words=["A", "\U00010101", "B"]))
        kinds = [t.kind for t in r.tokens]
        assert kinds == ["signgroup", "signgroup"]

    def test_consecutive_newlines_all_dropped(self):
        r = la.raw_tablet_to_record(raw(words=["A", "\n", "\n", "B"]))
        kinds = [t.kind for t in r.tokens]
        assert kinds == ["signgroup", "signgroup"]

    def test_no_ruling_token_kind_ever_produced_by_this_adapter(self):
        # Locks in the correction: this adapter (for this source) never
        # emits a ruling token at all -- Rule A relies on prior-total /
        # start-of-tablet only, per kuro_protocol.preceding_block's other
        # two boundary conditions.
        r = la.raw_tablet_to_record(raw(words=["A", "\n", "B", "\n", "KU-RO", "5"]))
        assert all(t.kind != "ruling" for t in r.tokens)

    def test_regression_multiple_newline_separated_entries_reach_kuro(self):
        # Reproduces the exact real-data pattern that exposed the bug
        # (tablet HT104's shape: heading, then several "\n"-separated
        # entries, then KU-RO): the preceding block must still reach back
        # through every entry, not stop at the "\n" immediately before
        # KU-RO.
        from kuro_protocol import preceding_block, numeral_value
        words = ["HEADING-WORD", "\n",
                 "AGENT-A", "45", "\n",
                 "AGENT-B", "20", "\n",
                 "AGENT-C", "29", "\n",
                 "KU-RO", "95"]
        r = la.raw_tablet_to_record(raw(words=words))
        kuro_idx = next(i for i, t in enumerate(r.tokens)
                         if t.kind == "signgroup" and t.sign_ids == KURO_IDS)
        block = preceding_block(r, kuro_idx, rule="A")
        assert [numeral_value(t) for t in block] == [45.0, 20.0, 29.0]


class TestMalformedRecords:
    def test_unrecognized_stray_symbol_treated_as_signgroup(self):
        r = la.raw_tablet_to_record(raw(words=["***"]))
        assert r.tokens[0].kind == "signgroup"
        assert r.tokens[0].sign_ids == ("***",)

    def test_empty_words_list(self):
        r = la.raw_tablet_to_record(raw(words=[]))
        assert r.tokens == []

    def test_none_name_does_not_crash_if_present_as_empty_string(self):
        d = {"name": "", "transliteratedWords": ["KU-RO", "1"]}
        r = la.raw_tablet_to_record(d)
        assert r.tablet_id == ""
