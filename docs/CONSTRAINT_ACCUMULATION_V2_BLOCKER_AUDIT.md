# Constraint accumulation V2: blocker-resolution audit

**Status: DESIGN AUDIT ONLY.** No V2 model has been fit against real
predictor–outcome relationships. No V2 ΔH, permutation p-value,
Holm-adjusted p-value, or verdict exists anywhere in this repository. This
document either resolves or explicitly leaves open the two blockers from
the prior round (`docs/CONSTRAINT_ACCUMULATION_V2_DESIGN.md`): **(1)
adequacy** and **(2) population-selection independence**. V1's result and
verdict (`results/CONSTRAINT_ACCUMULATION_RESULT.md`, WEAK POSITIVE
UPDATE) is untouched.

## Phase 1 — origin of the ≥30 positive/negative gate

Traced directly: `docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md` §11 states the
numbers (`N≥150, tablets≥50, positive≥30, negative≥30`) with **no
derivation, no citation, no formula**. The earliest occurrence in this
project's own history is `docs/CONSTRAINT_ACCUMULATION_CANDIDATES.md`
§"Phase 12 recommendation" (the round that first proposed accumulation
testing), which states the same numbers, again with no derivation — only a
note that V1's disclosed marginal counts (N=236, 133 tablets, 38
positives) comfortably exceeded it.

**No mathematical derivation, external statistical citation, or explicit
events-per-variable calculation is recorded anywhere for this number.**
For reference (not as the origin, since no such calculation was actually
performed when the number was chosen): a formal events-per-variable (EPV)
heuristic (Peduzzi et al. 1996, ≥10 events per predictor column) applied
to V1's largest model (M4, ~8 encoded columns) would suggest needing
**≥80** positives — meaning ≥30, if anything, is *looser* than a
literature EPV rule would recommend, not a conservative overshoot of one.

**Classification: PROJECT-SPECIFIC CONSERVATIVE RULE, bordering on
ARBITRARY/UNJUSTIFIED** — a round, plausible-sounding number chosen
without a shown derivation chain, not clearly tied to any of the actual
mechanisms (model fitting, CV, permutation, Holm) it was meant to protect.
It is load-bearing in the sense that the protocol commits to treating it
as the literal INCONCLUSIVE trigger, but its specific *value* (30 vs. 25
vs. 35) is not distinguishable from nearby values on any principled basis
recorded in this project.

**Should it automatically carry into V2? No.** Reusing an underived number
"because V1 used it" is not more principled than any other choice — the
correct response, per this round's own Phase 2–4, is to derive a new
criterion tied to V2's actual failure modes, independent of both the old
number and the observed 21.

## Phase 2 — adequacy from first principles, by component

| component | actual failure mode with few positives | hard requirement? |
|---|---|---|
| A. Model fitting | quasi-separation / unstable coefficients for thin categorical levels (e.g. a level with almost no positive rows); L2 (`C=1.0`) bounds true divergence but not estimate quality | No hard N; a soft, disclosed risk |
| B. Held-out log-loss estimation | small test-fold positive counts make `H_hat_k` volatile across folds | No hard N; power/precision concern |
| C. Grouped CV | **hard**: every training fold must contain both classes (`fold_is_evaluable`) — a definitional requirement, not a threshold | **Yes — definitional, already enforced** |
| D. Conditional permutation | fine-grained conditioning strata (especially M3→M4's 4-field cross-product) can leave many strata single-class, contributing zero permutation variance | No hard N; power/resolution concern, tied to stratum-level minority spread, not raw N |
| E. Holm inference | downstream of D; validity (Type-I control) is exact at any N under permutation — **only power is N-sensitive, not correctness** | No hard N |
| F. Category/block support | the existing `category_adequacy` check (`constraint_accumulation.category_adequacy`) is **marginal/Y-blind** — it checks row/tablet counts per category, never *positive* counts per category, so it does not actually protect against a category with plentiful rows but almost no positive signal | Gap identified — see Phase 3 |
| G. Fold/seed stability | cannot be fully assessed without execution; inherent to any pre-registration, not a V2-specific defect | Not resolvable this round |

**Key finding: there is no single N-based number that maps onto these
component-level failure modes.** Components C and E have **hard or
exact** guarantees unrelated to any chosen threshold; components A, B, D,
G are **power/precision** concerns, better addressed by fold- and
stratum-level minority counts than by a raw total-N cutoff; component F
reveals a genuine, previously undocumented gap in the existing category
check.

## Phase 3 — fold-level positive support (POST-V1 DESIGN INFORMATION — ADEQUACY ONLY)

Computed by restricting the already-computed, already-disclosed V1 row
labels to the V2 population (`numeric_value is not None`) and applying
the already-frozen, unmodified `GroupKFold` construction
(`run_constraint_accumulation._make_group_folds`) — no new model, no new
inference, purely label/group counting, exactly as this round's Phase 3
permits.

- **Positive tablets:** 16 of 89 (18%) — positives are **not** dominated by
  one or two tablets: per-positive-tablet counts are `[4, 2, 2, 1×13]`
  (the single most-loaded tablet contributes only 4/21 = 19% of all
  positives).
- **5-fold `GroupKFold`:** all 5 training folds evaluable (both classes
  present). Training positives per fold: **15, 18, 15, 18, 18** (min 15).
  Test positives per fold: **6, 3, 6, 3, 3** (min 3).
- **3-fold `GroupKFold`:** all 3 training folds evaluable. Training
  positives per fold: **13, 18, 11** (min 11). Test positives per fold:
  **8, 3, 10** (min 3).
- **5-fold vs. 3-fold:** 5-fold's minimum training-fold positive count
  (15) is *higher* than 3-fold's (11) — **3-fold is not materially
  better**, and 5-fold remains fully evaluable and credible. No fallback
  is needed for the current V2 population as constructed.
- **Per-block marginal positive counts** (also POST-V1 DESIGN
  INFORMATION): `site_block` HT=14/OTHER=7 (both healthy); `support_block`
  Tablet=20/**OTHER=1** (thin — see limitation below); `position_bucket`
  FIRST=8/SECOND=5/THIRD_OR_LATER=8 (all ≥5); `commodity_class`
  LIQUID=12/DRY=9 (both healthy).
- **Conditional-permutation stratum health** (the M3→M4 step's
  conditioning set, `(site,support,position,commodity)`, is the finest and
  most exposed to sparsity): of 14 populated strata, **10 (71%) contain
  both classes** (genuinely permutable/informative); 7 (50%) have ≥2
  positives. The coarser M1→M2 (3 strata, 3/3 mixed) and M2→M3 (7 strata,
  6/7 mixed) steps are healthier still.

**Disclosed limitation:** `support_block=OTHER` carries almost no positive
signal (1 positive in 5 rows). This affects M1 (baseline, does not gate
later steps under the already-recorded PRE_RESULT_IMPLEMENTATION_
INTERPRETATION) and is a pre-existing corpus-wide thinness (the same
category was thin in V1 too) — disclosed, not resolved, not blocking.

## Phase 4 — recommended V2 adequacy criterion (derived independently of 21)

Chosen **before** checking whether the real V2 population satisfies it —
see Phase 3's numbers as the *separate*, subsequent check, and Phase 5's
synthetic grid (10–40, not centered on 21) as an independent stability
check of the same criterion's mechanics.

**Recommended criterion — combination form (G):**

1. **Hard (definitional, unchanged):** every training fold contains both
   classes (`fold_is_evaluable`), 5-fold preferred, 3-fold fallback,
   `INCONCLUSIVE` if neither is evaluable (unchanged from V1's own rule —
   this part needed no re-derivation).
2. **Minimum minority (positive) count per TRAINING fold ≥ 5** — a
   borrowed, disclosed **analogy** to Cochran's classic ≥5-expected-cell-
   count convention for categorical/count-based inference. **This is not a
   rigorous derivation specific to grouped-CV binary log-loss estimation
   with permutation inference — no such derivation is known to exist in
   the general methodology literature for this exact combined procedure**
   — it is the most defensible off-the-shelf heuristic available, chosen
   for being tied to an actual per-fold mechanism rather than a raw total.
3. **At least 50% of the finest conditional-permutation step's
   (`M3→M4`) populated strata must contain both classes** — targets
   component D directly (permutation resolution/power), rather than
   inferring it indirectly from a total-N number.
4. **V1's coarse total-N/tablet minimums (`≥150`/`≥50`) are retained only
   as an initial feasibility screen, not as the primary or sole gate** —
   they were sized for V1's broader population; V2's population is by
   design smaller, so reusing them as load-bearing would conflate "is the
   overall corpus large enough" with "is this specific restricted
   estimand's minority class well-supported," which are different
   questions.

**Honesty note:** items 2 and 3 still contain irreducible judgment-call
elements (why 5, why 50%) — this criterion is **more targeted and
mechanism-linked** than a single blunt total-count cutoff, not a claim of
mathematical necessity. This is disclosed explicitly, not hidden.

**Does the current V2 population (21 positives) pass this criterion?**
(POST-V1 DESIGN INFORMATION, checked *after* the criterion was fixed):

| requirement | result |
|---|---|
| 1. Hard CV evaluability | **PASS** (5-fold fully evaluable) |
| 2. ≥5 minority/training fold | **PASS** (min 15, comfortably) |
| 3. ≥50% mixed strata at M3→M4 | **PASS** (71%) |
| 4. Coarse N/tablet screen | **PASS** (219≥150, 89≥50 — only the old raw positive-count threshold, ≥30, is what the population fails) |

## Phase 5 — synthetic engineering-stability stress test

`src/v2_adequacy_audit.py` / `tests/test_v2_adequacy_audit.py`
(**synthetic data only**, independently/randomly generated predictor–
outcome relationships — never the real corpus, never a real relationship).
Predeclared minority-count grid **{10, 15, 20, 25, 30, 40}**, not centered
on or optimized around 21.

**Result: the frozen pipeline (`run_constraint_accumulation.run_full_
pipeline`, unmodified) reaches `status: COMPLETE` at every grid point,
including 10 — well below the real V2 count of 21** — with no
convergence failure, no crash, and (correctly, since the synthetic
relationships are genuinely random) no spurious `SUPPORTED` verdict at
any grid point. This is a **method-stability** result, not an estimate of
V2's real chance of success: it shows the machinery does not mechanically
break down in the low-minority-count regime, and correctly returns null
results under a true null — nothing more is claimed.

## Phase 6 — adapter construction state table

| # | raw pattern | numeral token(s) created | `numeric_value` | `.fractions` | V2 included (`S`)? | `Y` |
|---|---|---|---|---|---|---|
| 1 | integer only (e.g. `"15"`) | one, `value=15.0` | 15.0 | `None`/empty | Yes | False |
| 2 | integer + fraction (e.g. `"3"` then `"½"`) | one (merged), `value=3.0` | 3.0 | `[{0.5}]` | Yes | True |
| 3 | fraction only (e.g. `"½"` alone, or after a non-numeral) | one (fresh), `value` never set | `None` | `[{0.5}]` | **No** | True |
| 4a | integer + multiple fractions | one (merged, ≥2 fraction entries) | set | non-empty, ≥2 entries | Yes | True |
| 4b | multiple fractions, no integer | one (fresh, ≥2 fraction entries) | `None` | non-empty, ≥2 entries | **No** | True |
| 5 | malformed/unresolved numeric expression (matches neither `is_numeral_string` nor `is_fraction_glyph`) | **none** — falls through to the signgroup branch | n/a | n/a | n/a — occurrence excluded upstream (`has_quantity=False`) | n/a |
| 6 | damaged/bracket-marked numeral (e.g. `"[15]"`) | **none, structurally** — `is_numeral_string`'s regex (`^\d+$`) cannot match a string containing `[`, `]`, or `?`, so this also falls through to the signgroup branch, same as row 5 | n/a | n/a | n/a — occurrence excluded upstream | n/a |

**New finding from this trace (row 6), not previously documented:** the
adapter's `damaged` flag on **numeral** tokens is **structurally
unreachable as `True`** — `is_numeral_string` and `is_damaged_string`'s
character sets are mutually exclusive by construction (a pure-digit string
can never contain `[`, `]`, or `?`), so a numeral token can only ever be
created with `damaged=False`. A genuinely damaged/bracketed numeral word
instead falls through to the **signgroup** branch (where `damaged` *can*
be `True`), which is never recognized as a numeral and therefore never
resolves as an associated quantity for anything. This is fully consistent
with, and explains, the already-published finding in
`results/EVIDENCE_DEPENDENCE_AUDIT.md` §4 ("DAMAGED/UNCERTAIN = 0" among
all 37 KU-RO occurrences) — recorded here as a disclosed representation
fact relevant to numeral recognition generally, not specific to the
`NO_INTEGER_VALUE` issue, and not itself a defect requiring correction in
this round.

## Phase 7 — formal selection-independence question

`S = 1{numeric_value is not None}`, `Y = 1{fractions non-empty}`.
Known: `S=0 ⟹ Y=1` (proven, `results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md`).

1. **Is `S` logically determined before fraction parsing?** For the
   plain-integer case (row 1/2's integer part), yes — `.value` is set
   immediately on encountering a digit-string word, independent of
   whatever comes next. `S=0` is only ever assigned *within* the
   fraction-glyph branch itself (row 3/4b) — not "before," but not
   *because of* Y either (see item 2).
2. **Is `S` affected by the existence of a fraction?** `S=0` only ever
   co-occurs with a fraction (by construction, row 3/4b) — but `S=1` is
   **unaffected** by whether a fraction later merges in (row 2/4a: `S`
   stays 1 regardless).
3. **For integer+fraction expressions, does `S` remain 1?** **Yes**
   (row 2/4a) — confirmed directly from the merge branch, which never
   clears `.value`.
4. **Is `S` essentially an indicator for "has an integer component"?**
   **Yes, exactly.**
5. **Is `S` merely a parser state?** Partially — it reflects a genuine raw
   fact (was a whole number written) via a specific representation choice
   (`None` vs. a float) that is itself an adapter decision.
6. **Is `S` a deterministic function of the same raw expression that
   determines `Y`?** They read **different sub-parts** (integer sub-token
   vs. fraction sub-token) of what can be the **same overall multi-word
   numeral expression** — related by sharing a source phrase, not by being
   the same computation.
7. **Does conditioning on `S=1` create target leakage?** **No.** Within
   `S=1`, `Y` genuinely varies (21 of 219) — `S` is constant within the
   conditioned population and therefore carries zero information about
   `Y` there. Leakage existed only in the excluded `S=0` subset, which V2
   removes entirely.
8. **Does it instead define a legitimate restricted estimand?** **Yes**
   — see Phase 8.
9. **Could it induce selection bias relative to the full population?**
   Any V2 finding is scoped to the `S=1` (≥1 whole unit) subpopulation
   only — a scope restriction, not an invalidity, **provided** it is
   always reported as such (never generalized to the excluded `S=0`
   range).
10. **What causal assumptions would be needed to call it collider bias?**
    Collider bias requires `S` to be a common *effect* of two variables
    whose association is under study. Here, per
    `results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md` §5, `S` is
    determined by whether the *true quantity* is ≥1 whole unit — i.e., by
    **magnitude itself**, the very quantity `C_MAGNITUDE` (M4) is
    designed to measure. Restricting to `S=1` is therefore best described
    as **left-truncation of the magnitude scale at 1**, not conditioning
    on a collider of two unrelated variables. **Per this round's own
    instruction not to misuse causal terminology: this is SELECTION
    DEPENDENCE (specifically, left-truncation of the predictor under
    study), not collider bias** — this corrects and supersedes the more
    cautious, less precise "collider-bias-adjacent" language used in the
    prior round's design document.

## Phase 8 — is V2 a legitimate conditional estimand?

Testing the exact formulation against the state table (Phase 6): within
`S=1`, both `Y=0` (row 1, integer-only, 198 rows) and `Y=1` (row 2/4a,
integer+fraction, 21 rows) occur, and `Y` is **not** mechanically fixed by
`S` there (§7 item 7). **This supports LEGITIMATE CONDITIONAL ESTIMAND,
not V2 POPULATION INVALID.**

## Phase 9 — raw-representation claim vs. historical/metrological claim

- **A. Raw representation claim (what V2 can test):** *"Among parsed
  numerical expressions containing a whole-number component, structural
  predictors (context, position, commodity, whole-component magnitude)
  predict whether a fractional glyph is also present in that same
  expression."*
- **B. Historical/metrological claim (what V2 cannot establish alone):**
  *"Minoan numerical magnitude affected fractional notation practice as a
  matter of scribal/administrative behavior."* B requires additional,
  unverified domain assumptions (that the parsed representation fully and
  faithfully captures scribal intent; that "fraction glyph present" maps
  onto a meaningful metrological practice rather than incidental
  variation) that V2's design does not, and cannot, verify.

## Phase 10 — M4 naming correction

`log2(1 + integer_value)` measures **only the resolvable whole-number
part** of a numeral expression — for an integer+fraction expression (e.g.
"3 ½"), it evaluates to `log2(4)`, **not** `log2(4.5)` (the true total
quantity). **"WHOLE-COMPONENT MAGNITUDE" is the scientifically precise
name; "numerical magnitude" or "total quantity" would overclaim.** This
naming correction has been applied to
`docs/CONSTRAINT_ACCUMULATION_V2_DESIGN.md` (a factual correction, not a
redesign — see the erratum note added there).

## Phase 11 — fraction-value limitation, stated explicitly

Fraction glyph values (Corazza et al.) are **not** imported into V2, per
the original, still-binding prohibition. Consequence, stated plainly: V2's
`C_MAGNITUDE` (whole-component magnitude) **cannot** measure the true
total quantity of integer+fraction expressions — "3 ½" and "3 ¾" receive
identical `C_MAGNITUDE` values despite differing true quantities. This is
a genuine, disclosed measurement limitation of M4 as designed, not
repaired by any change in this round.

## Phase 12 — information-type framework review

Reviewed `docs/CONSTRAINT_INFORMATION_TYPES.md` against the concern that
"independent" may overclaim for `C_SITE`/`C_SUPPORT` since all fields
describe the same tablet record. **Clarification (added to that document,
not a rewrite):** "independent" in this project's usage means
**construction-independent** — no shared code path or data field with
`Y`'s derivation (`site`/`support` are separate JSON metadata fields,
entirely outside the `transliteratedWords` token stream `Y` is parsed
from) — **not** a claim of statistical independence from `Y` in the world,
which remains exactly the empirical question the experiment is designed
to test. This clarification was judged necessary and has been added.

## Phase 13 — should M3 count toward the strongest accumulation claim?

**Recommendation adopted: NO.** `C_COMMODITY` is EXTERNAL MODEL
INFORMATION (an imported, not corpus-verified, semantic label) — allowing
it to count toward "ACCUMULATION EVIDENCE" (a claim meant to demonstrate
multiple *structural* constraints jointly reducing uncertainty) would let
part of that structural claim rest on an unverified external assumption.
This is coherent and is adopted as the governing rule:

**ACCUMULATION EVIDENCE requires ≥2 Holm-supported blocks drawn from
{DERIVED STRUCTURAL INFORMATION, INDEPENDENT STRUCTURAL INFORMATION}
only** — in V2's architecture, this concretely means **both M2
(`C_POSITION`) and M4 (`C_MAGNITUDE`) must be independently Holm-supported**
for the strongest label; `C_SITE`/`C_SUPPORT` (M1) never count
(baseline), and `C_COMMODITY` (M3) never counts toward this specific
label even if significant.

## Phase 14 — prospective outcome definitions

- **DESIGN BLOCKED** — population or inference construction invalid
  *before* execution. **Not the current state** (Phase 6–9 resolve
  population validity; Phase 1–5 resolve adequacy via a justified
  criterion).
- **INCONCLUSIVE** — design valid, but the Phase 4 adequacy criterion
  fails (globally, or CV is not evaluable at either fold count).
- **NEGATIVE UPDATE** — adequate, valid experiment; **among the
  blocks that were actually evaluable**, none is Holm-supported. (A block
  marked `NOT_EVALUABLE`, per V1's own established precedent, is reported
  separately and excluded from this determination — it does not by itself
  force `INCONCLUSIVE` unless *no* non-baseline block is evaluable at
  all.)
- **LIMITED POSITIVE** — exactly one qualifying block is Holm-supported
  (M2 alone, or M4 alone), **or** M3 alone is Holm-supported (reported as
  an external-model-only positive, explicitly distinguished from a
  structural finding).
- **ACCUMULATION EVIDENCE** — **both** M2 and M4 are independently
  Holm-supported (Phase 13's rule — M3's status is irrelevant to this
  label either way).

**Edge cases:** M3+M4 both significant, M2 not → LIMITED POSITIVE (only
M4 qualifies). M2+M3 both significant, M4 not (or `NOT_EVALUABLE`) →
LIMITED POSITIVE (only M2 qualifies). All three significant → ACCUMULATION
EVIDENCE (M2 and M4 both qualify; M3's significance is additionally
reported, not part of what earns the label).

## Phase 15 — decision point

**Q1 — Population validity: `V2 CONDITIONAL POPULATION VALID WITH
QUALIFICATION`.** Valid: non-tautological, no target leakage within the
conditioned population (Phase 7 item 7, Phase 8). Qualification: must
always be reported as scoped to quantities ≥1 whole unit
(left-truncated, Phase 7 item 10); a null V2 finding does not speak to
the excluded <1 range.

**Q2 — Adequacy: `V2 ADEQUACY CRITERION JUSTIFIED AND CURRENT DESIGN
PASSES`.** The Phase 4 criterion was derived from named, component-level
failure modes, before checking the real count; the real V2 population
(POST-V1 DESIGN INFORMATION, Phase 3) passes it; the machinery was
independently confirmed mechanically stable across a predeclared,
non-21-centered minority grid (Phase 5). The criterion's remaining
judgment-call elements (the specific values 5 and 50%) are disclosed, not
hidden.

**Both blockers are resolved, with disclosed, carried-forward
qualifications — not unconditional, silent passes.**
