# linear-a-constraint-validation

**Independent empirical validation project.** This repository exists to test
whether the structural claims in *"Structural Invariants in Linear A
Administrative Records: A Corridor-Based Framework for Semantic Constraint"*
(De Jesús, 2026) can be independently reconstructed from corpus data — not to
confirm them.

## What this is

- An **independent validation** of specific, falsifiable claims from an
  earlier exploratory paper, using a corpus this project builds itself from
  public sources.
- Structured so that each claim is operationally defined, with explicit
  exclusion rules and falsification criteria, **before** any corpus statistic
  is computed. See `docs/` for the frozen protocol of each hypothesis under
  test.

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

## Status

Pilot phase: **H1 (KU-RO positional and arithmetic behavior) only.** H2–H6
are explicitly out of scope until H1's protocol has been run and reported.

## License

To be finalized before any public release. Code in this repository will not
redistribute any third-party corpus data (see `data/README.md`); the license
covering original code and analysis here has not yet been chosen.
