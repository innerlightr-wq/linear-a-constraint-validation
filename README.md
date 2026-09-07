# linear-a-constraint-validation

**Independent computational validation and adversarial testing project.**
This repository exists to test whether the structural claims in *"Structural
Invariants in Linear A Administrative Records: A Corridor-Based Framework
for Semantic Constraint"* (De Jesús, 2026) can be independently reconstructed
from corpus data — not to confirm them. It also documents every subsequent
adversarial and methodological round run against those claims, including
the negative and inconclusive ones.

## What this is

- An **independent validation** of specific, falsifiable claims from an
  earlier exploratory paper, using a corpus this project builds itself from
  public sources.
- Structured so that each claim is operationally defined, with explicit
  exclusion rules and falsification criteria, **before** any corpus statistic
  is computed. See `docs/` for the frozen protocol of each hypothesis under
  test.
- A record of a **paused, currently inactive research program** — see
  Status below. Every result described here, positive, negative, or
  inconclusive, is retained and reported.

## What this is not

- **Not a decipherment project.** No phonetic value, translation, or lexical
  meaning is proposed, tested, or assumed anywhere in this repository.
- **Not an attempt to prove the original paper right.** The explicit goal is
  to let each claim survive, weaken, or fail against reconstructed data. A
  claim that fails here is a valid, reportable outcome, not a bug.
- **Not a claim that structural consistency implies lexical meaning.**
  Showing that a sign-group behaves arithmetically like a summation operator
  says nothing about what word it represents or how it sounded — an
  accountant's tally mark would test identically.

## Status: PAUSED

The research program described below is **complete through a feasibility
audit and paused**, pending domain-expert review and/or acquisition of
external data (archaeological context classification, geographic
coordinates) that this repository's own corpus does not supply. No
experiment is currently in progress. **All completed computational tests
pass** — see `test count` in each result document, and run `pytest` from
the repo root to reproduce (352 tests as of the current commit).

## Empirical sequence

Each stage below was frozen (protocol/harness committed) **before** the
corresponding result was computed, and each result is reported regardless
of outcome. Full detail, provenance, and adversarial audit for every stage
is in the linked result document.

| stage | outcome | result document |
|---|---|---|
| KU-RO / H1 (positional and arithmetic behavior) | **FAILURE** | `results/H1_RESULT.md` |
| Candidate 1 (commodity × fraction-presence) | **NOT SUPPORTED** | `results/CANDIDATE1_RESULT.md` |
| Constraint accumulation V1 | apparent **WEAK POSITIVE UPDATE** — later identified as construction-dependent, not a genuine effect (see below) | `results/CONSTRAINT_ACCUMULATION_RESULT.md` |
| Constraint accumulation V2 (construction-dependence removed by design) | **NEGATIVE UPDATE** | `results/CONSTRAINT_ACCUMULATION_V2_RESULT.md` |
| Constraint-information mechanism analysis | **USEFUL REFORMULATION** (methodological, not empirical) | `results/CONSTRAINT_INFORMATION_MECHANISM.md` |
| Contextual compression × geography feasibility | **UNDERPOWERED** (feasibility audit; no hypothesis tested) | `results/CONTEXTUAL_COMPRESSION_FEASIBILITY.md` |

**The V1 magnitude signal did not survive V2.** V1's headline finding
(`ΔH4 = +0.177`, Holm p = 0.0015, `SUPPORTED`) collapsed to
`ΔH4 ≈ −0.0006`, Holm p = 0.636, `NOT SUPPORTED` once V2 excluded the
population subset responsible for a deterministic construction dependence
identified in `results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md` *before*
V2 was run. V2 is the operative result for that question; V1's positive
finding is retained in this repository as a diagnosed artifact, not as
evidence.

**The constraint-information mechanism round's central finding** (proven,
not merely asserted — see `results/CONSTRAINT_INFORMATION_MECHANISM.md`
for the theorem and constructive counterexamples) is that these three
things are mathematically distinct and none implies another:

```
constraint  ≠  state-space reduction  ≠  target-specific information
```

A constraint can eliminate the overwhelming majority of a state space and
carry zero information about an outcome, or eliminate almost none of it
and carry enormous information — this is exactly what explains why V1's
apparent effect vanished under V2's population change.

**Contextual compression × geography is a prospective research direction
only.** The feasibility round (`results/CONTEXTUAL_COMPRESSION_FEASIBILITY.md`)
audited whether this corpus could support a future test of "shared context
enables communicative compression" and its link to geography, without
running that test. Its verdict is **UNDERPOWERED**, not a finding about
geography or compression. **Neither of its two candidate follow-up
experiments (P3: within-site vs. between-site structural similarity; P4:
similarity vs. terrain-adjusted travel cost) has been executed.**

## SigLA replication attempt (paused)

A parallel effort to cross-validate this project's corpus extraction
against the independent SigLA palaeographical database
(`docs/SIGLA_METHOD_OBSTRUCTION.md`, `docs/SIGLA_PROVENANCE_AUDIT.md`,
`docs/SIGLA_SCHEMA_MAPPING.md`, `docs/SIGLA_DATA_ADEQUACY_AUDIT.md`,
`src/sigla_adapter.py`) encountered a genuine methodological obstruction:
the sign-order traversal method tested against real document HT 13
returned spurious, duplicated entries and could not be trusted to reflect
true document order. **This thread is paused, not completed, and its
adapter output must not be read as validated evidence for or against any
claim in this repository.** It is retained here, unabridged, as a
documented negative/blocked replication attempt, in the same spirit of
disclosure as the failed and negative results above.

## Relationship to prior work

The original paper (`LinearA.pdf`) and its companion note
(`structuralinvariantsLinearACompanionNote.pdf`) are **frozen** — not part of
this repository, not modified by it, and not treated as ground truth by it.
This project is scientifically independent: its code, protocols, and corpus
construction are written fresh, and its results are reported regardless of
whether they agree with the original paper.

This project also builds on, and explicitly credits, prior independent work
on Linear A corpus validation — see `docs/EXTERNAL_FOUNDATION_AUDIT.md` for
the full account of what was reused (ideas/protocol only, not code) and what
was independently reimplemented, and why.

## Data policy

**No raw Linear A corpus data is committed to this repository, ever.**
Everything under `data/` is fetched or generated locally by scripts in
`src/`, is `.gitignore`d, and is rebuilt from documented upstream sources with
recorded checksums. See `data/README.md` for exact provenance and licensing
of every source this project touches, and `docs/H1_PROTOCOL.md` for how the
first hypothesis under test is operationally defined.

## Domain-expert review

This project's author is not a specialist in Aegean epigraphy, Bronze Age
archaeology, Minoan linguistics, or ancient accounting systems. Every
structural finding here is offered for domain-expert evaluation, correction,
or rejection — not as an authoritative claim. See `docs/H1_PROTOCOL.md` for
the specific judgment calls this project cannot make on its own.

## Reproducing the results

```
pip install pytest
pytest            # 352 tests, all currently passing
```

Corpus data is not included (see Data policy); result documents report
their source corpus's checksum so that a rebuilt corpus can be verified to
match before any result is reproduced from it.

## License

To be finalized before any public release. Code in this repository will not
redistribute any third-party corpus data (see `data/README.md`); the license
covering original code and analysis here has not yet been chosen.
