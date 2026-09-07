# Contextual compression x geography — feasibility / identifiability round

**Status: FEASIBILITY AUDIT ONLY. No hypothesis test was run. No model was
fit. No p-value was computed. No geography was attached to any record (none
exists in this corpus — see Task 4).** This document supports
`results/CONTEXTUAL_COMPRESSION_FEASIBILITY.md` (the final report) and is
backed entirely by `src/contextual_compression_feasibility.py` /
`tests/test_contextual_compression_feasibility.py`, run against the same,
unmodified `data/generated/lineara_extracted.json` used by H1/V1/V2 (SHA-256
`219b52569cab75b58e95afb0a969689c6c50f753ce690321f20abbaff3a8eff8`, verified
by `test_corpus_checksum_matches_v1_v2_provenance`). Does not touch, modify,
or reinterpret the frozen V1, V2, H1, or constraint-information-mechanism
results. Does not resume the paused SigLA thread.

**Governing distinction, stated once and held throughout:** everything
measured below is an **observable inscriptional compression proxy** —
sequence length, sign diversity, repetition, predictability of the *symbol
stream*. Linear A is undeciphered. **None of it is, or licenses, a claim
about semantic compression** (shared meaning, communicative efficiency of
content, scribal cognition). Where a measure could be misread as touching
meaning (e.g. "template similarity"), it is defined here strictly in terms
of token *kind* (signgroup/numeral/fraction) or literal transliteration
string, never gloss.

---

## TASK 1 — Corpus audit

Computed by `field_availability_audit()`, verified against real counts by
`tests/test_contextual_compression_feasibility.py`. Source: the same
`transliteratedWords`/`site`/`findspot`/`scribe`/`context`/`support`/`name`
fields documented in `docs/SCHEMA_MAPPING.md` — no new field, no new source
file, no re-extraction.

| requested field | classification | usable N | note |
|---|---|---:|---|
| inscription ID | AVAILABLE | 1721 | `name`, unique (0 duplicates confirmed) |
| site | AVAILABLE | 1718 | `site`, 52 distinct values |
| object/tablet ID | AVAILABLE | 1721 | same key as inscription ID — this corpus has no separate record-vs-physical-object identifier |
| archaeological context (period) | PARTIAL | 1390 | `context` is a **chronological period** label (e.g. `LMIB`), not a function classification |
| administrative/ritual classification | **NOT AVAILABLE** | 0 | no field encodes archaeological function anywhere in this corpus |
| building/room context | PARTIAL | 1063 | `findspot`, free text, only 10 distinct values corpus-wide |
| object type | AVAILABLE | 1721 | `support` (physical medium), 19 distinct values |
| sign sequence | AVAILABLE | 1706 | `transliteratedWords` filtered to signgroup tokens (15 records have zero signgroup tokens) |
| sign count | DERIVABLE | 1721 | `len(signgroups)` per record |
| line count | PARTIAL | 1590 | raw `"\n"` markers exist, but `docs/SCHEMA_MAPPING.md`'s own N1 finding is that this source places `"\n"` between **every entry**, not only true physical line breaks — usable only as an entry-count proxy, never presented as a clean physical line count |
| numerals | AVAILABLE | 349 | plain decimal tokens, same extraction as H1/V1/V2 |
| fractions | DERIVABLE | (see below) | same N2 merge rule as H1/V1/V2; confidence grading remains MISSING (unchanged finding) |
| commodities | **EXTERNAL DATA REQUIRED** | 0 | unchanged from `docs/CONSTRAINT_SPACE_DATA_AUDIT.md`/`docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md` — commodity identity requires a Linear B homology model, not recomputed here |
| repeated sign groups | PARTIAL | 1706 (corpus-pooled only) | computable corpus-wide (§Task 2 item 4/5); **not** meaningfully computable within most individual records given median sign count = 1 |
| findspot | PARTIAL | 1063 | same field as building/room context |
| coordinates | **NOT AVAILABLE** | 0 | no lat/long field anywhere in this corpus or any file this project has ingested (repo-wide search confirmed) |
| elevation | **NOT AVAILABLE** | 0 | same as coordinates |
| chronology | PARTIAL | 1390 | same field as archaeological context, reused for temporal ordering; 11 distinct period labels, 94.2% of non-null values are `LMIB` |
| preservation/damaged signs | DERIVABLE | (see below) | bracket/`?` convention, same as H1's adapter — undifferentiated between physical damage and disputed reading |
| physical-artifact dependence | PARTIAL | 9 | 9 `name` values are explicit fragment joins (e.g. `HT123+124a`, `HT42+59`); undisclosed joins in the remaining 1712 cannot be ruled out without external epigraphic literature |
| possible scribal attribution | PARTIAL | 592 | `scribe`, 102 distinct values, always nested within exactly one site (§Task 5) |

No missing metadata was inferred anywhere in this table — every "0" or
"NOT AVAILABLE" is a confirmed absence, not an unchecked gap.

---

## TASK 2 — Compression measures

No measure below is combined into a single score. Corpus-support numbers
come from `corpus_ngram_feasibility()` run on the **entire pooled corpus**
(not per-record): total signgroup token occurrences = 4429; distinct
unigram types = 1313 (**74.0% hapax**); distinct bigram types = 2257 out of
2723 occurrences (**91.9% hapax**); distinct trigram types = 2129 out of
2200 occurrences (**98.0% hapax**). These are corpus-pooled, ignoring
record boundaries — the sparsity is a property of the whole 1721-record
corpus, not an artifact of small per-record counts.

Median per-record sign count = **1**; mean = 2.57; 15/1721 records have
zero signgroup tokens; only 94/1721 have ≥10.

| # | measure | definition | min sample req. | small-sample bias | CV needed? | measures | corpus support |
|---|---|---|---|---|---|---|---|
| 1 | raw sign length | `len(signgroups)` | none (direct count) | negligible per se | No (descriptive) — Yes if used as a fitted predictor | length only, not predictability | **AVAILABLE**, trivially |
| 2 | distinct-sign count | `|set(signgroups)|` | none | mechanically bounded by length (can't exceed it) — confounds with #1 unless jointly modeled | No / Yes as above | length-bounded diversity, not normalized diversity | AVAILABLE but **not interpretable alone** — always report with length |
| 3 | normalized sign diversity (e.g. type-token ratio, Herdan's C) | distinct/length or a size-corrected index | tens of tokens per unit for stability | **severe** at this corpus's scale — TTR is degenerate (≈1.0) for any record at or near the median length of 1 | Yes, if compared across groups of unequal size | diversity, but conflated with length unless corrected | **NOT AVAILABLE at the individual-inscription level**; DERIVABLE only pooling many records per group (site/support) |
| 4 | repeated unigram structure | frequency table over pooled signgroup tokens | corpus-wide pooling only | high — 74% of types are hapax even pooled corpus-wide | Yes, if used predictively (train/test frequency leakage) | crude formulaicity | **PARTIAL** — usable only pooled, with heavy smoothing, never per-record |
| 5 | repeated bigram/trigram structure | frequency table over adjacent signgroup pairs/triples | far larger corpus than this one | **severe** — 92%/98% hapax even pooled corpus-wide | Yes | formulaicity | **NOT AVAILABLE reliably** at any grouping finer than the whole corpus, and marginal even there |
| 6 | repeated sign-group structure (specific, pre-declared groups) | occurrence counting of one declared target string (as H1 already does for KU-RO etc.) | depends on the specific group's base rate | same as H1's own documented N-adequacy concerns | No (counting), Yes if used inferentially | targeted formulaicity | **AVAILABLE**, but only for individually pre-declared, high-frequency strings — not a general "any repetition" scan |
| 7 | prefix/suffix reuse | shared leading/trailing substrings of transliteration strings | moderate | signgroup identity here is a transliterated string, not a validated morpheme boundary | Yes if used predictively | **string**-level reuse only — must never be presented as morphology, since Linear A is undeciphered | DERIVABLE as a literal string statistic; **interpretively must be labeled non-linguistic** |
| 8 | template similarity | sequence of **token kinds** (SIGNGROUP/NUMERAL/FRACTION), not sign identity | moderate | length-normalization needed | Yes | structural formulaicity, decipherment-free by construction | **AVAILABLE** and the most promising measure for the semantic firewall specifically, since it never touches sign identity or gloss |
| 9 | normalized edit distance | Levenshtein/length between two token sequences | pairs of comparable records | **severe** here: two records of length 1 differ by edit distance 0 or 1 only — almost no continuous signal at this corpus's median length | Not itself, but pair-selection must be principled (§Task 8) | pairwise similarity | mathematically well-defined and DERIVABLE, but **its dynamic range is crippled by median length 1** |
| 10 | conditional sign entropy | H(sign_t \| preceding signs) | many transitions per context | at median length 1 there are **zero within-record transitions** for at least half the corpus | Yes | predictability of the immediate next symbol | **NOT AVAILABLE within-record** for most of the corpus; only a heavily pooled, order-0 (no real conditioning) estimate is feasible corpus-wide |
| 11 | out-of-sample next-sign log loss | held-out ΔH via a trained sequence model, exactly the V1/V2/mechanism-round methodology | grouped CV, adequate positives/tokens per fold | this is precisely the discipline V1/V2 already built | **Yes, mandatory** — this project's own established practice | held-out predictability, the most rigorous of the eleven | **feasible only pooled at the whole-corpus level**; any per-context or per-site partition starves it, since the outcome variable here (the sign stream itself) is far sparser than V1/V2's binary fraction-presence target |
| 12 | corpus-level MDL/description-length proxy | compressed-size / token-count of a (sub)corpus | thousands of tokens per subcorpus for compressor overhead to amortize | **severe** below that scale | No (descriptive), but comparisons across groups need matched-size correction | overall formulaic redundancy of a corpus/subcorpus | **feasible only at the whole-corpus level or the 2-3 largest sites** (Haghia Triada 1110, Khania 226 records); NOT AVAILABLE for the other ~49 sites individually |

**Overall Task 2 conclusion:** length (#1), token-kind template structure
(#8), and pre-declared occurrence counting (#6) are the only measures that
are both well-supported by this corpus's scale and free of the small-sample
degeneracy that afflicts diversity, n-gram, edit-distance, and entropy
measures at the individual-inscription level. Anything requiring
within-record sequential structure is not viable given a median sign count
of 1.

---

## TASK 3 — Context classification

**No independent archaeological function classification (administrative /
ritual / palace / domestic / workshop / funerary / uncertain) exists in this
corpus as a field.** `field_availability_audit()` confirms this directly
(`administrative_ritual_classification`: NOT AVAILABLE, usable N = 0).

The two closest proxies, and why neither may be used as a substitute
without violating this round's own instruction ("must not depend on the
inscription statistics being tested; do not classify something as
administrative because it is short or repetitive"):

- **`support` (object type/medium):** 19 values, dominated by Nodule (890),
  Tablet (435), Roundel (151). Nodules and roundels are conventionally
  associated with administrative sealing practice in Aegean archaeology —
  but that association is itself an *archaeological* classification
  imported from outside this corpus (site-report literature), not a
  property this repository can certify. Using `support` as if it *were*
  a context label would silently substitute a medium proxy for a function
  classification — exactly the circularity risk this task warns against,
  since medium is also one of the measures directly implicated in H4
  (medium constraint, Task 6).
- **`findspot` (room/building label):** only 10 distinct values, 863 of
  1063 non-null records concentrated in one label (`Portico 11 and Room
  13`, Haghia Triada). A genuine administrative/domestic/ritual reading of
  a named room (e.g. "Portico 11 and Room 13" as an archive context) would
  require importing the excavation report for each of the 10 labels — an
  EXTERNAL DATA dependency, not something derivable from this repository.

**Conclusion:** any context classification usable for this research
thread must be **imported from published excavation/architectural
literature, per findspot label, before any inscription statistic is
computed from the same records** — exactly the discipline this project
already applies to commodity identity (`LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md`)
and to fraction confidence grading. Class counts cannot be reported this
round because the classification itself does not yet exist. This is a
**genuine, disclosed gap**, not a rounding error: at most 10 findspot
labels (concentrated at 2-3 sites) could ever receive an externally-sourced
context label, meaning even a successful external-literature pass would
leave the great majority of the corpus (which has no `findspot` value at
all — 658/1721) permanently unclassifiable for context.

---

## TASK 4 — Geography

`field_availability_audit()`: `coordinates` and `elevation` are both **NOT
AVAILABLE** — confirmed absent by direct repo-wide search, not merely
unchecked. What IS available is `site`, a controlled-vocabulary place name
(52 distinct values), which is a **necessary but not sufficient**
prerequisite for attaching geography: a place name can in principle be
matched to a published gazetteer entry, but that match, and everything
built on it, would be entirely **external to this corpus**.

| geography item | status |
|---|---|
| latitude/longitude | NOT AVAILABLE in-corpus; ATTACHABLE via EXTERNAL gazetteer, by site name |
| elevation | NOT AVAILABLE in-corpus; ATTACHABLE via EXTERNAL source, by site name |
| straight-line distance | DERIVABLE, but only *after* external coordinates are attached |
| slope/elevation gain | EXTERNAL DATA REQUIRED (a modern DEM/terrain model), and even then a MODERN one |
| terrain-adjusted travel cost | EXTERNAL DATA REQUIRED, and requires a **chosen mobility model** (e.g. Tobler's hiking function, least-cost-path over a modern DEM) — a modeling choice, not a fact |
| maritime accessibility | EXTERNAL DATA REQUIRED — some of the 52 site names are island sites (Thera, Kea, Kythera, Milos) or coastal, which changes the relevant cost model entirely (sea vs. land) |
| island/mainland status | DERIVABLE once site identity is resolved against a gazetteer, but not from this corpus alone |
| mountain/pass structure | EXTERNAL DATA REQUIRED |
| site connectivity | EXTERNAL DATA REQUIRED, and definitionally Bronze-Age-specific (road/path network), which no modern dataset directly provides |

**The critical distinction this task demands, stated explicitly:**
*modern measurable geography* (coordinates, modern elevation, modern
terrain, modern coastline) is attachable from external, non-corpus sources
with moderate confidence for a real, unambiguously identified site.
*Bronze Age inferred mobility* (actual LM-period travel time, actual route
choice, actual interaction frequency) is **not** the same object and is
**not directly measurable at all** — it would have to be modeled, with
disclosed, contestable assumptions (a specific hiking-cost function, an
assumed period-appropriate road/track network, an assumed relationship
between physical accessibility and *actual* administrative/social
interaction). **Terrain cost is not assumed equivalent to interaction
frequency anywhere in this document** — that equivalence is exactly the
first arrow in the round's own generative chain (terrain → mobility cost →
interaction structure) and is a hypothesis to be stated, never a
substitution to be made silently.

**Coverage feasibility, once geography is (hypothetically) attached:** only
5 sites have ≥30 records (Haghia Triada 1110, Khania 226, Phaistos 66,
Knossos 59, Zakros 53); 12 have ≥10; 15 have ≥5. The remaining 37 sites
have <5 records each, many with exactly 1. **Any geography-structure
comparison is therefore, in practice, a comparison among at most ~5-12
sites, not 52** — the other 40 site names contribute inscription IDs but
not usable statistical mass.

---

## TASK 5 — Dependence structure

Checked directly via `nesting_check()` against the real corpus (not
assumed):

| dependence source | finding | evidence |
|---|---|---|
| same physical tablet / same artifact | **9 explicit fragment joins** exist in `name` (e.g. `HT123+124a`, `HT42+59`, `HTWa1845+1733`) — meaning at least 9 records already represent >1 physical fragment merged into one row. Undisclosed joins among the other 1712 cannot be ruled out from this corpus alone. | `fragment_join_ids()` |
| same archaeological deposit | `findspot`, where present, is **perfectly nested within `site`** (0 violations, `nesting_check(records, "findspot", "site")`) — but only 1063/1721 records have a findspot value at all | test_findspot_perfectly_nested_within_site |
| same site | 1718/1721 records have a site; extreme concentration (Haghia Triada 64.6% of all site-labeled records, Herfindahl index 0.439 — roughly "2.3 effective sites" by that index, out of 52 nominal ones) | `site_concentration()` |
| same scribal hand | `scribe`, where present (592/1721, 34.4%), is **perfectly nested within `site`** (0 violations, 102 distinct scribes, `nesting_check(records, "scribe", "site")`) — scribal identity in this corpus never crosses a site boundary, at least as encoded | test_scribe_perfectly_nested_within_site |
| same chronological phase | `context`/period, where present, is highly non-independent of site: `mutual_information_categorical("context","site")` gives normalized I ≈ **0.83** — period is nearly (not perfectly — Iouktas alone has 2 period values, Khania has 4) determined by site in this corpus |

**Recommended clustering unit for any future test:** **`site`** is the
correct primary grouping unit for grouped cross-validation and for
permutation, because scribe, findspot, and (largely) chronology are all
already nested inside it — clustering at any finer level (scribe, findspot)
without also respecting site would under-count the true dependence, and
clustering coarser than site would discard exactly the geographic contrast
the round is designed to probe. **Fragment-joined records (`name` contains
`"+"`) must additionally be treated as a single dependence unit**, not two,
even though this corpus already merges them into one row — the risk is the
reverse one (an undisclosed join elsewhere in the corpus silently
double-counting one physical object as two independent rows), which cannot
be fully ruled out without external epigraphic cross-referencing. Any
permutation null must be **within-site** (or, if power requires pooling,
explicitly blocked by site), exactly mirroring the conditional-permutation
discipline already used in V1/V2 (`docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md`
§8) and validated by the elimination-asymmetry mechanism round
(`results/CONSTRAINT_INFORMATION_MECHANISM.md` §F) — a marginal (unconditioned)
permutation here would risk exactly the Simpson-type spurious-symmetry or
spurious-asymmetry failure modes that round proved can occur.

---

## TASK 6 — Generative hypotheses (competing mechanisms)

| hypothesis | can this corpus distinguish it, even in principle, from H1? |
|---|---|
| **H1 shared-context compression** | Only as a residual, after every other mechanism below is controlled for — H1 is not independently identified by any single measure in Task 2 |
| **H2 administrative templating** | **Severely confounded with H1 by construction**, because the only proxy for "administrative" this corpus offers (`support`=Nodule/Roundel) is itself part of what would be modeled — see Task 3. Any apparent compression effect attributed to context could equally be H2 unless context is defined independently (external literature) |
| **H3 genre effect** | Genre is not directly labeled either; would inherit the same `support`/`findspot` proxy problem as H2 |
| **H4 medium constraint** | **Directly testable in principle and already shows real confounding**: `mutual_information_categorical("support","site")` normalized I ≈ **0.44** — object type is substantially, not perfectly, entangled with site (e.g. Haghia Triada is Nodule-dominated 860/1110 ≈ 77%, Khania is Roundel-heavy 101/226 ≈ 45%, Zakros is Tablet-dominated 44/53 ≈ 83%). Any geography effect must be shown to survive controlling for `support`, or H4 cannot be ruled out |
| **H5 scribe effect** | Directly testable where `scribe` is present (592/1721): scribe is perfectly nested within site (Task 5) and near-perfectly determines `support` too (`mutual_information_categorical("scribe","support")` normalized I ≈ **0.98**) — meaning scribe, site, and medium are almost inseparable in this corpus wherever scribe is recorded at all. A geography effect and a scribe effect will be extremely difficult to tell apart with scribal data this entangled |
| **H6 site convention** | By definition confounded with any geography effect at the site-comparison level — this is the central identifiability problem for the whole round (Task 8/12) |
| **H7 preservation/corpus-construction bias** | Damage marking (`preservation_damaged_signs`) is derivable and can be checked as a covariate; corpus-construction bias (which sites/objects were excavated, published, and digitized) cannot be audited from inside this corpus at all — it is a property of the *field* history, not the data |

**No mechanism above is ruled out by this audit.** The corpus provides
enough structure to *state* each hypothesis precisely and to *measure* the
covariates needed to control for H4 and H5 specifically; H2/H3/H6 remain
structurally entangled with any context/geography signal until an
external, independently-sourced context classification exists (Task 3),
and H7 is not auditable from this corpus at all.

---

## TASK 7 — Prospective predictions, ranked

| pred. | statement | theoretical independence | measurement validity | effective N | confounding risk | falsifiability |
|---|---|---|---|---|---|---|
| P1 | admin inscriptions show more OOS predictability/template reuse | **low** — "administrative" is not independently classifiable in this corpus (Task 3) | low, inherits Task 3's circularity | small once restricted to labeled subset | very high (H2/H4 entangled with the very label) | in principle yes, but only after the label problem is solved externally |
| P2 | context predicts normalized length, controlling for object type/preservation | low, same labeling problem | moderate — length itself is clean (Task 2 #1) | moderate | high (H4 medium confound directly measured, I≈0.44) | yes, if "context" is replaced by an external classification |
| P3 | same-site inscriptions are more structurally similar than cross-site pairs | **highest of the six** — site is a clean, AVAILABLE, non-circular label | moderate-high, if similarity = template structure (Task 2 #8), not edit distance (crippled by length) | usable only for ~5-12 sites with real mass (Task 4) | high but *auditable*: H4/H5/H6 can be checked directly as covariates since `support`/`scribe` are measured | **yes, cleanly** — a clear null (no within/between difference) is well-defined |
| P4 | between-site similarity declines with terrain-adjusted cost more than raw distance | independent in principle, but **requires external geography (Task 4) end to end**, including a chosen mobility model | low until that model is chosen and justified | very small — effectively 5-12 sites means at most ~10-66 site-pairs, most involving thin sites | very high — an entire modeling choice (which terrain-cost function) becomes an extra researcher degree of freedom | yes in principle, but only as a *second-stage* test after P3 |
| P5 | geographically constrained sites show relatively more internal formulaicity | independent in principle | needs P4's geography machinery plus P3's similarity machinery | very small (same site-pair constraint as P4) | very high, compounds P3 and P4's risks | yes, but the weakest-powered of the six |
| P6 | geography's effect on structure differs by context | depends entirely on Task 3's unsolved classification problem | low | smallest of all six (an interaction term) | highest | yes in principle, essentially unratifiable with current data |

**Ranking (best to worst): P3 > P2 > P1 > P4 > P5 > P6.** P3 is the only
prediction that needs no external data at all and no unresolved
classification to be well-posed. P2 and P1 are next but both currently
require Task 3's external context classification. P4-P6 all require the
full external geography stack (Task 4) and are additionally starved by the
5-12-site effective coverage.

**Designated as the (at most two) possible future primary hypotheses:**
**P3** (within-site vs. between-site structural similarity) and **P4**
(between-site similarity vs. terrain-adjusted cost), because they are the
two rungs of the round's own core generative chain that can be posed
*without* solving the context-classification problem first — P3 needs only
`site` (already AVAILABLE, clean); P4 needs `site` plus externally-attached
geography (Task 4), a scoped, well-defined external-data addition, not an
open-ended one. P1, P2, P5, P6 are not designated, primarily because they
either depend on the currently-unsolved context classification (P1, P2,
P6) or compound P4's cost with P3's site-pair scarcity (P5).

---

## TASK 8 — Strongest test: within-site vs. between-site similarity

**Design as specified:** matched within-site vs. between-site structural
similarity, controlling for context, chronology, object type, inscription
length, preservation, and sign inventory; then ask whether between-site
similarity varies with geography/travel cost.

**Identifiability assessment (not executed):**

- **Similarity measure:** must be Task 2's #8 (token-kind template
  structure) or #1/#2 (length/diversity) — **not** #9 (edit distance),
  whose dynamic range collapses at this corpus's median length of 1.
  Template-structure similarity is defined without reference to sign
  identity or gloss, so it is decipherment-free and passes the semantic
  firewall.
- **Matching variables, availability:** context (period) — PARTIAL,
  1390/1721, and see Task 3's warning that "context" here is chronological,
  not functional; object type (`support`) — AVAILABLE, 1721/1721;
  inscription length — DERIVABLE, 1721/1721; preservation — DERIVABLE;
  sign inventory — AVAILABLE at the corpus-pooled level only (Task 2 #3/#4).
  **Chronology-as-matching-variable is nearly degenerate**: 94.2% of
  non-null `context` values are `LMIB`, and `LMIB` is also Haghia Triada's
  *only* recorded period (Task 5) — matching on chronology inside a
  within/between-site design will, for the dominant site, match on almost
  nothing.
- **Object-type matching interacts directly with H4**: because `support`
  and `site` already carry normalized mutual information ≈0.44 (Task 6),
  strict object-type matching will systematically **exclude** many
  within-Haghia-Triada-vs-elsewhere comparisons (HT is Nodule-heavy;
  most other sites are not), shrinking the usable matched set well below
  the raw N.
- **Identifiable in principle: YES, for the within-vs-between-site
  comparison alone (P3), restricted to the sites with real mass** (5 with
  ≥30, up to 12 with ≥10). **Identifiable in practice only with a
  substantially reduced effective N** once length/support/context matching
  is applied, and **the geography-vs-cost extension (P4) is identifiable
  only after Task 4's external data is attached and a specific
  terrain-cost model is chosen and justified independently of the
  outcome.**

---

## TASK 9 — Information-theoretic connection

Directly reusing `results/CONSTRAINT_INFORMATION_MECHANISM.md`'s own
theorem (§B): a constraint (here, geography `G`) carries zero information
about an outcome `L` (inscription structure) unless it eliminates or
reweights states **asymmetrically** with respect to `L`, evaluated
*conditionally* on whatever is already fixed (`Z` = the Task 5 dependence
structure: site, support, scribe, chronology). **Geography can constrain
mobility arbitrarily strongly while still satisfying `I(G;L|Z)=0`
exactly** — this is not a hedge, it is Example A of that round (90%
cardinality reduction, zero information) restated with `G` playing the role
of the eliminating constraint.

**What would have to be true, empirically, before `I(G;L|Z)>0` could be
expected (never assumed):**

1. Geography (via mobility/interaction cost) would have to produce a
   **real, conditional-on-`Z`** asymmetry in how inscriptions are
   generated — i.e. `P(\text{structure} \mid G, Z)` must genuinely differ
   across levels of `G` **after** site/support/scribe/chronology are held
   fixed, not merely correlate with them marginally.
2. Because `support` (I≈0.44 with site) and `scribe`/`context` are already
   substantially entangled with `site` in this corpus (Task 5/6), `Z` must
   include them explicitly — an apparent `I(G;L)>0` computed marginally
   (not conditioning on `Z`) would risk being **exactly the confounded-proxy
   construction** in `CONSTRAINT_INFORMATION_MECHANISM.md` §F item 3: an
   effect that is really `support`'s or `scribe`'s, laundered through its
   correlation with `G`.
3. Symmetrically, a apparently null marginal result would not rule out a
   real conditional effect masked by Simpson-type cancellation (§F item 2)
   — geography's effect could be strong and opposite-signed across, say,
   Nodule-dominated vs. Tablet-dominated sites and cancel in a pooled
   marginal check.
4. Given P3/P4's site-count scarcity (Task 4/8), any observed asymmetry
   would also have to be shown **stable across a reasonable perturbation of
   which sites are included**, since a handful of thin sites can dominate
   an apparent `r_1 \ne r_0`-style asymmetry by chance alone (small-N
   instability, distinct from the conditioning issue above).

**None of this is assumed to hold.** The corpus audit above establishes
only that the *machinery* to check condition 1 correctly (conditioning on
`Z`) is available; whether the asymmetry actually exists is exactly what a
future, properly-designed and pre-registered P3/P4 test would determine —
and is explicitly not tested in this feasibility round.

---

## TASK 10 — Negative controls (prospective only, for P3/P4)

Valid for the P3 (within/between-site similarity) and P4 (similarity vs.
cost) design specifically; not executed.

| control | valid here? | why |
|---|---|---|
| shuffled site labels (within the matched set) | **Yes** | directly tests whether the observed within/between split is an artifact of the matching procedure itself, not geography |
| shuffled context labels within strata | **Yes, but weak** | given `context`'s near-degeneracy (94.2% `LMIB`), this control will have very little power to detect anything — disclose, don't rely on it alone |
| geography permutation among matched sites | **Yes — the primary control for P4** | permutes which site gets which terrain-cost value while holding the observed similarity structure fixed; directly targets `I(G;L|Z)` per Task 9 |
| sequence randomization preserving length | **Yes, for Task 2 measures #1 excluded, #8 included** | a valid null for template-structure similarity (#8): shuffles token kinds while holding sequence length fixed, so "similarity" driven purely by length cannot masquerade as structural similarity |
| sequence randomization preserving unigram frequencies | **Yes, but only meaningful pooled corpus-wide** | given the 74-98% hapax rates (Task 2), this control is only well-behaved at the whole-corpus level, not per-site |
| object-type-matched nulls | **Yes — necessary, not optional**, given H4's measured confound (I≈0.44 support×site) | any P3/P4 null must be run within object-type strata, not marginally |
| artifact-level permutation | **Yes — mandatory**, given Task 5's fragment-join finding (9 confirmed joins) and site/scribe/findspot nesting | must permute at the site-clustered artifact level, never at the raw-record level, or the null will be anti-conservative |

**Controls explicitly NOT chosen:** a naive marginal (unconditioned) site
shuffle without object-type/scribe stratification is **not** a valid
control here, precisely because of the H4/H5 entanglement documented in
Task 6 — an unconditioned shuffle would fail to distinguish a geography
effect from a medium or scribe effect, defeating the test's own purpose.

---

## TASK 11 — Power / identifiability, per serious candidate (P3, P4)

Computed directly from `run_full_audit()` (not assumed):

| | P3 (within/between site) | P4 (adds terrain cost) |
|---|---|---|
| N inscriptions (site labeled) | 1718 | 1718 (before any external-geography attrition) |
| N sites (nominal) | 52 | 52 |
| N sites with real mass (≥30) | 5 | 5 |
| N sites with ≥10 | 12 | 12 |
| N physical artifacts | ≤1721 (≥9 known joins reduce this; true count unknown without external epigraphy) | same |
| context/period counts | 11 distinct, 94.2% one value (`LMIB`) among non-null | same, plus needs external geography attached without missingness among the ≥10-record sites |
| class balance (support) | 19 types, top 3 (Nodule/Tablet/Roundel) = 1476/1721 ≈ 85.8% | same |
| effective N after site clustering | **≈52 nominal clusters collapse to an effective count far below that** — Herfindahl index 0.439 implies an *effective number of sites* of roughly 1/0.439 ≈ **2.3** by that concentration measure; even the more generous ≥10-record threshold gives only 12 real clusters | same, minus whatever sites lack a confident gazetteer match |
| chronological overlap | poor — HT (64.6% of site-labeled records) is single-period; genuine cross-site chronological overlap exists mainly among the smaller sites, which are also the thinnest | same |
| geographic coverage | trivially "complete" by name (52 sites named) but **substantively thin** — practical comparison power lives in ≤12 sites | same, further reduced by whichever sites cannot be confidently geolocated |
| missingness | site 99.8% present; findspot 61.8% missing; scribe 65.6% missing; context 19.2% missing | adds: 100% missing for coordinates/elevation/terrain cost until externally attached |

**Verdict: P3 is powered, barely, at the site level (an effective handful
of real clusters, not 52) and only for measures that survive Task 2's
short-record constraint (length, template structure) — it is not powered
for anything requiring within-record sequential structure. P4 is
currently NOT powered as an independent hypothesis**: it inherits P3's
thin site count, adds a full external-data dependency with no missingness
information yet, and adds a Task 9 conditioning requirement (on `support`,
`scribe`) that will consume degrees of freedom P4 does not have to spare
at ~5-12 real sites. **A null result from P4 as currently scoped would not
be a useful negative finding** — it would be indistinguishable from an
underpowered design, which this round is instructed not to disguise as a
result.

---

## TASK 12 — Adversarial kill attempt

Every candidate mechanism this round names can, in this corpus, mimic a
"contextual compression" finding:

- **Genre** — not independently labeled; would ride on the same
  `support`/`findspot` proxy problem as H2/H3 (Task 3/6).
- **Tablet/object size** — `support` is directly measured and directly
  confounded with site (I≈0.44); a pure H4 effect (bigger objects hold
  longer, more repetitive inscriptions for purely physical reasons) would
  produce exactly a within/between-site structural difference with zero
  geography content.
- **Chronology** — nearly collapsed to one value at the dominant site
  (94.2% `LMIB` overall, 100% at Haghia Triada); a real period effect
  elsewhere in the corpus could masquerade as a site effect purely because
  period and site are entangled (I≈0.83), not because of geography.
- **Scribal convention** — scribe is perfectly nested in site and
  near-perfectly entangled with support (I≈0.98 where recorded); **any
  within-site formulaicity finding could be a single-scribe artifact**,
  especially at sites with one dominant hand (e.g. `HT Wa Scribe 10`:
  106 records).
- **Site bureaucracy (H6)** — by construction indistinguishable from a
  geography effect at the between-site comparison level; this is the
  central, unresolved identifiability gap of the whole round, not a minor
  caveat.
- **Sign inventory** — corpus-pooled and heavily long-tailed (74-98% hapax
  at 1-3 grams); any apparent "diversity" difference between sites could
  be an artifact of unequal token totals per site (Haghia Triada
  contributes the overwhelming majority of pooled tokens) rather than a
  real difference in generative process.
- **Preservation** — derivable and checkable as a covariate, but damage
  rates are not yet audited per site in this round; an uneven damage
  distribution across sites would inflate or deflate apparent length/
  diversity differences that have nothing to do with geography.
- **Corpus construction / survival bias** — not auditable from inside this
  corpus at all (Task 6); which sites happen to be excavated, published,
  and digitized in this specific source is a fact about 20th/21st-century
  scholarship, not about the Bronze Age, and this repository has no way to
  correct for it.
- **Transcription conventions** — this corpus is a single secondary
  digitization (`lineara.xyz`, per `docs/CORPUS_PROVENANCE.md`); any
  site-specific quirk in how that source's own contributors transcribed
  different excavation reports could produce spurious site-level
  structural differences unrelated to either geography or genuine scribal
  practice.

**Strongest claim that would remain defensible even if a future,
well-designed P3/P4 test "succeeds" (i.e. finds a statistically real,
properly-controlled, cross-validated, permutation-checked difference):**

> **"Linear A inscriptions exhibit context- and geography-associated
> differences in observable sequence structure."**

This claim is deliberately bounded to what the corpus can support even in
the best case: an **association**, in **observable** (not semantic)
structure, tagged to **context and geography jointly** (since Task 6/9
establish they cannot currently be cleanly separated from medium, scribe,
and site-bureaucracy at this corpus's scale). **Nothing stronger is
justified by this audit** — not "shared context enables compression," not
"scribes economized on communication for interlocutors they knew well,"
not any claim about the two-step generative chain (terrain → mobility →
interaction → shared context → compression) beyond its first observable
link (context/geography ↔ structure), which is itself not yet tested.

---

## TASK 13 — Preregistration gate

**UNDERPOWERED.**

Not READY: no fixed hypothesis has been tested this round (by design), and
P3 — the only candidate needing no external data — is powered only at an
effective handful of site clusters (Herfindahl-implied ≈2.3, generously
≤12 by the ≥10-record threshold), which is thin for the number of
covariates (support, scribe, chronology) Task 9's own conditioning
requirement obligates it to control for.

Not READY WITH EXTERNAL DATA: even after Task 4's geography is attached
(a scoped, achievable external-data addition for P4), the site-count
scarcity is not solved by better geography — it is a property of this
corpus's own site distribution (Herfindahl 0.439), which no external
dataset changes.

Not NOT IDENTIFIABLE: P3 specifically **is** identifiable in principle
(Task 8) — the problem is power/effective-N, not a structural
impossibility.

Not HYPOTHESIS FAILS CONCEPTUALLY: nothing in this audit shows the
generative chain is incoherent; it shows the current corpus cannot yet
support a properly-powered, cleanly-controlled test of even its cleanest
component (P3), let alone the full chain through to geography (P4).

**This gate deliberately does not favor READY**: a READY verdict would
require, at minimum, a solved context-classification problem (Task 3, not
solved), a site-count large enough to support the H4/H5 conditioning Task
9 requires (not currently true), and — for any geography-facing prediction
— externally attached, justified terrain-cost data (Task 4, not yet
attached). None of these three are optional relaxations; each is a
precondition this document itself derived from the corpus, not an
arbitrary bar.
