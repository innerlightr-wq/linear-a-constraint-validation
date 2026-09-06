"""
Constraint-accumulation SCAFFOLD: feature-block construction, statistical
machinery, and schema/feasibility checks only.

Per docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md (the canonical, frozen
protocol -- supersedes any conflicting statement in the earlier design
notes docs/CONSTRAINT_ACCUMULATION_{CANDIDATES,DESIGN,NULLS}.md). This
module builds the row-level feature table a future modeling round would
need, the mechanical statistics that round will use (log-loss, Holm
correction, conditional permutation, adequacy checks), and marginal (never
Y-conditional) cardinality/missingness checks. It deliberately contains NO
real cross-validation run, NO model fit against the real corpus, and NO
inspection of any real predictor-vs-Y relationship -- every function here
is exercised only by tests/test_constraint_accumulation.py's synthetic
fixtures in this round. The future driver that invokes this module against
data/generated/lineara_extracted.json (analogous to how
src/run_candidate1.py used src/constraint_candidate1.py) does not yet
exist and is a separate, separately-authorized step.

Reuses src/constraint_candidate1.py's frozen commodity-occurrence detection
and fraction-presence definition UNCHANGED -- no reimplementation.

SUPERSESSION NOTICE (resolved at canonical-protocol freeze time): the
earlier docs/CONSTRAINT_ACCUMULATION_CANDIDATES.md fixed C_NUMERIC's
SMALL/MEDIUM/LARGE cutoffs (3, 15) from a single marginal quantile check
over the FULL corpus. docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md's Phase 4
audit requires any quantile-derived bin to be fit inside each training
fold only, to avoid any cross-fold information sharing. `numeric_bin`
below (the old, fixed-global version) is kept only for the predeclared
Sensitivity comparison the canonical protocol names -- `numeric_bin_fold`
plus `fit_numeric_bin_cutoffs` is the PRIMARY, protocol-frozen version.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kuro_protocol import Record  # noqa: E402
import constraint_candidate1 as c1  # noqa: E402

# --------------------------------------------------------------------------- predeclared collapses / bins
SITE_DOMINANT = "haghia triada"
SUPPORT_DOMINANT = "tablet"

NUMERIC_SMALL_MAX = 3     # value <= 3 -> SMALL
NUMERIC_MEDIUM_MAX = 15   # 4 <= value <= 15 -> MEDIUM; value >= 16 -> LARGE
# SUPERSEDED as the primary rule (see module docstring) -- retained only
# for Sensitivity comparison against the fold-derived rule.


def site_block(site: Optional[str]) -> str:
    """C_SITE, collapsed per docs/CONSTRAINT_ACCUMULATION_CANDIDATES.md
    feasibility note: {Haghia Triada, OTHER}."""
    if (site or "").strip().casefold() == SITE_DOMINANT:
        return "Haghia Triada"
    return "OTHER"


def support_block(support: Optional[str]) -> str:
    """C_SUPPORT, collapsed: {Tablet, OTHER}."""
    if (support or "").strip().casefold() == SUPPORT_DOMINANT:
        return "Tablet"
    return "OTHER"


def position_bucket(rank: int) -> str:
    """C_POSITION: ordinal rank (1-indexed) of a qualifying occurrence among
    same-record qualifying occurrences, in token order -> {FIRST, SECOND,
    THIRD_OR_LATER}."""
    if rank == 1:
        return "FIRST"
    if rank == 2:
        return "SECOND"
    return "THIRD_OR_LATER"


def numeric_bin(value: Optional[float]) -> str:
    """C_NUMERIC: predeclared marginal-quantile bins -> {SMALL, MEDIUM,
    LARGE, NO_INTEGER_VALUE}. NO_INTEGER_VALUE is an explicit category
    (a fraction-only numeral with no whole-number part), never silently
    merged into SMALL or excluded."""
    if value is None:
        return "NO_INTEGER_VALUE"
    if value <= NUMERIC_SMALL_MAX:
        return "SMALL"
    if value <= NUMERIC_MEDIUM_MAX:
        return "MEDIUM"
    return "LARGE"


def fit_numeric_bin_cutoffs(training_values: list[Optional[float]]) -> tuple[float, float]:
    """PRIMARY, protocol-frozen rule (docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md
    Phase 4): tertile cutoffs (small_max, medium_max) computed from
    TRAINING-FOLD values only -- `training_values` must already be
    restricted to one GroupKFold training split before calling this. `None`
    entries (fraction-only numerals, no whole-number part) are excluded
    from the quantile computation itself (they get NO_INTEGER_VALUE
    regardless of cutoffs) but must NOT be silently dropped from the row
    set elsewhere. Requires at least 3 non-None training values; raises
    ValueError otherwise (an explicit CV_NOT_EVALUABLE condition for that
    fold, per Phase 6 -- never silently skipped)."""
    non_none = sorted(v for v in training_values if v is not None)
    if len(non_none) < 3:
        raise ValueError("fewer than 3 non-None training values: cannot fit tertile cutoffs")
    q = _quantiles_inclusive(non_none, (1 / 3, 2 / 3))
    return (q[0], q[1])


def _quantiles_inclusive(sorted_values: list[float], fractions: tuple[float, ...]) -> list[float]:
    """Linear-interpolation quantile (the same convention as
    statistics.quantiles(method='inclusive')), reimplemented directly so
    this module has no dependency on Python-version-specific stdlib
    quantile behavior."""
    n = len(sorted_values)
    out = []
    for f in fractions:
        pos = f * (n - 1)
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            out.append(sorted_values[lo])
        else:
            frac = pos - lo
            out.append(sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac)
    return out


def numeric_bin_fold(value: Optional[float], small_max: float, medium_max: float) -> str:
    """PRIMARY, protocol-frozen version of numeric_bin: uses cutoffs
    already fit on a training fold (fit_numeric_bin_cutoffs), applied
    identically to both that fold's training AND test rows -- no
    per-row/per-set re-fitting, no use of the test rows' own values to
    choose cutoffs."""
    if value is None:
        return "NO_INTEGER_VALUE"
    if value <= small_max:
        return "SMALL"
    if value <= medium_max:
        return "MEDIUM"
    return "LARGE"


# --------------------------------------------------------------------------- feature row construction
@dataclass
class FeatureRow:
    tablet_id: str
    index: int                 # token index of the commodity occurrence (for ordering/debugging only)
    site_block: str
    support_block: str
    position_bucket: str
    commodity_class: str       # "LIQUID" / "DRY"
    numeric_value: Optional[float]   # raw whole-number value, or None (fraction-only numeral)
    numeric_bin: str           # fixed-global bin -- SENSITIVITY comparison only, see module docstring
    fraction_present: bool     # Y


def build_feature_rows(record: Record, site: Optional[str], support: Optional[str]) -> list[FeatureRow]:
    """One row per qualifying (LIQUID/DRY, has-resolvable-quantity)
    commodity occurrence in `record`, in token order. Reuses
    constraint_candidate1.find_commodity_occurrences and
    constraint_candidate1.associated_quantity unchanged -- no
    reimplementation of occurrence detection, fraction presence, or the
    commodity<->quantity association rule. `numeric_value` is carried raw
    so a future CV driver can apply numeric_bin_fold with training-fold-fit
    cutoffs; `numeric_bin` (fixed-global) is retained only for the
    predeclared Sensitivity comparison."""
    occs = [o for o in c1.find_commodity_occurrences(record) if o.has_quantity]
    rows: list[FeatureRow] = []
    for rank, o in enumerate(occs, start=1):
        q = c1.associated_quantity(record, o.index)
        val = q.value if q is not None else None
        rows.append(FeatureRow(
            tablet_id=o.tablet_id,
            index=o.index,
            site_block=site_block(site),
            support_block=support_block(support),
            position_bucket=position_bucket(rank),
            commodity_class=o.commodity_class,
            numeric_value=val,
            numeric_bin=numeric_bin(val),
            fraction_present=o.fraction_present,
        ))
    return rows


# --------------------------------------------------------------------------- marginal schema/feasibility checks (never Y-conditional)
def cardinality(rows: list[FeatureRow], field: str) -> dict:
    """Marginal distinct-value counts for one field across `rows`. Never
    crosses with `fraction_present` -- this is a schema/feasibility check,
    not a result (docs/CONSTRAINT_ACCUMULATION_NULLS.md Phase 13/19
    firewall: cardinality counts are allowed, Y-conditional counts are
    not)."""
    counts: dict = {}
    for r in rows:
        v = getattr(r, field)
        counts[v] = counts.get(v, 0) + 1
    return counts


def missingness(rows: list[FeatureRow], field: str) -> int:
    """Count of rows where `field` is None. (In practice, no FeatureRow
    field is ever None by construction -- site_block/support_block/
    position_bucket/numeric_bin all resolve to an explicit category,
    including NO_INTEGER_VALUE -- this function exists for feasibility
    auditing of any future field that might be added.)"""
    return sum(1 for r in rows if getattr(r, field) is None)


def unique_tablets(rows: list[FeatureRow]) -> set:
    """Distinct tablet_id count -- the CV group count, a feasibility
    figure, not a result."""
    return {r.tablet_id for r in rows}


# --------------------------------------------------------------------------- fixed reference-level encoding (Phase 5)
# All five predictor fields are CLOSED, fully-enumerated category sets
# (fixed by site_block/support_block/position_bucket/commodity_class/
# numeric_bin(_fold) themselves) -- there is no open vocabulary and
# therefore no possible "unseen categorical level" at encode time, and no
# fitting step is needed for the categorical encoding itself (only
# fit_numeric_bin_cutoffs is fold-fit, and only on the raw numeral value,
# not on the category labels).
REFERENCE_LEVELS = {
    "site_block": "OTHER",
    "support_block": "OTHER",
    "position_bucket": "FIRST",
    "commodity_class": "DRY",
    "numeric_bin": "SMALL",
}
_LEVELS = {
    "site_block": ("OTHER", "Haghia Triada"),
    "support_block": ("OTHER", "Tablet"),
    "position_bucket": ("FIRST", "SECOND", "THIRD_OR_LATER"),
    "commodity_class": ("DRY", "LIQUID"),
    "numeric_bin": ("SMALL", "MEDIUM", "LARGE", "NO_INTEGER_VALUE"),
}


def encode_indicator(field: str, value: str) -> dict[str, float]:
    """One-hot indicators for `field`'s value, dropping the fixed
    reference level (REFERENCE_LEVELS) -- e.g. site_block='Haghia Triada'
    -> {'site_block__Haghia Triada': 1.0}; site_block='OTHER' -> {}
    (reference level contributes only via the intercept). Raises
    ValueError for any value outside the closed level set for `field` --
    by construction (see module note above) this should never happen for
    real data, since every value passed in is already produced by one of
    the fixed bucket functions."""
    levels = _LEVELS[field]
    if value not in levels:
        raise ValueError(f"{value!r} is not a declared level of {field!r}: {levels}")
    ref = REFERENCE_LEVELS[field]
    return {f"{field}__{lvl}": 1.0 for lvl in levels if lvl != ref and lvl == value}


# --------------------------------------------------------------------------- primary held-out metric (Phase 7)
LOG_LOSS_EPS = 1e-15  # frozen clipping epsilon, numerical stability only


def log_loss_bits(y_true: list[int], y_pred_prob: list[float], eps: float = LOG_LOSS_EPS) -> float:
    """Mean held-out binary log loss in bits (docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md
    Phase 7). Probabilities are clipped to [eps, 1-eps] only for numerical
    stability -- this never changes which class is favored, only avoids
    log2(0)."""
    if len(y_true) != len(y_pred_prob):
        raise ValueError("y_true and y_pred_prob must be the same length")
    if not y_true:
        raise ValueError("cannot compute log loss over zero observations")
    total = 0.0
    for y, p in zip(y_true, y_pred_prob):
        p = min(max(p, eps), 1 - eps)
        total += -(y * math.log2(p) + (1 - y) * math.log2(1 - p))
    return total / len(y_true)


def delta_h(h_prev: float, h_curr: float) -> float:
    """ΔH_k = H_hat_{k-1} - H_hat_k. Positive: the added block reduced
    held-out uncertainty. Negative: it increased held-out uncertainty
    (harmed prediction). Zero: no measurable added information. The sign
    convention is fixed here, once, so no future step can silently invert
    it."""
    return h_prev - h_curr


def delta_h_label(value: float) -> str:
    """Fixed interpretation labels for a ΔH value -- IMPROVES / HARMS /
    NO_INFORMATION (exact zero only)."""
    if value > 0:
        return "IMPROVES"
    if value < 0:
        return "HARMS"
    return "NO_INFORMATION"


# --------------------------------------------------------------------------- conditional permutation null (Phase 8, 9)
def conditional_permutation_delta(rows: list[tuple], stratum_key_fn, rng) -> list[tuple]:
    """One draw of the CORRECTED conditional null
    (docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md Phase 8): `rows` is a list of
    (stratum_predictors_tuple, y) pairs already restricted to the rows used
    for one accumulation step's comparison. `stratum_key_fn` maps a row's
    predictor tuple to the M_{k-1}-level stratum key (e.g., for testing
    step M2 -> M3, the key is (site_block, support_block, position_bucket)
    -- everything already in M2, NOT including the new C_COMMODITY block).
    Within each such stratum, Y values are shuffled among that stratum's
    rows; predictor values stay attached to their original row. Returns a
    new list of (predictors, y_permuted) pairs in the same order as `rows`.

    THIS SUPERSEDES the earlier, narrower per-step null proposed in
    docs/CONSTRAINT_ACCUMULATION_NULLS.md (which fixed (site, support)
    strata for every step regardless of which step was being tested) --
    that null was valid only for the M1->M2 step; for M2->M3 and M3->M4 it
    would have destroyed structure the preceding model had already
    captured, not just the new block's contribution. This generalized,
    per-step-conditioned version is the canonical, frozen rule."""
    from collections import defaultdict
    buckets = defaultdict(list)
    for i, (preds, y) in enumerate(rows):
        buckets[stratum_key_fn(preds)].append(i)

    y_values = [y for _, y in rows]
    permuted_y = list(y_values)
    for indices in buckets.values():
        original = [y_values[i] for i in indices]
        shuffled = original[:]
        rng.shuffle(shuffled)
        for i, y in zip(indices, shuffled):
            permuted_y[i] = y

    return [(rows[i][0], permuted_y[i]) for i in range(len(rows))]


def permutable_strata(rows: list[tuple], stratum_key_fn) -> tuple[set, set]:
    """Strata with >=2 rows (permutable at all) vs strata with <2 rows
    (cannot be meaningfully permuted -- excluded from both the observed
    statistic and the null for that step, reusing exactly the
    'excluded, retained descriptively' discipline already established in
    constraint_candidate1.exchangeable_strata)."""
    from collections import defaultdict
    buckets = defaultdict(list)
    for preds, _ in rows:
        buckets[stratum_key_fn(preds)].append(1)
    permutable = {k for k, v in buckets.items() if len(v) >= 2}
    not_permutable = {k for k, v in buckets.items() if len(v) < 2}
    return permutable, not_permutable


def finite_permutation_pvalue(count_extreme_or_equal: int, B: int) -> float:
    """p_k = (extreme + 1)/(B + 1) -- identical formula to
    constraint_candidate1.finite_permutation_pvalue, restated here so this
    module has no import-time coupling to Candidate 1's own module beyond
    the explicitly-reused commodity/fraction functions."""
    return (count_extreme_or_equal + 1) / (B + 1)


def step_permutation_pvalue(delta_obs: float, perm_deltas: list[float], B: int) -> float:
    """One-sided p_k = (#{ΔH_perm >= ΔH_obs} + 1)/(B+1)
    (docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md §9). PHASE 1 CORRECTION:
    computed UNCONDITIONALLY on the sign of `delta_obs` -- a negative or
    zero observed ΔH is not undefined, not skipped, and not special-cased;
    it is simply evaluated, and will naturally yield a large (non-
    supportive) p-value because most permutation draws exceed a very
    negative observed value. Whether a step's p-value exists must depend
    only on evaluability (see fold_is_evaluable / primary_adequacy_gate /
    category_adequacy), never on the observed effect's sign -- that is
    exactly the bug this function fixes relative to an earlier draft."""
    if len(perm_deltas) != B:
        raise ValueError(f"expected {B} permutation draws, got {len(perm_deltas)}")
    extreme = sum(1 for d in perm_deltas if d >= delta_obs)
    return finite_permutation_pvalue(extreme, B)


# --------------------------------------------------------------------------- multiple-testing correction (Phase 10)
def holm_correction(pvalues: list[float]) -> list[float]:
    """Holm step-down adjusted p-values, in the SAME ORDER as the input
    list (not sorted). Standard procedure: sort ascending, adjusted p_(i) =
    max(p_(i) * (m - i + 1) for i in 1..that index, enforced monotone
    nondecreasing), each clipped to <= 1.0."""
    m = len(pvalues)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted_sorted = []
    running_max = 0.0
    for rank, idx in enumerate(order):  # rank is 0-indexed
        raw_adj = pvalues[idx] * (m - rank)
        running_max = max(running_max, raw_adj)
        adjusted_sorted.append(min(running_max, 1.0))
    result = [0.0] * m
    for rank, idx in enumerate(order):
        result[idx] = adjusted_sorted[rank]
    return result


def holm_family(step_pvalues: dict) -> dict:
    """Holm correction applied over exactly the EVALUABLE steps in
    `step_pvalues` ({step_name: raw_p_or_None}). A step maps to `None`
    if and ONLY IF it is genuinely NOT_EVALUABLE (CV/adequacy/category-
    support failure per fold_is_evaluable / primary_adequacy_gate /
    category_adequacy) -- NEVER because its observed ΔH was zero or
    negative (every evaluable step, whatever its sign, must already carry
    a real p-value from step_permutation_pvalue, per the Phase 1
    correction above). Family membership -- and therefore family size `m`
    -- depends only on evaluability, never on observed effect sign.
    Returns {step_name: holm_adjusted_p} for evaluable steps only;
    NOT_EVALUABLE steps are simply absent from the result (report them
    separately, by name, as NOT_EVALUABLE -- never folded in here as
    p=1.0 or any other placeholder)."""
    evaluable_names = [k for k, v in step_pvalues.items() if v is not None]
    if not evaluable_names:
        return {}
    raw = [step_pvalues[n] for n in evaluable_names]
    adjusted = holm_correction(raw)
    return dict(zip(evaluable_names, adjusted))


# --------------------------------------------------------------------------- fold validity (Phase 6)
def fold_is_evaluable(y_values: list[int]) -> bool:
    """A fold (training split) is evaluable only if both classes (0 and 1)
    are present. A test-only fold with a single class is still scoreable
    (log loss is well-defined given valid predicted probabilities) -- this
    check is for TRAINING folds only, per Phase 6."""
    values = set(y_values)
    return {0, 1} <= values or {False, True} <= values


# --------------------------------------------------------------------------- adequacy gates (Phase 11)
ADEQUACY_MIN_TOTAL_N = 150
ADEQUACY_MIN_TABLETS = 50
ADEQUACY_MIN_POSITIVE = 30
ADEQUACY_MIN_NEGATIVE = 30
ADEQUACY_MIN_CATEGORY_TABLETS = 10   # binary blocks: site/support/commodity
ADEQUACY_MIN_CATEGORY_ROWS = 10      # position/numeric levels


def primary_adequacy_gate(n_total: int, n_tablets: int, n_positive: int, n_negative: int) -> bool:
    """Frozen minimums, docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md Phase 11."""
    return (n_total >= ADEQUACY_MIN_TOTAL_N
            and n_tablets >= ADEQUACY_MIN_TABLETS
            and n_positive >= ADEQUACY_MIN_POSITIVE
            and n_negative >= ADEQUACY_MIN_NEGATIVE)


def category_adequacy(counts: dict, min_count: int) -> dict:
    """{category: bool} -- whether each observed category clears
    `min_count` (ADEQUACY_MIN_CATEGORY_TABLETS for tablet-counted binary
    blocks, ADEQUACY_MIN_CATEGORY_ROWS for row-counted position/numeric
    levels, per Phase 11). Never merges a failing category -- the caller
    is expected to mark the corresponding model step NOT EVALUABLE rather
    than silently combining categories."""
    return {cat: (n >= min_count) for cat, n in counts.items()}
