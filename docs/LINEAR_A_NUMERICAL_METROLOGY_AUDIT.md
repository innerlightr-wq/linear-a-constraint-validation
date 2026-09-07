# External scholarship audit — numerals, fractions, metrology, commodities

**Phase 2 of the constraint-geometry research branch.** Purpose: know which
numerical/metrological relationships are already established scholarship
(so this project never presents rediscovery as a new result) and which are
genuinely open. Web research this session, not exhaustive; classifications
below are this project's own reading of what was found, not a claim of
complete literature coverage. Labels: ESTABLISHED SCHOLARSHIP, SUPPORTED
BUT CONTESTED, PROPOSED INTERPRETATION, UNKNOWN/OPEN.

## 1. Numeral system

Aegean scripts (Linear A and B) use an additive, base-10, non-positional
numeral notation (distinct signs/strokes for 1, 10, 100, 1000, with
repetition for multiples) — **ESTABLISHED SCHOLARSHIP**, part of the
long-standing consensus on the script family, consistent with the plain
decimal-string values already observed directly in `mwenge`.

## 2. Fraction signs and proposed values

The specific numeric values (binary: 1/2, 1/4, 1/8; sexagesimal-compatible:
1/10, 1/20, 1/30, 1/40, 1/60) are Corazza, Ferrara, Montecchi, Tamburini &
Valério (2021, *Journal of Archaeological Science* 125), via constraint
programming, statistical, and typological methods — **SUPPORTED BUT
CONTESTED**, not flatly ESTABLISHED: the paper's own framing (per this
round's search) notes the two hardest problems it addresses — every
document with both fractional sums *and* a registered total was damaged or
difficult to interpret, and some sign uses are inconsistent in a way
suggesting **the system may have changed over time**. The values are a
best-supported reconstruction via optimization, not a directly, unambiguously
attested table. **Direct, load-bearing implication for this project's own
constraint hypotheses**: any inter-record test assuming a *static* fraction
system across the whole corpus (all sites, all periods) risks importing an
unstated, contested assumption — worth testing *as* a hypothesis (does the
fraction system look uniform across site/period strata?) rather than
assuming it.

## 3–6. Metrological systems (liquid, dry/grain, weight)

Distinct liquid/dry/weight metrological systems are well-established for
Bronze Age Aegean societies generally, from architectural, ceramic-volume,
and balance-weight studies (multiple independent research programs found
this round) — **ESTABLISHED SCHOLARSHIP** at the level of "such systems
existed and differed." **However**, the search results found this round
describe **different, autonomous measurement systems that coexisted with
their own internal developments** (i.e. not a single unified Aegean-wide
metrology), and note Cretan measures specifically show site-level variation
(e.g. reported "heavy" ~65g vs. "light" ~61g Minoan weight standards). The
*specific sign-level* mapping from a Linear A ideogram to a metrological
system is **PROPOSED INTERPRETATION**, imported via provisional Linear B
homology (see item 8) — not independently, directly established for Linear
A's own undeciphered readings.

## 7. Commodity ideograms

Directly attested, standard mnemonic transliterations (`GRA`, `VIN`, `OLE`,
`OLIV`, etc.) — **ESTABLISHED SCHOLARSHIP** as sign identities (this is the
GORILA/Ventris-tradition transliteration convention itself, not a
contested reading). What each ideogram *denotes* semantically (grain, wine,
olive oil) is likewise broadly **ESTABLISHED**, again via the Linear-B
homology methodology named explicitly in this round's search results:
*"When scholars can confidently identify a sign as both graphically and
functionally equivalent in Linear A and Linear B, and when the Godart–Olivier
corpus and subsequent scholarship securely establish its meaning in Linear
B, that meaning can be provisionally applied to Linear A."* **The word
"provisionally" is load-bearing** — this is not the same epistemic status
as a directly-read Linear A meaning, and this project must not present it
as such.

## 8. Known commodity-class × measurement-system associations

**PROPOSED INTERPRETATION**, per item 3–6 and item 7 together: the
convention that grain-class ideograms imply a dry-measure system and
liquid-class ideograms (wine, oil) imply a liquid-measure system rests on
the same provisional Linear-B-homology methodology, not a Linear-A-internal
demonstration. Usable as a **positive-control hypothesis** (see
`docs/CONSTRAINT_NULL_MODELS.md`, Phase 8) precisely because it is
well-supported enough that failing to recover it would cast doubt on this
project's own methodology, while still being honestly labeled short of
"established beyond question."

## 9. Known arithmetic-closure examples

`ku-ro` = "total," `po-to-ku-ro` = "grand total," both **SUPPORTED BUT
CONTESTED** readings resting substantially on internal arithmetic
consistency (tablets whose own numbers close) rather than external
bilingual confirmation — this is the exact same evidentiary basis already
scrutinized at length by this project's own frozen H1 test, which found the
`ku-ro` positional/arithmetic claim **FAILS** under the primary corpus. This
project's own H1 result is therefore now **relevant primary evidence** on
this exact scholarly question, not merely an external citation — stated
here for completeness, not to relitigate it (per this round's explicit
instruction not to attempt to rescue KU-RO).

## 10. Known subtotal/total structures — a specific, checkable example

This round's search surfaced a specific, well-documented nested-arithmetic
claim: tablet **HT 122**, reportedly `ku-ro 31` + `ku-ro 65` = `po-to-ku-ro
97` (with a noted "+1 carried unit," since 31+65=96, not 97) — offered in
the literature as a worked demonstration of hierarchical `ku-ro`/`po-to-ku-ro`
accounting. **SUPPORTED BUT CONTESTED**, and worth flagging honestly: this
project's own already-completed primary H1 extraction independently
classified **both** `HT122a` and `HT122b` as `UNEXPLAINED_MISMATCH`
(`results/h1_occurrence_audit.csv`, cross-checked in
`results/EVIDENCE_DEPENDENCE_AUDIT.md` §3, where `HT122` was one of the
identified same-artifact face-pairs). **This is a genuine, specific,
checkable tension between a claim in the wider literature and this
project's own independent reconstruction — noted here, not resolved.**
Resolving it would require directly re-examining `HT122`'s po-to-ku-ro
occurrence specifically, which is out of scope for this documentation-only
round (doing so now would be exactly the kind of "another KU-RO
computation" this round's instructions prohibit).

## 11. Known numerical ordering conventions

Category/commodity → quantity → (repeated per entry) → total-marker →
grand-total is the broadly described administrative tablet template in
general treatments of Aegean accounting — **ESTABLISHED SCHOLARSHIP** as a
*typical* pattern, not a universal rule (both source papers this project
has already audited, and the external sources found this round, describe
exceptions and variation, e.g. headings without their own quantity).

## 12. Known administrative document templates

Formulaic, repeated per-site administrative structure is a broadly accepted
characterization in the literature consulted (and matches this project's
own direct observation of highly repetitive record shapes across `mwenge`)
— **ESTABLISHED SCHOLARSHIP** at the qualitative level; no specific
quantitative template-recurrence study was found or attempted this round.
