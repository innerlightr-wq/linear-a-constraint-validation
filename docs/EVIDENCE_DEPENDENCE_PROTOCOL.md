# Evidence-dependence protocol

**Status: FROZEN before any tablet-level, dependence, or confidence-stratified
figure has been computed.** This document predeclares definitions exactly as
`H1_PROTOCOL.md` predeclared H1's own definitions before any corpus
statistic was computed — the same discipline, applied one level up, to how
this project evaluates the *strength and independence* of the evidence
behind the already-frozen H1 result, not to the result itself.

**This audit does not reopen, recompute, or reinterpret the frozen H1
verdict** (`results/H1_RESULT.md`, commit `df2916485fbd97070d869c1fdefd54fdbd4798bd`).
It operates entirely on the already-frozen occurrence-level data
(`results/h1_occurrence_audit.csv`) plus, where explicitly noted, a
non-invasive re-derivation of one additional structural flag (fraction
involvement) from the same already-committed real corpus extraction and the
same frozen adapter/protocol code — never a new arithmetic classification,
never a changed residual, never a changed outcome category.

## LEVEL 1 — Occurrence level

The already-reported 37 KU-RO occurrences (`results/H1_RESULT.md` §5),
exactly as classified there. No redefinition.

## LEVEL 2 — Tablet level

Each tablet contributes **at most one unit of evidence**, regardless of how
many KU-RO occurrences it carries. For a tablet with N≥1 KU-RO occurrences,
classify using the arithmetic outcomes of that tablet's occurrences that
are **not** `NOT_TESTABLE`:

- **SUPPORT-outcomes** = {`EXACT_CLOSURE`, `ROUNDING_COMPATIBLE`}
- **MISMATCH-outcomes** = {`UNEXPLAINED_MISMATCH`}
- **NEUTRAL (excluded from the support/mismatch count, tracked separately)**
  = {`DAMAGED_OR_UNCERTAIN`, `NOT_TESTABLE`}

Tablet classification, applied in this fixed order:

| condition | label |
|---|---|
| ≥1 support-outcome AND 0 mismatch-outcomes | **ALL_SUPPORT** |
| ≥1 mismatch-outcome AND 0 support-outcomes | **ALL_MISMATCH** |
| ≥1 support-outcome AND ≥1 mismatch-outcome | **MIXED** |
| 0 support-outcomes AND 0 mismatch-outcomes | **UNTESTABLE** |

This mirrors the frozen protocol's own damage-before-residual precedence
(`H1_PROTOCOL.md` §7): a `DAMAGED_OR_UNCERTAIN` occurrence never counts as
either support or mismatch at the tablet level either.

## LEVEL 3 — Dependency-cluster / unique-artifact level

Document ID is **not assumed** to equal independent artifact. Candidate
dependence patterns to search for, in the primary corpus's own tablet
identifiers and metadata (no external source consulted):

- exact duplicate tablet IDs (should be structurally impossible given the
  corpus's own construction, but checked, not assumed)
- alternate/compound catalog IDs (e.g. `HT123+124a`-style joins, already
  known from earlier rounds)
- multiple face-labels of what might be the same physical object
  (`...a`/`...b`/`...c` suffixes)
- near-identical structural content (same site, same entry count, same
  numeral sequence) that might indicate a duplicate transcription rather
  than a distinct artifact

Classification labels, applied per finding: **CONFIRMED DUPLICATE**,
**PROBABLE SAME ARTIFACT**, **POSSIBLE DEPENDENCE**, **DISTINCT**, **OPEN**.
Where a judgment requires expertise this project does not have (e.g.
whether two face-labels represent one physical tablet or two), label
**DOMAIN-EXPERT DEPENDENT**. If reliable clustering is not possible for a
given case, it is labeled **OPEN**, not resolved by assumption.

## Confidence strata

Predeclared, using **only** fields already present in the primary corpus's
own occurrence audit plus one non-invasive re-derivation (fraction
involvement — see below), applied in this fixed priority order:

1. **DAMAGED/UNCERTAIN** — the occurrence's existing `flag_damaged` column
   (`results/h1_occurrence_audit.csv`) is `True`.
2. **MISSING FRACTION INFORMATION** — not damaged, but the total or any
   block numeral involved a fraction-glyph token whose confidence grade was
   unresolved (per `H1_PROTOCOL.md` §3's admission rule and the already-
   documented fraction-confidence gap, `results/H1_RESULT.md` §15). This
   flag is **re-derived**, not read from an existing CSV column (the
   original occurrence audit did not persist it) — computed by replaying
   the same frozen `lineara_adapter`/`kuro_protocol` extraction against the
   same already-extracted, unchanged `data/generated/lineara_extracted.json`,
   checking only whether a `fractions` list was non-empty on the relevant
   tokens. This changes no classification, residual, or outcome — it adds
   one descriptive boolean.
3. **SECURE** — not damaged, no fraction involvement, and arithmetically
   eligible with no exclusion reason (`primary_exclusion_reason` is empty).
4. **OTHER UNRESOLVED** — everything else (e.g. `MISSING`-excluded
   occurrences that are neither damaged nor fraction-involving).

**No confidence field is fabricated.** If a distinction cannot be made from
what actually exists in the source, it is reported as unavailable, not
guessed.
