"""
Constraint accumulation V2 (integer-conditional accumulation) — CANONICAL.

Frozen per docs/CONSTRAINT_ACCUMULATION_V2_PROTOCOL.md. This module
implements every V2-SPECIFIC scientific decision: the Y-independent
population-inclusion rule, the WHOLE_COMPONENT_MAGNITUDE transform, the
V2 model-block nesting, the V2 adequacy criteria, and the V2 verdict
architecture (including the M3-exclusion rule for ACCUMULATION EVIDENCE).
Cross-validation, model fitting, log-loss, conditional permutation, and
Holm correction are REUSED UNCHANGED from src/constraint_accumulation.py
-- not reimplemented here (see the frozen protocol §8-§10 for exactly
which functions are reused).

Deliberately contains NO real-data invocation and NO orchestration of a
full run (no CV loop, no model-fitting loop, no permutation loop) --
per the frozen protocol's own firewall, that orchestration belongs to
src/run_constraint_accumulation_v2.py (the execution harness, built only
after this module is frozen), never to this module. Every function here
is exercised only by tests/test_constraint_accumulation_v2.py's synthetic
fixtures -- none of them ever loads data/generated/lineara_extracted.json.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import constraint_accumulation as ca  # noqa: E402


# --------------------------------------------------------------------------- population (protocol §2)
def is_integer_resolvable(numeric_value: Optional[float]) -> bool:
    """V2 population-inclusion rule (docs/CONSTRAINT_ACCUMULATION_V2_PROTOCOL.md
    §2): True iff the associated numeral's whole-number `.value` is
    resolved. Reads ONLY `numeric_value` -- never `fraction_present` or
    any other field -- by construction, this function cannot depend on Y
    (proof, not just intent: its signature takes no Y-related argument at
    all)."""
    return numeric_value is not None


# --------------------------------------------------------------------------- M4 (protocol §4-§5)
def log2_magnitude(integer_value: float) -> float:
    """WHOLE_COMPONENT_MAGNITUDE = log2(1 + integer_value), a fixed,
    non-fitted transform (no cutoffs, no per-fold fitting step, no bins).
    Requires integer_value >= 0 -- guaranteed for every row admitted by
    is_integer_resolvable, since the numeral system's own no-zero-digit
    convention means any resolvable integer component is >= 1
    (docs/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md §5). Measures ONLY
    the resolvable whole-number component's magnitude -- NOT the total
    mathematical value of an integer+fraction expression (protocol §5) --
    this is a permanent, disclosed limitation, not a bug to fix."""
    if integer_value < 0:
        raise ValueError(f"log2_magnitude requires a nonnegative value, got {integer_value}")
    return math.log2(1 + integer_value)


@dataclass
class V2Row:
    tablet_id: str
    site_block: str
    support_block: str
    position_bucket: str
    commodity_class: str
    whole_component_magnitude: float   # log2(1 + integer_value)
    fraction_present: bool             # Y


def build_v2_rows(feature_rows: list) -> list[V2Row]:
    """Restricts `feature_rows` (constraint_accumulation.FeatureRow
    instances, e.g. from constraint_accumulation.build_feature_rows) to
    the V2 population (is_integer_resolvable) and computes
    WHOLE_COMPONENT_MAGNITUDE. Every other field is copied UNCHANGED from
    the input FeatureRow -- no re-derivation of site/support/position/
    commodity/Y."""
    out: list[V2Row] = []
    for r in feature_rows:
        if not is_integer_resolvable(r.numeric_value):
            continue
        out.append(V2Row(
            tablet_id=r.tablet_id,
            site_block=r.site_block,
            support_block=r.support_block,
            position_bucket=r.position_bucket,
            commodity_class=r.commodity_class,
            whole_component_magnitude=log2_magnitude(r.numeric_value),
            fraction_present=r.fraction_present,
        ))
    return out


def population_cardinality(rows: list[V2Row], field: str) -> dict:
    """Marginal (never Y-conditional) distinct-value counts -- schema/
    feasibility check only, matching the same convention already
    established in constraint_accumulation.cardinality."""
    counts: dict = {}
    for r in rows:
        v = getattr(r, field)
        counts[v] = counts.get(v, 0) + 1
    return counts


def unique_tablets(rows: list[V2Row]) -> set:
    return {r.tablet_id for r in rows}


# --------------------------------------------------------------------------- model nesting (protocol §4)
MODEL_BLOCKS_V2 = {
    "M0": [],
    "M1": ["site_support"],
    "M2": ["site_support", "position"],
    "M3": ["site_support", "position", "commodity"],
    "M4": ["site_support", "position", "commodity", "magnitude"],
}
STEP_PREV_MODEL_V2 = {"M2": "M1", "M3": "M2", "M4": "M3"}
# M_{k-1}'s own predictor fields, for the conditional null (protocol §9) --
# identical field names/structure to V1's STEP_STRATUM_FIELDS, restated
# here so this module is self-contained for V2's own model sequence.
STEP_STRATUM_FIELDS_V2 = {
    "M2": ("site_block", "support_block"),
    "M3": ("site_block", "support_block", "position_bucket"),
    "M4": ("site_block", "support_block", "position_bucket", "commodity_class"),
}

# --------------------------------------------------------------------------- information-type classification (protocol §11 rationale, docs/CONSTRAINT_INFORMATION_TYPES.md)
INFORMATION_TYPES_V2 = {
    "site_support": "INDEPENDENT STRUCTURAL INFORMATION",
    "position": "DERIVED STRUCTURAL INFORMATION",
    "commodity": "EXTERNAL MODEL INFORMATION",
    "magnitude": "POTENTIALLY INDEPENDENT NUMERICAL INFORMATION (scope: quantities >= 1 whole unit)",
}


# --------------------------------------------------------------------------- adequacy (protocol §7)
# B and C below are PROJECT-SPECIFIC MECHANISM-LINKED ADEQUACY SAFEGUARDS
# (power considerations) -- NOT universal theorems. See protocol §7's
# table for the full epistemic classification of every criterion.
MIN_MINORITY_PER_TRAINING_FOLD = 5     # criterion B
MIN_MIXED_STRATA_FRACTION = 0.5        # criterion C


def training_fold_minority_adequate(y_train: list) -> bool:
    """Criterion B: does this training fold contain >= MIN_MINORITY_
    PER_TRAINING_FOLD minority-class (Y=1) rows? A project-specific
    safeguard (analogous to, not derived from, Cochran's >=5-expected-
    cell-count convention), not a universal requirement."""
    count = sum(1 for y in y_train if y)
    return count >= MIN_MINORITY_PER_TRAINING_FOLD


def mixed_strata_fraction(rows_by_stratum: dict) -> float:
    """Criterion C helper: fraction of populated strata (values are lists
    of (class_or_dummy, y) pairs, OR any structure `permutable_strata`-
    style logic can be applied to) that contain BOTH Y=0 and Y=1 rows.
    `rows_by_stratum`: {stratum_key: [y0, y1, ...]} (list of Y values in
    that stratum)."""
    if not rows_by_stratum:
        return 0.0
    mixed = sum(1 for ys in rows_by_stratum.values() if any(ys) and not all(ys))
    return mixed / len(rows_by_stratum)


def strata_mixed_adequate(rows_by_stratum: dict) -> bool:
    """Criterion C: does the finest conditional-permutation step's
    populated-stratum set have >= MIN_MIXED_STRATA_FRACTION mixed
    (both-class) strata?"""
    return mixed_strata_fraction(rows_by_stratum) >= MIN_MIXED_STRATA_FRACTION


# --------------------------------------------------------------------------- verdict architecture (protocol §11)
STEP_VERDICTS = ("SUPPORTED", "NOT SUPPORTED", "NOT_EVALUABLE")


def classify_step_verdict(holm_p: Optional[float], delta_obs: Optional[float],
                           alpha: float = 0.05) -> str:
    """Per-step verdict: SUPPORTED iff evaluable, delta_obs > 0, and
    holm_p < alpha. NOT_EVALUABLE iff holm_p (equivalently delta_obs) is
    None. Otherwise NOT SUPPORTED -- including a negative or zero
    delta_obs, which is always evaluable and always NOT SUPPORTED, never
    treated as undefined."""
    if holm_p is None or delta_obs is None:
        return "NOT_EVALUABLE"
    if delta_obs > 0 and holm_p < alpha:
        return "SUPPORTED"
    return "NOT SUPPORTED"


def classify_broad_verdict(step_verdicts: dict) -> str:
    """Broad V2 verdict from {"M2": ..., "M3": ..., "M4": ...} step
    verdicts (each one of STEP_VERDICTS). Implements protocol §11 exactly,
    including the M3-exclusion rule: only M2 and M4 count toward
    ACCUMULATION EVIDENCE or (non-external-model) LIMITED POSITIVE; M3
    remains part of the statistical testing family (it can be SUPPORTED
    or NOT SUPPORTED like any other step) but its support alone earns
    only the distinct EXTERNAL-MODEL-ONLY label, never the stronger ones.
    Does NOT compute DESIGN BLOCKED or the population/adequacy-level
    INCONCLUSIVE -- those are determined upstream, before step verdicts
    exist at all (by the harness, from population/CV/adequacy checks),
    and passed to this function only when the experiment actually ran."""
    m2 = step_verdicts.get("M2", "NOT_EVALUABLE")
    m3 = step_verdicts.get("M3", "NOT_EVALUABLE")
    m4 = step_verdicts.get("M4", "NOT_EVALUABLE")

    evaluable = [v for v in (m2, m3, m4) if v != "NOT_EVALUABLE"]
    if not evaluable:
        return "INCONCLUSIVE"

    qualifying_supported = sum(1 for v in (m2, m4) if v == "SUPPORTED")
    if qualifying_supported >= 2:
        return "ACCUMULATION EVIDENCE"
    if qualifying_supported == 1:
        return "LIMITED POSITIVE"
    if m3 == "SUPPORTED":
        return "LIMITED POSITIVE (EXTERNAL-MODEL-ONLY)"
    return "NEGATIVE UPDATE"
