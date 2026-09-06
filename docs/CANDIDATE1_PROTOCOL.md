# Candidate 1 protocol: commodity class -> fraction-sign presence

**Status: PROTOCOL FREEZE ONLY. No result has been computed or inspected.**
This document, `src/constraint_candidate1.py`, and
`tests/test_constraint_candidate1.py` are frozen together as of this
commit. Per the same discipline already applied to `H1_PROTOCOL.md` and
`docs/EVIDENCE_DEPENDENCE_PROTOCOL.md`: once frozen, these files are not
silently amended. A genuine implementation obstruction discovered later is
reported as a new, explicit finding — never patched into this document
after the fact.

This is the first planned empirical test of the broader constraint-geometry
program (`docs/CONSTRAINT_HYPOTHESIS_CANDIDATES.md`, Phase 12 recommendation,
Candidate 1). It is explicitly **not** a rescue of the failed KU-RO H1
hypothesis (`results/H1_RESULT.md`, frozen **FAILURE**) — the two tests are
scientifically independent; nothing here can change, weaken, or strengthen
that frozen verdict.

## 1. Scientific hypothesis

Independently assigned commodity class (LIQUID vs. DRY, imported from
external scholarship, not fit to this dataset) is associated with the rate
at which the commodity's recorded quantity carries a fraction-sign glyph.
This is a narrow, specific test of the broader constraint-intersection
hypothesis, not a claim about cognition, decipherment, or arithmetic
correctness.

## 2. Primary observational unit — LEVEL B (tablet-level)

For each normalized tablet and each commodity class represented on that
tablet, **at most one observation per class**, with outcome in
`{FRACTION_PRESENT, FRACTION_ABSENT, AMBIGUOUS_UNUSABLE}`.

**Aggregation rule (frozen): FIRST-QUALIFYING-OCCURRENCE.** Scan the
tablet's commodity occurrences of that class in token order; the first one
with a resolvable associated quantity (§7) determines the tablet-level
outcome. A class with zero occurrences on a tablet produces **no row**
(not applicable, distinct from unusable). A class present only via
heading-form occurrences (none has a resolvable quantity) produces
`AMBIGUOUS_UNUSABLE`.

**Explicit rejection of the naive alternative, and why:** the originally
proposed rule ("`FRACTION_PRESENT` if *at least one* valid quantity of that
class on the tablet carries a fraction") was audited for opportunity bias
before freeze (per this round's own Phase 1 instruction) and **rejected**:
a tablet with five same-class occurrences has five chances for one to carry
a fraction glyph, versus one chance for a tablet with a single occurrence.
If LIQUID and DRY records differ systematically in typical occurrence-count
per tablet (plausible — different commodities may be recorded in batches of
different typical size), the "ANY" rule would let occurrence-count, not
class, drive `Δ_obs`. **First-qualifying-occurrence is deterministic and
chosen without reference to fraction content** (position in the token
stream only), so it cannot inflate either class's rate by opportunity
count. This is implemented in `constraint_candidate1.tablet_level_observations`
and directly tested (`test_tablet_level_first_occurrence_rule_not_any_rule`,
which constructs a tablet where the ANY-rule and the frozen rule would
disagree, and asserts the frozen rule's answer).

## 3. Secondary observational units

- **LEVEL A — raw commodity occurrence** (`constraint_candidate1.find_commodity_occurrences`):
  every in-scope commodity occurrence with its own associated quantity,
  unaggregated. Descriptive / sensitivity analysis only (Sensitivity A, §18)
  — never the primary inferential unit, precisely because of the opportunity
  bias identified in §2.
- **LEVEL C — physical-artifact collapse** (`constraint_candidate1.physical_artifact_key`):
  reuses the exact base-ID + trailing-face-letter heuristic already
  predeclared in `docs/EVIDENCE_DEPENDENCE_PROTOCOL.md` LEVEL 3
  (`HT11a`/`HT11b` -> `HT11`; `HT123+124a` -> `HT123+124`). Classification
  labels are the same five used there: **CONFIRMED SAME ARTIFACT / PROBABLE
  SAME ARTIFACT / POSSIBLE DEPENDENCE / DISTINCT / OPEN** — full
  confirmation of any specific pair remains **DOMAIN-EXPERT DEPENDENT**.
  Used only in the predeclared Sensitivity C (§18), never in the primary
  analysis.

## 4. Exact LIQUID definition

Base sign (§ wildcard rule, below) exactly one of: **`VIN`, `OLE`**.
Ligature-suffixed forms of `OLE` (`OLE+U`, `OLE+A`, `OLE+E`, `OLE+KI`,
`OLE+MI`, `OLE+DI` — all directly observed in the real corpus per
`docs/CONSTRAINT_SPACE_DATA_AUDIT.md` §C) are included via the wildcard
rule, not individually enumerated.

## 5. Exact DRY definition

Base sign exactly one of: **`GRA`, `OLIV`**. Ligature-suffixed forms of
`GRA` (e.g. `GRA+L4+L4`, directly observed) are included via the wildcard
rule.

## 6. Exact wildcard / family-normalization rule

`base_sign(sign_id)` = the substring of the raw sign-id string **before the
first `"+"`** (or the whole string, if no `"+"` is present). Class
membership requires **exact equality** between `base_sign(sign_id)` and one
of the four predeclared base signs above — **never** substring, prefix, or
`startswith` matching. This is a deliberate, tested exclusion: `"OLIVE"`,
`"OLIVX"`, `"XOLIV"`, and `"OLEX"` are all **out of scope** (base sign
`"OLIVE"`/`"OLIVX"`/`"XOLIV"`/`"OLEX"` respectively, none equal to `"OLIV"`
or `"OLE"`), even though several look superficially similar — this
prevents exactly the kind of loose-matching false positive Phase 2 warned
against. Any commodity whose base sign is not one of the four (`CYP`,
`CYP+D`, `CYP+E`, `VIR+KA`, and everything else) is **OUT OF SCOPE** for
Candidate 1 and will not be added to either class after seeing results.

**Epistemic status:** commodity sign identity = **AVAILABLE** (raw,
directly observed transliteration token). LIQUID/DRY semantic-class
assignment = **EXTERNAL DOMAIN MODEL INPUT / PROPOSED INTERPRETATION**,
resting on provisional Linear-B homology (`docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md`
items 7–8), imported unchanged from prior scholarship, not fit to this
dataset (anti-circularity §21, item 2).

## 7. Exact fraction-presence rule

`FRACTION_PRESENT` iff the token associated with a commodity occurrence
(§ commodity<->quantity association, below) is a numeral token whose
`.fractions` field is a non-empty list — **regardless of the fraction
entries' `confidence` field.** This is a deliberate, documented departure
from `kuro_protocol.numeral_value`'s confidence-admission gate
(`FRACTION_CONFIDENCE_ADMITTED = ("secure", "derived")`): Candidate 1 tests
**sign presence**, not resolved arithmetic value, so an unresolved-confidence
fraction glyph still counts as present. `FRACTION_ABSENT` iff the
associated token is a numeral with an empty/absent `.fractions` field.
`AMBIGUOUS`/no observation iff no associated quantity can be resolved at
all (§8).

**Fraction-value scholarship (Corazza et al.) plays no role in this rule or
in Candidate 1 at all** — only glyph presence, never numeric value, is
used, so the contested status of Corazza's specific fraction VALUES
(`docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md` item 2) cannot affect this
test's primary outcome.

**Adversarial resolution (Phase 15): commodity ligatures cannot cause false
fraction detection.** A ligature suffix on the commodity token itself (e.g.
`GRA+L4+L4`) is never inspected for fraction-like content by this rule —
only the *separate, associated numeral token's* `.fractions` field is
read. Directly tested:
`test_ligature_suffix_does_not_leak_into_fraction_presence` constructs a
`GRA+L4+L4` commodity token followed by a plain integer with no fraction
glyph, and asserts `FRACTION_ABSENT` is correctly returned despite the
ligature suffix.

## 8. Commodity <-> quantity association rule

The first token following the commodity occurrence's index that is a
numeral token, provided no signgroup (or ruling) token intervenes first —
`constraint_candidate1.associated_quantity`, an independent
re-implementation of the exact adjacency convention already frozen and
tested in `kuro_protocol.associated_numeral` (no import-time coupling to
KU-RO-specific target logic). Classified **DERIVABLE** (mechanical,
position-only, no arbitrary distance threshold — the one Phase-4 condition
that would otherwise force a METHOD OBSTRUCTION classification). A
commodity token immediately followed by another signgroup (heading-like
use, mirroring `kuro_protocol.is_commodity_heading`'s concept) has **no**
associated quantity — that specific occurrence is excluded, never guessed.

Multiple consecutive plain-integer numeral tokens after a commodity are
**not** merged; only the single, first, immediately-following numeral token
is the associated quantity, exactly matching the precedent already set by
`kuro_protocol.associated_numeral`'s own single-numeral convention — this
is reuse of an existing, tested convention, not a new ad hoc rule invented
for Candidate 1.

## 9. Ambiguity / exclusion rules

- A commodity occurrence with no resolvable associated quantity ->
  excluded from that occurrence's own Level-A row (`has_quantity=False`,
  `fraction_present=None`).
- A tablet x class combination where every occurrence is unusable ->
  `AMBIGUOUS_UNUSABLE` at Level B, excluded from all inferential
  computation (`constraint_candidate1.usable_rows`), never coerced to
  `FRACTION_ABSENT`.
- A commodity sign whose base is outside the four predeclared families ->
  out of scope entirely, not an exclusion category, simply never
  constructed as an occurrence.

## 10. Site / document-type stratification

**Site**: the raw corpus's own `site` metadata field, normalized
(stripped, casefolded), missing -> `"UNKNOWN"`.

**Document type**: the raw corpus's own `support` field (physical
support/object type — e.g. `"Tablet"`, `"Sealing"`, `"Nodule"`, `"Stone
vessel"`; 19 distinct values observed in a schema check this round, never a
Candidate-1 statistic), normalized identically. This field is assigned
independently of any fraction behavior — it describes the physical object,
not its content — satisfying Phase 5's explicit requirement not to invent a
document-type taxonomy by looking at fraction behavior. (Note: the raw
corpus's `context` field is a chronological period code, e.g. `"LMIB"`,
`"MMIIIA"` — **not** used as the document-type dimension here, since it
answers "when," not "what kind of object," though it remains available for
a future site x period stability test, Candidate 5.)

`constraint_candidate1.stratum_key(site, support)` returns the normalized
`(site, support)` pair.

## 11. Exact Δ statistic

    Δ_obs = p_L - p_D

where `p_L` = (# usable LIQUID tablet-level observations with
`FRACTION_PRESENT`) / (# usable LIQUID tablet-level observations), and
`p_D` analogously for DRY — computed **only over exchangeable strata**
(§12/§13). `constraint_candidate1.delta` returns `None` (not an exception)
if either class has zero usable rows in the exchangeable-stratum pool.

## 12. Exact permutation algorithm

**NULL 3** (`docs/CONSTRAINT_NULL_MODELS.md`): within each exchangeable
`(site, support)` stratum, shuffle the LIQUID/DRY class **labels** among
that stratum's usable rows — outcomes (`FRACTION_PRESENT`/`ABSENT`) stay
attached to their original row position; only which row is nominally
"LIQUID" vs. "DRY" is randomized. Preserves: total observation count,
site×support composition, each stratum's own class-count split, and every
row's own fraction-presence outcome. Destroys: the pairing between class
label and outcome. Strata with only one class present cannot be
permuted meaningfully (§13) and are excluded from both `Δ_obs` and every
`Δ_perm`, retained only descriptively.
`constraint_candidate1.stratified_permutation_delta` implements one draw;
`run_stratified_permutation_test` runs the full loop.

## 13. B = 2000

Frozen. `run_stratified_permutation_test(rows_by_stratum, B=2000, rng=...)`.

## 14. Exact finite-permutation p formula

    p = (count(|Δ_perm| >= |Δ_obs|) + 1) / (B + 1)

`constraint_candidate1.finite_permutation_pvalue`, unit-tested at B=2000
(zero-extreme, all-extreme, and midpoint cases).

## 15. α = 0.05

Frozen, two-sided.

## 16. Alternative hypothesis

**Two-sided.** Testing whether class constrains fraction usage at all, not
asserting a direction (the wine/grain motivation is explicitly "motivation
only," per this round's own instruction — it does not license a one-sided
test).

## 17. Adequacy gates

- At least **10 usable, tablet-deduplicated** observations in LIQUID **and**
  at least **10** in DRY, counted over exchangeable strata only. Otherwise:
  **INCONCLUSIVE.**
- At least **10 total usable observations located within exchangeable
  strata** (strata containing both classes) — a corpus in which every
  LIQUID observation happens to fall in a site×support stratum with no DRY
  observations at all (and vice versa) would have `Δ_obs` undefined
  (`None`) regardless of raw counts; this is checked directly by
  `observed_delta` returning `None`, not by a separate numeric gate.

Both gates are frozen now, before any real count is known — not tuned
after seeing data.

## 18. Predeclared sensitivity analyses

- **Sensitivity A** — raw commodity-occurrence level (Level A, no tablet
  dedup, no first-occurrence restriction).
- **Sensitivity B** — primary tablet-level (§2, the primary analysis
  itself, listed here per this round's own Phase 10 enumeration).
- **Sensitivity C** — probable-same-physical-artifact collapse (Level C,
  §3), predeclared collapse rule identical to
  `docs/EVIDENCE_DEPENDENCE_PROTOCOL.md`.
- **Sensitivity D** — Haghia Triada only, if sample size permits (site
  concentration is already known to be severe for KU-RO,
  `results/EVIDENCE_DEPENDENCE_AUDIT.md` §5; not yet checked for
  commodity/fraction occurrences specifically — that check itself would be
  a real-data computation and is deferred to the future analysis run, not
  performed this round).
- **Sensitivity E** — exclude all ligature-suffixed variants; test only
  bare base-sign occurrences (`VIN`, `OLE`, `GRA`, `OLIV` exactly, no
  `"+"`), to confirm no ligature variant is silently driving any effect.

All five use the identical fraction-presence definition (§7) and the
identical class definitions (§4–6) — no new commodity category is
introduced in any sensitivity.

## 19. Exclusion rules

See §9. No exclusion category is added or removed after seeing results.

## 20. Epistemic status of commodity semantics

Commodity sign identity: **AVAILABLE**. LIQUID/DRY class assignment:
**EXTERNAL DOMAIN MODEL INPUT / PROPOSED INTERPRETATION** (provisional
Linear-B homology — see `docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md` items
7–8). This is also this project's predeclared **positive control**
(`docs/CONSTRAINT_NULL_MODELS.md`): a constraint-detection method that
cannot recover *any* signal from this well-supported association would
indict the method, not the broader hypothesis — but that same imported
status means a positive result here does not, by itself, independently
validate the LIQUID/DRY semantic labels; it validates the *statistical
method* against an *externally supported* labeling.

## 21. Anti-circularity declaration

Answering Phase 12's six questions, before any real-data computation:

1. **Is commodity identity determined without using fraction presence?**
   Yes — `commodity_class` reads only the sign-id string; `fraction_present`
   reads only the separate numeral token. Structurally independent fields.
2. **Is LIQUID/DRY assignment imported from prior scholarship rather than
   fit to this dataset?** Yes — see §20; the four base signs and their
   class assignment were fixed in `docs/CONSTRAINT_HYPOTHESIS_CANDIDATES.md`
   (Phase 12) before this protocol document or its code existed.
3. **Is fraction presence determined without using commodity class?**
   Yes — `fraction_present` takes only a `Token`, with no commodity
   argument at all.
4. **Is commodity<->quantity association defined without reference to
   whether a fraction occurs?** Yes — `associated_quantity` returns the
   first following numeral token unconditionally; whether that token turns
   out to carry a fraction plays no role in whether it is selected as "the"
   associated quantity.
5. **Is the unit of analysis frozen before seeing class-specific rates?**
   Yes — this entire document, and the first-occurrence rule specifically
   (§2), is written and tested (§ Phase 13 test suite) with only synthetic
   fixtures; no real-data class-specific rate has been computed (§22).
6. **Is the null frozen before seeing Δ_obs?** Yes — NULL 3 was already
   predeclared in `docs/CONSTRAINT_NULL_MODELS.md` in the prior round,
   before this protocol's own code existed; §12 operationalizes it
   unchanged.

All six: **YES.** Test is **AUTHORIZED** to proceed to a future real-data
run under this frozen protocol.

## 22. Explicit statement: no result was inspected before freeze

`src/constraint_candidate1.py` has **never been invoked against
`data/generated/lineara_extracted.json`** in the round that produced it.
Every function in that module is exercised **exclusively** by hand-built
synthetic fixtures in `tests/test_constraint_candidate1.py` (54 tests, all
passing — see Final Report §20). No LIQUID rate, DRY rate, `Δ_obs`,
permutation p-value, effect size, or verdict of any kind exists anywhere in
this repository for Candidate 1. The only real-data engineering check
performed this round was a bounded schema scan of the `support` field's
distinct values (19 found, listed in §10) and the tablet-ID face-letter
pattern (222/1721 tablet IDs match, reused for `physical_artifact_key`) —
both pure schema/format checks, revealing nothing about commodity class or
fraction presence.
