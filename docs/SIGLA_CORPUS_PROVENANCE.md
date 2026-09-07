# SigLA corpus provenance (data acquisition)

**No raw SigLA data is reproduced in this file** — metadata only, per this
project's established policy (`data/README.md`).

## Source

- **URL:** `https://sigla.phis.me/database.js`
- **Retrieval method:** direct HTTP GET, no authentication, independently
  verified reachable this session (`curl`, HTTP 200).
- **Retrieval timestamp:** 2026-09-06T21:49:48Z
- **Server-reported version:** `Last-Modified: Fri, 26 Jun 2026 06:18:15 GMT`
  (this is the only version signal the server provides; SigLA publishes no
  separate release/version number for this endpoint as far as this project
  found).

## File facts

- **Size:** 2,516,528 bytes
- **sha256:** `cc624f148fd84c94fd2910b0adf92ecace25f52f9175664122bdf8384a8f1b9d`
- **md5:** `871bcfe6663d7db361c9a97dbdad8766`
- **Local path (gitignored, never committed):** `data/raw/sigla/database.js`

## Format

A JavaScript source file defining two variables, `signs` and `data`, each a
single-quoted JS string literal. The content is **not** plain decimal-escaped
octets (an earlier working assumption, corrected once tested against the
real file): it is the OCaml runtime's own string-escaping convention
(`Printf "%S"` / `String.escaped` style — literal printable-ASCII runs mixed
with `\NNN` 3-digit-decimal escapes and standard mnemonic escapes `\\ \" \'
\n \t \r \b`), itself wrapped inside ordinary JS single-quote string
escaping (only `\` needs protecting at that outer layer). Both layers must
be unwound in sequence to recover the raw bytes, which are then OCaml
`Marshal` binary-format blobs (magic number `0x8495A6BE`, confirmed as the
first 4 bytes of both decoded blobs).

## Record/document count

**NEW EMPIRICAL RESULT (schema-verification only, not an H1 statistic):**
the `data` blob decodes to an OCaml `Map.t` (standard-library balanced
binary tree, `Empty=0` / `Node(l,k,v,r,h)` as a 5-field block) keyed by
document ID string. **802 documents**, independently matching the earlier
external foundation project's own reported figure for the same live
endpoint — a strong correctness cross-check for this project's
independently-written decoder, not itself relied upon as ground truth.

**License:** CC BY-NC-SA 4.0 (confirmed directly on the site and in the
published paper; see `docs/SIGLA_PROVENANCE_AUDIT.md` item 3). This
project's fetch is for non-commercial research use; `data/raw/sigla/` is
gitignored and will never be committed, matching this project's existing
policy for the primary corpus.

## Retrieval/build procedure (exact, reproducible)

```bash
mkdir -p data/raw/sigla
curl -s -o data/raw/sigla/database.js https://sigla.phis.me/database.js
```

Decoding requires this project's own independently-written decoder
(`src/ocaml_marshal_decoder.py`) — no third-party OCaml-Marshal library was
used. Decoder correctness basis: (a) 8 hand-constructed byte sequences,
each verified by hand against the documented Marshal tag-byte layout, all
pass; (b) applied to the real `signs` blob, the declared `num_objects`
header field matched the decoder's own object count *exactly* (2535 = 2535);
(c) applied to the real `data` blob, decoding consumed the **entire**
declared body with zero leftover bytes, and produced immediately plausible,
domain-correct content (real tablet IDs, "Haghia Triada", "LM IB" period
notation, a genuine `cefael.efa.gr` GORILA-scan URL) on first successful
run. **OPEN, disclosed rather than hidden:** the `data` blob's declared
`num_objects` (56734) is smaller than the decoder's own object count
(57063) by 329 (~0.58%). The leading hypothesis, not fully confirmed: OCaml
does not count zero-size block "atoms" (e.g. empty-list literals) toward
this header field the way this decoder's registration logic does, since
atoms are shared static singletons requiring no fresh allocation on the
reading side — this would not indicate corruption, only a difference in
what is counted. Given (a)-(c) above, this project treats the decoder as
validated for the purposes of the present schema-audit phase, while
recording this discrepancy honestly rather than silently resolving it.

No OCaml runtime was available in this environment to cross-check the
decoder against a reference implementation; correctness rests on (a)-(c)
above and the documented, stable OCaml Marshal specification.
