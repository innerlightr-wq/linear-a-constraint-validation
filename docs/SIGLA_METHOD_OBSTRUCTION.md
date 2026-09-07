# SigLA method obstruction

**Status: frozen.** This document records why the SigLA cross-transcription
replication is paused, as a formal checkpoint, without modifying the
primary H1 result.

## Statement

- SigLA cannot currently support faithful H1 replication.
- The current target-sign traversal (`_collect_indexed_entries` in
  `src/sigla_adapter.py`) is **empirically invalid on real data**: tested
  directly against real document `HT 13`, it returned 129 spurious,
  duplicated entries for a ~15-syllable tablet (index value 1 repeated 44
  times; implausible outlier indices 704/705, consistent with picking up
  unrelated substructure such as pixel bounding-box coordinates rather than
  the true sign-attestation sequence).
- Rule-A boundaries cannot be reconstructed for SigLA without inventing a
  new geometric threshold from the observed corpus — no line, ruling,
  section, or prior-total marker was found; only pixel bounding boxes,
  and turning those into a section boundary would require a corpus-tuned
  distance rule, which this project's own rules explicitly prohibit
  inventing.
- **Therefore no SigLA H1 statistic is authorized.** Gate A (target
  reconstruction) = FAIL. Gate D (Rule-A sectioning) = FAIL. Gates B
  (numeral reconstruction) and C (fraction handling) = OPEN. All four gates
  must PASS for authorization; none do.

## What this is, and is not

**This is a METHOD OBSTRUCTION, not evidence for or against H1 itself.**
SigLA's inability to currently support this project's own adapter and
traversal logic says nothing about whether Linear A's `ku-ro` sequence
behaves as a summation operator. It says only that this project does not
yet have a validated way to extract SigLA's data faithfully enough to test
that question a second time, on a second source.

## What is not touched

The primary H1 result (`results/H1_RESULT.md`, `results/h1_occurrence_audit.csv`,
commit `df2916485fbd97070d869c1fdefd54fdbd4798bd`) is **not modified,
reinterpreted, or weakened by this document**. The frozen H1 protocol
(`docs/H1_PROTOCOL.md`, `src/kuro_protocol.py`, `tests/test_kuro_protocol.py`,
commit `5aae796f71245e359c2fb72d5b01b81f72d44288`) is untouched.

## Path forward, not pursued in this document

Per the prior round's own recommendation: resolving Gate A requires
identifying the correct field path to SigLA's true, reliably-ordered
sign-attestation array — not attempted here. Gate D has no current lead and
would need a source-defined structural signal that has not been found.
