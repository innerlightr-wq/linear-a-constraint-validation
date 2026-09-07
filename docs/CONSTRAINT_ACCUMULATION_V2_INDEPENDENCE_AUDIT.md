# Constraint-accumulation V2: predictor independence matrix

**Status: DESIGN AUDIT ONLY.** No V2 inference of any kind has been run.
This document distinguishes **statistical correlation** (what an
accumulation experiment is allowed to discover) from **construction
dependence** (what must be excluded or explicitly modeled, per
`results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md`).

| predictor | raw source | derivation | uses Y directly? | shares parser state with Y? | external semantic input? | potential circularity | leakage classification | authorized for V2? |
|---|---|---|---|---|---|---|---|---|
| `C_SITE` | raw `site` field on the tablet dict | `site_block`: casefold + collapse to {Haghia Triada, OTHER} | No | No — read from tablet metadata, entirely separate from token parsing | No | None identified | INDEPENDENT STRUCTURAL INFORMATION | **Yes**, unchanged from V1 |
| `C_SUPPORT` | raw `support` field | `support_block`: casefold + collapse to {Tablet, OTHER} | No | No — tablet metadata | No | None identified | INDEPENDENT STRUCTURAL INFORMATION | **Yes**, unchanged from V1 |
| `C_POSITION` | token order within a record | `position_bucket`: ordinal rank among qualifying commodity occurrences, 1-indexed | No | Reads token *order*/index only, never `.fractions` or `.value` | No | None identified — position is computed before, and without reference to, either the commodity's class or the numeral's content | DERIVED STRUCTURAL INFORMATION | **Yes**, unchanged from V1 |
| `C_COMMODITY` | commodity signgroup's sign-id string | `commodity_class`: base-sign match against frozen LIQUID/DRY families (Candidate 1, unchanged) | No | No — reads the signgroup token's `sign_ids`, a field entirely distinct from the numeral token's `.value`/`.fractions` | **Yes** — LIQUID/DRY grouping is imported via provisional Linear-B homology, not fit to this dataset | The semantic *label* is externally imported (not corpus-internal circularity, but an external-model dependency) | EXTERNAL MODEL INFORMATION | **Yes** — retained as a predeclared control block (see `docs/CONSTRAINT_ACCUMULATION_V2_DESIGN.md` §"Reconsidering M3"), not for its own sake |
| `integer_value` (raw `numeral.value`) | numeral token's `.value` field | Set only in the `is_numeral_string` adapter branch (§2, validity audit) | No — reading `.value` never requires reading `.fractions` | **Structurally entangled for one subcase**: whether `.value` ends up `None` depends on whether a fraction glyph immediately followed with no preceding numeral — the *same* raw-token adjacency fact that also determines whether `.fractions` gets populated on that token | No | **Yes, proven (validity audit §4–5): `value is None ⟹ fraction_present is True`, exactly, by construction** | **CONSTRUCTION INFORMATION** (for the "is it None" question) / independent for its resolved numeric content | **Existence check ("is it None") used only for V2's Y-independent population *inclusion* rule** (§"V2 population", design doc) — **never as a V2 predictor category on its own** |
| `C_MAGNITUDE` (V2) | `integer_value`, restricted to rows where it is resolved (not `None`) | `log2(1 + integer_value)`, a fixed, non-fitted transform (see design doc §"Magnitude representation") | No | No — computed purely from the resolved numeric value, never from `.fractions` | No | **None found**, conditional on the population already excluding the `NO_INTEGER_VALUE` subcase entirely (so the deterministic sub-relationship from the `integer_value` row above cannot re-enter through this predictor) | POTENTIALLY INDEPENDENT NUMERICAL INFORMATION — pending confirmation only insofar as the population-inclusion rule itself is re-examined (§"V2 population" independence questions, design doc) | **Yes**, as the primary M4 representation, pending the population-level caveat already disclosed (design doc) |

## Distinguishing correlation from construction dependence, explicitly

- `C_SITE`, `C_SUPPORT`, `C_POSITION`: any association found between these
  and `Y` in V2 would be genuine **statistical correlation** — nothing in
  their derivation reads any field that `Y` also reads.
- `C_COMMODITY`: any association found would be genuine correlation
  *conditional on* the external LIQUID/DRY label being a valid semantic
  grouping — not a construction dependence, but not fully independent of
  outside scholarship either (see EXTERNAL MODEL INFORMATION, restated in
  `docs/CONSTRAINT_INFORMATION_TYPES.md`).
- `integer_value`'s raw `None`/not-`None` distinction is **construction
  dependence**, proven exactly (not probabilistically) in
  `results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md` §4–5 — this is
  precisely why V2 excludes it as a predictor category and instead uses it
  only to define population membership, and even that use carries its own
  disclosed residual caveat (design doc).
- `C_MAGNITUDE`: once restricted to the integer-resolved population, its
  value is computed from `.value` alone, never `.fractions` — no
  construction dependence found. Any V2 finding about `C_MAGNITUDE` would
  be genuine correlation, **not** a repeat of V1's construction artifact.
