# Constraint information types: an operational classification

**Purpose:** state, once, the general methodological lesson learned from
the V1 `NO_INTEGER_VALUE` finding
(`results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md`), in a form that can
be checked mechanically against any future candidate predictor in this
project — not a philosophical essay, an operational checklist.

## The general lesson

**A constraint should count as independent accumulation evidence only
when its predictive information is not already mechanically encoded in
the construction of the target or another predictor.**

A predictor can look statistically powerful for two entirely different
reasons: it captures a genuine relationship in the world the corpus
describes, or it shares enough of its construction with the target that
some of its apparent power is guaranteed by definition rather than
discovered by data. V1's `C_NUMERIC` block did both at once, in different
sub-parts of the same feature (`results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md`)
— which is precisely why the audit had to be done at the level of
individual categories, not the whole feature.

## Three kinds of constraint

- **Structural constraint** — an independently defined relation that
  restricts the admissible state space, discoverable from the corpus's
  own directly observable structure (e.g., "does token position within a
  record correlate with X"). Two subtypes matter for this project:
  - **Independent structural information** — read from a field that
    shares no construction path with the target at all (e.g., `C_SITE`,
    `C_SUPPORT`: tablet metadata, entirely separate from token parsing).
  - **Derived structural information** — mechanically computed from the
    corpus's own token structure, but from fields the target does not
    also read (e.g., `C_POSITION`: token order, never `.fractions` or
    `.value`).

  **Clarification (added per `docs/CONSTRAINT_ACCUMULATION_V2_BLOCKER_
  AUDIT.md` Phase 12):** "independent" here means **construction-
  independent** — no shared code path or data field with the target's
  own derivation — not a claim of statistical independence from the
  target *in the world*. `C_SITE`/`C_SUPPORT` describe the same tablet
  record as everything else, but are read from separate JSON metadata
  fields entirely outside the token stream the target is parsed from;
  whether they *correlate* with the target is exactly the open empirical
  question an accumulation experiment is meant to test, not something
  the "independent" label presupposes.
- **Representation constraint** — a restriction introduced by how the
  encoding/parser/adapter chose to represent something, which may
  entangle two supposedly independent variables even when neither the raw
  corpus semantics nor the researcher intended it. This is exactly what
  happened with `NO_INTEGER_VALUE`: the raw corpus fact (a sub-unit
  quantity has no integer digits) is genuine, but the adapter's choice to
  represent "no integer part" as `value=None` **on the same token object**
  whose `.fractions` field defines `Y` created a deterministic coupling
  for that one subcase. Labeled **CONSTRUCTION INFORMATION** in this
  project's tables.
- **Semantic model constraint** — a restriction imported from external
  interpretation not verifiable from the corpus alone (e.g., `C_COMMODITY`'s
  LIQUID/DRY grouping, imported via provisional Linear-B homology).
  Labeled **EXTERNAL MODEL INFORMATION**. Not a construction dependence
  (no shared parser state with `Y`), but not free of outside assumptions
  either — a positive finding here supports "the imported label has
  conditional predictive usefulness," never "the semantic label is itself
  independently verified" (`results/CANDIDATE1_RESULT.md` §22,
  `docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md` §14).

## The operational check

Before authorizing any candidate predictor for an accumulation test, ask,
in this order:

1. **Does computing this predictor ever read the same object/field the
   target reads?** If yes, trace every code path that can produce each of
   the predictor's possible values, and check whether any value is
   *only* producible in a way that also fixes the target's value. If so:
   **CONSTRUCTION INFORMATION** for that value/category specifically — not
   necessarily the whole predictor.
2. **Does the predictor's definition require an imported, non-corpus-
   internal, non-independently-verifiable interpretation?** If yes:
   **EXTERNAL MODEL INFORMATION** — usable, but any positive result must
   be stated as "the imported label has conditional predictive
   usefulness," not as independent confirmation of that label.
3. **Otherwise**, is the predictor read from a field the target's
   construction never touches at all? **INDEPENDENT STRUCTURAL
   INFORMATION.**
4. Is it mechanically derived from the corpus's own structure (position,
   counts, ordering) without touching the target's fields?
   **DERIVED STRUCTURAL INFORMATION.**

**A predictor found to contain CONSTRUCTION INFORMATION for one or more of
its categories is not necessarily unusable wholesale** — as with V1's
`C_NUMERIC`, the clean fix is usually to **exclude the affected
subcategory from the population or the feature**, not to discard the
entire predictor, provided the resulting population restriction is itself
independently justified and disclosed (`docs/CONSTRAINT_ACCUMULATION_V2_DESIGN.md`
§"V2 population").

## Applying this to Linear A specifically, and beyond

This lesson is not specific to Linear A or to this corpus. Any project
that (a) derives both a target and a candidate predictor from the same
underlying parsed object, or (b) imports an external semantic label as a
predictor, faces exactly these two risks. The fix in both cases is the
same: **trace construction paths explicitly, in code, before trusting a
predictive result — a strong effect size is not, by itself, evidence that
the effect is not a construction artifact.**
