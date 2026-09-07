"""
Contextual compression x geography -- FEASIBILITY / IDENTIFIABILITY audit.

FEASIBILITY ROUND ONLY. This module computes descriptive, structural facts
about the already-extracted primary corpus (`data/generated/lineara_extracted.json`,
same file and same SHA-256 as V1/V2/H1 -- not re-extracted, not modified) --
field availability, usable N, categorical distributions, dependence/nesting
structure, and confound-risk diagnostics.

It does NOT:
  - compute or test any compression score against any outcome
  - fit any model
  - run any permutation/significance test
  - attach any geography (no coordinate data exists in this corpus at all --
    see `field_availability_audit`, item "coordinates")
  - classify any inscription's archaeological function (administrative /
    ritual / domestic / ...) -- no such field exists in this source, and per
    this round's own instruction, that classification must not be derived
    from the inscription statistics being tested

Every number returned by this module is a DESCRIPTIVE fact about corpus
structure or a FEASIBILITY diagnostic (e.g. mutual information between two
*design* variables, used only to flag confounding risk before any test is
designed) -- never a claim about geography's or context's relationship to
inscription structure. See results/CONTEXTUAL_COMPRESSION_FEASIBILITY.md for
the interpretive write-up this module supports.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
import statistics
from collections import Counter, defaultdict
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lineara_adapter import (  # noqa: E402
    is_numeral_string,
    is_fraction_glyph,
    is_damaged_string,
    WORD_SEPARATOR,
    LINE_BREAK,
)

CORPUS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "generated", "lineara_extracted.json"
)


# =============================================================================
# Loading
# =============================================================================
def load_corpus(path: str = CORPUS_PATH) -> list[dict]:
    """Loads the already-extracted corpus verbatim. Does not touch
    data/raw/, does not re-run extraction, does not modify the file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# Token classification (reuses lineara_adapter's own predicates -- no new
# parsing rule is invented here)
# =============================================================================
def is_signgroup_token(w: str) -> bool:
    if w in (LINE_BREAK, WORD_SEPARATOR):
        return False
    if is_numeral_string(w):
        return False
    if is_fraction_glyph(w):
        return False
    return True


def per_record_token_stats(record: dict) -> dict:
    """Per-inscription counts, computed directly from `transliteratedWords`,
    using only already-validated adapter predicates. No new normalization
    rule is introduced."""
    words = record.get("transliteratedWords") or []
    signgroups = [w for w in words if is_signgroup_token(w)]
    numerals = [w for w in words if is_numeral_string(w)]
    fractions = [w for w in words if is_fraction_glyph(w)]
    line_markers = [w for w in words if w == LINE_BREAK]
    damaged_signgroups = [w for w in signgroups if is_damaged_string(w)]
    damaged_numerals = [w for w in numerals if is_damaged_string(w)]
    return {
        "tablet_id": record.get("name"),
        "sign_count": len(signgroups),
        "distinct_sign_count": len(set(signgroups)),
        "numeral_count": len(numerals),
        "fraction_count": len(fractions),
        "line_marker_count": len(line_markers),
        "damaged_signgroup_count": len(damaged_signgroups),
        "damaged_numeral_count": len(damaged_numerals),
        "total_token_count": len(words),
    }


# =============================================================================
# TASK 1 -- field availability audit
# =============================================================================
def field_availability_audit(records: list[dict]) -> dict:
    """Classifies each field requested by the round's Task 1 as AVAILABLE /
    DERIVABLE / PARTIAL / EXTERNAL DATA REQUIRED / NOT AVAILABLE, with
    usable N computed directly from the corpus where the field is present
    in any form. Classifications for fields with NO corresponding raw key
    (coordinates, elevation, admin/ritual classification, building/room
    beyond findspot's own text, scribal identity beyond the bare `scribe`
    label) are fixed facts about this corpus's schema (cross-checked against
    docs/SCHEMA_MAPPING.md and docs/CORPUS_PROVENANCE.md), not inferred or
    guessed here."""
    n = len(records)

    def present(field):
        return sum(1 for r in records if r.get(field) not in (None, ""))

    tok_stats = [per_record_token_stats(r) for r in records]
    n_with_signs = sum(1 for t in tok_stats if t["sign_count"] > 0)
    n_with_numerals = sum(1 for t in tok_stats if t["numeral_count"] > 0)
    n_with_fractions = sum(1 for t in tok_stats if t["fraction_count"] > 0)
    n_with_line_markers = sum(1 for t in tok_stats if t["line_marker_count"] > 0)
    n_with_any_damage = sum(
        1 for t in tok_stats if t["damaged_signgroup_count"] + t["damaged_numeral_count"] > 0
    )
    n_fragment_joins = sum(1 for r in records if "+" in (r.get("name") or ""))

    return {
        "inscription_id": {
            "classification": "AVAILABLE",
            "usable_n": n,
            "basis": "`name` field, unique per record (verified: 0 duplicates)",
        },
        "site": {
            "classification": "AVAILABLE",
            "usable_n": present("site"),
            "basis": "`site` field, direct string",
        },
        "object_tablet_id": {
            "classification": "AVAILABLE",
            "usable_n": n,
            "basis": "same as inscription_id -- this corpus has no separate "
                     "record-vs-physical-object key (see physical_artifact_dependence)",
        },
        "archaeological_context_period": {
            "classification": "PARTIAL",
            "usable_n": present("context"),
            "basis": "`context` field is a CHRONOLOGICAL PERIOD label (e.g. "
                     "'LMIB'), not an archaeological FUNCTION/context "
                     "classification (administrative/ritual/domestic/...). "
                     "Present for the majority but heavily concentrated on "
                     "one value (see categorical_distribution('context')).",
        },
        "administrative_ritual_classification": {
            "classification": "NOT AVAILABLE",
            "usable_n": 0,
            "basis": "No field in this corpus encodes archaeological "
                     "function/use-category. `support` (physical medium) and "
                     "`findspot` (room/building label) are the closest proxies "
                     "but neither is a function classification, and building "
                     "either into one without independent literature would "
                     "risk classifying by the very statistics under test "
                     "(explicitly disallowed this round -- see Task 3).",
        },
        "building_room_context": {
            "classification": "PARTIAL",
            "usable_n": present("findspot"),
            "basis": "`findspot` gives a room/building-level free-text label "
                     "(e.g. 'Portico 11 and Room 13') for a minority of "
                     "records, concentrated on Haghia Triada; only 10 "
                     "distinct values exist across the whole corpus.",
        },
        "object_type": {
            "classification": "AVAILABLE",
            "usable_n": present("support"),
            "basis": "`support` field (physical medium/object type, e.g. "
                     "'Tablet', 'Nodule', 'Roundel'), present for every "
                     "record with a non-null value.",
        },
        "sign_sequence": {
            "classification": "AVAILABLE",
            "usable_n": n_with_signs,
            "basis": "`transliteratedWords`, order-preserving, filtered to "
                     "signgroup tokens via the already-validated adapter "
                     "predicates (no new parsing rule).",
        },
        "sign_count": {
            "classification": "DERIVABLE",
            "usable_n": n,
            "basis": "len(signgroup tokens) per record -- directly computed, "
                     "see sign_length_distribution.",
        },
        "line_count": {
            "classification": "PARTIAL",
            "usable_n": n_with_line_markers,
            "basis": "raw '\\n' markers exist in `transliteratedWords`, but "
                     "docs/SCHEMA_MAPPING.md's own N1 correction found this "
                     "source places '\\n' between EVERY entry, not only true "
                     "physical line breaks -- so a '\\n' count is an ENTRY-count "
                     "proxy, not a validated physical-line count. Usable only "
                     "with this caveat disclosed, never as a clean line count.",
        },
        "numerals": {
            "classification": "AVAILABLE",
            "usable_n": n_with_numerals,
            "basis": "plain decimal-string tokens, same extraction as H1/V1/V2.",
        },
        "fractions": {
            "classification": "DERIVABLE",
            "usable_n": n_with_fractions,
            "basis": "Unicode fraction glyphs, same extraction as H1/V1/V2 "
                     "(N2 merging rule); fraction CONFIDENCE grading remains "
                     "MISSING from this source (unchanged from H1/V2 finding).",
        },
        "commodities": {
            "classification": "EXTERNAL DATA REQUIRED",
            "usable_n": 0,
            "basis": "commodity-ideogram identity is not a labeled field; "
                     "the prior round's LIQUID/DRY classification "
                     "(docs/CONSTRAINT_SPACE_DATA_AUDIT.md, "
                     "docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md) already "
                     "required an EXTERNAL DOMAIN MODEL INPUT (Linear B "
                     "homology); unchanged here, not recomputed.",
        },
        "repeated_sign_groups": {
            "classification": "PARTIAL",
            "usable_n": n_with_signs,
            "basis": "computable CORPUS-WIDE (cross-record n-gram/sign-group "
                     "frequency, exactly what H1's own occurrence counting "
                     "already does) but the median per-record sign count is "
                     "very low (see sign_length_distribution) -- WITHIN-record "
                     "repetition structure is not meaningfully measurable for "
                     "most individual inscriptions.",
        },
        "findspot": {
            "classification": "PARTIAL",
            "usable_n": present("findspot"),
            "basis": "same field as building_room_context.",
        },
        "coordinates": {
            "classification": "NOT AVAILABLE",
            "usable_n": 0,
            "basis": "no latitude/longitude field or value exists anywhere "
                     "in this corpus or in any file previously ingested by "
                     "this project (confirmed by repo-wide search); would "
                     "have to be attached externally, by site name, from a "
                     "published gazetteer.",
        },
        "elevation": {
            "classification": "NOT AVAILABLE",
            "usable_n": 0,
            "basis": "same as coordinates -- no field exists; external "
                     "attachment only, and elevation is not a substitute for "
                     "the underlying terrain-cost/mobility model needed to "
                     "interpret it (see Task 4 discussion).",
        },
        "chronology": {
            "classification": "PARTIAL",
            "usable_n": present("context"),
            "basis": "same field as archaeological_context_period -- reused "
                     "here for its temporal-ordering sense, not its function "
                     "sense. 11 distinct period labels, extremely unevenly "
                     "distributed (see categorical_distribution('context')).",
        },
        "preservation_damaged_signs": {
            "classification": "DERIVABLE",
            "usable_n": n_with_any_damage,
            "basis": "bracket/'?' characters embedded in transliterated "
                     "strings, same convention as H1's adapter "
                     "(is_damaged_string) -- undifferentiated between "
                     "physical damage and disputed reading (unchanged, "
                     "already-disclosed limitation).",
        },
        "physical_artifact_dependence": {
            "classification": "PARTIAL",
            "usable_n": n_fragment_joins,
            "basis": "a minority of `name` values encode an explicit "
                     "fragment join (e.g. 'HT123+124a', 'HT42+59'), meaning "
                     "more than one physical fragment was combined into one "
                     "record; the remaining majority cannot be checked for "
                     "undisclosed joins/refits without external epigraphic "
                     "literature -- see dependence_structure_audit.",
        },
        "possible_scribal_attribution": {
            "classification": "PARTIAL",
            "usable_n": present("scribe"),
            "basis": "`scribe` field, a curated attribution (not this "
                     "project's own inference), present for a minority of "
                     "records, always nested within exactly one site (see "
                     "nesting_check).",
        },
    }


# =============================================================================
# Distributions and nesting / dependence
# =============================================================================
def categorical_distribution(records: list[dict], field: str) -> dict:
    values = [r.get(field) for r in records]
    non_null = [v for v in values if v not in (None, "")]
    counts = Counter(non_null)
    return {
        "field": field,
        "n_total": len(records),
        "n_non_null": len(non_null),
        "n_missing": len(records) - len(non_null),
        "n_unique": len(counts),
        "counts": dict(counts.most_common()),
    }


def nesting_check(records: list[dict], child_field: str, parent_field: str) -> dict:
    """Checks whether every non-null value of `child_field` maps to exactly
    one value of `parent_field` across the corpus (e.g. scribe -> site,
    findspot -> site). This is a DEPENDENCE-STRUCTURE fact, not a
    statistical test."""
    child_to_parents: dict = defaultdict(set)
    for r in records:
        c = r.get(child_field)
        p = r.get(parent_field)
        if c not in (None, "") and p not in (None, ""):
            child_to_parents[c].add(p)
    violations = {c: sorted(p) for c, p in child_to_parents.items() if len(p) > 1}
    return {
        "child_field": child_field,
        "parent_field": parent_field,
        "n_child_values": len(child_to_parents),
        "perfectly_nested": len(violations) == 0,
        "n_violations": len(violations),
        "violations": violations,
    }


def sign_length_distribution(records: list[dict]) -> dict:
    tok_stats = [per_record_token_stats(r) for r in records]
    lens = [t["sign_count"] for t in tok_stats]
    distinct = [t["distinct_sign_count"] for t in tok_stats]
    return {
        "n": len(lens),
        "sign_count": {
            "min": min(lens), "max": max(lens),
            "mean": statistics.mean(lens), "median": statistics.median(lens),
            "n_zero": sum(1 for x in lens if x == 0),
            "n_le_2": sum(1 for x in lens if x <= 2),
            "n_ge_10": sum(1 for x in lens if x >= 10),
        },
        "distinct_sign_count": {
            "min": min(distinct), "max": max(distinct),
            "mean": statistics.mean(distinct), "median": statistics.median(distinct),
        },
    }


def site_concentration(records: list[dict]) -> dict:
    """Descriptive concentration diagnostic (site counts + Herfindahl index),
    used to assess grouped-CV / geographic-coverage feasibility (Task 5,
    Task 11) -- not a test of anything."""
    counts = Counter(r.get("site") for r in records if r.get("site"))
    total = sum(counts.values())
    shares = [c / total for c in counts.values()]
    herfindahl = sum(s ** 2 for s in shares)
    return {
        "n_sites": len(counts),
        "n_records_with_site": total,
        "top_site": counts.most_common(1)[0] if counts else None,
        "top_site_share": (counts.most_common(1)[0][1] / total) if counts else None,
        "herfindahl_index": herfindahl,
        "n_sites_with_ge_5": sum(1 for c in counts.values() if c >= 5),
        "n_sites_with_ge_10": sum(1 for c in counts.values() if c >= 10),
        "n_sites_with_ge_30": sum(1 for c in counts.values() if c >= 30),
        "counts": dict(counts.most_common()),
    }


def fragment_join_ids(records: list[dict]) -> list[str]:
    return sorted(r["name"] for r in records if "+" in (r.get("name") or ""))


# =============================================================================
# TASK 9 / confound-risk diagnostic -- generic discrete mutual information
# =============================================================================
def mutual_information_categorical(records: list[dict], field_a: str, field_b: str) -> dict:
    """I(A;B) in bits between two categorical DESIGN fields (e.g.
    support x site), computed directly from the joint empirical
    distribution over non-null pairs. This is a CONFOUND-RISK diagnostic
    only -- it says how entangled two candidate predictors already are in
    this corpus, and says NOTHING about either field's relationship to any
    inscription-structure outcome. Never interpret this as evidence for or
    against H1 (shared-context compression) or any other outcome-facing
    hypothesis in this round."""
    pairs = [
        (r.get(field_a), r.get(field_b)) for r in records
        if r.get(field_a) not in (None, "") and r.get(field_b) not in (None, "")
    ]
    n = len(pairs)
    if n == 0:
        return {"field_a": field_a, "field_b": field_b, "n_pairs": 0, "I_bits": None}
    joint = Counter(pairs)
    pa = Counter(a for a, _ in pairs)
    pb = Counter(b for _, b in pairs)
    mi = 0.0
    for (a, b), c in joint.items():
        p_ab = c / n
        p_a = pa[a] / n
        p_b = pb[b] / n
        mi += p_ab * math.log2(p_ab / (p_a * p_b))
    # normalized by min(H(A), H(B)) for interpretability across field pairs
    def entropy(counter, total):
        return -sum((c / total) * math.log2(c / total) for c in counter.values())
    h_a = entropy(pa, n)
    h_b = entropy(pb, n)
    denom = min(h_a, h_b) if min(h_a, h_b) > 0 else None
    return {
        "field_a": field_a, "field_b": field_b, "n_pairs": n,
        "I_bits": mi, "H_a_bits": h_a, "H_b_bits": h_b,
        "normalized_I": (mi / denom) if denom else None,
        "n_unique_a": len(pa), "n_unique_b": len(pb),
    }


# =============================================================================
# Corpus-level repetition structure (Task 2 feasibility only -- no scoring)
# =============================================================================
def corpus_ngram_feasibility(records: list[dict], n: int = 1) -> dict:
    """Counts distinct n-grams and hapax fraction over CORPUS-POOLED
    signgroup sequences (never within a single short record). Purely
    descriptive of whether pooled n-gram statistics are even computable at
    this corpus size -- not a compression score, not cross-validated, not
    tied to any outcome."""
    ngrams = Counter()
    total = 0
    for r in records:
        words = r.get("transliteratedWords") or []
        seq = [w for w in words if is_signgroup_token(w)]
        for i in range(len(seq) - n + 1):
            ngrams[tuple(seq[i:i + n])] += 1
            total += 1
    hapax = sum(1 for c in ngrams.values() if c == 1)
    return {
        "n": n, "total_ngram_occurrences": total,
        "n_distinct_ngrams": len(ngrams),
        "n_hapax": hapax,
        "hapax_fraction": (hapax / len(ngrams)) if ngrams else None,
    }


# =============================================================================
# Assembled audit
# =============================================================================
def run_full_audit(path: str = CORPUS_PATH) -> dict:
    records = load_corpus(path)
    return {
        "corpus_path": "data/generated/lineara_extracted.json",
        "n_records": len(records),
        "field_availability": field_availability_audit(records),
        "distributions": {
            "site": categorical_distribution(records, "site"),
            "support": categorical_distribution(records, "support"),
            "context": categorical_distribution(records, "context"),
            "findspot": categorical_distribution(records, "findspot"),
            "scribe": categorical_distribution(records, "scribe"),
        },
        "nesting": {
            "scribe_within_site": nesting_check(records, "scribe", "site"),
            "findspot_within_site": nesting_check(records, "findspot", "site"),
        },
        "sign_length_distribution": sign_length_distribution(records),
        "site_concentration": site_concentration(records),
        "fragment_joins": fragment_join_ids(records),
        "confound_diagnostics": {
            "support_x_site": mutual_information_categorical(records, "support", "site"),
            "scribe_x_support": mutual_information_categorical(records, "scribe", "support"),
            "context_x_site": mutual_information_categorical(records, "context", "site"),
        },
        "ngram_feasibility": {
            "unigram": corpus_ngram_feasibility(records, 1),
            "bigram": corpus_ngram_feasibility(records, 2),
            "trigram": corpus_ngram_feasibility(records, 3),
        },
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None, help="write JSON audit to this path")
    args = parser.parse_args()
    audit = run_full_audit()
    text = json.dumps(audit, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
