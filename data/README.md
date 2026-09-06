# Data directory

**No corpus data is committed here, ever.** Everything below is fetched or
generated locally by scripts in `src/`, and is `.gitignore`d.

## Strategy: reuse the documented provenance, not the code

Per this project's external foundation audit (`docs/EXTERNAL_FOUNDATION_AUDIT.md`),
this project uses the same **documented upstream build steps** as prior
independent work (Tsirkas 2026), rather than re-deriving a corpus-extraction
pipeline from scratch — but implements its own extraction/parsing code
independently (see that audit for why).

### Primary substrate: GORILA → `mwenge/lineara.xyz`

**Raw-data location convention: `data/raw/lineara_xyz/`, not a root-level
directory.** This keeps every fetched/cloned upstream source under `data/`,
where the `.gitignore` policy (`data/raw/`, `data/generated/`, `data/cache/`
all excluded; only `data/README.md` retained) applies uniformly, rather than
relying on separately-declared root-level ignore rules per source.

**Future first-data command (documented here, NOT executed in this
protocol-freeze phase):**

```bash
git clone --depth 1 \
  https://github.com/mwenge/lineara.xyz.git \
  data/raw/lineara_xyz
```

**Upstream snapshot to record on every build:** the clone's own HEAD commit
hash (`git -C data/raw/lineara_xyz rev-parse HEAD`), recorded in
`results/build_manifest.json` alongside the build date. This project does
**not** assume the 2026-08-05 snapshot referenced in the external audit is
still current — a fresh clone may differ, and that is expected, not an
error (see below).

**Provenance chain:** GORILA (Godart & Olivier 1976–1985, Études Crétoises
XXI) → George Douros's tabulation + John G. Younger's commentary →
`mwenge/lineara.xyz`'s digital extraction. **LICENSE FACT:** the upstream
repository carries no LICENSE file; under default copyright this is all
rights reserved. **This project does not redistribute anything from it** —
the corpus is built locally, once, on the user's own machine, exactly as the
external foundation project does.

**Build command (to be implemented before H1 is actually run — not yet
implemented in this protocol-freezing phase):**

```bash
python3 src/build_kuro_corpus.py --raw data/raw/lineara_xyz/LinearAInscriptions.js \
                                  --out data/kuro_corpus.json
```

**What the build must record, per §3 of this project's instructions:**

| item | how it's recorded |
|---|---|
| upstream commit/snapshot | `data/raw/lineara_xyz`'s HEAD commit hash, in `results/build_manifest.json` |
| checksums | md5 + sha256 of the generated `data/kuro_corpus.json`, in the same manifest |
| build command | the exact command line invoked, logged verbatim |
| corpus counts | record count, distinct-document count, KU-RO/KI-RO/PO-TO-KU-RO occurrence counts |

A checksum or count differing from a previously recorded run is **not an
error** — it means the upstream source changed, which is expected of a
living digitization effort, and the manifest records both the old and new
values rather than silently overwriting history.

### Independent cross-check substrate: SigLA

```bash
python3 src/fetch_sigla.py --fetch   # opt-in, deliberate, not run by default
```

**LICENSE FACT:** SigLA's data (`database.js`) is CC BY-NC-SA 4.0 — attributed,
non-commercial, share-alike. Fetching it locally for this project's own
non-commercial research use is within those terms; **redistributing anything
derived from it is not**, without carrying the same license forward. Cite:
Salgarella, E. & Castellan, S. (2021), "SigLA: The Signs of Linear A. A
Paleographical Database."

SigLA is the one source in this project's provenance graph that is
genuinely independent of the GORILA→`mwenge` lineage (see the earlier
feasibility audit's dependency-graph finding). It is reserved for a
**future** cross-check of the H1 result — not part of the pilot build.

## What is preserved through the build

Per this project's own instructions and the H1 protocol's requirements:

- **Tablet identifiers** — GORILA catalogue numbers (e.g. `HT13`), preserved
  unchanged, to permit direct comparison against GORILA/SigLA scholarship.
- **Certainty/damage fields** — parsed into structured flags (not left
  embedded in transcription strings), matching the granularity the H1
  protocol's exclusion categories (`H1_PROTOCOL.md` §6) require.
- **Sign order** — preserved as an ordered token sequence per record.
- **No semantic normalization beyond identifying KU-RO/KI-RO/PO-TO-KU-RO and
  numerals** — per this project's explicit instruction, the build does not
  attempt sign-by-sign phonetic or lexical interpretation of anything else in
  the record.

## Committed vs. generated

| file | status |
|---|---|
| `data/README.md` | committed (this file) |
| `data/kuro_corpus.json` | **generated, gitignored** — never committed |
| `data/raw/lineara_xyz/` | **cloned, gitignored** — never committed |
| `results/build_manifest.json` | committed (contains only checksums/counts/commit hash — no corpus text) |
| `results/*.csv` (H1 statistics, once computed) | committed, once actually produced — aggregate counts and rates only, no verbatim corpus content |

## Status

**Not yet built.** This document declares the strategy; the fetch/build
scripts referenced above are not implemented in this protocol-freezing
phase (see `docs/EXTERNAL_FOUNDATION_AUDIT.md` and the pre-analysis report
for what is and is not done yet).
