# Constraint accumulation V2 protocol (canonical)

**Status: PROTOCOL FREEZE ONLY. No real V2 model has been fit, no real
ΔH/permutation p-value/Holm-adjusted p-value/verdict has been computed
against `data/generated/lineara_extracted.json`.** This document is the
**single canonical authority** for V2 — a reader should be able to execute
V2 from this document alone, without consulting
`docs/CONSTRAINT_ACCUMULATION_V2_DESIGN.md`,
`docs/CONSTRAINT_ACCUMULATION_V2_INDEPENDENCE_AUDIT.md`, or
`docs/CONSTRAINT_ACCUMULATION_V2_BLOCKER_AUDIT.md`, all of which remain as
**historical working notes only**, superseded by this document wherever
they differ. Where a working note added context this document omits for
brevity, this document still governs.

V2 is scientifically independent of, and does not reinterpret, weaken, or
rescue: the frozen KU-RO H1 **FAILURE**, the frozen Candidate 1 **NOT
SUPPORTED** result, or the frozen V1 accumulation result (WEAK POSITIVE
UPDATE, `results/CONSTRAINT_ACCUMULATION_RESULT.md`, commit
`d397f2e42ec0d7ed66300379430db5ebcd03c3ae`). V2 is a **new,
prospectively-defined estimand**, not a rerun or correction of V1.

## 1. Scientific question

*Among parsed numerical expressions with a resolvable whole-number
component, do structural predictors (context, position, commodity,
whole-component magnitude) provide incremental held-out information about
fraction-sign presence?*

## 2. Population (frozen exactly)

**Include row iff `numeric_value is not None`** — computed by reading
only the associated numeral token's `.value` field
(`constraint_accumulation_v2.is_integer_resolvable`); this check never
reads `.fractions` or `Y`.

This defines a **conditional population of parsed numerical expressions
with a resolvable whole-number component**:

- Fraction-only expressions (`numeric_value is None`) are **outside the
  V2 estimand entirely** — not included, not a comparison group.
- Integer-only expressions (`Y=0`) remain.
- Integer+fraction expressions (`Y=1`) remain.
- **`Y` genuinely varies within the included population** (21 of 219 real
  rows are `Y=1`, per already-disclosed POST-V1 DESIGN INFORMATION) — the
  selection rule does not mechanically determine `Y` for included rows.
- **V2 does not generalize to fraction-only expressions.** Any V2 finding
  is scoped to quantities of at least one whole unit.
- This is a **left-truncated conditional estimand** (truncated at
  whole-unit magnitude ≥1) — **not** established collider bias, and this
  document does not use that term for it
  (`docs/CONSTRAINT_ACCUMULATION_V2_BLOCKER_AUDIT.md` Phase 7 item 10).

## 3. Target (unchanged)

**`Y = FRACTION_SIGN_PRESENCE`** — identical construction to V1 and
Candidate 1: the associated numeral token's `.fractions` non-empty,
confidence-independent. No parsing change. Fraction numeric values
(Corazza et al.) are **not** imported, exactly as in every prior round of
this project.

## 4. Models (frozen exactly)

| model | adds |
|---|---|
| M0 | intercept only |
| M1 | `C_SITE` + `C_SUPPORT` |
| M2 | M1 + `C_POSITION` |
| M3 | M2 + `C_COMMODITY` |
| M4 | M3 + `WHOLE_COMPONENT_MAGNITUDE` |

`C_SITE`, `C_SUPPORT`, `C_POSITION`, `C_COMMODITY` are **identical,
unchanged** to V1 (`{Haghia Triada, OTHER}`, `{Tablet, OTHER}`,
`{FIRST, SECOND, THIRD_OR_LATER}`, `{LIQUID, DRY}` via Candidate 1's
frozen base-sign rule).

**`WHOLE_COMPONENT_MAGNITUDE = log2(1 + numeric_value)`** — one
**continuous** predictor. All included rows have `numeric_value ≥ 1`
(the numeral system's own additive, no-zero-digit convention, confirmed
in `docs/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md` §5, guarantees this
for every row admitted by §2's population rule — there is no
`numeric_value` in (0,1) representable without a fraction, and such rows
are excluded by construction). **No tertiles, no bins, no splines, no
nonlinear alternatives, no interactions, no feature selection, no
outcome-driven transformation choice** — this was audited structurally,
never against real `Y` (`docs/CONSTRAINT_ACCUMULATION_V2_DESIGN.md`
§"Magnitude representation").

## 5. M4 interpretation (frozen exactly)

**`WHOLE_COMPONENT_MAGNITUDE` measures the magnitude of the resolvable
whole-number component only.** It does **not** measure the total
mathematical value of the complete numerical expression. For an
integer+fraction expression, e.g. "3 + fraction A" and "3 + fraction B",
**both receive the identical M4 value** (`log2(4)`), regardless of which
fraction is attached. **This is recorded as a permanent limitation of M4,
not something to repair** — repairing it would require importing
contested Corazza fraction values, which remains prohibited.

## 6. Grouped cross-validation (frozen exactly)

**`GroupKFold(n_splits=5)`, grouped by `tablet_id`. Exactly 5 folds — no
3-fold fallback.** If the frozen fold-evaluability criterion (§7.A) fails
at 5 folds: **`INCONCLUSIVE`.**

**Rationale for dropping V1's 5→3 fallback (decided prospectively, not
after seeing an unfavorable result):** the blocker audit
(`docs/CONSTRAINT_ACCUMULATION_V2_BLOCKER_AUDIT.md` Phase 3) directly
checked both fold counts against the real, already-disclosed label
distribution and found 5-fold fully evaluable with **better** per-fold
minority support than 3-fold (minimum training-fold positives: 15 vs. 11)
— 3-fold offered no advantage. Retaining an unused fallback would be
needless complexity with no demonstrated benefit, and — more importantly
— would leave open exactly the kind of "try the alternative and see"
degree of freedom this project's discipline exists to close off. If a
future re-extraction of the corpus ever changes this balance, that is a
new, separate design question for a new round, not something this
protocol pre-authorizes a fallback for today.

## 7. Adequacy (frozen exactly, with honest epistemic classification)

Four distinct criteria, **deliberately not collapsed into one N-based
number**, each classified honestly — **none of B or C is presented as a
universal theorem; both are disclosed, project-specific safeguards**:

| # | criterion | protects against (failure mode) | epistemic classification |
|---|---|---|---|
| **A** | Every training fold (of the 5) contains both `Y` classes | Logistic regression cannot fit a coefficient for an outcome absent from its training data — a strict impossibility, not a judgment call | **MATHEMATICAL / ENGINEERING REQUIREMENT** (hard, definitional) |
| **B** | ≥5 minority-class (`Y=1`) rows in every training fold | High-variance, poorly-estimated coefficients and held-out log-loss from too few positive examples in a fold | **PROJECT-SPECIFIC MECHANISM-LINKED ADEQUACY SAFEGUARD** (power consideration) — an analogy to Cochran's classic ≥5-expected-cell-count convention for categorical inference, **not** a rigorous derivation specific to grouped-CV binary log-loss estimation with permutation inference; no such derivation is known to exist for this exact combined procedure |
| **C** | ≥50% of the finest conditional-permutation step's (M3→M4) populated strata contain both classes | A permutation null with too many single-class (zero-variance) strata has degraded resolution/power, even though it remains exactly valid (Type-I error controlled) at any N | **PROJECT-SPECIFIC MECHANISM-LINKED ADEQUACY SAFEGUARD** (power consideration) — not a universal permutation-testing theorem |
| **D** | Coarse feasibility screen: total N ≥150 (informational threshold, not V2-specific), tablets ≥50 | Catches a grossly inadequate population early | **PROJECT-SPECIFIC CONSERVATIVE SAFEGUARD**, weakest justification of the four, retained only as an initial screen, **never the primary or sole gate** |

**If A fails at 5 folds: `INCONCLUSIVE`, full stop (§6).** If A passes but
B or C fails: **`INCONCLUSIVE`** also — both are frozen, binding
requirements for this protocol despite their disclosed heuristic
epistemic status; "heuristic" here describes the *derivation* of the
threshold, not its *bindingness* once frozen.

**Constants:** `MIN_MINORITY_PER_TRAINING_FOLD = 5`,
`MIN_MIXED_STRATA_FRACTION = 0.5`
(`constraint_accumulation_v2.MIN_MINORITY_PER_TRAINING_FOLD`,
`constraint_accumulation_v2.MIN_MIXED_STRATA_FRACTION`).

## 8. Estimator and metric (unchanged from V1)

Logistic regression: `C=1.0`, `solver="lbfgs"`, `max_iter=1000`,
`random_state=20260906` (ENGINEERING REPRODUCIBILITY CHOICE, unchanged
seed). **No hyperparameter optimization of any kind.**

**Metric:** held-out binary log loss in bits
(`constraint_accumulation.log_loss_bits`, reused unchanged).
`ΔH_k = H_hat_{k-1} - H_hat_k`
(`constraint_accumulation.delta_h`, reused unchanged). `ΔH_k > 0`:
incremental predictive improvement. `ΔH_k = 0`: none. `ΔH_k < 0`: worse
held-out prediction.

## 9. Conditional permutation (unchanged mechanism from V1's corrected design)

For each non-baseline step (`M1→M2`, `M2→M3`, `M3→M4`):

- **What is permuted:** `Y` labels, within strata.
- **Within which strata:** the full cross-product of `M_{k-1}`'s own
  predictors — `(site_block, support_block)` for M1→M2;
  `(site_block, support_block, position_bucket)` for M2→M3;
  `(site_block, support_block, position_bucket, commodity_class)` for
  M3→M4 (`constraint_accumulation.conditional_permutation_delta`, reused
  unchanged — the mechanism was already re-audited as valid for V2 in
  `docs/CONSTRAINT_ACCUMULATION_V2_DESIGN.md` §"Null model re-audit").
- **What is preserved:** total N, tablet-group structure (permutation is
  within-stratum, not within-tablet — `GroupKFold` fold assignment is
  unaffected), every `M_{k-1}` predictor's stratum-level `Y`-count
  composition.
- **What is destroyed:** the pairing between `Y` and the newly-added
  block specifically.
- **Tablet dependence:** handled entirely by §6's grouped CV, not by the
  permutation (unchanged separation of concerns from V1).
- **B = 2000.** **Seed = 20260906** (same engineering seed, reused for
  consistency).
- **p-value formula:**
  `p_k = (#{ΔH_k^perm >= ΔH_k^obs} + 1) / (B + 1)`
  (`constraint_accumulation.step_permutation_pvalue`), computed
  **unconditionally on the sign of `ΔH_k^obs`** — a negative or zero
  observed `ΔH_k` still receives a real p-value (the V1 Phase-1
  correction, unchanged and reused).
- Strata with fewer than 2 rows are excluded from both the observed
  statistic and every null draw for that step
  (`constraint_accumulation.permutable_strata`), retained only
  descriptively.

## 10. Multiple testing (frozen exactly)

**Holm family = all evaluable {M2, M3, M4}, regardless of observed
sign** (`constraint_accumulation.holm_family`, reused unchanged). A step
is excluded from the family **only** for genuine, predeclared
evaluability failure (§7 criteria B/C applied at that step, or CV
non-evaluability) — **never** because it is external-model information.
**`C_COMMODITY` (M3) remains part of the statistical testing family on
equal footing with M2 and M4** — its EXTERNAL MODEL INFORMATION status
affects only how a *significant* M3 result is *interpreted* (§12), never
whether it is *tested*.

## 11. Verdict architecture (frozen exactly)

**Step verdict** (per M2/M3/M4, each exactly one of):
`SUPPORTED` (Holm-adjusted p < 0.05 **and** `ΔH_k > 0`), `NOT SUPPORTED`,
`NOT_EVALUABLE` (excluded from the Holm family per §7/§10).

**Broad verdict** (`constraint_accumulation_v2.classify_broad_verdict`):

- **DESIGN BLOCKED** — population or inference construction invalid
  *before* execution. (Not expected under this frozen protocol — §2's
  population validity and §7–10's mechanisms were audited and found
  sound — but the label remains defined for a genuine, currently
  unforeseen construction failure.)
- **INCONCLUSIVE** — design valid, but §7's adequacy criteria fail
  (globally, or at the 5-fold CV level, §6).
- **NEGATIVE UPDATE** — adequate, valid experiment; among the blocks that
  were actually evaluable, **none** is `SUPPORTED`.
- **LIMITED POSITIVE** — exactly one of {M2, M4} is `SUPPORTED` (M3's
  status does not change this label, whether or not M3 is also
  supported).
- **LIMITED POSITIVE (EXTERNAL-MODEL-ONLY)** — **only** M3 is
  `SUPPORTED`, and neither M2 nor M4 is.
- **ACCUMULATION EVIDENCE** — **both** M2 and M4 are `SUPPORTED`
  (independently, via the Holm-adjusted family) — M3's status is
  irrelevant to earning this label either way.

`M1` never appears in this determination — it is contextual baseline
only, exactly as in V1.

**Edge cases (all covered by the single rule above, and each has a
dedicated synthetic test, §13):** M2-only, M3-only, M4-only, M2+M3 (not
M4), M3+M4 (not M2), M2+M4 (ACCUMULATION EVIDENCE regardless of M3), all
three supported (still ACCUMULATION EVIDENCE, M3 noted separately), none
supported (NEGATIVE UPDATE), one step `NOT_EVALUABLE` (excluded, verdict
computed from the remaining evaluable steps), all three `NOT_EVALUABLE`
(falls through to `INCONCLUSIVE`, no evaluable non-baseline block at
all), M4 `NOT_EVALUABLE` specifically (M2/M3 verdict unaffected).

## 12. Claim firewall (frozen exactly)

Even **ACCUMULATION EVIDENCE** means only:

> Within the conditional V2 population (quantities ≥1 whole unit), at
> least two independently constructed structural/numerical blocks
> contribute sequential, conditionally distinct held-out information
> about fraction-sign presence.

It does **not** establish: decipherment, commodity semantics, Minoan
cognition, metrological intent, arithmetic sophistication, causal
scribal behavior, or cross-site universality. Any such claim requires a
separate, later, explicitly-scoped discussion — never this protocol or
its result document alone.

## 13. Anti-circularity declaration

1. Is `Y` defined without using predictor values? Yes — unchanged from
   V1/Candidate 1.
2. Is model order fixed before performance? Yes — identical rationale to
   V1 (context → structure → content → magnitude), unchanged.
3. Are feature categories fixed before performance? Yes — all four
   categorical blocks are closed, predeclared sets; `WHOLE_COMPONENT_
   MAGNITUDE` uses a fixed, non-fitted transform (§4) — no per-fold
   cutoff-fitting exists in V2 at all, unlike V1's `C_NUMERIC`.
4. Is the population-inclusion rule independent of `Y`? Yes, proven
   (§2; `docs/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md`).
5. Is `C_COMMODITY` reused unchanged from Candidate 1/V1? Yes.
6. Is the null fixed before `ΔH` is observed? Yes (§9, unchanged
   mechanism from V1's own corrected design).
7. Are all model steps retained even if they perform poorly? Yes — no
   step is dropped for underperforming; `NOT_EVALUABLE` is reserved for
   genuine adequacy failure, never for a disappointing result.
8. Can the protocol generate a negative program update? Yes, explicitly
   (§11, `NEGATIVE UPDATE`).
9. Are semantic claims separated from raw structural claims? Yes (§12).
10. Does M4 overclaim total quantity? No (§5, explicit limitation).

All ten: **YES.**

## 14. Explicit statement: no real model performance was inspected before freeze

No `ΔH_k`, held-out log loss, permutation p-value, Holm-adjusted p-value,
or verdict has been computed against `data/generated/lineara_extracted.json`
for V2, anywhere in this repository. Every V2-specific function is
exercised exclusively by synthetic fixtures in
`tests/test_constraint_accumulation_v2.py`. The only real-data-derived
figures referenced anywhere in this protocol (N=219, 89 tablets, 21
positives, per-fold counts, per-stratum counts) are figures **already
disclosed** in `docs/CONSTRAINT_ACCUMULATION_V2_BLOCKER_AUDIT.md`,
themselves computed from already-published V1 row labels via marginal
counting, not new inference.
