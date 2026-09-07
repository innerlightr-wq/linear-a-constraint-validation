# Constraint null models, positive/negative controls

**Phase 7–8 of the constraint-geometry research branch.** Predeclared
*before* any headline outcome is computed for any constraint hypothesis
(none has been, this round). No null model here has been run against real
data; this document defines what each would preserve and destroy, and why
that matters, per this round's own explicit warning against trivial nulls
that destroy everything and therefore guarantee an apparently-structured
result.

## Predeclared null models

| null | preserves | destroys | intended use |
|---|---|---|---|
| **NULL 1 — quantity shuffle** | record structure, entry count per record, commodity/position labels, marginal distribution of all numeral values corpus-wide | the pairing between a specific quantity and its specific record/commodity/position | tests whether numeral magnitude is conditioned on commodity/site/position, without changing what magnitudes exist at all |
| **NULL 2 — fraction-assignment shuffle** | fraction-sign *locations* (which numerals carry a fraction glyph at all, and how many), commodity/site context | which specific fraction-value is assigned to which located fraction sign | tests whether the *accepted* Corazza-et-al. mapping participates in arithmetic closure more than an equally-plausible relabeling would — directly answers Phase 4B |
| **NULL 3 — commodity-label shuffle within strata** | site, document type, and numeral/fraction content of each record | the specific commodity label attached to a record, *shuffled only within the same site/document-type stratum* (not corpus-wide) | tests commodity-conditioned hypotheses (Phase 5A–C) without also destroying genuine site-level structure, which would bias toward false rejection |
| **NULL 4 — local position shuffle** | record length, sign inventory (multiset of signs used), numeral/fraction values present | the specific order/position of signs within a record | tests positional hypotheses (Phase 4D, C_POS) |
| **NULL 5 — mass-preserving, relation-destroying** | each record's own total numeral mass (sum of its numeral values) | the specific decomposition of that mass into individual entries | tests whether *local arithmetic relationships* (not just aggregate mass) carry structure beyond what total mass alone would predict |

**Every null above is explicitly a *within-stratum* or *value-preserving*
shuffle, never a full randomization of the corpus.** This is deliberate,
per this round's own instruction: a null that destroys all structure
trivially guarantees the real corpus looks more structured than the null,
which would be a meaningless, foregone result, not a test.

## Positive controls

The strongest available positive control, per the Phase 2 scholarship
audit: **commodity class → metrological/measurement-system association**
(item 8, `docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md`) — well-supported
enough in the wider literature (via provisional Linear-B homology) that a
constraint-detection framework which *cannot* recover a
liquid-vs-dry-commodity distinction in fraction/quantity patterning would
itself be evidence against this project's own methodology, not against the
constraint hypothesis. **This must be run, if any test is run, and its
failure must be treated as a methodology red flag, not quietly dropped.**

A second, more specific positive-control candidate: the `HT 122`
`ku-ro`+`ku-ro`=`po-to-ku-ro` nested-arithmetic example (item 10 of the
scholarship audit) — though this project's own independent extraction
already shows a discrepancy with the popular framing of that example,
itself worth resolving before leaning on it as a clean control.

## Negative controls

Constructed by deliberately breaking a known relationship while preserving
basic marginals — e.g., for the commodity×metrology positive control: keep
every quantity and fraction exactly where it is, but relabel which
commodity class it is nominally attached to (this is exactly NULL 3 applied
as an adversarial rather than a null-hypothesis tool) and confirm the
recovered association degrades. **Not run this round** — recorded here as
the predeclared design, per this round's explicit "do not yet compute
outcomes" instruction.

## Anti-circularity checklist (applied per-hypothesis in `docs/CONSTRAINT_HYPOTHESIS_CANDIDATES.md`)

For every candidate hypothesis, before any test is run:

1. Was the structural category defined before examining the numerical relationship?
2. Was a total identified independently of arithmetic success?
3. Was commodity identity assigned independently of the numerical pattern being tested?
4. Was the fraction mapping imported from prior scholarship rather than fitted to maximize closure?
5. Was the null model defined before seeing the result?
6. Are multiple observations from the same tablet being treated as independent?
7. Are recto/verso faces or joined fragments creating pseudo-replication?
8. Is Haghia Triada dominating the apparent relationship?

Any hypothesis failing (1)–(5) structurally, or not accounting for (6)–(8)
using the already-established Level 2/3 machinery from
`docs/EVIDENCE_DEPENDENCE_PROTOCOL.md`, is labeled **CIRCULAR — NOT
EVIDENCE** and excluded from the shortlist.
