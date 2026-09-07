# Constraint accumulation V2: integer-conditional accumulation — DESIGN ONLY

**Status: DESIGN ONLY. No V2 cross-validation, log loss, ΔH, permutation
p-value, Holm-adjusted p-value, or verdict has been computed against real
data.** V2 is a **new, prospectively-defined estimand** — not a rerun,
correction, or "V1 with bad rows removed." V1's result and verdict
(`results/CONSTRAINT_ACCUMULATION_RESULT.md`, WEAK POSITIVE UPDATE) is
unchanged and unchangeable by anything in this document.

**ERRATUM (added by `docs/CONSTRAINT_ACCUMULATION_V2_BLOCKER_AUDIT.md`
Phase 10, a factual naming correction, not a redesign):** `C_MAGNITUDE`
should be read throughout this document as **WHOLE-COMPONENT MAGNITUDE**,
not general "numerical magnitude" or "total quantity." `log2(1 +
integer_value)` measures only the resolvable whole-number part of a
numeral expression — for an integer+fraction expression (e.g. "3 ½") it
evaluates to `log2(4)`, not `log2(4.5)`. This does not change any
predictor definition, model, or plan below — only its name and the
claims it is entitled to support.

## Two questions V1 conflated (Phase 4)

- **Question A:** Does the presence/absence of an integer component
  predict fraction-sign presence?
- **Question B:** Conditional on a genuine integer component existing,
  does its *magnitude* predict fraction-sign presence?

V1's `C_NUMERIC` (`SMALL`/`MEDIUM`/`LARGE`/`NO_INTEGER_VALUE`) answered a
blend of both, dominated by Question A's degenerate, tautological
sub-case (`results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md` §4–5,
§11). **Question A, as literally phrased ("does no-integer predict
fraction-presence"), is not a genuine empirical question at all in this
representation — it is a proven tautology** (§5 of the validity audit).
It is **not**, however, scientifically meaningless in a different framing:
"does a quantity's sub-unit-vs-whole-unit-or-more notational form
correlate with *other* structural features (site, position, commodity)"
is a coherent, open, un-tested question — tentatively named
**`INTEGER_COMPONENT_STRUCTURE`**, recorded here as a candidate for a
**future, separately designed and frozen hypothesis**, using a target
other than `FRACTION_SIGN_PRESENCE`. **Not tested in this round.**

V2 is designed to cleanly isolate **Question B only**.

## Estimand (Phase 5)

**Prospectively defined new estimand, not a correction of V1:**

> Among qualifying commodity-associated numerical observations for which
> an integer component is independently resolvable, do structural
> predictors (context, position, commodity, and integer magnitude)
> provide incremental held-out information about fraction-sign presence?

Working names: **CONSTRAINT ACCUMULATION V2**, or
**INTEGER-CONDITIONAL ACCUMULATION**. V1 is not overwritten; both results
stand side by side, addressing different populations and different
(though related) questions.

## V2 population and inclusion-rule independence audit (Phase 6)

**Candidate inclusion rule:** a row belongs to the V2 population iff its
associated numeral token's `.value` is resolved (not `None`) — i.e.,
`numeric_value is not None`, exactly the complement of V1's
`NO_INTEGER_VALUE` category.

Adversarial audit, per Phase 6's six questions:

1. **Can "integer component resolvable" be determined independently of
   `FRACTION_SIGN_PRESENCE`?** Yes — `.value is not None` is read directly
   from the numeral token's own `.value` field; checking it never requires
   reading `.fractions` (`results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md`
   §2, §9).
2. **Does the adapter expose integer-value existence before constructing
   Y?** Both fields are set on the same token at construction time in
   `lineara_adapter.py`; there is no temporal "before" in a strict sense,
   but the two fields (`.value`, `.fractions`) are structurally
   independent reads of that token — inspecting one does not require
   inspecting the other.
3. **Could fraction parsing affect whether integer existence is
   recognized?** No — `.value` is only ever set in the plain-integer
   branch (`is_numeral_string`), which runs independently of whether a
   fraction glyph later merges into that same token.
4. **Does selecting integer-resolvable rows condition on a descendant of
   Y?** Mechanically, no (the inclusion check reads `.value`, never
   `.fractions`). Causally, a residual concern remains and is **not fully
   dismissed**: per the validity audit §5, a row lacks an integer
   component *because* its true quantity is < 1 whole unit — i.e., the
   *reason* a row is excluded is itself a fact about magnitude (the low
   extreme of it). This is not "conditioning on Y" in the mechanical
   sense, but it does mean the excluded subset is not a random slice of
   the full magnitude range — it is precisely the smallest-magnitude
   subset. **Disclosed as a genuine, unresolved limitation, not treated as
   dismissed** (see "Remaining limitation" below).
5. **Does the selection induce collider bias?** Classic collider bias
   would require conditioning on a common effect of two variables under
   study. Here, restricting to "has-integer-value" conditions on a fact
   (true magnitude ≥ 1) that is arguably a *cause*, not a common *effect*,
   of both the retained magnitude signal and (indirectly, via the
   sub-unit case) fraction presence — this is closer to ordinary
   **left-truncation of the magnitude scale** than to textbook collider
   bias. Not proven risk-free, but not the specific collider-bias pattern
   either. Flagged **OPEN / not fully resolved without deeper domain
   input**, not silently assumed away.
6. **Does this population correspond to a coherent structural question?**
   Yes — "among quantities of at least one whole unit, does that whole-
   unit magnitude predict whether a sub-unit fraction is *also* recorded"
   is a well-defined, non-circular, meaningful question distinct from
   Question A.

**Conclusion: NOT BLOCKED.** The inclusion rule is mechanically
Y-independent (items 1–3), and the residual truncation-style concern
(items 4–5) is disclosed as an open limitation rather than resolved by
assumption — per this round's own instruction, this is reported, not
hidden, and does not by itself meet the bar for `V2 DESIGN BLOCKED`
(reserved for a case where independence *cannot* be established at all,
which is not the case here — it *can* be established for the inclusion
rule itself; only a secondary, harder causal question remains open).

**Remaining limitation (carried into the design, not resolved here):**
V2's population is implicitly restricted to quantities ≥ 1 whole unit.
Any V2 finding is scoped to that restricted population and must not be
described as covering "all fraction-bearing quantities" — the excluded
sub-unit population is a real, disclosed, separate part of the corpus,
covered instead by the future `INTEGER_COMPONENT_STRUCTURE` candidate,
not by V2.

## Predictor architecture (Phase 7)

| model | adds |
|---|---|
| M0 | intercept only |
| M1 | `C_SITE` + `C_SUPPORT` |
| M2 | M1 + `C_POSITION` |
| M3 | M2 + `C_COMMODITY` |
| M4 | M3 + `C_MAGNITUDE` |

Identical nesting rationale to V1 (context → structure → content →
magnitude), reused because nothing about the V1 construction-dependence
finding implicates this ordering — only `C_NUMERIC`'s *content* was
compromised, not the sequence's logic.

**`C_MAGNITUDE` contains only `{SMALL, MEDIUM, LARGE}` in the categorical
alternative, or a single continuous value in the recommended primary
representation (below) — `NO_INTEGER_VALUE` is not a permitted level of
`C_MAGNITUDE` in V2 under any representation**, by the population
restriction itself (§ population, above).

## Magnitude representation (Phase 8)

Four representations were structurally compared, **none tested against
real Y**:

| option | structural advantages | structural disadvantages |
|---|---|---|
| A. fold-derived tertiles (V1's approach, restricted to non-null values) | familiar, matches V1's categorical framing | requires per-fold cutoff-fitting (an extra moving part); arbitrary category-count choice (why 3, not 2 or 4); equal-count bins may not reflect equal magnitude gaps on a right-skewed count distribution |
| B. fixed domain-motivated thresholds | no fitting step; interpretable in absolute units | no defensible external ("domain-motivated") threshold is available in this project's own scholarship audit (`docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md`) — would itself be an invented, unjustified choice |
| C. log-scale bins | reduces skew sensitivity vs. A | still requires arbitrary bin-count/edge choices; same fitting-step complexity as A |
| **D. continuous `log2(1 + integer_value)`** | **no cutoffs to fit at all — eliminates the entire fold-derived-fitting mechanism V1 needed, and the leakage-control complexity that came with it; standard, off-the-shelf, non-arbitrary transform for multiplicatively-distributed count/quantity data; single coefficient, maximally interpretable as a magnitude effect; mathematically coherent since all observed values are positive integers (range 1–976, confirmed in `docs/CONSTRAINT_ACCUMULATION_CANDIDATES.md`'s own marginal, Y-blind quantile check), so `log2(1+x)` is always defined and monotonic** | imposes a linear effect in log-space in the logistic-regression model — could miss a genuinely non-monotonic or threshold relationship |

**Recommendation: Option D, continuous `C_MAGNITUDE = log2(1 +
integer_value)`, as the PRIMARY V2 representation.** This choice is
justified structurally — by the reduction in fitting complexity (no
per-fold cutoffs at all, sidestepping an entire class of potential
leakage/arbitrary-choice concerns that V1's category-fitting required),
by log-transforms being the standard, non-dataset-specific treatment for
right-skewed positive quantity data, and by interpretability — **not**
because any representation was tried against real `Y` (none was; per this
round's own firewall, real inference was not run). Option A (fold-derived
tertiles, non-null values only) is retained as a **predeclared
SENSITIVITY**, not primary, to check whether the primary continuous
finding (if V2 is ever run) is robust to a categorical alternative.

## Reconsidering M3 / commodity (Phase 10)

Commodity has now failed twice under related but distinct designs
(Candidate 1's marginal test, `results/CANDIDATE1_RESULT.md`; V1's
conditional test, `results/CONSTRAINT_ACCUMULATION_RESULT.md`). **M3 is
retained in V2**, for reasons that do not depend on hoping it will
"work this time":

- it remains the strongest pre-existing, theory-motivated candidate from
  `docs/CONSTRAINT_HYPOTHESIS_CANDIDATES.md`'s own ranked shortlist — its
  status as a theoretically motivated block does not change because two
  related tests found no support;
- V2's population differs from both prior tests (restricted to
  integer-resolvable rows only), so retaining M3 lets a reader compare its
  behavior across three related-but-distinct designs, which is itself
  informative;
- it functions as a **predeclared negative/control block**: a method that
  cannot recover the KU-RO-adjacent commodity signal three times running,
  under three different reasonable designs, is itself a disclosable,
  informative pattern — dropping it would remove that signal from view;
- **retaining it prevents exactly the kind of selective predictor-dropping
  this round's own firewall prohibits** ("do not decide based on improving
  V2 performance").

No claim is made that M3 is likely to succeed in V2; it is retained on
principle, not on optimism.

## Context baseline M1 (Phase 11)

V1 found `ΔH1 = -0.021844`: site/support did not improve held-out
prediction over the intercept. **M1 is retained unchanged in V2**, for the
same principled reason as M3's retention — V2 must not selectively keep
only predictors that looked favorable in V1. M1 remains contextual
baseline only and does not count toward V2's accumulation-evidence grade
(§"Verdict architecture" below), exactly as in V1.

## Null model re-audit (Phase 12)

1. **Is exact cross-product conditional permutation still valid?** Yes,
   unchanged in mechanism — the null for step `k` conditions on
   `M_{k-1}`'s own (categorical) predictors, exactly as in V1
   (`docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md` §8). Nothing about V2
   changes M1/M2/M3's predictor types (still `{site_block, support_block}`,
   `{..., position_bucket}`, `{..., commodity_class}` — all categorical),
   so the M1→M2 and M2→M3 conditional strata are structurally identical in
   form to V1's.
2. **Does continuous magnitude make such conditioning easier or harder?**
   Neither, directly — the M3→M4 step's null still conditions on
   `(site_block, support_block, position_bucket, commodity_class)`
   (`M3`'s own predictors), which are unchanged categorical fields; the
   fact that the *new* block (`C_MAGNITUDE`) is continuous doesn't change
   what the null conditions ON, only what the held-out model being tested
   contains.
3. **Are enough exchangeable observations available?** Population is
   smaller than V1's (§"Adequacy" below: N=219 vs. 236) — the same
   `permutable_strata` (≥2 rows) mechanism from `constraint_accumulation.py`
   applies unchanged and would need to be checked at execution time, not
   assumed now.
4. **Is there a better predeclared conditional-randomization
   construction?** No better construction was identified; the existing
   one remains the most defensible predeclared choice, reused rather than
   reinvented (per this round's own preference for validity over power).
5. **Would grouped permutation at tablet level be required?** No change
   from V1: the permutation operates on rows already restricted to
   membership in exchangeable `(site,support,position,commodity)` strata;
   grouping by tablet is handled separately, at the CV-fold level (§"Group
   dependence" below), not by the permutation itself.
6. **Does permuting row-level Y within strata preserve within-tablet
   dependence adequately?** Unchanged from V1's own design — this was not
   re-litigated or re-justified beyond what V1's protocol already
   established; carried forward unchanged.

**Conclusion: V2 NULL MODEL — VALID, UNCHANGED IN MECHANISM.** No
redesign was needed or attempted; the existing conditional-permutation
construction transfers directly to the V2 population and predictor set.

## Group dependence (Phase 13)

**PRIMARY: `GroupKFold` by `tablet_id`**, unchanged from V1.
**SENSITIVITY (already predeclared, not primary, still not implemented in
either the V1 or V2 harness):** grouping by `constraint_candidate1.
physical_artifact_key(tablet_id)` instead, using only the already-
documented base-ID + trailing-face-letter heuristic
(`docs/EVIDENCE_DEPENDENCE_PROTOCOL.md`) — no new artifact mapping is
invented. Physical-artifact grouping is **not** proposed as V2's primary
unit: tablet-level grouping remains the cleanest, most directly
interpretable primary choice, consistent with V1 and with this round's
own instruction not to construct favorable groupings post hoc.

## Adequacy — Y-independent design information, plus disclosed post-V1 counts (Phase 14)

**Y-independent (computable without inspecting any `fraction_present`
value):**

| | value |
|---|---|
| Candidate V2 rows (`numeric_value` resolved) | **219** |
| Unique tablets | **89** |
| Site counts | Haghia Triada 157, OTHER 62 |
| Support counts | Tablet 214, OTHER 5 |
| Position counts | FIRST 87, SECOND 41, THIRD_OR_LATER 91 |
| Commodity counts | LIQUID 114, DRY 105 |

**POST-V1 DESIGN INFORMATION (Y-informed — disclosed explicitly, per this
round's own labeling requirement; NOT used to tune any V2 design choice
above):**

| | value |
|---|---|
| Positives (Y=1) | **21** |
| Negatives (Y=0) | **198** |
| LIQUID tablets | 49 |
| DRY tablets | 61 |

**Adequacy is NOT presently established.** Reusing V1's own frozen
minimums (`min_positive=30`) verbatim, V2's candidate population has only
**21** positives — **below** that threshold. This is disclosed plainly,
not minimized: **as currently scoped, V2 would very likely return
INCONCLUSIVE if V1's ≥30-positive gate were reused unmodified.** This
round does **not** lower that threshold to make V2 viable — doing so
immediately after learning it would fail is exactly the kind of post-hoc
rescue this project's discipline prohibits. Any future round that wishes
to proceed must either (a) explicitly, transparently re-derive and justify
a different adequacy minimum appropriate to this smaller, more specific
population **before** running V2, argued on grounds independent of this
count, or (b) accept that V2, run as designed, is likely to terminate at
`INCONCLUSIVE`. **This document does not decide between (a) and (b)** —
that is left open for the user.

## Verdict architecture (Phase 15)

V1's WEAK/MODERATE terminology is **not reused automatically**. Proposed
V2-specific criteria (not frozen — a candidate for a future canonicalization
round):

- **NEGATIVE UPDATE:** adequate V2 and no structural block beyond
  contextual baseline (M1) contributes Holm-significant positive held-out
  information.
- **LIMITED POSITIVE:** exactly one clean, non-construction-dependent
  block contributes significant incremental information.
- **ACCUMULATION EVIDENCE:** at least two sequential, independently
  constructed structural blocks contribute significant incremental
  information.

**A positive `C_MAGNITUDE` (M4) block alone would support only:**
*"integer magnitude contains conditional predictive information about
fraction-sign presence, among quantities ≥ 1 whole unit"* — **it would
NOT, by itself, support "general constraint accumulation."** The word
"accumulation" is reserved for **at least two** independent information
sources contributing, per this round's own explicit instruction (Phase
15). This is a deliberately **stricter** bar than V1's own WEAK POSITIVE
UPDATE label implied for a single significant block — a disclosed,
intentional tightening for V2, motivated directly by the V1 lesson that a
single significant block can be a construction artifact rather than
genuine accumulated structure.

## Information-type classification (Phase 16)

| predictor | information type |
|---|---|
| `C_SITE` | INDEPENDENT STRUCTURAL INFORMATION |
| `C_SUPPORT` | INDEPENDENT STRUCTURAL INFORMATION |
| `C_POSITION` | DERIVED STRUCTURAL INFORMATION |
| `C_COMMODITY` | EXTERNAL MODEL INFORMATION |
| `NO_INTEGER_VALUE` (V1, not used in V2) | CONSTRUCTION INFORMATION |
| `C_MAGNITUDE` (V2) | POTENTIALLY INDEPENDENT NUMERICAL INFORMATION — pending the population-level caveat (§"V2 population" item 4–5) |

Fully elaborated, with the general operational lesson, in
`docs/CONSTRAINT_INFORMATION_TYPES.md`.
