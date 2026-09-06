"""
Independent implementation of the H1 protocol (docs/H1_PROTOCOL.md).

INDEPENDENT IMPLEMENTATION — written from this project's own frozen protocol
document, not copied from any external project (see
docs/EXTERNAL_FOUNDATION_AUDIT.md for what was and was not reused from prior
work). Pure functions only; no corpus I/O here (see src/build_kuro_corpus.py,
not yet implemented, for that).

This module makes no claim about real Linear A data. It implements the rules
the protocol document declares, so they can be tested against synthetic data
before being pointed at anything real.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

# --------------------------------------------------------------------------- targets
# GORILA sign-identifier sequences. These are the canonical, citable
# identifiers for these sign-groups in the published scholarly edition, not
# copyrightable expression -- reusing them is ordinary scholarly citation.
KURO_IDS = ("AB081", "AB002")
KIRO_IDS = ("AB067", "AB002")
POTOKURO_IDS = ("AB011", "AB005", "AB081", "AB002")

TARGETS = {"KU-RO": KURO_IDS, "KI-RO": KIRO_IDS, "PO-TO-KU-RO": POTOKURO_IDS}

FRACTION_CONFIDENCE_ADMITTED = ("secure", "derived")

NEAR_TERMINAL_MAX_FOLLOWING = 2   # declared in H1_PROTOCOL.md #2, not tuned
ROUNDING_ABS_TOLERANCE = 1.0      # declared in H1_PROTOCOL.md #7
ROUNDING_REL_TOLERANCE = 0.05     # Paper 1's own +/-5%, H1_PROTOCOL.md #7
EXACT_EPSILON = 1e-9
MIN_TESTABLE_N = 10               # H1_PROTOCOL.md #11
MAX_UNTESTABLE_FRACTION = 0.5     # H1_PROTOCOL.md #11


# --------------------------------------------------------------------------- data model
@dataclass
class Token:
    kind: Literal["signgroup", "numeral", "ruling"]
    sign_ids: Optional[tuple] = None          # signgroup only
    value: Optional[float] = None             # numeral: direct whole-number label
    fractions: Optional[list] = None          # numeral: [{"value":float,"confidence":str}, ...]
    damaged: bool = False
    sign_identity_uncertain: bool = False     # signgroup only


@dataclass
class Record:
    tablet_id: str
    tokens: list = field(default_factory=list)


# --------------------------------------------------------------------------- 1. occurrences
def find_occurrences(record: Record, target_label: str) -> list[int]:
    """Indices of tokens matching the declared target sign-id sequence for
    `target_label` ('KU-RO' / 'KI-RO' / 'PO-TO-KU-RO')."""
    target = TARGETS[target_label]
    return [i for i, t in enumerate(record.tokens)
            if t.kind == "signgroup" and t.sign_ids == target]


def _is_any_target(t: Token) -> bool:
    return t.kind == "signgroup" and t.sign_ids in TARGETS.values()


# --------------------------------------------------------------------------- 2. position
def classify_position(record: Record, idx: int) -> str:
    """TERMINAL / NEAR_TERMINAL / NON_TERMINAL, per H1_PROTOCOL.md #2."""
    following_signgroups = sum(
        1 for t in record.tokens[idx + 1:] if t.kind == "signgroup"
    )
    if following_signgroups == 0:
        return "TERMINAL"
    if following_signgroups <= NEAR_TERMINAL_MAX_FOLLOWING:
        return "NEAR_TERMINAL"
    return "NON_TERMINAL"


# --------------------------------------------------------------------------- 3. numeral value
def numeral_value(token: Token) -> Optional[float]:
    """Resolve a numeral token's value per H1_PROTOCOL.md #3, or None if
    unresolvable (no direct label and no admitted-confidence fraction)."""
    if token.kind != "numeral":
        return None
    if token.value is not None:
        return float(token.value)
    if token.fractions:
        contributing = [f["value"] for f in token.fractions
                         if f.get("confidence") in FRACTION_CONFIDENCE_ADMITTED]
        if contributing:
            return float(sum(contributing))
    return None


def associated_numeral(record: Record, idx: int) -> Optional[Token]:
    """The numeral token associated with the occurrence at `idx`, per
    H1_PROTOCOL.md #3: first numeral token following idx, before the next
    signgroup or ruling token."""
    for t in record.tokens[idx + 1:]:
        if t.kind == "numeral":
            return t
        if t.kind in ("signgroup", "ruling"):
            return None
    return None


# --------------------------------------------------------------------------- 4. preceding block
def is_commodity_heading(record: Record, j: int, commodity_ids: set) -> bool:
    """A commodity-ideogram token not immediately followed by a numeral
    (H1_PROTOCOL.md #4, Rule B). `commodity_ids` must be supplied by the
    caller -- this project does not hardcode a commodity-sign inventory, see
    module docstring / EXTERNAL_FOUNDATION_AUDIT.md."""
    t = record.tokens[j]
    if t.kind != "signgroup" or not t.sign_ids:
        return False
    if not (set(t.sign_ids) & commodity_ids):
        return False
    for u in record.tokens[j + 1:]:
        if u.kind == "numeral":
            return False   # inline entry
        if u.kind == "signgroup":
            return True    # heading
    return True


def preceding_block(record: Record, idx: int, rule: str = "A",
                     commodity_ids: Optional[set] = None) -> list[Token]:
    """Numeral tokens in the block preceding `idx`, per H1_PROTOCOL.md #4.
    `rule` is 'A' (ruling/prior-total only) or 'B' (also commodity headings).

    A prior total's own associated numeral (its slot, per associated_numeral)
    is part of *that* total, not an entry in the new block -- the boundary
    must skip past it, not just past the total's signgroup token.
    """
    start = 0
    for j in range(idx - 1, -1, -1):
        t = record.tokens[j]
        if t.kind == "ruling":
            start = j + 1
            break
        if _is_any_target(t):
            following = record.tokens[j + 1] if j + 1 < len(record.tokens) else None
            start = j + 2 if following is not None and following.kind == "numeral" else j + 1
            break
        if rule == "B" and is_commodity_heading(record, j, commodity_ids or set()):
            start = j + 1
            break
    return [t for t in record.tokens[start:idx] if t.kind == "numeral"]


# --------------------------------------------------------------------------- 6/7. exclusion + classification
ExclusionCategory = Literal[
    "AMBIGUOUS", "MISSING", "DAMAGED", "NON_COMPARABLE",
    "NO_IDENTIFIABLE_TOTAL", "OTHER",
]
ArithmeticCategory = Literal[
    "EXACT_CLOSURE", "ROUNDING_COMPATIBLE", "DAMAGED_OR_UNCERTAIN",
    "UNEXPLAINED_MISMATCH", "NOT_TESTABLE",
]


def classify_exclusion(occurrence_token: Token, total_token: Optional[Token],
                        block_tokens_a: list[Token],
                        block_tokens_b: Optional[list[Token]] = None) -> Optional[ExclusionCategory]:
    """First matching exclusion reason, in the order declared in
    H1_PROTOCOL.md #6, or None if the occurrence is arithmetically
    testable."""
    if occurrence_token.sign_identity_uncertain:
        return "AMBIGUOUS"

    total_value = numeral_value(total_token) if total_token else None
    block_values_a = [v for v in (numeral_value(t) for t in block_tokens_a) if v is not None]
    if total_value is None or not block_values_a:
        return "MISSING"

    damaged = occurrence_token.damaged or (total_token.damaged if total_token else False) \
        or any(t.damaged for t in block_tokens_a)
    if damaged:
        return "DAMAGED"

    if block_tokens_b is not None:
        block_values_b = [v for v in (numeral_value(t) for t in block_tokens_b) if v is not None]
        if block_values_a != block_values_b:
            r_a, _ = residual(total_value, block_values_a)
            r_b, _ = residual(total_value, block_values_b)
            cls_a = classify_arithmetic(r_a, _rel(r_a, total_value), damaged=False)
            cls_b = classify_arithmetic(r_b, _rel(r_b, total_value), damaged=False)
            if cls_a != cls_b:
                return "NON_COMPARABLE"

    return None


def residual(total: float, values: list[float]) -> tuple[float, Optional[float]]:
    """r, r_rel per H1_PROTOCOL.md #8."""
    r = total - sum(values)
    r_rel = abs(r) / abs(total) if total != 0 else None
    return r, r_rel


def _rel(r: float, total: float) -> Optional[float]:
    return abs(r) / abs(total) if total != 0 else None


def classify_arithmetic(r: float, r_rel: Optional[float], damaged: bool) -> ArithmeticCategory:
    """EXACT_CLOSURE / ROUNDING_COMPATIBLE / DAMAGED_OR_UNCERTAIN /
    UNEXPLAINED_MISMATCH, per H1_PROTOCOL.md #7. Order matters: damage is
    checked before residual size."""
    if damaged:
        return "DAMAGED_OR_UNCERTAIN"
    if abs(r) < EXACT_EPSILON:
        return "EXACT_CLOSURE"
    if abs(r) <= ROUNDING_ABS_TOLERANCE or (r_rel is not None and r_rel <= ROUNDING_REL_TOLERANCE):
        return "ROUNDING_COMPATIBLE"
    return "UNEXPLAINED_MISMATCH"


# --------------------------------------------------------------------------- 11. verdict
Verdict = Literal["SUPPORT", "WEAKENING", "FAILURE", "INCONCLUSIVE"]


def verdict(non_terminal_rate: float, unexplained_mismatch_rate: float,
            n_arithmetically_testable: int, not_testable_or_damaged_fraction: float) -> Verdict:
    """H1_PROTOCOL.md #11, applied exactly as declared."""
    if n_arithmetically_testable < MIN_TESTABLE_N:
        return "INCONCLUSIVE"
    if not_testable_or_damaged_fraction > MAX_UNTESTABLE_FRACTION:
        return "INCONCLUSIVE"

    positional_survives = non_terminal_rate <= 0.10

    if unexplained_mismatch_rate <= 0.10:
        arithmetic = "survives"
    elif unexplained_mismatch_rate <= 0.20:
        arithmetic = "weakened"
    else:
        arithmetic = "falsified"

    if not positional_survives:
        return "FAILURE"
    if arithmetic == "survives":
        return "SUPPORT"
    return "WEAKENING"
