# SigLA schema mapping

Findings from decoding and directly inspecting the real `data`/`signs`
blobs (via this project's own `src/ocaml_marshal_decoder.py`), to the depth
needed to determine implementability of the frozen H1 protocol
(`docs/H1_PROTOCOL.md`) — **schema mapping only, no H1 statistic computed.**
Individual short attested strings (single tablet IDs, single syllable
transliterations) are cited below as ordinary scholarly/technical citation,
consistent with this project's existing practice for `mwenge`; no
substantial transcription content is reproduced.

## Raw structure, as decoded

`data` decodes to an OCaml `Map.t` (standard balanced binary tree: `Empty=0`,
`Node(l,k,v,r,h)` as tag-0, 5-field blocks) keyed by document-ID string
(e.g. `"HT 13"`, `"ARKH 1a"` — **note the space** between site code and
number, unlike `mwenge`'s `"HT13"`). Each value is a nested tuple containing:
document metadata (support/type, id, site, several optional fields, an
`Option<(height,width,thickness)>` dimensions triple, `Option<period>`,
`Option<source-URL>`), a path-like string (`"document/HT 13"`), a
word-grouping substructure, image pixel dimensions, and an **ordered array
of per-sign attestation records**, each carrying a bounding box
(`[x,y,w,h]` in pixels on the document image) and an index.

The separate `signs` blob decodes to a `Map.t` keyed by an integer
(transnumeration number within a sign class), value = a 9-field record:
`[sign_class (e.g. "AB"), sign_number, Option<Option<(transliteration,
homophone_index)>>, Option<citation_reference>, field5..field9]`. Directly
observed example: sign `AB 21` carries `Option("OVIS")` in its 5th field —
the Latin logogram gloss "sheep", i.e. this source appears to carry
**logogram-meaning annotations** for at least some signs, a richer signal
than `mwenge` provides directly. Whether this specific field slot is used
consistently is **OPEN** — not exhaustively surveyed in this session.

## Field-by-field mapping

| protocol need | raw representation | status |
|---|---|---|
| tablet/document identifier | `Map` key string (e.g. `"HT 13"`) | **AVAILABLE** |
| site/archive | present in the per-document metadata tuple (e.g. `"Haghia Triada"`, `"Arkhanes"`) | **AVAILABLE** |
| sign-group ordering | per-document array of sign-attestation records, each carrying a positional index | **AVAILABLE** |
| KU-RO / KI-RO / PO-TO-KU-RO | **not stored as a single joined string anywhere** — confirmed by direct search (zero matches for the literal strings) — but the **individual syllable transliterations are directly present** (e.g. `"ku"`, `"ro"` both independently confirmed as attested sign transliterations on tablet `HT 13`, which is known from the primary-corpus result to bear a KU-RO occurrence) | **AMBIGUOUS** — downgraded from an earlier DERIVABLE classification after real-document validation (Task 6, schema-resolution round): the ordered-sign-sequence extraction this depends on (`_collect_indexed_entries`) was tested against real document "HT 13" and found to return 129 spurious "entries" for a ~15-syllable tablet (index value 1 repeated 44 times; implausible outlier indices 704/705, almost certainly misidentified pixel bounding-box coordinates). The syllables themselves ARE present in the source; this project does not yet have a validated, reliable method to recover their true document order or true word-grouping, so a target match cannot currently be trusted to reflect genuine word-adjacency rather than an artifact of over-broad pattern matching. See `docs/SIGLA_DATA_ADEQUACY_AUDIT.md`, Gate A. |
| numerals | **OPEN** — not directly located in this session's sampling of sign/document records; the sign records inspected carry transliteration and citation fields but no numeral value was confirmed in the fields sampled | **OPEN** |
| fractions | the SigLA paper's own interface description (`docs/SIGLA_PROVENANCE_AUDIT.md` item 10) confirms fractions are a distinctly color-coded, first-class sign-function category ("orange for fractions") | **AMBIGUOUS** — function-tag identity confirmed to exist conceptually; which of the 9 sign-record fields encodes it, and whether a numeric *value* is stored or must be looked up externally (as with `mwenge`), is **OPEN**, not confirmed this session |
| fraction certainty | SigLA's own paper describes a question-mark convention for "doubtful reading or unreadable" and a separate erasure category (item 9, `SIGLA_PROVENANCE_AUDIT.md`) | **AMBIGUOUS** — the *existence* of a certainty signal is SOURCE-DERIVED FACT; whether it is graded (matching Corazza et al.'s secure/derived/open scheme) or only binary (certain vs. doubtful-or-unreadable) is not confirmed; which specific field encodes it was not identified this session |
| damaged readings | same question-mark convention as above | **AMBIGUOUS**, same reasoning |
| uncertain readings | same | **AMBIGUOUS**, same reasoning |
| reconstructed readings | not confirmed present or absent in this session's sampling | **OPEN** |
| line/ruling boundaries | not confirmed — the per-document sign array carries positional bounding boxes (pixel coordinates), which is a *different* kind of positional signal than `mwenge`'s line-break tokens, and was not tested for ruling-equivalent semantics | **OPEN** — likely requires either the bounding-box geometry or the word-grouping structure to approximate, neither confirmed sufficient this session |
| section boundaries | not confirmed | **OPEN** |
| commodity headings | **not investigated this session** — per this project's own instruction not to implement Rule B, and to keep any future Rule-B work separately labeled, this was deliberately not pursued | **OPEN, DELIBERATELY NOT PURSUED** (Rule B scope) |
| reading certainty (general) | see fraction/damage/uncertain rows above | **AMBIGUOUS** |
| duplicate/reconstructed readings | joined-tablet notation exists in both sources but with **different conventions** (`mwenge`: `"HT123+124a"` as one compound ID; SigLA: `"HT 123a"` and `"HT 124a"` observed as apparently-separate keys in a spot check) — whether SigLA has its own explicit reconstruction/join marker elsewhere was not confirmed | **DOMAIN-EXPERT DEPENDENT** whether these should be treated as the same physical evidence |

## What this means for the frozen protocol

**Updated after real-document validation (Task 6, schema-resolution round)
— no protocol incompatibility was found, but the earlier "not blocked"
reading of the target-identification step was premature.** Tablet ID and
site are confirmed AVAILABLE, correctly extracted from real data (see the
`iter_documents` option-wrapper fix below). Ordered sign sequence,
however — the prerequisite for target-string identification — is **not yet
reliably extractable**: the only method implemented so far
(`_collect_indexed_entries`'s loose structural heuristic) was tested
directly against a real document and demonstrably returns spurious,
duplicated, and implausible entries. This is not a claim that the frozen
protocol is incompatible with SigLA — it is a claim that this project does
not yet have a validated way to supply the protocol with a faithful ordered
sign sequence for this source. No change to `H1_PROTOCOL.md` is implied or
needed; the gap is entirely on the adapter side.

**A separate, real bug was found and fixed in this same validation round:**
`iter_documents` originally treated each document's raw Map value as the
5-field document tuple directly; real data showed the Map value is actually
`Some(doc_tuple)` — one extra OCaml `option` layer. This was masked by the
project's own earlier synthetic tests, whose fixtures modeled the unwrapped
shape directly (a lesson square with the primary corpus's own earlier
`\n`-as-ruling incident: synthetic tests validate the *code's own logic*
correctly, but cannot substitute for real-document validation of *schema
assumptions*). Fixed; site/period now correctly extract from real data
(confirmed: `HT 13` → site `"Haghia Triada"`, period `"LM IB"`).

**What remains genuinely open, honestly, rather than resolved by
assumption:** numeral value extraction, fraction-value extraction and
confidence grading, and any ruling/section-boundary signal are **not yet
confirmed** from this source. `src/sigla_adapter.py` implements what is
confirmed (document iteration, site/metadata extraction, syllable-level
transliteration extraction and word-adjacency detection for target
identification) and leaves the unconfirmed pieces unimplemented rather than
guessed — documented explicitly in `docs/SIGLA_DATA_ADEQUACY_AUDIT.md`.
