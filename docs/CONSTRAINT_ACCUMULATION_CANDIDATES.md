# Constraint-accumulation: feature audit, target ranking, candidate designs

**Status: DESIGN ONLY. No predictive performance, cross-validated score,
entropy-reduction estimate, model comparison, p-value, or accumulation
verdict has been computed anywhere in this document or its companions**
(`docs/CONSTRAINT_ACCUMULATION_DESIGN.md`, `docs/CONSTRAINT_ACCUMULATION_NULLS.md`).
Every count below is either a **marginal** schema/cardinality count (not
crossed with the candidate target `Y`) or a figure **already disclosed** in
the committed `results/CANDIDATE1_RESULT.md` (commit `3a68afb650895552eda65ac5f69d16816140bfd3`)
— nothing new about any `Y`-vs-predictor relationship is revealed here.

This round tests a scientifically different question from Candidate 1:
**constraint accumulation** (does sequentially adding independently defined
structural information reduce held-out uncertainty about a target?), not
**single-constraint association** (does one feature correlate with one
target?). Candidate 1's own frozen commodity-class definition may be
*reused* as one predictor block among several — this is not "rebuilding
Candidate 1," because the question asked of it is different (conditional
contribution after other blocks are already accounted for, via held-out
prediction, not a marginal permutation test).

## Phase 4 — feature-family audit

| family | status | basis |
|---|---|---|
| **C_SITE** | **AVAILABLE** | raw `site` field; 53 distinct values corpus-wide, but only ~9 co-occur with a qualifying LIQUID/DRY commodity occurrence (per `docs/CONSTRAINT_SPACE_DATA_AUDIT.md`/`results/CANDIDATE1_RESULT.md` site distribution) — see feasibility note below on collapsing |
| **C_SUPPORT** | **AVAILABLE** | raw `support` field; 19 distinct values corpus-wide, only 3 (`Tablet`, `Clay vessel`, `Roundel`) observed among usable commodity-bearing rows in the Candidate 1 run — heavily skewed toward `Tablet` |
| **C_POSITION** | **DERIVABLE** | ordinal rank (1st / 2nd / 3rd-or-later) of a qualifying occurrence among same-record qualifying occurrences, in token order — a direct generalization of the token-order concept already frozen in `constraint_candidate1.py` (not a new heuristic) |
| **C_COMMODITY** | **AVAILABLE (identity)** / **EXTERNAL DOMAIN MODEL INPUT (LIQUID/DRY class)** | reuses `constraint_candidate1.commodity_class` **unchanged** — see scope note below; not broadened to the full raw ideogram inventory |
| **C_NUMERIC** | **AVAILABLE (identity)**, **DERIVABLE (bin)** | the associated numeral token's whole-number `.value`; binned into predeclared, marginal-quantile-based buckets (below) |
| **C_FRACTION** | excluded as a predictor in this design (it is the recommended target `Y`, see Phase 5) | — |
| **C_LOCAL_ORDER** | **DERIVABLE**, but **not used as a separate block** | overlaps substantially with C_POSITION as defined here; kept as one block to avoid two near-collinear position-like predictors |
| **C_DOC** | **AVAILABLE**, but **not used this round** | the raw `context` field (12 distinct chronological-period codes, e.g. `LMIB`, `MMIIIA`) is available and independent of fraction behavior, but adding a 5th block was judged to over-extend model complexity relative to sample size (Phase 12 firewall) — deferred to a future round, not silently dropped |
| **C_REPEAT** | **OPEN** | repeated-sign/repeated-quantity/template detection was already flagged OPEN, not measured, in `docs/CONSTRAINT_SPACE_DATA_AUDIT.md` §D — not usable reliably this round |

**Scope note on C_COMMODITY (important, disclosed up front):** this design
does **not** broaden commodity-occurrence detection beyond Candidate 1's
frozen four families (`VIN`, `OLE*`, `GRA*`, `OLIV`). A marginal schema
check this round found **508 distinct base signs** appear as
single-element signgroups followed by a resolvable quantity somewhere in
the full corpus (1323 such occurrences total) — but manual inspection
(consistent with the same finding already made in
`docs/CONSTRAINT_SPACE_DATA_AUDIT.md` §C) shows the overwhelming majority
of these are short syllabic transliterations (personal/place names, verbs)
incidentally followed by a number, not genuine commodity ideograms. Defining
a broader, defensible "known commodity" allowlist beyond the four already-
vetted families would require domain expertise this project does not have
and cannot invent ad hoc under this round's own firewall against
post-hoc-tuned categories — so it is left **DOMAIN-EXPERT DEPENDENT / OPEN**,
and C_COMMODITY reuses exactly the existing frozen LIQUID/DRY scope, with
non-LIQUID/DRY commodities remaining **OUT OF SCOPE** (excluded from this
test's universe, exactly as in Candidate 1 — not a new decision).

**Feasibility collapses (predeclared now, not tuned after results):**
Given known severe concentration (Haghia Triada ≈ 70–80% of Candidate 1's
usable rows; `Tablet` support ≈ 96% of the same), one-hot-encoding the full
site/support cardinality against a few-hundred-row sample risks
near-empty cells and unstable estimates (Phase 20 Q8). C_SITE is therefore
collapsed to **{Haghia Triada, OTHER}** and C_SUPPORT to **{Tablet, OTHER}**
— coarser than the raw field, but a defensible, predeclared choice that
keeps the model simple (Phase 12 firewall) rather than a post-hoc fix.

**C_NUMERIC bin edges (predeclared from a marginal, Y-blind quantile check
this round):** among the 219 (of 236) qualifying occurrences with a
resolvable whole-number value, tertile cut-points were **3** and
**≈15.7** (marginal distribution only — not crossed with fraction
presence). Frozen bins: **SMALL** (value ≤ 3), **MEDIUM** (4–15),
**LARGE** (≥16), plus an explicit **NO_INTEGER_VALUE** category for the 17
occurrences whose numeral token carries a fraction only, no integer part
(not silently merged into any numeric bin).

## Phase 5 — held-out target ranking

| rank | candidate | for | against |
|---|---|---|---|
| **1 — recommended** | **A. fraction-sign presence** | already precisely operationalized (`constraint_candidate1.fraction_present`); genuinely open (Candidate 1 found no marginal association, so a *conditional* test is a new question, not rediscovery); reasonably balanced marginal prevalence (38/236 ≈ 16.1%, already disclosed in `results/CANDIDATE1_RESULT.md` Sensitivity A); every predictor block is structurally independent of how `Y` itself is defined | commodity identity (one candidate predictor block) already failed as a *marginal* predictor of this exact `Y` — must be framed carefully as a *conditional*, not repeat, test (done, see design doc) |
| 2 | D. numerical-magnitude bin | genuinely available, DERIVABLE; interesting complementary question (does structural/contextual information predict quantity size); bin edges can be predeclared from a marginal quantile check, as done above | bin edges are inherently somewhat arbitrary (tertiles is a convention, not a natural law); 3-level ordinal target is less central to this project's own motivating fraction/metrology question than (A) |
| 3 | B. commodity-family identity (LIQUID/DRY) | available in principle as a target too | rejected for this role: the class assignment is **itself** EXTERNAL DOMAIN MODEL INPUT (§ Phase 2 audit, `docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md` item 8) — using it as the *target* to be predicted from raw structural features would test something close to "can raw structure recover an externally-imposed label," a different and less interesting question than testing whether structure predicts a directly-observed corpus property |

**Rejected outright, with reasons:** C (support/document type) — near-
degenerate base rate (`Tablet` ≈ 96% of usable rows), too little uncertainty
to reduce, uninteresting null by construction. E (local positional class)
and F (quantity-after-signgroup presence) — both are themselves *position-
derived* properties, and this design's own C_POSITION predictor block would
then partially define the target it is supposedd to help predict — a real,
avoidable circularity risk (Phase 20 Q1) that (A) does not share, since
`fraction_present` reads only the numeral token's own field, never
positional information.

**Recommended target: Y = fraction-sign presence** (identical definition to
`constraint_candidate1.fraction_present` — reused unchanged, not
redefined).

## Phase 14 — three candidate designs

### Design 1 (recommended) — sequential context→structure→content→magnitude

1. **Target Y:** fraction-sign presence (as above).
2. **Predictor families, in order:** {C_SITE, C_SUPPORT} → C_POSITION →
   C_COMMODITY → C_NUMERIC.
3. **Nesting:** M0 (intercept) → M1 (+site/support) → M2 (+position) → M3
   (+commodity) → M4 (+numeric bin).
4. **Primary metric:** held-out cross-validated log-loss (bits), ΔH_k =
   logloss(M_{k-1}) − logloss(M_k).
5. **Grouped CV:** `GroupKFold(n_splits=5)`, grouped by `tablet_id`.
6. **Null model:** within-site×support-stratum permutation of `Y` (NULL 3
   reused), applied per added block, B=2000 (see
   `docs/CONSTRAINT_ACCUMULATION_NULLS.md`).
7. **Adequacy gate:** total usable N ≥ 150; unique tablets (CV groups) ≥
   50; minority-class (`FRACTION_PRESENT`) count ≥ 30. (Marginal counts
   already disclosed put this design at N=236, 133 tablets, 38 positives —
   comfortably above gate, without this round re-running that computation.)
8. **Circularity risks:** C_COMMODITY reuses an externally imported
   semantic label (disclosed, unchanged from Candidate 1's own audit);
   otherwise low.
9. **Dependence risks:** same-tablet occurrences (mean ≈1.8/tablet in this
   universe) — addressed by grouped CV, not tablet-level dedup (a
   deliberate, disclosed methodological difference from Candidate 1's own
   approach, justified by the shift from a permutation-test framing to a
   predictive-accumulation framing).
10. **Site risks:** severe HT concentration; C_SITE collapsed to
    HT-vs-OTHER; true leave-one-site-out across ~9 individual sites is
    infeasible (most have far below the adequacy threshold individually).
11. **External-domain inputs:** C_COMMODITY's LIQUID/DRY label only.
12. **Interpretability:** high — plain logistic regression, ≤4 low-
    cardinality blocks.
13. **Expected sample size:** N≈236 occurrences, 133 tablets, 38 positive
    (already-disclosed marginal figures).
14. **Falsifies accumulation if:** M2/M3/M4 fail to reduce held-out
    log-loss beyond null permutation variation at any step.
15. **Positive evidence if:** at least one of M2/M3/M4 shows a held-out
    log-loss reduction exceeding its predeclared permutation null,
    reproducibly across folds.

### Design 2 — numeral-magnitude as target (alternative, not recommended)

1. **Target Y:** numerical-magnitude bin (SMALL/MEDIUM/LARGE, dropping the
   NO_INTEGER_VALUE category from the target definition itself — those rows
   excluded from this design's universe, not this design's C_NUMERIC-as-
   predictor case).
2. **Predictors:** {C_SITE, C_SUPPORT} → C_POSITION → C_COMMODITY →
   C_FRACTION (fraction-presence now used as a *predictor*, flipping
   Design 1's target/predictor roles).
3–15. Structurally parallel to Design 1, substituting the target/predictor
   roles. **Not recommended** as the primary design because a 3-level
   ordinal target is a slightly weaker, less central fit to this project's
   own motivating question (fraction/metrology structure) than binary
   fraction-presence, and because C_FRACTION-as-predictor reintroduces
   exactly the marginal relationship Candidate 1 already tested, making the
   "conditional, not repeat" framing slightly muddier than Design 1's.

### Design 3 — commodity identity as target (alternative, not recommended)

1. **Target Y:** commodity class (LIQUID vs. DRY), among occurrences already
   restricted to those two families (i.e., "which of the two known classes
   is this," not "is this commodity-bearing at all").
2. **Predictors:** {C_SITE, C_SUPPORT} → C_POSITION → C_NUMERIC →
   C_FRACTION.
3–15. Structurally parallel. **Not recommended:** the target itself is
   externally imposed (EXTERNAL DOMAIN MODEL INPUT), so "raw structure
   predicts an externally-imposed label" is a different, less scientifically
   central question than "raw structure predicts a directly observed
   corpus property" (Design 1). Also carries the same circularity
   flag as Phase 5's rejection of candidate target B, now made a full
   design rather than just a ranked-and-rejected option.

**Ranking: Design 1 > Design 2 > Design 3.** Design 1 is recommended.
