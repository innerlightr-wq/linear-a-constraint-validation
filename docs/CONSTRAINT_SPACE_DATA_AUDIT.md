# Constraint-space data-reality audit (primary corpus, mwenge lineage)

**Phase 1 of the constraint-geometry research branch.** Determines what the
existing extracted corpus (`data/generated/lineara_extracted.json`, same
extraction used by the frozen H1 run, not regenerated) can actually
support, *before* any hypothesis is designed. No hypothesis outcome is
computed here. Labels: AVAILABLE, DERIVABLE, EXTERNAL DOMAIN MODEL INPUT,
AMBIGUOUS, OPEN, DOMAIN-EXPERT DEPENDENT.

## A. Numerical information

| item | status | basis |
|---|---|---|
| Integers | **AVAILABLE** | plain decimal-string tokens, already used by the frozen H1 adapter |
| Multi-sign integers | **AVAILABLE** | same mechanism; no upper bound observed on digit count |
| Fractional signs (identity) | **AVAILABLE** | Unicode fraction-glyph tokens adjacent to numerals (`lineara_adapter.py` N2) |
| Fractional numerical values | **EXTERNAL DOMAIN MODEL INPUT** | not encoded by the source; requires Corazza et al. (2021)'s published value table — already the case for the frozen H1 run, unchanged here |
| Integer + fraction combinations | **AVAILABLE** (identity), **EXTERNAL DOMAIN MODEL INPUT** (value) | same composite as above |
| Repeated quantities | **DERIVABLE** | computable by comparing numeral tokens within/across records; not a raw field, but mechanical, not requiring external interpretation |
| Zero | **OPEN, likely not directly relevant** | no zero-valued numeral token observed in this audit's sampling; Aegean numeral notation is additive/positive-only by established convention, so "zero" as a written value is not expected — this is a domain expectation, not confirmed by direct search this round |
| Numerical magnitude | **AVAILABLE** | direct integer value of decimal-string tokens |
| Numerical ordering | **DERIVABLE** | computable once magnitude is available |

## B. Metrological information

| item | status | basis |
|---|---|---|
| Metrological sign classes as a *separate* structural field | **NOT FOUND / OPEN** | no field distinct from (a) commodity ideogram identity and (b) fraction-sign identity was located |
| Units/subunits | **DERIVABLE, via EXTERNAL DOMAIN MODEL INPUT** | fraction-sign ligatures attached directly to commodity ideograms (e.g. `GRA+L4+L4`, directly observed on real record `HT15`) are the closest thing to an explicit "subunit" marker in the raw source; whether `L4` means "1/40 of the grain measure" specifically (as opposed to a generic fraction) is imported from Corazza et al., not read off the source |
| Liquid measures | **EXTERNAL DOMAIN MODEL INPUT** | inferred from commodity identity (`VIN`, `OLE`) via provisional Linear-B homology (see `docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md`), not a separately-encoded liquid-measure sign confirmed this round |
| Dry/grain measures | **EXTERNAL DOMAIN MODEL INPUT** | same reasoning, via `GRA`, `OLIV`, `HORD`-class ideograms |
| Weight measures | **OPEN** | not investigated this round in the primary corpus's own transliterations |
| Other measurement classes | **OPEN** | not investigated |

**The central finding of this section:** Linear A's raw transliteration
does **not** appear to carry an independent "metrological system" tag.
What looks like metrological information is, in this source, a
**composite** of (1) directly observed commodity-ideogram identity
(AVAILABLE) and (2) an externally-supplied scholarly convention mapping
that ideogram to a measurement system (EXTERNAL DOMAIN MODEL INPUT, resting
on provisional Linear-B homology — see Phase 2 audit). This composite
nature must be preserved explicitly in any constraint feature built from
it, never silently collapsed into a single "observed" field.

## C. Commodity information

Commodity ideograms **are** directly observable as recognizable,
standard Latin-mnemonic tokens in the raw transliteration — confirmed
directly in this round on real records: `GRA` (grain), `VIN` (wine), `OLE`
and its ligatured variants `OLE+U`/`OLE+A`/`OLE+E`/`OLE+KI`/`OLE+MI`/`OLE+DI`
(olive oil, variant forms), `OLIV` (olive), `VIR+KA` (personnel-related
composite), `CYP` and ligatured variants `CYP+D`/`CYP+E` (identity not
resolved this round — flagged **OPEN**, not guessed). **AVAILABLE** as raw
sign identity.

A bounded, imprecise composition scan (not a hypothesis test, not a
corpus-wide target-frequency statistic) found ~116 candidate all-uppercase
tokens; manual inspection shows most are false positives (short syllabic
transliterations that happen to render uppercase in isolated positions,
e.g. `KU`, `KA`, `SI` as headings), with a genuine commodity-ideogram core
of roughly 15–25 distinct types carrying double-digit-to-60+ occurrence
counts for the most common ones (`GRA`, `VIN`, `OLE` variants). This is
**enough raw material, in principle, for inter-record commodity-conditioned
hypotheses to have a plausible sample size** — a data-adequacy observation,
not a result.

**Commodity → semantic class (liquid/grain/personnel/etc.) is EXTERNAL
DOMAIN MODEL INPUT**, not raw corpus data. The source gives you the token
`GRA`; that this denotes "grain" is imported from a century of comparative
Linear B scholarship (see Phase 2 audit), applied to Linear A by
provisional homology, not independently established for Linear A's own
undeciphered language.

## D. Document structure

| item | status | basis |
|---|---|---|
| Line/group structure | **AMBIGUOUS** (already established, frozen H1 round) | `mwenge`'s `"\n"` tokens mark line breaks, already known (via the primary H1 adapter fix) to be more frequent than genuine section rulings — usable as a *weak* structural signal, not a validated ruling |
| Sign ordering | **AVAILABLE** | ordered token array, already used throughout |
| Numerical blocks | **DERIVABLE** | via the same Rule-A-style preceding-block logic already implemented (`kuro_protocol.preceding_block`), reusable without modification |
| Headings | **DERIVABLE, imprecisely** | a signgroup with no immediately-following numeral is plausibly a heading (matches the frozen protocol's own commodity-heading concept, `H1_PROTOCOL.md` §4 Rule B — still BLOCKED there, but the *concept* is reusable descriptively here without invoking Rule B's arithmetic role) |
| Commodity markers | **AVAILABLE** | per §C above |
| Subtotal candidates | **DERIVABLE, WITH AN EXPLICIT ANTI-CIRCULARITY WARNING** | a subtotal candidate can be *identified* structurally (a numeral immediately following a non-KU-RO signgroup, at a position preceding a later KU-RO/PO-TO-KU-RO) independent of whether it arithmetically closes — this independence must be preserved; see `docs/CONSTRAINT_NULL_MODELS.md` |
| Total candidates | **AVAILABLE** | `KU-RO`/`PO-TO-KU-RO` occurrences, already identified by the frozen adapter |
| Section boundaries | **AMBIGUOUS**, same as line/group structure | no signal beyond line breaks confirmed |
| Repeated templates | **OPEN, not surveyed this round** | plausible (administrative tablets are known to be formulaic per both papers' own framing) but not measured |

**Explicit refusal, per this round's own instruction:** this audit does
**not** reuse the already-known-unreliable SigLA sign-ordering heuristic,
and does **not** invent a new "reliable structure" for `mwenge` merely
because one would be convenient — every DERIVABLE label above names the
exact mechanical derivation involved, so a future test can be checked
against this document rather than trusting a black box.
