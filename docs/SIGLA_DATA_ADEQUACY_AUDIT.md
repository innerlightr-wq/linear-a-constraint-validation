# SigLA data adequacy audit

Covers Phase 3 (adequacy classification), Phase 6 (cross-corpus document-ID
audit), Phase 7 (replication adequacy decision), and Phase 8 (adversarial
pre-result audit) together, since they are tightly coupled decisions about
the same evidence. **No H1 statistic (KU-RO occurrence rate, terminal rate,
arithmetic closure rate, mismatch rate, or verdict) is computed anywhere in
this document.**

## Phase 3 — Adequacy classification summary

| field | classification |
|---|---|
| Tablet/document ID | AVAILABLE — ENGINEERING VERIFIED against real data (`iter_documents`) |
| Site/archive | AVAILABLE — ENGINEERING VERIFIED against real data, after fixing a real `option`-wrapper bug found this round (see Schema Resolution Addendum below) |
| Sign-group ordering | **AMBIGUOUS** — downgraded from AVAILABLE. The only implemented extraction method was tested against real document `HT 13` and demonstrably returns spurious/duplicated entries (129 "entries" for a ~15-syllable tablet). Not ENGINEERING VERIFIED. |
| KU-RO / KI-RO / PO-TO-KU-RO | **AMBIGUOUS** — downgraded from DERIVABLE for the same reason: target detection depends on a faithful ordered sign sequence, which is not currently available. Individual syllables are confirmed present (SOURCE-DERIVED FACT); their true order and word-grouping are not. |
| Numerals | OPEN |
| Fractions | AMBIGUOUS |
| Fraction certainty | AMBIGUOUS |
| Damaged readings | AMBIGUOUS |
| Uncertain readings | AMBIGUOUS |
| Line/ruling boundaries | OPEN |
| Section boundaries | OPEN |
| Commodity headings | OPEN, DELIBERATELY NOT PURSUED (Rule B scope) |
| Reading certainty (general) | AMBIGUOUS |
| Duplicate/reconstructed readings | DOMAIN-EXPERT DEPENDENT |

Full per-field reasoning: `docs/SIGLA_SCHEMA_MAPPING.md`.

## Schema Resolution Addendum (Tasks 1–7, real-document validation round)

Built `src/explore_sigla_schema.py` (Task 1): a bounded explorer requiring
explicit tablet IDs (or explicit sign numbers), with **no corpus-wide mode
by design**. Used it, plus targeted scratch scripts, to inspect **`HT 13`**
— chosen and recorded *before* inspection because it is Paper 1's own cited
worked arithmetic example, appears as a genuine EXACT_CLOSURE case in the
primary mwenge H1 result, and is known to contain both numerals and
fractions adjacent to a KU-RO occurrence.

**Task 2 — numeral encoding: OPEN, unresolved.** No numeral-value field was
located in any record inspected this round. Short uppercase-letter strings
observed near sign entries (`"E"`, `"F"`, `"A"`) are suspected to be
GORILA's own fraction/simple-sign class prefixes (Paper 1's Table 1 lists
`E=1/4`, `F=1/8`) rather than numerals — a plausible lead, not confirmed.
No cross-check against SigLA's own documentation for a numeral-specific
field was completed this round.

**Task 3 — fraction encoding: OPEN, unresolved beyond FRACTION TYPE
SUSPECTED.** SigLA's own paper confirms fractions are a distinctly
color-coded sign-function category (SOURCE-DERIVED FACT, prior round). No
specific field encoding a numeric fraction *value* was located this round.
**FRACTION TYPE KNOWN** (conceptually, from the paper) is not the same claim
as **NUMERIC FRACTION VALUE KNOWN** or **FRACTION CONFIDENCE KNOWN** —
neither of the latter two is established. If a numeric value is ever
needed, it would most likely have to come from **EXTERNAL DOMAIN MODEL
INPUT** (a Corazza-et-al.-style lookup, as `mwenge`'s adapter already
documents needing) rather than from SigLA's own data directly — not
confirmed, but flagged now so it is not silently assumed either way later.

**Task 4 — word boundaries: TARGET RECONSTRUCTION AMBIGUOUS.** The sliding-
window target detector (`detect_targets`) is itself correctly unit-tested
against synthetic input, but its **real input**
(`extract_ordered_signs`/`_collect_indexed_entries`) was tested directly
against `HT 13` and found to return 129 spurious entries for a ~15-syllable
tablet — duplicated indices (index 1 repeated 44 times) and implausible
outliers (704, 705) consistent with the heuristic matching unrelated
substructure (most likely pixel bounding-box coordinates) rather than the
true sign-attestation array specifically. **Per this round's own explicit
instruction, this is exactly the condition that requires marking TARGET
RECONSTRUCTION AMBIGUOUS and stopping before H1** — done here. No explicit
word-group identifier was confirmed reachable by a validated path this
round; whether one exists and simply wasn't found is itself OPEN.

**Task 5 — Rule-A boundaries: NOT YET FAITHFULLY REPRODUCIBLE.** No line
number, explicit ruling metadata, section identifier, or prior-total marker
was found in any inspected record. The only positional signal confirmed
present is pixel bounding-box coordinates (`[x,y,w,h]`) per sign. Turning
these into a section boundary would require choosing a geometric distance
or alignment threshold **from the observed corpus itself** — exactly the
"new corpus-specific analysis rule" this round's instructions explicitly
prohibit inventing. No external/source-defined structural rule supplying
such a threshold was found. Classified NOT YET FAITHFULLY REPRODUCIBLE, as
instructed.

**Task 6 — target reconstruction validation, real bug found and fixed:**
`iter_documents` was found, via direct testing against `HT 13`, to
incorrectly treat each document's raw Map value as the 5-field document
tuple directly. Real data shows the Map value is `Some(doc_tuple)` — one
extra `option` layer. **This was masked by this project's own earlier
synthetic tests**, whose fixtures modeled the already-unwrapped shape.
Fixed in `src/sigla_adapter.py`; `tests/test_sigla_adapter.py` fixtures
corrected to match (all 100 tests still pass). Site/period extraction now
**ENGINEERING VERIFIED** against real data (`HT 13` → site `"Haghia
Triada"`, period `"LM IB"`, both exactly matching the raw structure). This
validation exercise is exactly what surfaced the Task 4 finding above —
the adapter's target-reconstruction *output* was checked against real
structure, not merely against its own synthetic model, and found wanting.

**Task 7 — cross-corpus structural spot check (`HT 13`, both sources):**
Document identity: `mwenge` `"HT13"` vs. SigLA `"HT 13"` (space
difference, already known). Numeral representation: **structurally
different in kind** — `mwenge` stores numerals as adjacent array elements
directly readable as decimal strings; SigLA's numeral representation is
OPEN (Task 2). Fraction representation: `mwenge` uses adjacent Unicode
fraction-glyph tokens; SigLA's is OPEN/suspected-class-prefix (Task 3), a
materially different mechanism if the class-prefix hypothesis holds.
Damage/uncertainty: `mwenge` uses embedded bracket/`?` characters; SigLA's
paper describes a distinct question-mark-plus-erasure-category convention,
not yet mapped to fields. **No arithmetic comparison was made** — this
spot check is representation-only, per this round's explicit instruction.

## Phase 6 — Cross-corpus document-ID audit

**NEW EMPIRICAL RESULT** (corpus coverage metadata, explicitly not an H1
outcome, per this project's own instructions):

| | count |
|---|---|
| Document IDs in `mwenge` (primary corpus) | **1721** |
| Document IDs in SigLA | **802** |
| Intersection (whitespace-insensitive, case-insensitive normalization) | **697** |
| `mwenge`-only | **1024** |
| SigLA-only | **105** |

**Document-ID normalization rule used, stated explicitly:** strip all
whitespace, uppercase, compare. This is a *loose* normalization sufficient
for a first-pass count, not a validated one-to-one mapping — spot-checking
the non-overlapping sets surfaced real, unresolved formatting differences:

- `mwenge` uses compound-join notation for reconstructed tablets (e.g.
  `"HT123+124a"`); SigLA, in a spot check, appears to carry `"HT 123a"` and
  `"HT 124a"` as **separate** keys rather than a joined one. Whether these
  represent the same underlying archaeological join decision is
  **DOMAIN-EXPERT DEPENDENT**, not resolved here.
- SigLA document IDs were observed to include **Greek-letter face
  labels** (e.g. `"HTWA1019Α"` using Greek capital alpha Α, not Latin A) for
  a `"WA"`-prefixed document class not seen in this project's `mwenge`
  sampling — a genuine notational difference, not a normalization bug to
  paper over.
- `mwenge`-only IDs sampled (`ANZB1`, `APZA1`, `ARGZG1`, `ARKHZC8`, ...) are
  overwhelmingly from **non-Haghia-Triada, non-administrative-looking**
  document classes.

**Why the intersection is well under either total's full size, explained
by direct source evidence, not guessed:** the SigLA paper itself states
(`docs/SIGLA_PROVENANCE_AUDIT.md` item 4, directly quoted): *"At present the
database only contains administrative documents, more precisely, the
Linear A tablets found at the most prominent sites on Crete... the
long-term plan is to implement the database by adding all inscriptions
recovered so far."* `mwenge`'s corpus (1721 records) is not scoped this way
— it includes non-administrative supports (e.g. libation/religious
inscriptions, roundels, sealings) that SigLA's current release deliberately
excludes. **This is a genuine, source-confirmed scope difference between
the two corpora, not a data-quality problem in either.**

## Phase 7 — Replication adequacy decision (SUPERSEDED — see Gates below)

**Original decision (prior round, before real-document validation): GO WITH
DOCUMENTED CORPUS LIMITATIONS.** That decision was made before any real
SigLA document had been tested end-to-end and rested on an untested
assumption that target reconstruction was merely "more complex," not
unreliable. Real-document validation (Schema Resolution Addendum, above)
has since shown the ordered-sign-sequence extraction it depended on is
demonstrably unreliable. **This decision is superseded by the formal Gate
evaluation below (Task 9); do not act on the "GO" line above.**

Per this project's own terminology guidance and the Phase 1 classification
(**B — partially independent digitization/re-examination**), any *eventual*
H1 run on SigLA — once the Gates below are resolved — should still be
reported as a **CROSS-TRANSCRIPTION REPLICATION**, not an independent
replication in the strongest sense — both corpora share GORILA as their
textual root. This framing is unaffected by the Gate outcome; it concerns
interpretation once/if a run occurs, not whether one is currently
authorized.

## Task 9 — GO/NO-GO Gates

| Gate | Question | Result | Basis |
|---|---|---|---|
| **A — Target reconstruction** | Can KU-RO/KI-RO/PO-TO-KU-RO be reconstructed without cross-boundary false positives? | **FAIL** | `_collect_indexed_entries` demonstrated to return 129 spurious/duplicated entries for a 15-syllable real tablet (`HT 13`) — concrete evidence of exactly the cross-boundary/false-positive risk this gate asks about, not merely an untested concern |
| **B — Numeral reconstruction** | Can numeric values be reconstructed without an undeclared model? | **OPEN** | No numeral-value field was located in any record inspected this round; not shown possible, not shown impossible |
| **C — Fraction handling** | Can the frozen protocol's fraction behavior be reproduced faithfully? | **OPEN** | Fraction *type* is plausibly identifiable (suspected class-prefix signal); numeric *value* and *confidence* are neither confirmed available nor confirmed absent |
| **D — Rule-A sectioning** | Can the preceding arithmetic block be reconstructed per the frozen Rule-A concept without inventing a new corpus-tuned boundary rule? | **FAIL** | No ruling/line/section signal found; the only positional signal (pixel bounding boxes) would require an invented geometric threshold, explicitly disallowed by this round's own instructions |

**A = FAIL, B = OPEN, C = OPEN, D = FAIL.** Per this round's own explicit
authorization rule (all four gates must be PASS), a strict SigLA H1 run is
**NOT AUTHORIZED**.

## Phase 8 — Adversarial pre-result audit

- **Are both corpora ultimately derived from the same GORILA readings?**
  Yes — established directly in `docs/SIGLA_PROVENANCE_AUDIT.md` items 4–6.
  This is the single most important caveat for interpreting any eventual
  agreement *or* disagreement between the two corpora's H1 results.
- **Does SigLA correct readings independently?** Partially — genuine
  redrawing and sign-by-sign re-classification occurred (not a fresh
  primary reading of the physical tablets); see provenance audit item 7.
- **Are tablet IDs normalized differently?** Yes, confirmed directly (space
  vs. no-space, compound-join vs. split, Greek-letter face labels) — see
  Phase 6 above.
- **Does one source split tablets differently?** Possibly — the
  `HT123+124a` vs. `HT 123a`/`HT 124a` case is a concrete, unresolved
  example.
- **Does one source merge lines or sections differently?** OPEN — SigLA's
  positional signal (pixel bounding boxes) is structurally different from
  `mwenge`'s line-break tokens; no equivalence has been established.
- **Are fractions encoded differently?** Confirmed materially different in
  kind: `mwenge` encodes fraction glyphs as extra array elements adjacent
  to a numeral (this project's own N2 rule); SigLA's fraction representation
  is not yet confirmed at the field level (AMBIGUOUS, above).
- **Are damaged readings handled differently?** `mwenge` uses embedded
  bracket/`?` characters within word strings; SigLA uses a described
  question-mark convention plus a separate erasure category — likely
  richer, but not yet mapped to specific fields.
- **Does SigLA contain more or fewer documents?** Fewer (802 vs. 1721),
  explained by its administrative-only current scope (Phase 6, above), not
  by missing/incomplete retrieval.
- **Are commodity ideograms represented differently?** Not investigated
  (Rule B explicitly out of scope this round, per instruction).
- **Could line-boundary encoding alone change terminal classification?**
  This is exactly the failure mode that required a real adapter fix in the
  primary-corpus run (`\n` wrongly mapped to a ruling boundary). SigLA has
  **no line-break token at all** in the structures inspected — position is
  conveyed by array index and pixel bounding box instead — meaning the
  primary corpus's specific bug **cannot recur in the same form**, but a
  **different, SigLA-specific positional-mapping bug is entirely possible**
  and has not yet been ruled out, since the terminal/near-terminal/
  non-terminal classification (`H1_PROTOCOL.md` §2) depends only on
  sign-group order, which is confirmed available, but was not exercised
  end-to-end against real data this round (Phase 9 forbids this).
- **Could numeral parsing differences alone change arithmetic closure?**
  Numerals are OPEN (not yet located in this source) — this is the single
  largest open risk for any future SigLA arithmetic result; it cannot yet
  be assessed.
- **Are there duplicated readings or alternate reconstructions?** Not
  confirmed present or absent; flagged DOMAIN-EXPERT DEPENDENT above.

**Strongest concern overall:** both corpora share GORILA as their common
textual ancestor, so a future SigLA H1 result that *agrees* with the
primary-corpus FAILURE would not constitute two independent confirmations
of the same underlying fact about Linear A — it could equally reflect a
shared upstream reading. A *disagreement* would be more informative (it
would show the result is sensitive to transcription/classification choices
downstream of GORILA), but even then, this project cannot attribute a
disagreement to "SigLA is right" or "`mwenge` is right" without
domain-expert adjudication.
