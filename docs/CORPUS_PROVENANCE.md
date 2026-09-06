# Corpus provenance — primary substrate

**No raw corpus content is reproduced in this file.** Everything below is
metadata: URLs, commit hashes, checksums, sizes, and counts.

## Upstream source

- **Repository:** `https://github.com/mwenge/lineara.xyz.git`
- **Clone target (this project's convention):** `data/raw/lineara_xyz/`
  (gitignored, never committed)
- **Upstream HEAD commit at clone time:** `43fe7cf1abc8e6bb1ea3228c3a1bd5938709620a`
- **That commit's own date:** 2026-08-03 10:26:11 +0100
- **That commit's message:** "Issue #7: Add copyright disclaimer"
- **Clone date/time (this project):** 2026-09-06T21:13:29Z
- **Clone method:** `git clone --depth 1` (shallow — only this one commit's
  tree is present locally; full upstream history is not fetched)

## Exact source files inspected/used for schema mapping

| file | role | size (bytes) | sha256 | md5 |
|---|---|---|---|---|
| `LinearAInscriptions.js` | primary inscription data (tablet records) | 1,609,137 | `4da8e1f9693d30880ee505e56541fc189add70605bad88436c44a8e11a57764c` | `dc93692f1e2bd6fcffb2ce86293b814c` |
| `annotations.js` | per-word structural/semantic tags, secondary reference for schema mapping only | 2,239,932 | `7ce1f87a98827d059a732cc00506c635b4d5f65b2d0e2f1592fc2b67827758cd` | not recorded (secondary file; recorded if it becomes load-bearing) |

`ideograms.js`, `tags.js`, `explorer.js` and other files in the clone were
noted to exist but were **not inspected in detail** and are **not used** by
this project's adapter — see the licensing note below for why `explorer.js`
specifically is excluded on purpose.

## Document/tablet count (approximate, provenance-level fact only)

**1705** top-level entries in `LinearAInscriptions.js`, counted by a regex
match on the file's `["<ID>",{` key pattern. **This is an approximate,
mechanical count, not a validated parse** — the file is a JavaScript `Map`
literal, not JSON, and a correct count requires evaluating it as JavaScript
(as the external foundation project's `extract_raw.js` does), which this
project has not done in this ingestion-only phase. It differs from the
external foundation project's own reported figures (1721 records / 1621
distinct documents, from their 2026-08-05 snapshot) — **this is expected,
not an error**: different snapshot dates, and a regex key-count is not the
same operation as a full parse that also deduplicates and validates records.
**This count is a DATASET FACT about corpus size for provenance purposes
only; it is not, and must not be read as, any H1 statistic.**

## Version metadata available

No explicit version tag or release number is present in the cloned tree.
The upstream commit hash above is the only available version identifier.
`CNAME` (a GitHub Pages configuration file) and the presence of `charts/`,
`broken/`, and an image-mapping toolchain confirm this is the live
`lineara.xyz` website's own source tree, not a separate data-only export.

## Licensing note — a finding more precise than prior audits, not a policy change

**IMPORTANT, and stated precisely rather than summarized:** `LinearAInscriptions.js`
itself carries an embedded header disclaiming copyright:

> "The author disclaims copyright to this source code. In place of a legal
> notice, here is a blessing: May you do good and not evil. May you find
> forgiveness for yourself and forgive others. May you share freely, never
> taking more than you give."

The same header appears in `tags.js`. **This is different, file-by-file,
from what the earlier feasibility audit and the external foundation
project's `LICENSE.md` reported** ("the upstream repository carries no
LICENSE file... default all rights reserved") — that conclusion was reached
by checking for a repository-level `LICENSE` file (confirmed absent here
too, independently re-checked in this round), not by reading individual
source-file headers. **`explorer.js`, in the same repository, carries a
separate, more restrictive BSD-style copyright notice** ("Copyright (c) 2019
Robert Hogan... All rights reserved... Redistribution and use... permitted
provided that..."), and `annotations.js`/`ideograms.js` carry no visible
header at all. **License status is therefore not uniform across this
repository and must be assessed per file, not assumed repo-wide in either
direction.**

**This finding does not change this project's redistribution policy in this
round.** `data/README.md`'s "fetch locally, never commit" policy for
corpus-derived data remains in force unchanged — revisiting it in light of
this more permissive per-file disclaimer is a separate, deliberate decision
for later, not something this ingestion-only phase acts on unilaterally.

## What was NOT done in this step

No H1 statistic was computed. No KU-RO occurrence was counted beyond a raw
string-literal grep used only to confirm representability (see
`docs/SCHEMA_MAPPING.md`). The upstream clone was not modified.
