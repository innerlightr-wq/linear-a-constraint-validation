# External foundation audit

Before writing any analysis code, this project inspected an existing,
independent corpus-validation effort on the same script, to avoid duplicating
its work and to check whether its licensing permits reuse.

**Source inspected:** Tsirkas, C. (2026), *Auditing the Unread — A Corpus
Validation Framework for Undeciphered Scripts, with a Demonstration on Linear
A*. https://github.com/ChristosTsirkas/corpus-validation-for-undeciphered-scripts-linear-a
(HEAD at inspection time: `84a3375874bc8fc6006f736282eeafed5f58d561`, 2026-09-06).

**EPISTEMIC LABEL: EXTERNAL METHOD / EXTERNAL DATA FOUNDATION.** Everything in
this document describes Tsirkas's project, not a claim of this project's own.

## What corpus it generates

`data/corpus_v1.json` — a compiled derivative of GORILA (Godart & Olivier
1976–1985), George Douros's tabulation, John G. Younger's commentary, and the
`mwenge/lineara.xyz` digital extraction. **DATASET FACT** (as of the
2026-08-05 upstream snapshot, per that project's `data/README.md`):

| property | value |
|---|---|
| records | 1721 |
| distinct documents | 1621 |
| complete sign-groups | 2659 |
| damaged sign-groups | 953 |
| complete multi-sign groups | 927 |
| md5 | `2f5c936f0848fcbcb4ef35669eccca99` |
| sha256 | `a642976320aaaa52f67f3fc29539a3ee88ea683e25bc2d6d8969e6d6114a93a1` |

This is the same upstream lineage (GORILA → `mwenge/lineara.xyz`) previously
identified as the source behind `pyaegean`'s bundled 1,721-inscription corpus
(see the prior feasibility audit) — consistent with, not independent of, that
earlier finding.

A second corpus, `data/sigla_corpus.json`, is generated separately from
SigLA's own served data (`database.js`, an OCaml `Marshal`-encoded blob),
decoded by an original OCaml-`Marshal`-format implementation
(`src/ocaml_marshal.py`). **DATASET FACT:** 802 documents, 5144 attestations
(4712 confident / 44 doubtful / 388 unreadable or unclassified), md5
`f3cb6d5805bd5376eef7099705d3d2ef`. This is the genuinely independent-source
corpus (Salgarella & Castellan's own palaeographic work, not a re-export of
the GORILA→mwenge lineage).

## Upstream source / snapshot / checksum

Documented exhaustively in that project's `data/README.md` and reproduced
above. Neither corpus file is shipped in that repository; both are built
locally by scripts that project provides, from sources it does not control
and does not redistribute.

## Corrections applied

**DATASET FACT / CORPUS QUALITY RISK, directly relevant to this project:**
`build_corpus.py` applies a **D4 correction** — "a systematic AB21/AB22
(sheep/goat) sign-identity inversion identified against SigLA, corrected once
here at build time rather than patched ad hoc downstream." Per
`AI_DISCLOSURE.md`, this rests on "a fifteen-of-fifteen agreement between two
witnesses against a third at the sign-family level" — i.e., a genuine
multi-witness cross-check (GORILA-lineage transcription vs. SigLA), not an
assumption. This project's own future corpus build should check whether this
correction needs to be reapplied independently, since AB21/AB22 confusion is
exactly the kind of systematic transcription-disagreement risk flagged in
this project's own prior feasibility audit (§6, Corpus Quality Risks).

Damage markers (`[`, `]`, `?`, combinations) are parsed into structured
boolean flags rather than left embedded in strings. Numeric measures are
graded by confidence ('secure', 'derived', etc.) following Corazza et al.
(2021)'s published fraction values, cited by number rather than copied.

## How AB21/AB22 is handled

See "Corrections applied" above — resolved via a documented, cross-checked
correction (the D4 finding) rather than left as an open transcription
ambiguity, in that project specifically. **OPEN** for this project: whether
to trust that correction outright, re-derive it independently, or flag it as
an assumption inherited from prior work — deferred to when this project's own
corpus build is implemented (out of scope for the H1 protocol-freezing phase).

## What SigLA extraction provides

Sign identifiers, document metadata, and certainty/boundary fields —
explicitly *not* the drawings, which are described as "the substantial
creative content of SigLA" and are left untouched. **LICENSE FACT:** CC
BY-NC-SA 4.0 attaches to any output of this extraction, regardless of the
extractor code's own license, because re-encoding a format does not create a
new copyright in the underlying material.

## Which data files are generated locally vs. committed

Only two files are committed in that repository: `data/divergences.json`
(an original divergence register, citing sign identifiers as ordinary
scholarly citation) and `data/power_analysis.json` (statistics computed on
**synthetic** corpora only). Every corpus file — `corpus_v1.json`,
`database.js`, `sigla_corpus.json`, and all intermediate pipeline outputs —
is `.gitignore`d and rebuilt locally. That project's own test suite includes
`test_corpus_not_committed` and `test_sigla_not_committed` as an explicit
safeguard against accidental redistribution.

## Which files may legally be redistributed

None of the corpus files. **LICENSE FACT**, summarized from that project's
`LICENSE.md`:

| component | license | redistributable here? |
|---|---|---|
| `src/`, `tests/`, `docs/` (their code) | PolyForm Shield 1.0.0 + academic carve-out | Code reuse would be permitted under the academic carve-out (personal, non-commercial research use) — but see "Code reuse decision" below |
| `corpus_v1.json` | derivative of an unlicensed upstream (`mwenge/lineara.xyz` has no LICENSE file — default all-rights-reserved) | **No** |
| `sigla_corpus.json` | CC BY-NC-SA 4.0 | **No** (share-alike/noncommercial/attribution would all bind if redistributed) |
| `divergences.json`, `power_analysis.json` | PolyForm Shield 1.0.0 + academic carve-out; contain no third-party corpus content | Could be cited/referenced, not needed for H1 |

## Which derived outputs may safely be committed

Aggregate statistics with no verbatim corpus text (counts, rates, checksums,
z-scores) — the same principle that project itself follows. This project
will follow the identical policy: **derived statistics yes, raw transcription
content no.**

## Code reuse decision: INDEPENDENT IMPLEMENTATION

**Licensing is not the blocking factor** — the PolyForm Shield academic
carve-out clearly permits this project (an individual acting in a personal
research capacity) to reuse Tsirkas's `src/` code outright. The decision to
reimplement independently instead is made for a different reason, stated
explicitly per this project's own instructions: prefer independent
implementation when there is any doubt, and — more importantly here —
**an independently-written reconstruction of H1 is a more informative test of
whether the claim reconstructs than reusing someone else's extraction logic
wholesale.** Reusing Tsirkas's `kuro_test.py` verbatim would make this
project's H1 result partially non-independent of his.

What *is* reused, explicitly, as **EXTERNAL METHOD** (ideas, not code):

- The **sectioning problem** itself: tablets are frequently mixed-commodity
  and carry multiple totals, so "preceding entries" must be scoped to a
  block, not the whole tablet. This project's own H1 protocol (see
  `H1_PROTOCOL.md`) defines its own sectioning rule independently, informed
  by — but not copied from — this observation.
- The **null-model design principle**: a raw match rate is circular if the
  section boundary was implicitly chosen to make sums work. Tsirkas's project
  addresses this with a permutation test (shuffle which stated total pairs
  with which section, compare against the observed exact-match rate). This
  project's own eventual arithmetic analysis (out of scope for this
  protocol-freezing phase) will independently implement an analogous
  permutation-based null check, not import his code.
  **Prior finding, not assumed true, to be independently reconstructed:**
  Tsirkas's own results reportedly show a KU-RO exact/near match rate
  substantially below the 90%/85% targets in the paper under test here (his
  own documentation references a "50% mismatch rate" as a phenomenon his
  project investigates via a damage-flag breakdown). This is recorded here as
  a prior, independent data point this project's own H1 test should be aware
  of — not as ground truth, and not as something this project's protocol was
  adjusted to match. **OPEN:** this project has not verified that number
  itself; it will emerge independently from this project's own reconstruction
  once run.
- The general shape of a **damage/uncertainty exclusion category** (a numeral
  or total flagged damaged/incomplete is excluded from "genuine mismatch"
  counts) — reflected independently in this project's own exclusion
  categories (`H1_PROTOCOL.md` §6), not copied field-for-field.

## Summary verdict for this phase

**EXTERNAL DATA FOUNDATION identified and usable** (the GORILA→`mwenge`
lineage, and separately SigLA, both independently confirmed reachable and
license-documented). **INDEPENDENT IMPLEMENTATION** chosen for all analysis
code. **CORPUS QUALITY RISK noted** (AB21/AB22, unreviewed-extraction status)
and carried forward into this project's own protocol rather than silently
inherited.
