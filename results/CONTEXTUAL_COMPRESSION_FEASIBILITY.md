# Linear A contextual compression x geography — feasibility / identifiability round

**FEASIBILITY AUDIT ONLY. No hypothesis was tested. No model was fit. No
p-value was computed. No geography was attached to any record.** Full
task-by-task derivation: `docs/CONTEXTUAL_COMPRESSION_GEOGRAPHY_DESIGN.md`.
Computation: `src/contextual_compression_feasibility.py`
(`tests/test_contextual_compression_feasibility.py`, 23/23 passing; full
suite 352/352 passing, no regressions). Machine-readable audit:
`results/contextual_compression_feasibility.json`.

**Firewall, held throughout:** everything below is an **observable
inscriptional compression proxy** (sequence length, sign diversity,
repetition, predictability of the symbol stream). Linear A is undeciphered.
**Nothing here claims, or licenses a future claim of, semantic
compression.**

## A. Provenance

| | |
|---|---|
| Commit at start of round | `c351e2f189db69487e7ffbd9b70f4c58f343908f` |
| Git status at start | clean at HEAD except the same 24 pre-existing untracked design/audit/paused-SigLA files already disclosed in the prior recovery audit — untouched here |
| Corpus | `data/generated/lineara_extracted.json`, SHA-256 `219b52569cab75b58e95afb0a969689c6c50f753ce690321f20abbaff3a8eff8` — **identical file** to H1/V1/V2 (checksum-verified by `test_corpus_checksum_matches_v1_v2_provenance`), not re-extracted |
| Modified | none of: V1 result, V2 result, constraint-information-mechanism result, any frozen protocol/harness file, any SigLA file |
| New files | `docs/CONTEXTUAL_COMPRESSION_GEOGRAPHY_DESIGN.md`, `src/contextual_compression_feasibility.py`, `tests/test_contextual_compression_feasibility.py`, `results/CONTEXTUAL_COMPRESSION_FEASIBILITY.md`, `results/contextual_compression_feasibility.json` |
| Staged/committed | nothing — per instruction |

## B. Available corpus variables and usable N

N = 1721 inscriptions, all with a unique `name` (0 duplicates). Per-field
usable N (full table with basis: design doc §Task 1):

| field | class | usable N |
|---|---|---:|
| inscription ID | AVAILABLE | 1721 |
| site | AVAILABLE | 1718 (52 distinct) |
| object type (`support`) | AVAILABLE | 1721 (19 distinct) |
| sign sequence / sign count | AVAILABLE / DERIVABLE | 1706 non-empty / 1721 |
| numerals | AVAILABLE | 349 |
| fractions | DERIVABLE | see JSON `field_availability.fractions` |
| findspot / building-room | PARTIAL | 1063 (10 distinct) |
| chronology / period (`context`) | PARTIAL | 1390 (11 distinct, 94.2% one value) |
| scribal attribution | PARTIAL | 592 (102 distinct) |
| preservation/damage | DERIVABLE | see JSON |
| physical-artifact dependence | PARTIAL | 9 confirmed fragment joins |
| **administrative/ritual classification** | **NOT AVAILABLE** | **0** |
| **coordinates** | **NOT AVAILABLE** | **0** |
| **elevation** | **NOT AVAILABLE** | **0** |
| commodities | EXTERNAL DATA REQUIRED | 0 (unchanged from prior rounds) |
| repeated sign groups | PARTIAL, corpus-pooled only | 1706 |
| line count | PARTIAL (entry-count proxy only, not a validated physical line count) | 1590 |

## C. Defensible compression measures

Of 11 candidate proxies (full definitions/bias/CV analysis: design doc
§Task 2), only three are well-supported at this corpus's scale (median
sign count per inscription = **1**; mean 2.57; unigram/bigram/trigram
corpus-pooled hapax rates **74.0% / 91.9% / 98.0%**):

- **raw sign length** — AVAILABLE, trivially.
- **token-kind template structure** (SIGNGROUP/NUMERAL/FRACTION sequence,
  never sign identity) — AVAILABLE, and the cleanest fit for the
  decipherment firewall since it never touches sign meaning.
- **pre-declared occurrence counting** (as H1 already does) — AVAILABLE
  for specific, individually justified target strings only.

Diversity indices, n-gram repetition beyond corpus-pooled unigrams, edit
distance, and conditional/next-sign entropy are **not usable at the
individual-inscription level** — the median record is too short to carry
internal sequential structure, and even pooled bigram/trigram statistics
are almost entirely hapax.

## D. Context classification

**No independent administrative/ritual/palace/domestic/workshop/funerary
classification exists in this corpus.** The two available proxies
(`support`, `findspot`) cannot substitute for one without circularity (design
doc §Task 3): `support` is itself a candidate confound (H4), and `findspot`
has only 10 distinct values, 658/1721 records missing entirely. **A usable
classification would have to be imported from excavation literature, per
findspot label, before any inscription statistic is computed from the same
records** — not derivable from this repository.

## E. Geography feasibility

`site` (a clean, controlled place name, 52 values) is AVAILABLE.
**Coordinates and elevation are confirmed NOT AVAILABLE anywhere in this
corpus or any file this project has ingested.** Everything else geographic
(distance, terrain cost, maritime accessibility, connectivity) is
EXTERNAL DATA REQUIRED, and terrain-adjusted mobility cost additionally
requires a **chosen, disclosed model** — modern measurable geography is not
the same object as Bronze Age inferred mobility, and the two are never
equated in this document (design doc §Task 4). Practical geographic
coverage: only 5 sites have ≥30 records, 12 have ≥10 — the other 40 named
sites contribute identity, not statistical mass.

## F. Dependence structure

Verified directly against the real corpus (design doc §Task 5, `nesting_check`):
**scribe is perfectly nested within site** (0 violations, 102 scribes);
**findspot is perfectly nested within site** (0 violations, 10 values); 9
confirmed physical-fragment joins exist in the ID field itself; chronology
is nearly (I≈0.83) determined by site. **`site` is the correct primary
clustering/grouped-CV/permutation unit**; permutation must be conditional
(within-site or site-blocked), never marginal, per the elimination-asymmetry
mechanism already established in `results/CONSTRAINT_INFORMATION_MECHANISM.md`.

## G. Competing explanations

Measured, not assumed, confounding (design doc §Task 6, `mutual_information_categorical`):
`support`×`site` normalized I ≈ **0.44**; `scribe`×`support` normalized I ≈
**0.98**; `context`×`site` normalized I ≈ **0.83**. H4 (medium constraint)
and H5 (scribe effect) are directly measurable and already show real
entanglement with any geography signal. H2 (templating), H3 (genre), and
H6 (site convention) remain structurally inseparable from a geography
effect until Task D's classification problem is solved. H7 (corpus
construction/survival bias) is not auditable from inside this corpus at
all.

## H. Ranked candidate predictions

Full ranking and rationale: design doc §Task 7. Order: **P3 > P2 > P1 > P4
> P5 > P6**. P3 (within-site vs. between-site structural similarity) needs
no external data and no unresolved classification. **Designated future
primary hypotheses (at most two, per instruction): P3 and P4** — the two
rungs of the round's own generative chain answerable without first solving
context classification.

## I. Negative controls

For the P3/P4 design specifically (design doc §Task 10): site-label
shuffling within the matched set, geography permutation among matched
sites (primary control for P4), token-kind-sequence randomization
preserving length, and **mandatory** object-type-matched and
artifact/site-clustered permutation, given the measured H4 confound and
Task F's dependence structure. A naive unconditioned marginal shuffle is
explicitly rejected as invalid here.

## J. Power / effective sample

Design doc §Task 11 (all numbers computed, not assumed): 1718 site-labeled
inscriptions nominally span 52 sites, but site concentration (Herfindahl
index **0.439**) implies an **effective cluster count of roughly 2.3**;
even the generous ≥10-record threshold yields only **12** real clusters.
Haghia Triada alone is 64.6% of site-labeled records and is >99% one
chronological period. **P3 is powered, barely, at the site level for
length/template measures only. P4 is currently NOT powered** — it inherits
P3's thin clustering, adds a full external-data dependency, and adds
conditioning requirements (Task I) that a ~5-12-site design cannot
comfortably afford. **A null from P4 as currently scoped would not be a
useful finding.**

## K. Strongest identifiable claim

> **"Linear A inscriptions exhibit context- and geography-associated
> differences in observable sequence structure."**

This is the ceiling claim even if a future, correctly-designed P3/P4 test
succeeds — bounded to *observable* structure, *associated with* (not
*caused by*) context/geography jointly (since they are not yet separable
from medium/scribe/site-bureaucracy at this corpus's scale). See design
doc §Task 12 for the full adversarial audit against genre, tablet size,
chronology, scribal convention, site bureaucracy, sign inventory,
preservation, corpus construction, and transcription convention — none of
which this corpus can currently rule out.

## L. What cannot be inferred

- Semantic compression, shared meaning, or communicative efficiency of
  content (Linear A is undeciphered — firewall stated once, held
  throughout).
- Any causal claim (terrain → mobility → interaction → shared context →
  compression) — only the *final observable link* (context/geography ↔
  structure) is even prospectively testable with this corpus, and it is
  not tested this round.
- Any administrative/ritual/domestic function for a specific inscription,
  room, or site — no such classification exists in this corpus (§D).
- Any Bronze-Age-specific mobility or interaction-frequency fact from
  modern geographic data alone (§E) — terrain cost is never treated as
  equivalent to interaction frequency.
- Scribal cognition, intent, or individual economizing behavior.
- Generalization beyond this specific, already-disclosed corpus
  (`lineara.xyz` snapshot, `docs/CORPUS_PROVENANCE.md`) — transcription
  convention itself is an unruled-out confound (§G, design doc §Task 12).

## M. Preregistration gate

**UNDERPOWERED.**

Not READY (context classification unsolved, effective site clusters ≈2.3-12,
Task 9's conditioning requirement not affordable at that scale); not READY
WITH EXTERNAL DATA (external geography does not fix the site-count
scarcity, which is intrinsic to this corpus's own concentration); not NOT
IDENTIFIABLE (P3 specifically is identifiable in principle — design doc
§Task 8); not HYPOTHESIS FAILS CONCEPTUALLY (the generative chain is
coherent; the corpus is not yet adequate to test even its cleanest
component with real power). This gate does not favor READY: every
precondition withheld above was derived from this audit, not asserted.

## N. Final recommendation

**The single cleanest prospective experiment this corpus can support is
P3: a matched within-site vs. between-site structural-similarity
comparison, using token-kind template structure and/or raw sign length as
the similarity measure, restricted to the 12 sites with ≥10 records,
stratified/matched on object type (`support`) and scribe where available,
with permutation and cross-validation conditioned on site.** It requires
no external data, uses only fields already confirmed AVAILABLE or
DERIVABLE (§B), and has a well-defined null and falsification condition
(design doc §Task 8/10). It is **not** currently at READY — the
context-classification and effective-N gaps in §D/§J must be resolved or
explicitly re-scoped (e.g. restricting to the ≥30-record sites only, or
formally declaring `support` as the primary stratifying covariate instead
of an unsolved context label) before any prospective test of it should be
pre-registered. **P4 (geography/terrain cost) should not be attempted as
an independent test until P3 itself is adequately powered and its
external-geography dependency (§E) is resolved** — attempting P4 first
would compound two unresolved problems (site-count scarcity and unattached
geography) into one under-identified test.

**This is the end of the feasibility round. No hypothesis test was
executed.**
