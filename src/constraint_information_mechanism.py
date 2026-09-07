"""
Constraint accumulation V3 — mechanism discovery / asymmetric elimination
audit. PURE MATHEMATICS / VERIFICATION MODULE.

Does NOT touch data/generated/lineara_extracted.json. Does NOT modify,
import, or recompute anything from H1, Candidate 1, V1, or V2. It builds
and numerically verifies the finite exact examples and identities used in
docs/CONSTRAINT_INFORMATION_MECHANISM... no wait, see
results/CONSTRAINT_INFORMATION_MECHANISM.md for the write-up this module
supports.

Every function here operates on small, hand-specified finite probability
spaces (explicit dicts of state -> probability, or explicit counts) --
never on real corpus data. This is a theory-verification module, not a
data-analysis module.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


# =============================================================================
# TASK 1 — the minimal single-constraint theorem
# =============================================================================
def posterior_after_elimination(n1: int, n0: int, e1: int, e0: int) -> Optional[float]:
    """p' = P(Y=1 | S') for a uniform-state population with n1 positive
    and n0 negative states, after eliminating e1 positives and e0
    negatives (0 <= e1 <= n1, 0 <= e0 <= n0). Returns None if S' is empty."""
    if not (0 <= e1 <= n1 and 0 <= e0 <= n0):
        raise ValueError("eliminated counts must not exceed available counts")
    n1p, n0p = n1 - e1, n0 - e0
    if n1p + n0p == 0:
        return None
    return n1p / (n1p + n0p)


def elimination_rates(n1: int, n0: int, e1: int, e0: int) -> tuple[float, float]:
    """r1 = P(eliminated | Y=1), r0 = P(eliminated | Y=0)."""
    r1 = e1 / n1 if n1 > 0 else 0.0
    r0 = e0 / n0 if n0 > 0 else 0.0
    return r1, r0


def theorem_p_prime_equals_p(n1: int, n0: int, e1: int, e0: int, tol: float = 1e-12) -> bool:
    """Direct check of the derived identity p'=p <=> r1=r0 (not an
    independent computation -- this literally re-derives p' from the
    counts and compares, so it is a computational proof-check, not a
    restatement of the theorem)."""
    p = n1 / (n1 + n0)
    p_prime = posterior_after_elimination(n1, n0, e1, e0)
    r1, r0 = elimination_rates(n1, n0, e1, e0)
    lhs = (p_prime is not None) and abs(p_prime - p) < tol
    rhs = abs(r1 - r0) < tol
    return lhs == rhs   # the iff itself: both sides must agree


# =============================================================================
# TASK 2 — explicit finite counterexamples
# =============================================================================
def example_A_huge_reduction_zero_information() -> dict:
    """S=100 states, 50 positive/50 negative. Eliminate 45 of each
    (90% cardinality reduction) -- r1=r0=0.9 exactly -> p'=p exactly."""
    n1, n0 = 50, 50
    e1, e0 = 45, 45
    p = n1 / (n1 + n0)
    p_prime = posterior_after_elimination(n1, n0, e1, e0)
    r1, r0 = elimination_rates(n1, n0, e1, e0)
    reduction = (e1 + e0) / (n1 + n0)
    return {"n1": n1, "n0": n0, "e1": e1, "e0": e0, "p": p, "p_prime": p_prime,
            "r1": r1, "r0": r0, "cardinality_reduction_fraction": reduction,
            "information_gain": p_prime is not None and abs(p_prime - p) < 1e-12}


def example_B_tiny_reduction_large_information() -> dict:
    """S=10000 states, 100 positive/9900 negative (p=0.01). Eliminate 99
    of the 100 positives, 0 negatives -- only 0.99% of |S| removed, but
    the posterior odds of Y=1 collapse ~100-fold."""
    n1, n0 = 100, 9900
    e1, e0 = 99, 0
    p = n1 / (n1 + n0)
    p_prime = posterior_after_elimination(n1, n0, e1, e0)
    r1, r0 = elimination_rates(n1, n0, e1, e0)
    reduction = (e1 + e0) / (n1 + n0)
    return {"n1": n1, "n0": n0, "e1": e1, "e0": e0, "p": p, "p_prime": p_prime,
            "r1": r1, "r0": r0, "cardinality_reduction_fraction": reduction,
            "odds_ratio_p_to_pprime": (p / (1 - p)) / (p_prime / (1 - p_prime))}


def example_C_progressive_no_accumulation() -> dict:
    """S0(100: 50/50) -> S1(90: 45/45) -> S2(80: 40/40) -> S3(70: 35/35).
    Balanced elimination at every step (5 pos + 5 neg each time) ->
    p constant at 0.5 throughout despite genuine, repeated cardinality
    shrinkage."""
    stages = []
    n1, n0 = 50, 50
    stages.append({"stage": 0, "n1": n1, "n0": n0, "n_total": n1 + n0, "p": n1 / (n1 + n0)})
    for j in range(1, 4):
        n1, n0 = n1 - 5, n0 - 5
        stages.append({"stage": j, "n1": n1, "n0": n0, "n_total": n1 + n0, "p": n1 / (n1 + n0)})
    ps = [s["p"] for s in stages]
    return {"stages": stages, "all_p_equal": all(abs(p - ps[0]) < 1e-12 for p in ps),
            "cardinality_shrunk_every_stage": all(
                stages[j]["n_total"] < stages[j - 1]["n_total"] for j in range(1, 4))}


def example_D_progressive_accumulation() -> dict:
    """S0(100: 50/50) -> S1(80: 50/30) -> S2(70: 50/20) -> S3(60: 50/10).
    Each stage eliminates negatives only (r1=0, r0>0 every stage,
    conditionally) -> p strictly increases at every stage."""
    stages = []
    n1, n0 = 50, 50
    stages.append({"stage": 0, "n1": n1, "n0": n0, "n_total": n1 + n0, "p": n1 / (n1 + n0)})
    for removed in (20, 10, 10):
        n0 = n0 - removed
        stages.append({"stage": len(stages), "n1": n1, "n0": n0, "n_total": n1 + n0, "p": n1 / (n1 + n0)})
    ps = [s["p"] for s in stages]
    strictly_increasing = all(ps[j] > ps[j - 1] for j in range(1, len(ps)))
    return {"stages": stages, "strictly_increasing": strictly_increasing}


# =============================================================================
# TASK 3 — I(C;X) > 0 while I(C;Y) = 0 (Y = f(X), data-processing inequality)
# =============================================================================
def mutual_information_binary(joint: dict) -> float:
    """I(A;B) in bits from an explicit joint pmf {(a,b): prob, ...} over
    two variables with finitely many values. Exact, no approximation."""
    from collections import defaultdict
    pa: dict = defaultdict(float)
    pb: dict = defaultdict(float)
    for (a, b), p in joint.items():
        pa[a] += p
        pb[b] += p
    mi = 0.0
    for (a, b), p in joint.items():
        if p > 0:
            mi += p * math.log2(p / (pa[a] * pb[b]))
    return mi


def construction_IX_positive_IY_zero() -> dict:
    """X uniform over {a,b,c,d} (4 states, each prob 1/4).
    Y = f(X) = 1{X in {a,b}}  (a 2-to-1 coarsening -- Y=f(X) exactly).
    C = 1{X in {a,c}}          (cuts across the Y partition).

    Claim: I(C;Y) = 0 exactly (C independent of Y) while I(C;X) > 0
    (in fact I(C;X) = 1 bit, since (C,Y) jointly determine X exactly).
    """
    states = ["a", "b", "c", "d"]
    px = {s: 0.25 for s in states}
    Y = {"a": 1, "b": 1, "c": 0, "d": 0}
    C = {"a": 1, "b": 0, "c": 1, "d": 0}

    joint_CY: dict = {}
    for s in states:
        key = (C[s], Y[s])
        joint_CY[key] = joint_CY.get(key, 0.0) + px[s]
    I_CY = mutual_information_binary(joint_CY)

    joint_CX = {(C[s], s): px[s] for s in states}
    I_CX = mutual_information_binary(joint_CX)

    # verify (C,Y) jointly determine X (a Markov/bijection check)
    cy_to_x: dict = {}
    bijective = True
    for s in states:
        key = (C[s], Y[s])
        if key in cy_to_x and cy_to_x[key] != s:
            bijective = False
        cy_to_x[key] = s

    return {
        "I_C_Y_bits": I_CY, "I_C_X_bits": I_CX,
        "C_independent_of_Y": abs(I_CY) < 1e-12,
        "C_informative_about_X": I_CX > 1e-9,
        "(C,Y)_jointly_determine_X": bijective,
        "data_processing_inequality_satisfied": I_CY <= I_CX + 1e-12,
    }


# =============================================================================
# TASK 5 / 8 — sequential conditioning, Simpson-type reversal constructions
# =============================================================================
def sequential_null_then_informative() -> dict:
    """S0 (8 states: 4 pos p1-p4, 4 neg n1-n4, uniform).
    Stage 1 eliminates {p1,p2,n1,n2} -- r1=r0=0.5 (marginally AND
    conditionally, since this IS stage 1) -> null step.
    Stage 2 (conditioned on survivors {p3,p4,n3,n4}) eliminates {n3} only
    -- r1=0, r0=0.5 conditionally -> informative step, despite stage 1
    contributing nothing. Demonstrates a null step does not preclude a
    later informative step."""
    p0 = 4 / 8
    # stage 1
    n1, n0 = 4, 4
    e1, e0 = 2, 2
    r1_1, r0_1 = elimination_rates(n1, n0, e1, e0)
    p1 = posterior_after_elimination(n1, n0, e1, e0)
    # stage 2, conditioned on stage-1 survivors
    n1_s1, n0_s1 = n1 - e1, n0 - e0   # 2 pos, 2 neg
    e1_2, e0_2 = 0, 1
    r1_2, r0_2 = elimination_rates(n1_s1, n0_s1, e1_2, e0_2)
    p2 = posterior_after_elimination(n1_s1, n0_s1, e1_2, e0_2)
    return {
        "p0": p0, "stage1": {"r1": r1_1, "r0": r0_1, "p_after": p1, "informative": abs(r1_1 - r0_1) > 1e-12},
        "stage2": {"r1": r1_2, "r0": r0_2, "p_after": p2, "informative": abs(r1_2 - r0_2) > 1e-12},
        "null_step_did_not_block_later_information": (abs(r1_1 - r0_1) < 1e-12) and (abs(r1_2 - r0_2) > 1e-12) and (p2 != p1),
    }


def simpson_marginal_balanced_conditional_asymmetric() -> dict:
    """Two equal-size strata A, B (20 each, 10 pos/10 neg in each,
    stratifying variable C1). Within A, constraint C2 eliminates 8 neg +
    2 pos (r1=0.2, r0=0.8). Within B, C2 eliminates 8 pos + 2 neg
    (r1=0.8, r0=0.2) -- REVERSED. Pooled (ignoring the C1 stratification)
    the eliminated counts are symmetric (10 pos + 10 neg total out of 20
    each) -- marginal r1=r0=0.5, appearing perfectly uninformative, while
    C2 is in fact highly informative (in opposite directions) within each
    stratum."""
    # stratum A
    nA1, nA0, eA1, eA0 = 10, 10, 2, 8
    rA1, rA0 = elimination_rates(nA1, nA0, eA1, eA0)
    pA_after = posterior_after_elimination(nA1, nA0, eA1, eA0)
    # stratum B (reversed)
    nB1, nB0, eB1, eB0 = 10, 10, 8, 2
    rB1, rB0 = elimination_rates(nB1, nB0, eB1, eB0)
    pB_after = posterior_after_elimination(nB1, nB0, eB1, eB0)
    # pooled / marginal (ignoring stratification)
    pooled_n1, pooled_n0 = nA1 + nB1, nA0 + nB0
    pooled_e1, pooled_e0 = eA1 + eB1, eA0 + eB0
    pooled_r1, pooled_r0 = elimination_rates(pooled_n1, pooled_n0, pooled_e1, pooled_e0)
    pooled_p_after = posterior_after_elimination(pooled_n1, pooled_n0, pooled_e1, pooled_e0)
    pooled_p_before = pooled_n1 / (pooled_n1 + pooled_n0)
    return {
        "stratum_A": {"r1": rA1, "r0": rA0, "p_after": pA_after},
        "stratum_B": {"r1": rB1, "r0": rB0, "p_after": pB_after},
        "pooled_marginal": {"r1": pooled_r1, "r0": pooled_r0,
                             "p_before": pooled_p_before, "p_after": pooled_p_after},
        "marginal_appears_balanced": abs(pooled_r1 - pooled_r0) < 1e-12,
        "within_strata_are_strongly_asymmetric_and_reversed": (
            abs(rA1 - rA0) > 0.5 and abs(rB1 - rB0) > 0.5 and (rA1 - rA0) * (rB1 - rB0) < 0
        ),
    }


def confounded_proxy_marginal_asymmetric_conditionally_null() -> dict:
    """Mirror construction: C1 (e.g. site) is itself associated with Y.
    C2 (e.g. position) is correlated with C1 but, CONDITIONAL on C1,
    carries no further Y-information. Evaluated marginally (ignoring
    C1), C2 APPEARS asymmetric purely because it is a confounded proxy
    for C1; conditional on C1, C2's asymmetry vanishes in every stratum.

    Construction: 2 strata by C1: 'HT' (60 states: 40 pos/20 neg) and
    'OTHER' (40 states: 10 pos/30 neg) -- C1 itself is clearly
    informative (0.667 vs 0.25 positive rate). C2='LATE' is assigned so
    that within EACH stratum, LATE and Y are independent (r1=r0 within
    each stratum), but LATE occurs disproportionately in OTHER (say 80%
    of OTHER is LATE, 20% of HT is LATE) -- so marginally, "eliminating
    LATE" looks associated with Y purely because it is correlated with
    C1, not because it carries independent information."""
    # HT stratum: 40 pos, 20 neg; LATE = 20% of each class (independent within stratum)
    HT_pos, HT_neg = 40, 20
    HT_late_pos, HT_late_neg = round(0.2 * HT_pos), round(0.2 * HT_neg)
    # OTHER stratum: 10 pos, 30 neg; LATE = 80% of each class (independent within stratum)
    OT_pos, OT_neg = 10, 30
    OT_late_pos, OT_late_neg = round(0.8 * OT_pos), round(0.8 * OT_neg)

    # within-stratum asymmetry (should be ~0 -- LATE is independent of Y given C1)
    r1_HT, r0_HT = elimination_rates(HT_pos, HT_neg, HT_late_pos, HT_late_neg)
    r1_OT, r0_OT = elimination_rates(OT_pos, OT_neg, OT_late_pos, OT_late_neg)

    # marginal (pooled) asymmetry
    total_pos, total_neg = HT_pos + OT_pos, HT_neg + OT_neg
    total_late_pos, total_late_neg = HT_late_pos + OT_late_pos, HT_late_neg + OT_late_neg
    r1_marg, r0_marg = elimination_rates(total_pos, total_neg, total_late_pos, total_late_neg)

    return {
        "within_HT": {"r1": r1_HT, "r0": r0_HT, "asymmetric": abs(r1_HT - r0_HT) > 1e-9},
        "within_OTHER": {"r1": r1_OT, "r0": r0_OT, "asymmetric": abs(r1_OT - r0_OT) > 1e-9},
        "marginal_pooled": {"r1": r1_marg, "r0": r0_marg, "asymmetric": abs(r1_marg - r0_marg) > 1e-9},
        "confound_produces_spurious_marginal_asymmetry": (
            abs(r1_HT - r0_HT) < 1e-9 and abs(r1_OT - r0_OT) < 1e-9 and abs(r1_marg - r0_marg) > 1e-9
        ),
    }


# =============================================================================
# TASK 6/8 — soft (reweighting) generalization, sanity check
# =============================================================================
def soft_reweighting_generalization(n1: int, n0: int, w1: float, w0: float) -> dict:
    """Generalizes elimination (hard 0/1 exclusion) to reweighting: each
    Y=1 state gets weight w1 in [0,1], each Y=0 state weight w0 in [0,1]
    (uniform within class for simplicity). p' = (n1*w1)/(n1*w1+n0*w0).
    p'=p iff w1=w0, the direct weighted analogue of r1=r0."""
    p = n1 / (n1 + n0)
    numer = n1 * w1
    denom = n1 * w1 + n0 * w0
    p_prime = numer / denom if denom > 0 else None
    return {"p": p, "p_prime": p_prime, "w1": w1, "w0": w0,
            "equal_weight_iff_p_unchanged": (abs(w1 - w0) < 1e-12) == (p_prime is not None and abs(p_prime - p) < 1e-12)}


# =============================================================================
# TASK 6 — V1 -> V2 mechanism check (numbers only, already-disclosed figures)
# =============================================================================
def v1_v2_elimination_diagnostic() -> dict:
    """Re-expresses the ALREADY-DISCLOSED V1->V2 population change
    (results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md;
    docs/CONSTRAINT_ACCUMULATION_V2_BLOCKER_AUDIT.md) in elimination-
    asymmetry terms. Uses only already-published counts (V1 N=236,
    positives=38; V2 excludes exactly the 17 NO_INTEGER_VALUE rows, all
    of which were positive) -- no new data access, no re-derivation of
    the underlying corpus facts, purely arithmetic on already-published
    numbers."""
    n1_v1, n0_v1 = 38, 198          # V1 population (236 total)
    e1, e0 = 17, 0                   # V1 -> V2 elimination: 17 positives, 0 negatives removed
    r1, r0 = elimination_rates(n1_v1, n0_v1, e1, e0)
    p_v1 = n1_v1 / (n1_v1 + n0_v1)
    p_v2 = posterior_after_elimination(n1_v1, n0_v1, e1, e0)
    return {
        "V1_population": {"n1": n1_v1, "n0": n0_v1, "p": p_v1},
        "eliminated_going_to_V2": {"e1": e1, "e0": e0},
        "r1_r0": {"r1": r1, "r0": r0},
        "V2_population_implied": {"n1": n1_v1 - e1, "n0": n0_v1 - e0, "p": p_v2},
        "extreme_asymmetry": abs(r1 - r0) > 0.4,   # r1=0.447, r0=0 -- a large, not subtle, asymmetry
        "note": ("r1=17/38 (0.447) vs r0=0/198 (0.0) is the exact, already-disclosed "
                 "asymmetry between V1's and V2's populations -- consistent with, and a direct "
                 "numerical restatement of, why the NO_INTEGER_VALUE category behaved as a "
                 "near-deterministic predictor of Y within V1's full population."),
    }
