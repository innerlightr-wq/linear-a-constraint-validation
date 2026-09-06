"""
Candidate 1 protocol machinery: commodity class -> fraction-sign presence.

FROZEN PROTOCOL: docs/CANDIDATE1_PROTOCOL.md. This module implements only
the mechanical construction of an analysis table and the permutation-test
machinery it requires -- it does NOT compute, print, or persist any
class-specific rate, delta, p-value, or verdict against real data. Per
docs/CANDIDATE1_PROTOCOL.md item 22, this module has deliberately NEVER been
invoked against data/generated/lineara_extracted.json in the round that
created it -- every function below is exercised only by
tests/test_constraint_candidate1.py's synthetic fixtures. Running it against
the real corpus is a SEPARATE, future, explicitly-authorized step.

INDEPENDENT IMPLEMENTATION, reusing only the already-frozen, already-tested
Record/Token data model and adjacency conventions from kuro_protocol.py (the
same "first token of the target kind, before the next signgroup" rule
already used by kuro_protocol.associated_numeral) -- no KU-RO/KI-RO/PO-TO-KU-RO
target logic is imported or reused; commodity-occurrence detection here is
entirely independent of TARGETS.

WILDCARD / FAMILY NORMALIZATION (docs/CANDIDATE1_PROTOCOL.md #4): a
commodity signgroup's raw sign-id string (e.g. "GRA", "OLE+U", "GRA+L4+L4")
is split on "+"; only the leading component (the "base sign") is compared,
by EXACT equality, against the four predeclared base signs. Ligature/subunit
suffixes (anything after the first "+") are never inspected for class
membership and are NEVER treated as a fraction signal -- fraction presence
is determined exclusively from the associated NUMERAL token's own
`.fractions` field, never from substrings of the commodity token's sign-id
string. This is deliberate: it is the direct fix for the Phase 15
adversarial question "can commodity ligatures create false fraction
detection?" -- see test_ligature_suffix_does_not_leak_into_fraction_presence.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kuro_protocol import Token, Record  # noqa: E402

# --------------------------------------------------------------------------- frozen family definitions
LIQUID_BASES = frozenset({"VIN", "OLE"})
DRY_BASES = frozenset({"GRA", "OLIV"})

CommodityClass = Literal["LIQUID", "DRY"]


def base_sign(sign_id: str) -> str:
    """Leading component of a sign-id string, split on '+'. No substring or
    prefix matching beyond this exact split -- 'OLIVE' (hypothetical, not a
    real ligature form) is NOT 'OLIV', by design."""
    return sign_id.split("+", 1)[0]


def commodity_class(sign_id: str) -> Optional[CommodityClass]:
    """LIQUID / DRY / None (out of scope), per the frozen base-sign families.
    Any sign whose base is not exactly one of the four predeclared bases is
    OUT OF SCOPE for Candidate 1 -- never guessed, never added post-hoc."""
    base = base_sign(sign_id)
    if base in LIQUID_BASES:
        return "LIQUID"
    if base in DRY_BASES:
        return "DRY"
    return None


# --------------------------------------------------------------------------- fraction presence (structural, not value-based)
def fraction_present(token: Token) -> bool:
    """Whether `token` (expected: kind='numeral') structurally carries a
    fraction-sign glyph, per docs/CANDIDATE1_PROTOCOL.md #6. This is
    INDEPENDENT of kuro_protocol.numeral_value's confidence-admission gate
    (FRACTION_CONFIDENCE_ADMITTED) -- Candidate 1 tests sign PRESENCE, not
    resolved arithmetic value, so an unresolved-confidence fraction glyph
    still counts as present here. Only `token.fractions` is inspected --
    never the commodity signgroup's own sign-id string (see module
    docstring)."""
    return bool(token.fractions)


# --------------------------------------------------------------------------- commodity <-> quantity association
def associated_quantity(record: Record, idx: int) -> Optional[Token]:
    """The numeral token associated with the commodity occurrence at `idx`,
    per docs/CANDIDATE1_PROTOCOL.md #7: the first token after idx that is a
    numeral, provided no signgroup token intervenes first. None if the next
    signgroup-or-end comes first (a heading-like use, per kuro_protocol's
    own is_commodity_heading concept -- not re-implemented here, only its
    concept reused descriptively). Mirrors kuro_protocol.associated_numeral's
    adjacency rule exactly, independently re-implemented so this module has
    no import-time coupling to KU-RO-specific target semantics."""
    for t in record.tokens[idx + 1:]:
        if t.kind == "numeral":
            return t
        if t.kind in ("signgroup", "ruling"):
            return None
    return None


# --------------------------------------------------------------------------- Level A: raw commodity occurrences
@dataclass
class RawOccurrence:
    tablet_id: str
    index: int
    sign_id: str
    commodity_class: CommodityClass
    has_quantity: bool
    fraction_present: Optional[bool]   # None iff has_quantity is False


def find_commodity_occurrences(record: Record) -> list[RawOccurrence]:
    """LEVEL A (docs/CANDIDATE1_PROTOCOL.md #2): every in-scope commodity
    signgroup occurrence, in token order, with its own single associated
    quantity (if any). Descriptive / sensitivity-analysis unit only -- never
    the primary inferential unit (see LEVEL B)."""
    out: list[RawOccurrence] = []
    for i, t in enumerate(record.tokens):
        if t.kind != "signgroup" or not t.sign_ids:
            continue
        # a commodity occurrence has exactly one sign-id in this source's
        # transliteration-string fallback representation (N4); a
        # multi-element sign_ids tuple denotes a resolved TARGET (KU-RO
        # etc.), never a commodity -- out of scope here, not miscounted.
        if len(t.sign_ids) != 1:
            continue
        cls = commodity_class(t.sign_ids[0])
        if cls is None:
            continue
        q = associated_quantity(record, i)
        out.append(RawOccurrence(
            tablet_id=record.tablet_id,
            index=i,
            sign_id=t.sign_ids[0],
            commodity_class=cls,
            has_quantity=q is not None,
            fraction_present=(fraction_present(q) if q is not None else None),
        ))
    return out


# --------------------------------------------------------------------------- Level B: tablet-level (PRIMARY)
TabletOutcome = Literal["FRACTION_PRESENT", "FRACTION_ABSENT", "AMBIGUOUS_UNUSABLE"]


@dataclass
class TabletObservation:
    tablet_id: str
    commodity_class: CommodityClass
    outcome: TabletOutcome
    source_index: Optional[int]   # the token index of the FIRST usable occurrence chosen, or None


def tablet_level_observations(record: Record) -> list[TabletObservation]:
    """LEVEL B, PRIMARY ANALYSIS UNIT (docs/CANDIDATE1_PROTOCOL.md #2).

    For each commodity class represented at all on this tablet, at most one
    observation is emitted, chosen by the FIRST-QUALIFYING-OCCURRENCE rule:
    the first occurrence (in token order) that has a resolvable associated
    quantity. This rule is a deliberate departure from the naive
    "FRACTION_PRESENT if ANY occurrence on the tablet has a fraction" rule
    considered and REJECTED in docs/CANDIDATE1_PROTOCOL.md #2 -- the "ANY"
    rule gives tablets with more same-class occurrences more chances to
    register PRESENT, which would confound occurrence-count with class if
    LIQUID and DRY records differ in typical entry count per tablet (they
    plausibly do). The first-qualifying-occurrence rule is deterministic and
    chosen without reference to fraction content, so it cannot inflate
    either class's rate by opportunity count.

    A class absent from the tablet entirely produces no row at all (not
    AMBIGUOUS -- "not applicable" and "unusable" are kept distinct). A class
    present only via heading-form occurrences (no occurrence anywhere on the
    tablet has a resolvable quantity) produces AMBIGUOUS_UNUSABLE.
    """
    raw = find_commodity_occurrences(record)
    out: list[TabletObservation] = []
    for cls in ("LIQUID", "DRY"):
        class_occurrences = [o for o in raw if o.commodity_class == cls]
        if not class_occurrences:
            continue
        usable = [o for o in class_occurrences if o.has_quantity]
        if not usable:
            out.append(TabletObservation(record.tablet_id, cls, "AMBIGUOUS_UNUSABLE", None))
            continue
        first = usable[0]   # class_occurrences already in token order (Level A preserves it)
        outcome: TabletOutcome = "FRACTION_PRESENT" if first.fraction_present else "FRACTION_ABSENT"
        out.append(TabletObservation(record.tablet_id, cls, outcome, first.index))
    return out


# --------------------------------------------------------------------------- Level C: physical-artifact key
_FACE_SUFFIX_RE = re.compile(r"^(.*\d)([a-z])$")


def physical_artifact_key(tablet_id: str) -> str:
    """Best-effort base-artifact identifier: strips a single trailing
    lowercase face letter following a digit (e.g. 'HT11a' -> 'HT11',
    'HT123+124a' -> 'HT123+124'). Reuses the exact heuristic already applied
    in docs/EVIDENCE_DEPENDENCE_PROTOCOL.md LEVEL 3 (PROBABLE SAME ARTIFACT,
    not CONFIRMED -- full confirmation remains DOMAIN-EXPERT DEPENDENT).
    Tablet IDs with no trailing face letter are returned unchanged."""
    m = _FACE_SUFFIX_RE.match(tablet_id)
    return m.group(1) if m else tablet_id


# --------------------------------------------------------------------------- site / document-type stratum
def stratum_key(site: Optional[str], support: Optional[str]) -> tuple[str, str]:
    """(site, document-type) stratum key, per docs/CANDIDATE1_PROTOCOL.md
    #10. 'document type' = the raw corpus's own 'support' field (physical
    support/object type, e.g. 'Tablet', 'Sealing', 'Nodule') -- chosen
    because it is independently available in the source metadata and
    assigned without any reference to fraction behavior (Phase 5's own
    requirement). Normalized by stripping surrounding whitespace and
    casefolding only -- no semantic re-bucketing. Missing values map to the
    literal string 'UNKNOWN', not silently dropped."""
    s = (site or "UNKNOWN").strip().casefold()
    d = (support or "UNKNOWN").strip().casefold()
    return (s, d)


# --------------------------------------------------------------------------- permutation machinery
def usable_rows(observations: list[TabletObservation]) -> list[TabletObservation]:
    """AMBIGUOUS_UNUSABLE rows are excluded from any inferential
    computation -- never treated as absent."""
    return [o for o in observations if o.outcome != "AMBIGUOUS_UNUSABLE"]


def delta(rows: list[tuple[CommodityClass, bool]]) -> Optional[float]:
    """p_L - p_D over `rows` (class, is_fraction_present) pairs. None if
    either class has zero usable rows (undefined, not ZeroDivisionError)."""
    liquid = [present for cls, present in rows if cls == "LIQUID"]
    dry = [present for cls, present in rows if cls == "DRY"]
    if not liquid or not dry:
        return None
    p_l = sum(liquid) / len(liquid)
    p_d = sum(dry) / len(dry)
    return p_l - p_d


def exchangeable_strata(rows_by_stratum: dict[tuple, list[tuple[CommodityClass, bool]]]) -> tuple[set, set]:
    """Splits stratum keys into (exchangeable, nonexchangeable), per
    docs/CANDIDATE1_PROTOCOL.md #6. A stratum is exchangeable only if it
    contains at least one usable LIQUID row AND at least one usable DRY
    row -- otherwise a within-stratum label permutation could never produce
    a different assignment, and the stratum is excluded from the primary
    inferential computation (retained separately, descriptively only)."""
    exch, non_exch = set(), set()
    for key, rows in rows_by_stratum.items():
        classes = {cls for cls, _ in rows}
        (exch if {"LIQUID", "DRY"} <= classes else non_exch).add(key)
    return exch, non_exch


def stratified_permutation_delta(rows_by_stratum: dict[tuple, list[tuple[CommodityClass, bool]]],
                                  rng) -> Optional[float]:
    """One permutation draw: within each stratum, shuffle the CLASS LABELS
    among that stratum's rows (outcomes stay put), per NULL 3
    (docs/CONSTRAINT_NULL_MODELS.md). Only exchangeable strata participate;
    nonexchangeable strata are omitted entirely from both delta_obs and every
    delta_perm, per docs/CANDIDATE1_PROTOCOL.md #6's predeclared choice."""
    exch, _ = exchangeable_strata(rows_by_stratum)
    permuted_rows: list[tuple[CommodityClass, bool]] = []
    for key in exch:
        rows = rows_by_stratum[key]
        labels = [cls for cls, _ in rows]
        outcomes = [present for _, present in rows]
        shuffled_labels = labels[:]
        rng.shuffle(shuffled_labels)
        permuted_rows.extend(zip(shuffled_labels, outcomes))
    return delta(permuted_rows)


def observed_delta(rows_by_stratum: dict[tuple, list[tuple[CommodityClass, bool]]]) -> Optional[float]:
    """delta_obs computed over exchangeable strata only (same restriction as
    the permutation null, so the observed statistic and its null are
    computed over the identical row set)."""
    exch, _ = exchangeable_strata(rows_by_stratum)
    rows: list[tuple[CommodityClass, bool]] = []
    for key in exch:
        rows.extend(rows_by_stratum[key])
    return delta(rows)


def finite_permutation_pvalue(count_extreme_or_equal: int, B: int) -> float:
    """(extreme + 1) / (B + 1), per docs/CANDIDATE1_PROTOCOL.md #12 --
    frozen now, applied verbatim in any future run."""
    return (count_extreme_or_equal + 1) / (B + 1)


def run_stratified_permutation_test(rows_by_stratum: dict[tuple, list[tuple[CommodityClass, bool]]],
                                     B: int, rng) -> Optional[dict]:
    """Full predeclared permutation test. Returns None (not a partial
    result) if delta_obs is undefined (an empty or fully-nonexchangeable
    exchangeable set). Does not decide adequacy-gate pass/fail -- that is a
    separate, explicit check against docs/CANDIDATE1_PROTOCOL.md #13's
    frozen minimums, applied by the future analysis script, not here."""
    delta_obs = observed_delta(rows_by_stratum)
    if delta_obs is None:
        return None
    extreme = 0
    for _ in range(B):
        d = stratified_permutation_delta(rows_by_stratum, rng)
        if d is not None and abs(d) >= abs(delta_obs):
            extreme += 1
    p = finite_permutation_pvalue(extreme, B)
    return {"delta_obs": delta_obs, "p_value": p, "B": B}
