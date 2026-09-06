# Data adequacy audit — `lineara.xyz` vs. the frozen H1 protocol

**No H1 verdict is computed here.** This classifies whether each field the
frozen protocol (`docs/H1_PROTOCOL.md`) requires is implementable from the
raw corpus schema (`docs/SCHEMA_MAPPING.md`), using the labels: AVAILABLE /
DERIVABLE / AMBIGUOUS / MISSING (and BLOCKED / DOMAIN-EXPERT DEPENDENT for a
field that cannot be completed without material this project does not have
and will not invent).

## Field-by-field classification

| protocol requirement | classification | basis |
|---|---|---|
| Tablet identifier | **AVAILABLE** | Map key / `name` field |
| Token order | **AVAILABLE** | `transliteratedWords` array order |
| KU-RO / KI-RO / PO-TO-KU-RO identification | **AVAILABLE**, via the protocol's own declared fallback (§1) | exact transliteration-string match; GORILA sign IDs themselves are MISSING from this source (see `SCHEMA_MAPPING.md`), but the protocol explicitly anticipated this exact contingency |
| §2 TERMINAL / NEAR-TERMINAL / NON-TERMINAL classification | **DERIVABLE** | computable directly from ordered, typed tokens once N1/N3 normalization is applied — no blocking gap |
| §3 associated numeral (whole-number component) | **AVAILABLE** | direct decimal-string tokens |
| §3 associated numeral (fractional component, value) | **DERIVABLE** | Unicode fraction-glyph merging (N2), confirmed against one real example (1/2) during schema mapping; 8 further glyphs constructed by the same pattern, individually unconfirmed — see `SCHEMA_MAPPING.md` |
| §3 fraction **confidence grading** (`secure`/`derived` admission) | **MISSING** | not present in this raw source at all — see consequence below, stated plainly, not hidden |
| §4 Rule A block boundary (ruling signal specifically) | **MISSING** (corrected after the first real-corpus run — see `SCHEMA_MAPPING.md` N1) | `"\n"` was tried as a ruling proxy, then found to appear between every entry, not only true section boundaries — using it as a ruling emptied every preceding block. Not a blocker: this source's absence of a ruling signal is a valid degenerate case of Rule A, which still functions via its other two boundary conditions |
| §4 Rule A block boundary (prior-total / start-of-tablet, overall) | **DERIVABLE** | fully functional once the ruling-signal correction above was applied; confirmed against the real corpus (H1 driver run) |
| §4 Rule B commodity-heading boundary | **BLOCKED / DOMAIN-EXPERT DEPENDENT** | see dedicated section below — required by instruction, not invented from `ideograms.js` or any other source |
| §6 DAMAGED exclusion | **DERIVABLE** | bracket/`?`-character parsing, confirmed working against a real attested example (`TE+RO[`, tablet HT104) and against 21 synthetic tests |
| §6 AMBIGUOUS exclusion (disputed sign **identity**, distinct from physical damage) | **MISSING** | this source does not distinguish "reading disputed" from "text broken/incomplete" — both surface as the same bracket/`?` convention. The adapter therefore never marks `sign_identity_uncertain`; every flagged case falls under DAMAGED instead. This is a conservative simplification, documented, not silently absorbed |
| §6 MISSING exclusion | **DERIVABLE** | mechanical, once numeral/block extraction runs |
| §6 NO_IDENTIFIABLE_TOTAL | **DERIVABLE** | mechanical (tablet has sign-groups, zero target occurrences) |
| §6 NON_COMPARABLE (Rule A vs. B disagreement) | **BLOCKED**, as a direct consequence of Rule B being blocked | `kuro_protocol.classify_exclusion` already degrades gracefully when `block_tokens_b` is not supplied (verified by the pre-data-freeze synthetic tests) — no crash risk, just an honest scope limit until Rule B is unblocked |
| Site/archive metadata | **AVAILABLE** | `site`, `findspot` fields (bonus: `scribe`, `context`/period also present, beyond what the protocol strictly requires) |

## Rule B: intentionally left BLOCKED, as instructed

The Rule B commodity-ID set was deliberately left unspecified in
`src/kuro_protocol.py` (no default `COMMODITY_IDS`) when the protocol was
frozen, and remains unspecified now. `data/raw/lineara_xyz/ideograms.js`
exists in the cloned upstream tree and **was noted but not opened for this
purpose** — populating Rule B from it (or from any other source, including
prior projects' own commodity lists) would require separate, explicit
justification and documentation this project has not done. **Rule B is
therefore marked BLOCKED / DOMAIN-EXPERT DEPENDENT, exactly as instructed,
and is not filled in.**

This does not block H1 itself: the frozen protocol's §11 verdict depends
only on Rule A's results (Rule B is reported "side by side" as a robustness
check, per §4, never as a requirement for the verdict). **H1 remains fully
computable on Rule A alone.**

## The fraction-confidence-grading finding, stated plainly

Because this raw source supplies no confidence grade for any fraction
reading, and the frozen protocol's §3 rule requires `secure` or `derived`
grading before a fraction contributes to a numeral's value, **every
fraction-bearing numeral drawn from this source alone will currently resolve
to unrelated-to-confidence-grade `None` contribution from its fractional
part** unless a supplementary, explicitly cited confidence source (e.g.
Corazza et al. 2021's published grades, as the external foundation project
uses) is incorporated in a later phase. Concretely: a composite value like
"45 + ¹⁄₂" will resolve to whole-number `45.0` only, with the ¹⁄₂ component
present in the `fractions` list but not counted, **because its confidence is
unset, not because it is graded `open`/contested** — the frozen protocol's
own text already specifies this exact behavior for an unadmitted fraction
("if it is the only candidate value present, the numeral is treated as
absent"; here there IS a whole-number component too, so the numeral is not
absent, but the fractional remainder is dropped). **This is a mechanical,
correct application of the already-frozen §3 rule to a harsher-than-hoped
data-adequacy fact — not a protocol incompatibility, and not silently
patched.** It will make KU-RO's true arithmetic residuals appear larger than
they would with confidence-graded fractions properly admitted, for any
tablet whose total or block entries include a fractional component. This is
flagged here for the record and for whoever runs the real analysis next; it
is not resolved in this ingestion phase.

## Verdict: does the frozen protocol remain implementable, unchanged?

**Yes.** No genuine corpus-schema incompatibility was discovered that makes
implementation of the frozen H1 protocol impossible. Two real, honestly
documented limitations exist (fraction-confidence grading is MISSING;
sign-identity-uncertain vs. physical-damage is not distinguishable), and one
feature is deliberately BLOCKED pending domain input (Rule B) — **none of
these required, and none received, any change to `docs/H1_PROTOCOL.md`'s
definitions, thresholds, verdict rules, sample definitions, or target
roles.** The protocol as frozen at commit `5aae796f71245e359c2fb72d5b01b81f72d44288`
stands unmodified.
