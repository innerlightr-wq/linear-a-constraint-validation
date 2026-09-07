"""
Synthetic schema-level tests for src/sigla_adapter.py.

ALL structures here are hand-constructed, modeled on this project's own
confirmed observations of the real SigLA schema (docs/SIGLA_SCHEMA_MAPPING.md)
-- NOT copied from, and not reproducing, substantial real SigLA transcription
content. Short syllable strings ("ku", "ro", "ki") are the same canonical
scholarly transliteration units already cited throughout this project
(kuro_protocol.py); document IDs used here (e.g. "SYN 1") are invented, not
real SigLA document IDs.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

import sigla_adapter as sa
from kuro_protocol import KURO_IDS, KIRO_IDS, POTOKURO_IDS
from ocaml_marshal_decoder import OcamlBlock


# --------------------------------------------------------------- Map fixtures
def leaf(key, value):
    """A single Map.Node with no children (Empty=0 on both sides), height 1."""
    return OcamlBlock(0, [0, key, value, 0, 1])


def node(left, key, value, right, height):
    return OcamlBlock(0, [left, key, value, right, height])


class TestMapTraversal:
    def test_empty_map(self):
        assert list(sa.map_items(0)) == []

    def test_single_node(self):
        m = leaf(b"HT1", b"value1")
        assert list(sa.map_items(m)) == [(b"HT1", b"value1")]

    def test_multi_node_inorder(self):
        # tree: root b, left a, right c -- inorder must yield a,b,c
        m = node(leaf(b"a", 1), b"b", 2, leaf(b"c", 3), 2)
        assert list(sa.map_items(m)) == [(b"a", 1), (b"b", 2), (b"c", 3)]

    def test_deep_chain_does_not_recursion_error(self):
        # left-leaning chain of 2000 nodes -- must not hit Python's
        # recursion limit (this project's own real-data exploration hit
        # exactly this failure mode with a naive recursive walk).
        m = 0
        for i in range(2000):
            m = node(m, i, i, 0, i + 1)
        items = list(sa.map_items(m))
        assert len(items) == 2000
        assert [k for k, v in items] == list(range(2000))


class TestOptionUnwrap:
    def test_none_is_zero(self):
        assert sa._opt(0) is None

    def test_some_unwraps_one_field_block(self):
        assert sa._opt(OcamlBlock(0, [b"x"])) == b"x"


# ---------------------------------------------------------- document extraction
def make_sign_entry(index, translit_syllable):
    """Minimal synthetic sign-attestation entry: an OcamlBlock carrying the
    index (plain int) and a nested block containing the transliteration
    syllable as a short lowercase-ascii bytes value -- matching the shape
    _collect_indexed_entries/_find_short_transliteration look for."""
    nested = OcamlBlock(0, [translit_syllable.encode("ascii"), 0])
    return OcamlBlock(0, [nested, index, 0, 0, 0])


def make_sign_array(syllables):
    """Chain the sign entries together (order doesn't matter for
    _collect_indexed_entries -- it sorts by the index field)."""
    entries = [make_sign_entry(i, s) for i, s in enumerate(syllables, start=1)]
    # nest them so the traversal has to walk through structure, not just a flat list
    root = 0
    for e in entries:
        root = OcamlBlock(0, [root, e])
    return root


def some(x):
    """OCaml Some(x), matching sigla_adapter._opt's expected shape."""
    return OcamlBlock(0, [x])


def make_doc_value(site: bytes, period: bytes, syllables: list):
    """Returns the UNWRAPPED 5-field document tuple [metadata, path,
    word_groups, dims, sign_array] -- matching what sa.extract_ordered_signs
    and sa.SiglaDocument.raw_value expect directly. Callers that place this
    as a Map VALUE (via leaf()/node()) must wrap it with some(...) first --
    real SigLA data stores Some(doc_tuple) as the map value, one extra
    `option` layer confirmed only via real-document validation (Task 6),
    not something the earlier version of this fixture modeled."""
    metadata = OcamlBlock(0, [
        b"Tablet", b"SYN 1", site, 0, 0, 0, 0,
        OcamlBlock(0, [period]),  # Some(period) at index 7
    ])
    sign_array = make_sign_array(syllables)
    return OcamlBlock(0, [metadata, b"document/SYN 1", 0, 0, sign_array])


class TestDocumentIteration:
    def test_tablet_id_and_site_extracted(self):
        doc_map = leaf(b"SYN 1", some(make_doc_value(b"Synthetic Site", b"LM IB", ["a"])))
        top = OcamlBlock(0, [doc_map])
        docs = list(sa.iter_documents(top))
        assert len(docs) == 1
        assert docs[0].tablet_id == "SYN 1"
        assert docs[0].site == "Synthetic Site"
        assert docs[0].period == "LM IB"

    def test_missing_metadata_does_not_crash(self):
        malformed_value = OcamlBlock(0, [0])  # metadata field is just 0 (None-shaped)
        doc_map = leaf(b"SYN BAD", malformed_value)
        top = OcamlBlock(0, [doc_map])
        docs = list(sa.iter_documents(top))
        assert docs[0].tablet_id == "SYN BAD"
        assert docs[0].site is None
        assert docs[0].period is None

    def test_multiple_documents_in_id_order(self):
        m = node(leaf(b"SYN A", some(make_doc_value(b"S1", b"P1", ["x"]))),
                  b"SYN B", some(make_doc_value(b"S2", b"P2", ["y"])),
                  leaf(b"SYN C", some(make_doc_value(b"S3", b"P3", ["z"]))), 2)
        top = OcamlBlock(0, [m])
        docs = list(sa.iter_documents(top))
        assert [d.tablet_id for d in docs] == ["SYN A", "SYN B", "SYN C"]


class TestOrderedSignExtraction:
    def test_extracts_syllables_in_index_order(self):
        doc_val = make_doc_value(b"Site", b"Period", ["ku", "ro", "si"])
        signs = sa.extract_ordered_signs(doc_val)
        assert signs == ["ku", "ro", "si"]

    def test_empty_sign_array(self):
        doc_val = make_doc_value(b"Site", b"Period", [])
        assert sa.extract_ordered_signs(doc_val) == []

    def test_malformed_document_value_returns_empty(self):
        assert sa.extract_ordered_signs(0) == []
        assert sa.extract_ordered_signs(OcamlBlock(0, [1, 2])) == []


class TestTargetDetection:
    def test_detects_kuro_adjacent_syllables(self):
        matches = sa.detect_targets(["si", "ku", "ro", "pa"])
        assert (1, 2, "KU-RO") in matches

    def test_detects_kiro(self):
        matches = sa.detect_targets(["ki", "ro"])
        assert (0, 2, "KI-RO") in matches

    def test_detects_potokuro_four_syllables(self):
        matches = sa.detect_targets(["po", "to", "ku", "ro"])
        assert (0, 4, "PO-TO-KU-RO") in matches

    def test_no_false_positive_on_non_adjacent_syllables(self):
        # 'ku' and 'ro' present but NOT adjacent -- must not match
        matches = sa.detect_targets(["ku", "si", "ro"])
        assert not any(label == "KU-RO" for _, _, label in matches)

    def test_case_insensitive_match(self):
        matches = sa.detect_targets(["KU", "RO"])
        assert (0, 2, "KU-RO") in matches

    def test_no_matches_on_empty_list(self):
        assert sa.detect_targets([]) == []


class TestFullPipeline:
    def test_kuro_occurrence_gets_canonical_sign_ids(self):
        doc_val = make_doc_value(b"Site", b"Period", ["si", "ku", "ro"])
        docs_top = OcamlBlock(0, [leaf(b"SYN 1", some(doc_val))])
        doc = next(sa.iter_documents(docs_top))
        record = sa.sigla_document_to_record(doc)
        kuro_tokens = [t for t in record.tokens if t.sign_ids == KURO_IDS]
        assert len(kuro_tokens) == 1

    def test_non_target_syllables_get_placeholder_ids(self):
        doc_val = make_doc_value(b"Site", b"Period", ["si", "pa"])
        docs_top = OcamlBlock(0, [leaf(b"SYN 1", some(doc_val))])
        doc = next(sa.iter_documents(docs_top))
        record = sa.sigla_document_to_record(doc)
        assert [t.sign_ids for t in record.tokens] == [("si",), ("pa",)]

    def test_tablet_id_preserved_in_record(self):
        doc_val = make_doc_value(b"Site", b"Period", ["a"])
        docs_top = OcamlBlock(0, [leaf(b"SYN 42", some(doc_val))])
        doc = next(sa.iter_documents(docs_top))
        record = sa.sigla_document_to_record(doc)
        assert record.tablet_id == "SYN 42"

    def test_no_numeral_tokens_produced_ever(self):
        # Numerals are OPEN/not implemented (docs/SIGLA_DATA_ADEQUACY_AUDIT.md)
        # -- this adapter must never silently fabricate a numeral token.
        doc_val = make_doc_value(b"Site", b"Period", ["ku", "ro"])
        docs_top = OcamlBlock(0, [leaf(b"SYN 1", some(doc_val))])
        doc = next(sa.iter_documents(docs_top))
        record = sa.sigla_document_to_record(doc)
        assert all(t.kind != "numeral" for t in record.tokens)

    def test_no_damage_or_uncertainty_ever_set(self):
        # Damage/uncertainty extraction is AMBIGUOUS/not implemented --
        # every token's damaged/sign_identity_uncertain flags must be their
        # dataclass default (False), never silently guessed True or False
        # from unconfirmed fields.
        doc_val = make_doc_value(b"Site", b"Period", ["ku", "ro", "si"])
        docs_top = OcamlBlock(0, [leaf(b"SYN 1", some(doc_val))])
        doc = next(sa.iter_documents(docs_top))
        record = sa.sigla_document_to_record(doc)
        assert all(t.damaged is False for t in record.tokens)
        assert all(t.sign_identity_uncertain is False for t in record.tokens)


class TestMalformedAndMissing:
    def test_empty_document_map(self):
        top = OcamlBlock(0, [0])
        assert list(sa.iter_documents(top)) == []

    def test_document_with_no_resolvable_signs(self):
        doc_val = OcamlBlock(0, [
            OcamlBlock(0, [b"Tablet", b"SYN X", b"Site", 0, 0, 0, 0, 0]),
            b"document/SYN X", 0, 0, 0,
        ])
        docs_top = OcamlBlock(0, [leaf(b"SYN X", some(doc_val))])
        doc = next(sa.iter_documents(docs_top))
        record = sa.sigla_document_to_record(doc)
        assert record.tokens == []

    def test_duplicate_document_ids_in_map_are_impossible_by_construction(self):
        # An OCaml Map.t cannot contain duplicate keys by construction
        # (insertion overwrites); this test documents that expectation
        # rather than asserting adapter-level dedup logic that doesn't
        # exist (none is needed).
        m = leaf(b"SYN 1", some(make_doc_value(b"S", b"P", ["a"])))
        top = OcamlBlock(0, [m])
        docs = list(sa.iter_documents(top))
        assert len(docs) == 1
