# Schema mapping — `LinearAInscriptions.js`

Findings from inspecting the raw corpus structure, to the depth needed to
determine implementability of the frozen H1 protocol (`docs/H1_PROTOCOL.md`)
— **schema mapping only, no H1 statistic computed.** No raw corpus content
is reproduced here beyond the minimum single-token examples needed to
justify a mapping decision (consistent with ordinary scholarly citation of
individual attested forms, not corpus reproduction).

## Raw structure

`LinearAInscriptions.js` defines `var inscriptions = new Map([...])` — a
JavaScript `Map` literal, not JSON (confirmed by direct inspection; matches
the external foundation project's own documented finding for the same
source). Each entry: `[tabletID, {fields...}]`.

Per-tablet fields observed: `context` (period), `facsimileImages`,
`findspot`, `imageRights`, `imageRightsURL`, `images`, `name`, `names`,
`parsedInscription` (raw Unicode glyphs, one physical-line-wrapping),
`scribe`, `site`, `support` (medium, e.g. `"Tablet"`), `transcription` (raw
Unicode glyphs, alternate line-wrapping), `translatedWords` (semantic
glosses — e.g. `"owed"`, `"olive oil"` — **interpretation, not
transcription**), `transliteratedWords` (ASCII transliteration, one array
element per word/numeral/separator/line-break, in original order), `words`
(raw Unicode glyph clusters, positionally parallel to `transliteratedWords`).

## Field-by-field mapping

| protocol need | raw representation | status |
|---|---|---|
| tablet/document identifier | the Map key itself (e.g. `"HT1"`) | **AVAILABLE** |
| sign-group order | `transliteratedWords` array, order-preserving | **AVAILABLE** |
| numeral representation | plain decimal-string tokens (e.g. `"197"`) inline in `transliteratedWords` | **AVAILABLE** |
| fraction representation | a **separate, adjacent** array element carrying a Unicode fraction glyph (e.g. `"¹⁄₂"`) immediately following a whole-number token — composite values are split across two list positions, not one combined token | **DERIVABLE** — requires an adapter rule to detect and merge an adjacent recognized fraction-glyph token onto the preceding numeral (documented as Normalization Rule N2 below) |
| fraction confidence grading (protocol §3: `secure`/`derived`/`open`) | **not present in this raw source at all** — no confidence/certainty field accompanies fraction tokens | **MISSING** from this source specifically. Per the external foundation project's own documented approach, confidence grading would need to be **derived from Corazza et al. (2021)'s published table as a separate, explicitly cited input**, not invented — this is additional work, out of scope for this ingestion-only phase, and is a real, honest data-adequacy gap, not silently patched |
| section/line/ruling markers | `"\n"` appears as its own array element wherever the transcription breaks to a new physical line | **AMBIGUOUS** — see Normalization Rule N1 below; not confirmed identical to a GORILA-sense incised ruling |
| word-internal separator | `"𐄁"` (U+10101), independently confirmed via `annotations.js`'s own per-word tag `"word separator"` | **AVAILABLE**, but is **not** a structural boundary in the protocol's sense — filtered out, not treated as content or as a ruling (Normalization Rule N3) |
| damage/uncertainty representation | embedded **within** transliterated word strings as bracket characters, e.g. `TE+RO[` (attested, tablet HT104) — no separate structured boolean field found in `LinearAInscriptions.js` | **DERIVABLE** via string-pattern parsing (`[`, `]`, `?` and combinations), following the same documented convention the external foundation project's `build_corpus.py` uses (independently reimplemented, not copied). `annotations.js`'s tag vocabulary was not exhaustively inventoried in this pass and may offer a cleaner structured signal — **OPEN**, not relied upon |
| site/archive field | `site` and `findspot` fields, directly present per tablet | **AVAILABLE** (bonus: `scribe` and `context`/period are also directly present, beyond what the protocol requires) |
| KU-RO / KI-RO / PO-TO-KU-RO representability | present as **literal ASCII transliteration strings** in `transliteratedWords`. Literal occurrences of each target transliteration were observed during schema inspection, confirming that KU-RO, KI-RO, and PO-TO-KU-RO are representable in this source. Raw grep counts were deliberately omitted from the frozen ingestion record because they are unparsed, potentially duplicated across source representations, and are not the validated per-target samples defined by H1_PROTOCOL.md §9. | **AVAILABLE via the protocol's own declared fallback (§1)** — see below |
| GORILA canonical sign identifiers (protocol §1's *preferred* matching method) | **not present anywhere in this raw source** — no `AB081`/`AB002`-style identifiers exist in `LinearAInscriptions.js` | **MISSING**. This is exactly the situation `H1_PROTOCOL.md` §1 already anticipated and declared a fallback for — **not a protocol incompatibility, no STOP required.** |

> **PRE-ANALYSIS DISCLOSURE:** During schema inspection, crude literal-string
> grep counts for the three target transliterations were observed by the
> research workflow before the formal H1 analysis. These counts were
> unparsed, undeduplicated, and unclassified and therefore are not H1
> statistics. They were not used to modify `H1_PROTOCOL.md`, its thresholds,
> sample definitions, exclusion rules, or verdict rules. The frozen H1
> protocol remains commit `5aae796f71245e359c2fb72d5b01b81f72d44288`.

## Whether token normalization is needed

**Yes**, in four specific, now-documented ways (the adapter, `src/lineara_adapter.py`, implements exactly these and no others):

- **N1 — line breaks as sectioning boundaries.** `"\n"` tokens are mapped to
  the protocol's `Token(kind="ruling")` slot, as the closest available proxy
  for a structural boundary. **Caveat, stated plainly:** this is an
  operational choice, not a confirmed equivalence — a transcription line
  break is not guaranteed to coincide with a physical incised ruling in the
  GORILA epigraphic sense. This is an implementation-level adapter decision
  within the frozen protocol's existing `ruling` concept (§4), not a change
  to the protocol itself.
- **N2 — adjacent fraction-glyph merging.** A recognized Unicode fraction
  glyph token immediately following a numeral token is merged into that
  numeral's `fractions` list, with `confidence` left **unset/absent** rather
  than invented, since the raw source supplies no grading (see the MISSING
  row above) — an adapter-level numeral with no admitted-confidence fraction
  correctly resolves to `None` per `kuro_protocol.numeral_value`, which is
  the mathematically correct behavior given real data-adequacy limits, not a
  special case.
- **N3 — word-separator filtering.** `"𐄁"` tokens are dropped entirely (not
  represented as any `Token` in the adapter's output) — confirmed, not
  assumed, to be a word-internal separator via `annotations.js`'s own tag.
- **N4 — target-sequence matching via transliteration string, not sign ID.**
  Per `H1_PROTOCOL.md` §1's declared fallback, `KU-RO`/`KI-RO`/`PO-TO-KU-RO`
  are matched as exact transliteration strings against `transliteratedWords`
  elements. **This fact — that GORILA sign-ID matching is unavailable for
  this source and the fallback is load-bearing, not a backup — is logged
  explicitly per the protocol's own requirement ("this fact will be logged
  per-tablet, not silently absorbed"), not just noted here once.**

No normalization beyond these four rules is introduced. No semantic
interpretation (`translatedWords`) is used anywhere in the adapter.
