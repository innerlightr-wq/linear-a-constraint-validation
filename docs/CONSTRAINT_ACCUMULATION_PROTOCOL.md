# Constraint-accumulation protocol (canonical)

**Status: PROTOCOL FREEZE ONLY. No real cross-validation, log-loss,
entropy-reduction, model-comparison, permutation p-value, or accumulation
verdict has been computed against `data/generated/lineara_extracted.json`
anywhere in this repository.** This document is the single canonical
authority for the constraint-accumulation experiment, analogous in status
to `docs/H1_PROTOCOL.md` and `docs/CANDIDATE1_PROTOCOL.md`. **Where this
document conflicts with `docs/CONSTRAINT_ACCUMULATION_CANDIDATES.md`,
`docs/CONSTRAINT_ACCUMULATION_DESIGN.md`, or
`docs/CONSTRAINT_ACCUMULATION_NULLS.md`, this document governs** — two
conflicts were found and are resolved explicitly below (§4 numeric bins,
§8 null model), not silently carried forward.

This experiment is scientifically independent of, and does not reinterpret,
weaken, or rescue: the frozen KU-RO H1 **FAILURE** (`results/H1_RESULT.md`),
or the frozen Candidate 1 **NOT SUPPORTED** result
(`results/CANDIDATE1_RESULT.md`, commit
`3a68afb650895552eda65ac5f69d16816140bfd3`; `CANDIDATE1_PRE_RESULT_FREEZE`
= `f86e4a1af9014cc6b0a18a7ccc0b7affcc7555e2`).

## 1. Scientific hypothesis

Independently defined structural constraint families may progressively
reduce held-out uncertainty about an independently observed target. This
is a **conditional accumulation** test — not a repeat, in more variables,
of Candidate 1's marginal commodity→fraction association test.

## 2. Target Y

**Y = FRACTION_SIGN_PRESENCE.** `Y = 1` iff the associated numeral token's
`.fractions` is non-empty (confidence-independent, identical in spirit to
`constraint_candidate1.fraction_present`, reused unchanged). `Y = 0` iff a
resolvable associated numeral exists and `.fractions` is empty. Rows with
no resolvable quantity association, or with an ambiguous/damaged structural
parse, are **excluded** from Y's domain entirely (not coerced to Y=0). No
fraction numeric value, no Corazza value table, no confidence grade is
used anywhere in Y's definition.

## 3. Unit of analysis and dependence grouping

**Primary unit: raw qualifying commodity occurrence** (one row per
LIQUID/DRY commodity occurrence with a resolvable associated numeral;
`src/constraint_accumulation.build_feature_rows`) — **not** deduplicated to
one-per-tablet, unlike Candidate 1. **Dependence strategy: occurrence-level
analysis + tablet-grouped validation** — every occurrence from the same
tablet stays in the same CV fold (`GroupKFold`, grouped by `tablet_id`; §6).
This is a deliberate substitute for Candidate 1's tablet-level dedup,
appropriate to a predictive/held-out framing rather than a single
permutation-test framing — not an oversight.

**Probable same-physical-artifact grouping** (reusing
`constraint_candidate1.physical_artifact_key` unchanged) is a
**predeclared SENSITIVITY only** (§13) — grouping CV by physical artifact
instead of by raw tablet ID — never the primary analysis.

## 4. Feature blocks and nesting order

| model | adds |
|---|---|
| **M0** | intercept only |
| **M1** | `C_SITE` + `C_SUPPORT` |
| **M2** | M1 + `C_POSITION` |
| **M3** | M2 + `C_COMMODITY` |
| **M4** | M3 + `C_NUMERIC` |

Order fixed before any empirical performance was inspected: context
(archival/physical) → structure (syntactic position) → content (commodity
semantics) → magnitude (quantitative content). **No reordering after
results, in this or any future round.**

**`C_SITE`** — binary `{Haghia Triada, OTHER}`.
`site_block(site)`: `site.strip().casefold() == "haghia triada"` →
`"Haghia Triada"`, else `"OTHER"` (missing/`None` → `"OTHER"`).

**`C_SUPPORT`** — binary `{Tablet, OTHER}`.
`support_block(support)`: `support.strip().casefold() == "tablet"` →
`"Tablet"`, else `"OTHER"` (missing/`None` → `"OTHER"`). 19 raw support
categories are **not** retained in the primary model (sample-size /
collinearity control, per instruction).

**`C_POSITION`** — `{FIRST, SECOND, THIRD_OR_LATER}`. Defined **relative
to**: the ordinal rank (1st, 2nd, 3rd-or-later, 1-indexed) of this
qualifying occurrence among all qualifying (LIQUID/DRY, has-resolvable-
quantity) occurrences within the **same tablet record**, in token order —
`src/constraint_accumulation.position_bucket`, fed by
`build_feature_rows`'s own token-order enumeration. Not "position within
the tablet's raw token stream" in general — specifically, rank among
*qualifying commodity occurrences only*.

**`C_COMMODITY`** — binary `{LIQUID, DRY}`, **exactly** Candidate 1's
frozen classification, reused unchanged: `LIQUID = {VIN, OLE*}`,
`DRY = {GRA*, OLIV}`; base-sign rule = substring before first `"+"`, then
exact equality (`constraint_candidate1.commodity_class`, imported without
modification). No new commodity classes. **Epistemic status: EXTERNAL
DOMAIN MODEL INPUT** — the commodity ideogram identity is directly
observed; the LIQUID/DRY semantic grouping is imported from prior
scholarship (`docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md` items 7–8). Any
M3 interpretation inherits Candidate 1's own **PARTIAL EVIDENTIAL
DEPENDENCE** classification (`results/CANDIDATE1_RESULT.md` §22) unless a
future, separate audit establishes otherwise.

**`C_NUMERIC`** — `{SMALL, MEDIUM, LARGE, NO_INTEGER_VALUE}`. **See §4a —
this is one of the two resolved conflicts with the earlier design notes.**

### 4a. Numeric bin rule — CONFLICT RESOLVED

`docs/CONSTRAINT_ACCUMULATION_CANDIDATES.md` fixed `SMALL ≤ 3`,
`MEDIUM 4–15`, `LARGE ≥ 16` from a single tertile check computed over the
**full corpus** (all 236 occurrences), before any CV split existed. This
round's own instruction is explicit: *"If a distribution-derived rule such
as quantiles is used, it MUST be fit inside each training fold only. Do
not compute global quantiles on the full dataset before CV."* The earlier
rule violates this.

**Resolution — this document's rule governs:** cutoffs are
**TRAINING-FOLD-DERIVED**, computed independently inside each GroupKFold
training split, from that split's own non-`None` numeral values only
(tertile method, `constraint_accumulation.fit_numeric_bin_cutoffs`), then
applied **identically** to both that fold's training rows and its held-out
test rows (`constraint_accumulation.numeric_bin_fold`) — the test rows are
never used to choose the cutoffs. `NO_INTEGER_VALUE` (a fraction-only
numeral, no whole-number part) is an explicit category, excluded from the
quantile computation itself but never dropped from the row set. If a
training fold has fewer than 3 non-`None` values, cutoff-fitting raises
(§6 `CV_NOT_EVALUABLE` for that fold — not silently skipped).

The old, fixed-global rule (`constraint_accumulation.numeric_bin`,
`NUMERIC_SMALL_MAX=3`, `NUMERIC_MEDIUM_MAX=15`) is **retained in code**
but is **not primary** — usable only for a descriptive comparison
(does fold-derived vs. fixed-global binning change the qualitative
result), never for the primary `ΔH_4`.

If, at execution time, no training fold can produce 3+ non-`None` values
(implausible given N≈219 with resolvable integer values, but not yet
verified against real data this round), **M4 is removed** per this
round's own instruction — not kept "to force four steps."

## 5. Model family

**Plain logistic regression**, one-hot-encoded categorical predictors with
**fixed reference levels dropped** (`REFERENCE_LEVELS` —
`site_block="OTHER"`, `support_block="OTHER"`, `position_bucket="FIRST"`,
`commodity_class="DRY"`, `numeric_bin="SMALL"`;
`constraint_accumulation.encode_indicator`). Because every predictor is a
**closed, fully-enumerated category set** fixed by the bucket functions
themselves (never an open vocabulary read directly from the corpus), there
is no "unseen categorical level" possible at encode time and no fitting
step is required for the encoding itself — only the numeric-bin cutoffs
(§4a) are fold-fit.

- **Intercept:** included.
- **Regularization:** L2, fixed `C=1.0` (sklearn convention) —
  **ENGINEERING REPRODUCIBILITY CHOICE**, not a scientific tuning
  parameter; no regularization-strength search of any kind.
- **Solver:** `lbfgs`.
- **Max iterations:** `1000` (fixed, generous, to avoid non-convergence
  without needing to tune).
- **Random state:** `20260906` (the same engineering seed already used in
  `src/run_candidate1.py`, reused for consistency).

**Excluded by design:** random forest, gradient boosting, neural network,
feature selection, stepwise regression.

## 6. Cross-validation

**Primary: `GroupKFold(n_splits=5)`, grouped by `tablet_id`.** No tablet's
occurrences appear in both a fold's train and test split.

**Fold-validity rule:** every **training** fold must contain both Y
classes (`constraint_accumulation.fold_is_evaluable`). A **test** fold with
only one class is still scoreable (log loss is well-defined given valid
predicted probabilities) and is not itself a failure condition. If any
training fold is not evaluable: that fold configuration is
**`CV_NOT_EVALUABLE`**.

**Fallback, predeclared now (not chosen after seeing failure):** if 5-fold
`GroupKFold` is not fully evaluable, fall back to **`GroupKFold(n_splits=3)`**.
If 3-fold is also not evaluable, the **whole design is `INCONCLUSIVE`** —
fold counts are never tuned downward beyond this one predeclared fallback,
and never tuned upward to search for a lucky split.

**Secondary, feasibility-only, not primary:** true leave-one-individual-
site-out is **infeasible** (most of the ≈9 sites with any qualifying
occurrence fall far below any per-fold adequacy threshold). The only
honestly supportable leave-one-site-out check is the coarse HT-held-out
vs. OTHER-held-out split already implied by the `C_SITE` collapse (§12).

## 7. Primary metric

**Held-out binary log loss in bits** (`constraint_accumulation.log_loss_bits`):

    L_i = -[y_i * log2(p_i) + (1-y_i) * log2(1-p_i)]

Probabilities clipped to `[1e-15, 1-1e-15]` (`LOG_LOSS_EPS`) for numerical
stability only — never changes which class is favored.

    H_hat_k = mean held-out log loss across all out-of-fold predictions, model M_k

    ΔH_k = H_hat_{k-1} - H_hat_k     (constraint_accumulation.delta_h)

`ΔH_k > 0`: added block **improves** held-out prediction.
`ΔH_k = 0`: **no information** added.
`ΔH_k < 0`: added block **harms** held-out prediction.
(`constraint_accumulation.delta_h_label`, fixed labels.)
**No monotonicity is required or assumed.** Training loss is never reported
as evidence.

## 8. Null model — CONFLICT RESOLVED (this is the second, more important resolution)

`docs/CONSTRAINT_ACCUMULATION_NULLS.md` proposed a single null — *"within
each `(site, support)` stratum, permute Y"* — applied uniformly at every
step. **This is WRONG beyond the M1→M2 step, and is superseded here.**

**Why:** for testing whether block `C_k` (added in step `M_{k-1} → M_k`)
contributes information, the null must preserve exactly what `M_{k-1}`
already captures and destroy only `C_k`'s incremental relationship with Y.
A null conditioned only on `(site, support)` correctly does this for step
`M1→M2` (since `M1 = {site, support}`), but for step `M2→M3` it would
**also** destroy any real `C_POSITION`–Y relationship `M2` had already
captured — conflating `C_POSITION`'s and `C_COMMODITY`'s effects instead of
isolating `C_COMMODITY`'s incremental contribution. Likewise for `M3→M4`.

**Resolution — the frozen, generalized rule:** for step `k`, permute Y
**within strata defined by the full cross-product of every predictor
already included in `M_{k-1}`** (`constraint_accumulation.conditional_permutation_delta`,
parameterized by a `stratum_key_fn`):

| step | conditioning stratum (M_{k-1}'s own predictors) |
|---|---|
| M1→M2 (testing `C_POSITION`) | `(site_block, support_block)` |
| M2→M3 (testing `C_COMMODITY`) | `(site_block, support_block, position_bucket)` |
| M3→M4 (testing `C_NUMERIC`) | `(site_block, support_block, position_bucket, commodity_class)` |

**Preserves** (per step): total N, tablet-group structure (permutation is
within-stratum, not within-tablet — GroupKFold fold assignment is
unaffected by the permutation itself), every `M_{k-1}` predictor's
stratum-level Y-count composition. **Destroys**: the pairing between Y and
the newly-added block `C_k` specifically (not `M_{k-1}`'s own captured
structure).

**Strata with fewer than 2 rows** cannot be meaningfully permuted at all —
excluded from both the observed statistic and every null draw for that
step (`constraint_accumulation.permutable_strata`), retained only
descriptively — exactly the "excluded, retained descriptively" discipline
already established in `constraint_candidate1.exchangeable_strata`, reused
here rather than reinvented.

**B = 2000** for every step.

**Disclosed adequacy risk (not yet checked against real data this round):**
step `M3→M4`'s conditioning stratum has up to `2×2×3×2 = 24` cells against
N≈236 rows — average ≈10 rows/cell, but with known severe HT/Tablet
concentration, many cells will be far smaller or empty. This could leave
step M4's inferential test underpowered or partly non-evaluable at
several strata. This is flagged explicitly as a real risk in §21 (adversarial
audit), not smoothed over.

## 9. One-sided test, α, p-value formula

**One-sided**, `H_A: ΔH_k > (null expectation)`. Large negative `ΔH_k` is
**never** treated as support — it is simply recorded as harming prediction.

    p_k = (count(ΔH_k^perm >= ΔH_k^obs) + 1) / (B + 1)

(`constraint_accumulation.step_permutation_pvalue`, using
`constraint_accumulation.finite_permutation_pvalue`, identical formula to
`constraint_candidate1.finite_permutation_pvalue`.) **α = 0.05.**

**CORRECTED (Phase 1 micro-audit, this round): `p_k` is computed for
EVERY evaluable step, unconditionally on the sign of `ΔH_k^obs`.** An
earlier draft of this document special-cased `ΔH_k^obs ≤ 0` as "no
p-value computed, already fails" — that was wrong: it makes whether a
step's p-value (and hence whether it enters the Holm family, §10) exists
depend on the *observed effect's sign*, which is an outcome-dependent,
not a pre-data-independent, criterion for multiplicity-family membership.
A negative or zero `ΔH_k^obs` is not undefined or skipped — the formula
above is evaluated exactly as written, and naturally produces a large,
non-supportive `p_k` (since most permutation draws will then be `≥`
a very negative observed value) — it is simply evaluated, not omitted.

## 10. Multiple-testing correction

**Holm step-down correction**, applied across the family of steps that
count as accumulation evidence: **M2, M3, M4 only** (§16 — M1 is baseline
context, not evidentiary). **The Holm family consists of ALL EVALUABLE
incremental steps among {M1→M2, M2→M3, M3→M4} (§6, §11 evaluability —
CV-evaluable, adequacy-gate-passing, per-category-support-passing),
regardless of whether the corresponding `ΔH_k^obs` is positive, zero, or
negative.** `m` = however many of {M2, M3, M4} are **evaluable**; a step
is excluded from the family **only** if it is genuinely `NOT_EVALUABLE`
(CV/adequacy failure) — **never** because its observed effect was
non-positive. (`constraint_accumulation.holm_family`, wrapping
`constraint_accumulation.holm_correction`: standard step-down, sort
ascending, `adj_p_(i) = max(p_(i)·(m-i+1))` over `i' ≤ i`, monotone
nondecreasing, clipped to ≤1, applied to exactly the evaluable steps'
raw p-values.) **Adjusted p is used for inferential support
classification** (§16); raw p is also always reported alongside, for
every evaluable step, whatever its sign.

## 11. Adequacy gates

**Primary (`constraint_accumulation.primary_adequacy_gate`):**
total usable N ≥ **150**; unique tablets (CV groups) ≥ **50**; positive
(Y=1) count ≥ **30**; negative (Y=0) count ≥ **30**.

**CV evaluability:** 5 (fallback 3, §6) evaluable grouped folds, every
training fold containing both classes.

**Per-category minimums** (`constraint_accumulation.category_adequacy`):
- Binary blocks (`site_block`, `support_block`, `commodity_class`): each
  level ≥ **10 unique tablets**.
- `position_bucket` (3 levels) and `numeric_bin`/`numeric_bin_fold`
  (4 levels): each retained category ≥ **10 usable rows**.

**If a category fails its minimum: no post-hoc merge.** The corresponding
model step is declared **NOT EVALUABLE** for that category/step — reported
plainly, never silently combined with another category to rescue adequacy.

## 12. Site-generalization firewall

Per §6, true leave-one-site-out is infeasible. **No claim of cross-site
generalization will be made, regardless of result.** Primary conclusion
scope is: *within the available Haghia-Triada-dominated corpus, under
grouped-by-tablet validation.* Predeclared secondary descriptive checks:
**HT-only** and, only if adequacy permits, **OTHER-only** — neither is a
substitute for genuine cross-site replication.

## 13. Artifact-dependence sensitivity

**Predeclared sensitivity, not primary:** re-run the full pipeline grouping
CV by `constraint_candidate1.physical_artifact_key(tablet_id)` instead of
raw `tablet_id` (probable recto/verso/joined-fragment pairs sharing one
group). Tests whether physical-object dependence materially changes `ΔH_k`.
**Does not alter the primary result under any outcome.**

## 14. External semantic dependence (M3)

`M3` adds `C_COMMODITY` = LIQUID/DRY, labeled **EXTERNAL DOMAIN MODEL
INPUT** (§4). If `M3` produces positive, Holm-supported `ΔH_3`, the
result supports **conditional predictive usefulness of the imported
commodity grouping** — it does **not**, on its own, establish an
independently discovered Linear-A-internal semantic constraint. These two
claims are kept explicitly separate in any future result document.

## 15. Synergy firewall

Primary test is **ACCUMULATION**, not **SYNERGY**. `M3` outperforming `M2`
is accumulation evidence only — it is never, by itself, evidence of
synergistic/interaction information. An optional `C_POSITION × C_COMMODITY`
interaction-vs-additive comparison is **designed** (held-out log-loss,
same grouped CV) but **explicitly NOT RUN** in the first accumulation
experiment, per this round's own recommendation. If no interaction
analysis is ever run, no synergy claim of any kind is authorized.

## 16. Broad-program update rule

Using **Holm-adjusted** p-values, and counting only **M2, M3, M4** as
evidentiary (M1 is contextual baseline — informative or not, it does not
by itself count toward the deeper multi-constraint accumulation claim):

- **NO UPDATE** — experiment blocked / inadequate (adequacy gate or CV
  evaluability fails).
- **NEGATIVE UPDATE** — adequate experiment, but none of M2/M3/M4 shows a
  Holm-adjusted-significant positive `ΔH_k`.
- **WEAK POSITIVE UPDATE** — exactly one of M2/M3/M4 shows Holm-adjusted-
  significant positive `ΔH_k`.
- **MODERATE POSITIVE UPDATE** — at least two of M2/M3/M4 independently
  show Holm-adjusted-significant positive `ΔH_k`.
- **STRONG POSITIVE UPDATE** — **reserved for later replication; this
  single experiment cannot produce STRONG POSITIVE UPDATE**, regardless of
  outcome.

## 17. Falsification rule

If **M2, M3, and M4 all fail** to produce a Holm-adjusted-significant
positive `ΔH_k`, with adequate data and evaluable CV, the verdict is
**BROAD CONSTRAINT PROGRAM: NEGATIVE UPDATE** for this tested domain.
Consistent-but-nonsignificant positive `ΔH_k` direction may be described
**descriptively**, exactly as Candidate 1's sensitivity directions were
handled, but never substituted for the frozen inferential verdict.

## 18. Anti-circularity declaration

1. **Is Y defined without using predictor values?** Yes — `fraction_present`
   reads only the numeral token's own field.
2. **Is model order fixed before performance?** Yes — §4's order was fixed
   on a stated context→structure→content→magnitude rationale, before any
   real-data model was fit.
3. **Are feature categories fixed before performance?** Yes — all five
   blocks use closed, predeclared category sets (§4, §5); `C_NUMERIC`'s
   cutoffs are fold-fit from X's marginal distribution only, never from Y
   (§4a).
4. **Is `C_COMMODITY` reused unchanged from Candidate 1?** Yes (§4).
5. **Are numeric bins independent of Y?** Yes — fold-fit from the training
   fold's own numeral-magnitude values only, never crossed with Y (§4a).
6. **Are CV groups independent of performance?** Yes — grouped by
   `tablet_id`, fixed before any model is fit, unaffected by outcome.
7. **Is the null fixed before ΔH is observed?** Yes — the corrected,
   per-step conditional-permutation null (§8) is fully specified in this
   document before any real `ΔH` exists.
8. **Are all model steps retained even if they perform poorly?** Yes — a
   negative or zero `ΔH_k` is recorded plainly (§7, §17), never grounds to
   drop, reorder, or hide a step.
9. **Can the protocol generate a negative program update?** Yes,
   explicitly (§17) — this is the plausible, expected-to-be-possible
   outcome the design is built to detect, not a corner case.
10. **Are semantic claims separated from raw structural claims?** Yes
    (§14).

All ten: **YES.**

## 19. Explicit statement: no real model performance was inspected before freeze

No `ΔH_k`, held-out log-loss, permutation p-value, Holm-adjusted p-value,
or accumulation verdict has been computed against
`data/generated/lineara_extracted.json` anywhere in this repository. Every
function in `src/constraint_accumulation.py` is exercised exclusively by
hand-built synthetic fixtures in `tests/test_constraint_accumulation.py`
(66 new tests this round, 220 total passing — see the round's Final
Report). The only real-data-adjacent figures referenced anywhere in this
document (N≈236, 133 tablets, 38 positives, site/support concentration
percentages) are figures **already disclosed** in the committed
`results/CANDIDATE1_RESULT.md` (commit `3a68afb650895552eda65ac5f69d16816140bfd3`)
or from marginal, Y-blind schema/cardinality checks performed in the prior
design round (`docs/CONSTRAINT_ACCUMULATION_CANDIDATES.md`) — nothing new
about any Y-vs-predictor relationship is computed or revealed here.

## 20. Adversarial freeze audit

1. **Are numeric bins genuinely frozen?** The *rule* is frozen (§4a,
   training-fold tertile fitting); the specific numeric cutoff *values*
   are deliberately **not** frozen as constants — they will vary per fold
   by design (that is the whole point of fold-only fitting). This is a
   frozen procedure, not frozen numbers, and that distinction is
   intentional.
2. **Does M4 have enough data to be meaningful?** Uncertain — flagged as a
   real, disclosed risk (§8's adequacy-risk note): M4's conditional null
   uses up to 24 strata against N≈236, likely leaving several strata too
   small to permute meaningfully. Per-category adequacy (§11) will need to
   be checked at execution time; M4 may turn out `NOT EVALUABLE`, which
   this protocol treats as a valid, informative outcome, not a design
   failure.
3. **Does site/support dominate so strongly that later blocks are nearly
   redundant proxies?** A real, disclosed risk (§8 conditioning, this
   design's own adversarial notes in `docs/CONSTRAINT_ACCUMULATION_NULLS.md`
   item 4/10) — the design cannot rule this out in advance; it is exactly
   what the conditional-null structure is built to help distinguish
   (accumulation vs. redundant-proxy stacking), not something assumed away.
4. **Is within-(site,support) Y permutation a valid conditional null for
   every step?** **No** — this was the flaw found and corrected in §8. The
   canonical rule now conditions on the full `M_{k-1}` predictor set per
   step, not a fixed (site,support) stratification for every step.
5. **Does GroupKFold create unstable prevalence across folds?** Plausible,
   given known HT/Tablet concentration and a modest positive count (38);
   not yet checked against real data this round — a real risk to monitor
   at execution time, not resolved by this design alone.
6. **Is 38 positives enough for M4?** Borderline — clears the primary
   adequacy gate (§11, ≥30) but is thin once split across 5 CV folds
   (≈7–8 positives/fold) and further thinned by M4's stratified null
   (item 2 above); disclosed as a real limitation, not hidden.
7. **Could M3 simply reproduce Candidate 1 in conditional form without
   adding a genuinely distinct constraint?** This is exactly why M3's
   contribution is measured *conditionally* (after M1, M2 already fit) via
   held-out `ΔH_3`, not as a repeat of Candidate 1's marginal permutation
   test — a positive `ΔH_3` would mean commodity adds information *beyond*
   site/support/position, which Candidate 1 never tested and did not find
   (Candidate 1 tested and found no *marginal* commodity effect at all,
   `results/CANDIDATE1_RESULT.md` — a conditional finding here would be a
   genuinely new result, not a repeat, though a *null* `ΔH_3` result here
   would be broadly consistent with Candidate 1's own finding).
8. **Is the external LIQUID/DRY mapping too circular to count as program
   evidence?** Not circular in the strict sense (§4, §14) — but per
   Candidate 1's own disclosed **PARTIAL EVIDENTIAL DEPENDENCE**, a
   positive `ΔH_3` should not be read as fully independent confirmation of
   the broader constraint-intersection hypothesis on its own, exactly as
   already stated for Candidate 1.
9. **Does multiple testing make the positive-evidence standard
   appropriately hard?** Yes — Holm correction across up to 3 tests (§10)
   is a genuinely conservative, standard family-wise error control, not a
   token gesture.
10. **Can a clean null result genuinely yield NEGATIVE UPDATE?** Yes,
    explicitly (§17) — this is the plausible, well-specified, and (given
    Candidate 1's own null commodity finding) not-unlikely outcome this
    design is built to detect and report honestly.

**No unresolved-and-unaddressed major issue remains: item 4 (the most
serious) has been corrected in §8; items 2/3/5/6 are disclosed, real,
but not resolvable further without running the actual analysis (which
this round does not do) — they are risks to interpret carefully at
execution time, not blockers to freezing the protocol itself.**
