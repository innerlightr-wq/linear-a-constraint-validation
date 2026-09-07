"""
Tests for src/contextual_compression_feasibility.py.

Runs against the real, already-frozen primary corpus (same file, same
SHA-256, as V1/V2/H1 -- data/generated/lineara_extracted.json), because
this feasibility round's entire purpose is to report true facts about that
corpus's structure. No corpus data is modified. No hypothesis is tested
here -- these are structural/descriptive assertions only.
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import contextual_compression_feasibility as ccf  # noqa: E402

CORPUS_SHA256 = "219b52569cab75b58e95afb0a969689c6c50f753ce690321f20abbaff3a8eff8"


def test_corpus_checksum_matches_v1_v2_provenance():
    with open(ccf.CORPUS_PATH, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    assert digest == CORPUS_SHA256


def test_load_corpus_record_count():
    records = ccf.load_corpus()
    assert len(records) == 1721


def test_inscription_ids_are_unique():
    records = ccf.load_corpus()
    names = [r["name"] for r in records]
    assert len(names) == len(set(names))


# --------------------------------------------------------------------------- field availability
def test_field_availability_audit_covers_all_requested_fields():
    records = ccf.load_corpus()
    audit = ccf.field_availability_audit(records)
    expected_fields = {
        "inscription_id", "site", "object_tablet_id",
        "archaeological_context_period", "administrative_ritual_classification",
        "building_room_context", "object_type", "sign_sequence", "sign_count",
        "line_count", "numerals", "fractions", "commodities",
        "repeated_sign_groups", "findspot", "coordinates", "elevation",
        "chronology", "preservation_damaged_signs",
        "physical_artifact_dependence", "possible_scribal_attribution",
    }
    assert expected_fields <= set(audit.keys())
    valid = {"AVAILABLE", "DERIVABLE", "PARTIAL", "EXTERNAL DATA REQUIRED", "NOT AVAILABLE"}
    for field, info in audit.items():
        assert info["classification"] in valid
        assert info["usable_n"] >= 0


def test_coordinates_and_elevation_not_available():
    records = ccf.load_corpus()
    audit = ccf.field_availability_audit(records)
    assert audit["coordinates"]["classification"] == "NOT AVAILABLE"
    assert audit["coordinates"]["usable_n"] == 0
    assert audit["elevation"]["classification"] == "NOT AVAILABLE"
    assert audit["elevation"]["usable_n"] == 0


def test_administrative_classification_not_available():
    records = ccf.load_corpus()
    audit = ccf.field_availability_audit(records)
    assert audit["administrative_ritual_classification"]["classification"] == "NOT AVAILABLE"


def test_inscription_id_and_site_available_with_expected_n():
    records = ccf.load_corpus()
    audit = ccf.field_availability_audit(records)
    assert audit["inscription_id"]["classification"] == "AVAILABLE"
    assert audit["inscription_id"]["usable_n"] == 1721
    assert audit["site"]["classification"] == "AVAILABLE"
    assert audit["site"]["usable_n"] == 1718


# --------------------------------------------------------------------------- distributions
def test_site_distribution_matches_known_counts():
    records = ccf.load_corpus()
    dist = ccf.categorical_distribution(records, "site")
    assert dist["n_non_null"] == 1718
    assert dist["n_missing"] == 3
    assert dist["n_unique"] == 52
    assert dist["counts"]["Haghia Triada"] == 1110


def test_support_distribution_matches_known_counts():
    records = ccf.load_corpus()
    dist = ccf.categorical_distribution(records, "support")
    assert dist["n_non_null"] == 1721
    assert dist["n_unique"] == 19
    assert dist["counts"]["Nodule"] == 890
    assert dist["counts"]["Tablet"] == 435


def test_scribe_distribution_matches_known_counts():
    records = ccf.load_corpus()
    dist = ccf.categorical_distribution(records, "scribe")
    assert dist["n_non_null"] == 592
    assert dist["n_unique"] == 102


def test_context_distribution_dominated_by_single_period():
    records = ccf.load_corpus()
    dist = ccf.categorical_distribution(records, "context")
    assert dist["n_non_null"] == 1390
    assert dist["counts"]["LMIB"] == 1310  # >90% of the non-null values


# --------------------------------------------------------------------------- nesting / dependence
def test_scribe_perfectly_nested_within_site():
    records = ccf.load_corpus()
    result = ccf.nesting_check(records, "scribe", "site")
    assert result["perfectly_nested"] is True
    assert result["n_violations"] == 0
    assert result["n_child_values"] == 102


def test_findspot_perfectly_nested_within_site():
    records = ccf.load_corpus()
    result = ccf.nesting_check(records, "findspot", "site")
    assert result["perfectly_nested"] is True
    assert result["n_child_values"] == 10


def test_nesting_check_detects_violation_on_constructed_example():
    fake_records = [
        {"scribe": "S1", "site": "A"},
        {"scribe": "S1", "site": "B"},  # S1 now spans two sites -- a violation
    ]
    result = ccf.nesting_check(fake_records, "scribe", "site")
    assert result["perfectly_nested"] is False
    assert result["n_violations"] == 1
    assert result["violations"]["S1"] == ["A", "B"]


# --------------------------------------------------------------------------- sign length
def test_sign_length_distribution_is_short_and_skewed():
    records = ccf.load_corpus()
    dist = ccf.sign_length_distribution(records)
    assert dist["n"] == 1721
    assert dist["sign_count"]["median"] == 1
    assert dist["sign_count"]["min"] == 0
    assert dist["sign_count"]["n_zero"] > 0


def test_per_record_token_stats_shape():
    stats = ccf.per_record_token_stats({
        "name": "TEST1",
        "transliteratedWords": ["A-B", "10", "\n", "A-B", "C-D"],
    })
    assert stats["sign_count"] == 3
    assert stats["distinct_sign_count"] == 2
    assert stats["numeral_count"] == 1
    assert stats["line_marker_count"] == 1


# --------------------------------------------------------------------------- site concentration
def test_site_concentration_shows_extreme_dominance():
    records = ccf.load_corpus()
    conc = ccf.site_concentration(records)
    assert conc["n_sites"] == 52
    assert conc["top_site"][0] == "Haghia Triada"
    assert conc["top_site_share"] > 0.6
    assert conc["n_sites_with_ge_30"] < 10  # most sites are far too thin


# --------------------------------------------------------------------------- fragment joins
def test_fragment_join_ids_found():
    records = ccf.load_corpus()
    joins = ccf.fragment_join_ids(records)
    assert "HT42+59" in joins
    assert len(joins) == 9


# --------------------------------------------------------------------------- confound diagnostics
def test_mutual_information_categorical_zero_for_independent_construction():
    fake_records = [
        {"A": "x", "B": "p"}, {"A": "x", "B": "q"},
        {"A": "y", "B": "p"}, {"A": "y", "B": "q"},
    ]
    result = ccf.mutual_information_categorical(fake_records, "A", "B")
    assert abs(result["I_bits"]) < 1e-9


def test_mutual_information_categorical_positive_for_deterministic_construction():
    fake_records = [{"A": "x", "B": "p"}, {"A": "x", "B": "p"}, {"A": "y", "B": "q"}]
    result = ccf.mutual_information_categorical(fake_records, "A", "B")
    assert result["I_bits"] > 0.9  # near-total mutual determination

def test_support_x_site_shows_real_confounding():
    records = ccf.load_corpus()
    result = ccf.mutual_information_categorical(records, "support", "site")
    assert result["I_bits"] > 0
    assert result["normalized_I"] is not None
    assert 0 < result["normalized_I"] <= 1.0001


# --------------------------------------------------------------------------- n-gram feasibility
def test_ngram_feasibility_pools_across_records():
    records = ccf.load_corpus()
    uni = ccf.corpus_ngram_feasibility(records, 1)
    bi = ccf.corpus_ngram_feasibility(records, 2)
    assert uni["total_ngram_occurrences"] > 0
    assert bi["total_ngram_occurrences"] < uni["total_ngram_occurrences"]
    assert uni["hapax_fraction"] is not None


# --------------------------------------------------------------------------- full audit assembly
def test_run_full_audit_assembles_all_sections():
    audit = ccf.run_full_audit()
    assert audit["n_records"] == 1721
    for key in ("field_availability", "distributions", "nesting",
                "sign_length_distribution", "site_concentration",
                "fragment_joins", "confound_diagnostics", "ngram_feasibility"):
        assert key in audit
