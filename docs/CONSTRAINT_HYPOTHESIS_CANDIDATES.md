# Constraint hypothesis candidates

**Phases 3–6, 9–12 of the constraint-geometry research branch.** Design
only — no hypothesis outcome is computed in this document. Grounded in
`docs/CONSTRAINT_SPACE_DATA_AUDIT.md` (what the data supports) and
`docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md` (what scholarship already
establishes), tested against `docs/CONSTRAINT_NULL_MODELS.md`'s
anti-circularity checklist.

## Phase 3 — Constraint feature families, as actually supported by the data

Restricted to what `docs/CONSTRAINT_SPACE_DATA_AUDIT.md` classifies
AVAILABLE or cleanly DERIVABLE — fields that would require inventing new
structure are excluded, not silently included:

```
X(record) = (
    site,                    -- C_SITE, AVAILABLE
    commodity_ideogram,      -- C_COM, AVAILABLE
    numeral_value,           -- C_NUM, AVAILABLE
    fraction_present,        -- C_FRAC, AVAILABLE (identity only)
    fraction_value,          -- C_FRAC, EXTERNAL DOMAIN MODEL INPUT
    position_index,          -- C_POS, AVAILABLE
    entry_count,             -- C_DOC, DERIVABLE
    heading_present,         -- C_DOC, DERIVABLE (imprecise, see data audit)
)
```

**Deliberately excluded from the feature space**, per the data audit:
metrological-system tag as an independent field (does not exist separately
from commodity identity — folding it in as if it were directly observed
would be exactly the "silently treat scholarly interpretation as raw data"
error this round's instructions warn against); section/ruling boundary
(AMBIGUOUS, already known unreliable from the primary H1 round's own `\n`
finding); repeated-template detection (OPEN, not measured).

## Phase 4 — Intra-record candidates considered

**A. Arithmetic closure.** Already tested for the one case with an
independently-strong "total" identification (`ku-ro`) — **FAILURE**,
frozen, not reopened here. A *new* arithmetic-closure test would need an
independently-identified total *not* resting on `ku-ro`/`po-to-ku-ro`
semantics, which this round did not find a non-circular way to define
(any other "this numeral is the total" criterion this project can
currently construct ultimately reduces to position/labeling that assumes
what it would need to test). **Not shortlisted, for exactly this
circularity reason.**

**B. Fractional completion (accepted vs. permuted fraction-value
assignment).** Directly testable (NULL 2). Deferred, not shortlisted this
round, because it is a *refinement* of the already-tested `ku-ro` arithmetic
question rather than a genuinely different constraint family — running it
now would risk looking like exactly the "rescue KU-RO" move this round's
instructions explicitly forbid, even though its logic is sound. Recorded
as a legitimate *future* candidate once separated in time from the H1
result.

**C. Numerical decomposition (whole → attested subdivisions).** Requires
assuming which subdivisions are "attested" — circular unless the candidate
subdivisions are fixed from Corazza et al.'s table *before* looking at
which ones the corpus favors. Feasible with that discipline; not
shortlisted this round for scope reasons (would essentially duplicate
Candidate 4 below, which already exercises fraction-value distributions).

**D. Local order (category → quantity → total-marker sequence vs. position
null).** **Shortlisted (Candidate 3 below).**

**E. Nested arithmetic (block A → subtotal A, block B → subtotal B →
total).** Requires independently identifying subtotal boundaries without
inferring them from successful arithmetic — this round did not find a
non-circular way to do so (the only strong subtotal/total markers
available are `ku-ro`/`po-to-ku-ro` themselves). **Not shortlisted,
CIRCULAR as currently formulable.**

## Phase 5 — Inter-record candidates considered

**A. Commodity × fraction pattern (presence).** **Shortlisted (Candidate 1,
top-ranked).**

**B. Commodity × numerical scale.** **Shortlisted (Candidate 4, lower-ranked
— see reasoning there).**

**C. Commodity × metrological system.** Collapses into Candidate 1/4/5
combined, since "metrological system" is not an independent field (Phase
3) — there is no separate C_MET test distinct from a commodity-conditioned
fraction/magnitude test given this data.

**D. Metrology × fraction (does the fraction system itself vary by
site/period, addressing Corazza et al.'s own noted caveat).**
**Shortlisted (Candidate 5, most novel, weakest power).**

**E. Document type × numerical structure.** Not shortlisted — document-type
metadata beyond "Tablet" was not confirmed reliably differentiated in this
round's data audit (OPEN).

**F. Cross-site stability.** Not independently shortlisted — folded into
Candidate 5's site-stratification, and explicitly **not** claimed from
Haghia Triada alone anywhere in this document, per this round's own
warning and the primary H1 result's own already-documented site
concentration.

## Phase 6 — Intersection / conditional-information framing

The central methodological commitment across every shortlisted candidate:
report the **individual** constraint's apparent effect (e.g. commodity
class alone) *and* the **joint** effect (commodity class combined with
site/document-type stratification, as NULL 3 already requires) side by
side, using conditional rejection rate under the appropriate null rather
than an unconditional one. A result of the shape "commodity alone: weak;
commodity + site-stratified null: clearly rejects" would be the single
most direct piece of evidence *for* the constraint-intersection idea named
in this round's motivation — and the reverse (no detectable effect at any
level) would be equally informative *against* it. **No mutual-information
or entropy estimator is proposed for the first frozen test** (Candidate 1)
— at the sample sizes available (dozens to low hundreds of occurrences
after tablet-level dedup), a permutation test on a simple rate difference
is the appropriate tool; sophisticated information-theoretic estimators
would not be justified by the data and are explicitly not used merely for
appearance, per this round's own instruction.

## Phase 9 — Cognitive interpretation firewall (binding on every candidate)

None of the five candidates below, if run, may be reported as evidence for
modern rational-number theory, explicit multiplicative inverses, algebra,
decimal thinking, or abstract reciprocal operators. The evidence ladder
this project commits to:

- Fraction notation observed (already true) → supports systematic
  part-whole representation only.
- A commodity-conditioned fraction-presence effect, if found → supports
  systematic association between commodity handling and fractional
  notation use, nothing about *how* that association was cognized.
- Nothing in this round's candidates reaches evidence-ladder Level 3
  (transformational relationships among units), and none should be
  described as if it did.

## Phase 10 — Anti-circularity audit, applied per candidate

| # | Candidate | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Commodity × fraction-presence | ✓ | n/a | ✓ | n/a | ✓ (predeclared below) | must apply Level-2 dedup | must apply Level-3 pairs | must check | **CLEAR, pending dedup discipline at run time** |
| 2 | Local order vs. position null | ✓ | n/a | ✓ | n/a | ✓ | same | same | same | **CLEAR, pending dedup discipline** |
| 3 | Commodity × fraction-value | ✓ | n/a | ✓ | **imports Corazza, not fitted — OK** | ✓ | same | same | same | **CLEAR, but inherits the "static fraction system" scholarly caveat as a confound, not just a footnote** |
| 4 | Commodity × magnitude | ✓ | n/a | ✓ | n/a | ✓ | same | same | same | **CLEAR, but see importance/novelty ranking below** |
| 5 | Fraction-system site/period stability | ✓ | n/a | n/a (no commodity assignment involved) | n/a | ✓ | same | same | same, explicitly the point of the test | **CLEAR, weakest power** |

(Questions 2 and 4 are "n/a" where a candidate does not involve identifying
a total or a fraction-value fit at all.) **No candidate in this shortlist
is labeled CIRCULAR — NOT EVIDENCE.** The excluded Phase 4 items (A, C, E)
were excluded specifically because they failed this checklist.

## Phase 11 — Ranked shortlist (at most five, as instructed)

| Rank | Candidate | Independence from decipherment | Data quality | Sample size | Dependence resistance | Falsifiability | Null available | Importance | Novelty |
|---|---|---|---|---|---|---|---|---|---|
| **1** | Commodity × fraction-presence (C_COM ∩ C_FRAC identity) | High | High | Moderate–good | Good (Level-2/3 machinery reused) | High | Yes (NULL 3) | High (positive control + genuine test) | Moderate |
| **2** | Local order vs. position null (C_DOC ∩ C_POS) | High | Moderate (heading detection imprecise) | Good | Good | High | Yes (NULL 4) | Moderate–high | Moderate |
| **3** | Commodity × fraction-*value* (C_COM ∩ C_FRAC ∩ C_MET, finer) | High | Moderate (EXTERNAL value model) | Moderate | Good | High | Yes (NULL 2/3 combined) | High if it works | High |
| **4** | Commodity × numerical magnitude (C_COM ∩ C_NUM) | High | High | Good | Good | High | Yes (NULL 1/3) | **Lower** — plausibly near-trivial (bulk commodities mundanely have larger numbers) | Low |
| **5** | Fraction-system site/period stability (C_MET ∩ C_FRAC across strata) | High | Moderate | **Weak** (Haghia-Triada dominance, already documented) | Good | High | Yes (stratified permutation) | **Highest in principle** — directly tests a named open scholarly caveat | **Highest** |

## Phase 12 — Recommended first frozen test

# Candidate 1: Commodity class → fraction-sign presence rate

Chosen over the higher-novelty Candidate 5 specifically on **feasibility
and power grounds** (Candidate 5's own honestly-reported weakness is site
concentration, the exact problem this project's evidence-dependence audit
already spent a full round documenting for KU-RO) and over Candidate 3 on
**confound-avoidance grounds** (Candidate 1 needs only fraction *presence*,
not the contested Corazza value table, so it does not inherit the "system
may have changed over time" caveat as a live confound). It also
simultaneously serves as the **positive control** named in Phase 8 — a
methodology check, not just a new question.

### Exact proposed statistic

For every numeral token immediately following a token in a **predeclared**
commodity-class set (see below), record a binary indicator: does that
numeral carry an adjacent fraction-glyph (per the existing, frozen
`lineara_adapter.py` N2 fraction-merge logic — reused unmodified, not
redefined)? Compute:

```
rate(class) = (# fraction-bearing quantities in class) / (# quantities in class)
Δ_obs = rate(LIQUID) - rate(DRY)
```

**Predeclared commodity classes** (fixed now, per the Phase 2 scholarship
audit's own item 7/8 — not tuned after inspection):

- **LIQUID** = tokens matching `VIN` or `OLE` (including `OLE+*` ligatures)
- **DRY** = tokens matching `GRA` or `OLIV` (including `GRA+*` ligatures)
- Any other candidate ideogram (`CYP`, `VIR+KA`, etc.) is **excluded from
  both classes** rather than guessed into one — per this round's own
  instruction not to silently treat interpretation as data.

### Exact proposed null model

**NULL 3** (`docs/CONSTRAINT_NULL_MODELS.md`): shuffle the LIQUID/DRY class
label among commodity-bearing quantity occurrences **within the same site
× document-type stratum** (not corpus-wide), B=2000 replicates (matching
this project's existing convention), recomputing `Δ_null` each time.
Two-sided permutation p-value = fraction of replicates with
`|Δ_null| ≥ |Δ_obs|`.

### Exact falsification criterion

Predeclared **before** the test is run: **α = 0.05.** If `p ≥ 0.05`, the
hypothesis (in this specific instantiation) **FAILS** — reported as a null
result, not "inconclusive." If `p < 0.05`, report the sign and magnitude of
`Δ_obs` exactly, without interpreting an unexpected-direction result as
confirmatory.

**Adequacy gate, predeclared:** if either class has fewer than 10
tablet-level-deduplicated occurrences after applying
`docs/EVIDENCE_DEPENDENCE_PROTOCOL.md`'s Level-2 discipline, the test is
**INCONCLUSIVE**, not run to a FAIL/PASS conclusion.

### Expected sample size / dependence limitations

A bounded, imprecise composition scan this round (not a hypothesis-level
count) found raw token occurrence counts of roughly `VIN`≈53, `OLE`-family
≈96 combined (LIQUID ≈149 raw), `GRA`≈62 (+`GRA+PA`≈19), `OLIV`≈24 (DRY
≈105 raw) — plausibly adequate before dedup, but **tablet-level
deduplication and site/document-type stratification will shrink the
effective per-cell count substantially**, and this has not been measured
precisely. The same face-pair/joined-fragment dependence issues documented
for KU-RO (`results/EVIDENCE_DEPENDENCE_AUDIT.md`) apply here and must be
re-applied, not assumed absent.

### Domain-expert dependencies

Whether `VIN`/`OLE` are correctly liquid-class and `GRA`/`OLIV` correctly
dry-class rests on the provisional Linear-B-homology methodology (Phase 2,
item 7–8) — **PROPOSED INTERPRETATION**, not independently proven for
Linear A. Whether excluded ideograms (`CYP` etc.) truly belong to neither
class, or were simply not resolved by this project's identification
methods, is **OPEN**.

## Answer to the section-11 gate question

**The broad constraint hypothesis is currently: PARTIALLY TESTABLE.**
Candidate 1 above is fully specified and ready to freeze; Candidates 2–4
are feasible with modest further design work; Candidate 5, the most
directly novel, is honestly underpowered given already-documented site
concentration. Not BLOCKED (unlike the SigLA branch); not fully TESTABLE
across the whole constraint-intersection vision at once — only one
well-scoped piece of it at a time, exactly as this round's own instructions
prefer over a fishing expedition.
