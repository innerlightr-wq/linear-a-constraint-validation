# Constraint-accumulation design (Design 1, recommended)

**Status: DESIGN ONLY.** No cross-validated score, entropy-reduction
estimate, model-comparison result, p-value, or accumulation verdict exists
anywhere in this repository for this design. See
`docs/CONSTRAINT_ACCUMULATION_CANDIDATES.md` for the feature audit, target
ranking, and rejected alternative designs.

This design tests **constraint accumulation** — whether independently
defined structural information reduces held-out uncertainty about a target
*progressively*, as blocks are added — not single-constraint association.
It is scientifically independent of, and does not reinterpret, weaken, or
rescue, either the frozen KU-RO H1 **FAILURE**
(`results/H1_RESULT.md`) or the frozen Candidate 1 **NOT SUPPORTED**
result (`results/CANDIDATE1_RESULT.md`, commit
`3a68afb650895552eda65ac5f69d16816140bfd3`).

## Target

**Y = fraction-sign presence**, identical definition to
`constraint_candidate1.fraction_present` (associated numeral token's
`.fractions` non-empty, confidence-independent) — reused unchanged.

## Observational unit

**Raw occurrence level** (one row per qualifying LIQUID/DRY commodity
occurrence with a resolvable associated quantity — the same universe as
Candidate 1's Sensitivity A, N=236, 133 unique tablets, already disclosed
in `results/CANDIDATE1_RESULT.md`), **not** deduplicated to one-per-tablet.
This is a deliberate, disclosed difference from Candidate 1's own tablet-
level primary unit: Candidate 1 used tablet-level dedup + a
first-qualifying-occurrence rule specifically to defend a single marginal
permutation test against opportunity bias. This design instead needs more
rows to fit a multi-block predictive model and uses **grouped
cross-validation by tablet** (below) to control for same-tablet
non-independence directly, rather than discarding rows — a different, but
equally principled, way of handling the same underlying dependence
concern, appropriate to a predictive-accumulation framing rather than a
single-hypothesis-test framing.

## Nested predictor blocks

| model | adds | rationale for this position in the sequence |
|---|---|---|
| **M0** | intercept only | base rate of Y, no information |
| **M1** | + C_SITE {Haghia Triada, OTHER}, C_SUPPORT {Tablet, OTHER} | purely archival/physical context — where and on what kind of object a record was written, independent of the record's own content |
| **M2** | + C_POSITION {FIRST, SECOND, THIRD_OR_LATER} | purely structural/syntactic — where within the record this occurrence falls, still no semantic content about *what* is recorded |
| **M3** | + C_COMMODITY {LIQUID, DRY} | semantic content — *what* commodity, reusing Candidate 1's frozen, externally-imported label unchanged |
| **M4** | + C_NUMERIC {SMALL, MEDIUM, LARGE, NO_INTEGER_VALUE} | quantitative content — *how much*, predeclared marginal-quantile bins |

**This order was fixed before any model was fit or performance inspected,**
on the stated rationale (context → structure → content → magnitude, each
step a genuinely different *kind* of information) — not reordered after
seeing results, and not permitted to be reordered after seeing results in
any future round that executes this design.

## Primary metric

**Held-out cross-validated log-loss**, base-2 (bits), so it reads directly
as an entropy estimate: `H_hat(Y | M_k)` = mean held-out log-loss of model
`M_k` across CV folds. `ΔH_k = H_hat(Y | M_{k-1}) - H_hat(Y | M_k)`
(positive ΔH = the added block reduced held-out uncertainty). Secondary,
descriptive only, not used for any verdict: held-out accuracy, held-out
Brier score.

**No monotonic improvement is required by construction.** If `ΔH_k ≤ 0`
at some step, that step is recorded plainly as a genuine failure of
accumulation at that point — not smoothed over, not used to justify
dropping or reordering that block.

## Model class (Phase 12 complexity firewall)

**Plain logistic regression only**, one-hot-encoded categorical predictors,
a single **fixed, predeclared, untuned regularization strength** (no
regularization-strength search — that would itself be a form of held-out
tuning this round's firewall prohibits). No random forest, gradient
boosting, neural network, or embedding of any kind. Given the small
predictor cardinality (≤4 blocks, each 2–4 levels) and moderate sample size
(N≈236), a plain GLM is judged adequate and appropriate; a more complex
model would risk exceeding what N≈236 can reliably support (Phase 20 Q8).

## Grouped cross-validation (Phase 8)

**Primary: `GroupKFold(n_splits=5)`, grouped by `tablet_id`.** No tablet's
occurrences appear in both a fold's train and test split. GroupKFold's
split is deterministic given the group labels' fixed input order — no
separate shuffling seed is required or introduced.

**Secondary, feasibility only, not primary: leave-one-site-out.** True
leave-one-*individual*-site-out (across the ≈9 sites with any qualifying
occurrence) is judged **INFEASIBLE**: per `results/CANDIDATE1_RESULT.md`
§7, most individual sites fall far below any reasonable per-fold adequacy
threshold once restricted to this universe. The only leave-one-site-out
check this design can honestly support is the coarse **HT-held-out vs.
OTHER-held-out** split already implied by the C_SITE collapse — and even
that is a weak generalization check, not a demonstration of cross-site
robustness across Crete's archaeological diversity. **No claim of
cross-site generalization will be made beyond what this coarse, two-level
check can actually support.**

## Interaction/synergy analysis (Phase 11, optional, design only)

A secondary, **optional**, **not-run-this-round** design: compare M3
(additive C_SITE/SUPPORT + C_POSITION + C_COMMODITY) against an
interaction model adding a single predeclared `C_POSITION × C_COMMODITY`
interaction term, using the same held-out log-loss metric and the same
grouped CV. If the interaction model does not improve held-out
performance beyond M3, that is recorded as **no evidence of synergy** — a
plain additive/accumulation finding is **not**, by itself, a synergy
finding, and this project will not describe it as such (Phase 10). This
analysis is designed but explicitly **not executed** in this round.

## Falsification criterion (Phase 16)

**If M2, M3, and M4 each fail to reduce held-out log-loss beyond what the
predeclared within-stratum permutation null for that step would predict by
chance (`docs/CONSTRAINT_ACCUMULATION_NULLS.md`), this experiment provides
a NEGATIVE UPDATE to the broad constraint-accumulation program** — not
merely "inconclusive," and not rescued by any single model "beating base
rate" by a trivial margin. A meaningful positive finding requires at least
one block's `ΔH_k` to exceed its own predeclared null distribution's
extreme values, reproducibly (i.e., not solely on one arbitrarily chosen
CV fold split).

## Cognitive-interpretation firewall (Phase 18)

**No claim about ancient cognitive capability will be drawn from any
result this design could produce.** A held-out predictive relationship
among administrative-record structural features, if found, would support
at most a claim about **structured quantitative record-keeping
organization** — it would not, on its own, license any claim about
algebra, inverse operations, formal probability, abstract rational-number
theory, or modern measurement concepts. Any such discussion is deferred to
a separate, later document, explicitly not this one.
