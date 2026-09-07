# Evidence-dependence audit (primary corpus, KU-RO)

**The primary H1 FAILURE remains the frozen result** (`results/H1_RESULT.md`,
commit `df2916485fbd97070d869c1fdefd54fdbd4798bd`). **This audit evaluates
the strength and independence of the evidence supporting that result** —
it does not recompute, reinterpret, or challenge the verdict itself. No
predeclared view in this audit rescues, weakens the falsification of, or
otherwise changes the frozen verdict.

## 1. Original occurrence-level H1 result (unchanged, cited not recomputed)

Positional: N=37, non-terminal rate 37.84% (falsified per the paper's own
criterion). Arithmetic: N_testable=26, unexplained-mismatch rate 38.46%
(falsified per the project's own declared band). Verdict: **FAILURE**.

## 2. Tablet-level evidence structure (LEVEL 2)

| | occurrence level | tablet level |
|---|---|---|
| N (positional) | 37 | 34 unique tablets |
| N (arithmetically testable) | 26 | 26 (identical — see below) |
| mismatch count | 10 | 10 |
| mismatch rate | 38.46% | 38.46% |

Tablet classification (predeclared, `docs/EVIDENCE_DEPENDENCE_PROTOCOL.md`):
**ALL_SUPPORT = 16, ALL_MISMATCH = 10, MIXED = 0, UNTESTABLE = 8** (sums to
34). Three tablets carry two KU-RO occurrences each (`HT25b`, `HT123+124a`,
`HT127b`); in every one of the three, one occurrence is `NOT_TESTABLE` and
the other is the tablet's sole testable outcome — so, **in this specific
dataset, deduplicating occurrences to tablets leaves the arithmetic rate
numerically unchanged** (26/26 testable, 10/10 mismatch, both levels). This
is a real, checked finding, not an assumption that dedup never matters.

## 3. Duplicate/dependence findings (LEVEL 3)

No exact duplicate tablet IDs found (structurally precluded by the
corpus's own construction). **Found: 5 candidate same-physical-artifact
face-pairs** among the 34 KU-RO-bearing tablets — `HT11(a,b)`, `HT122(a,b)`,
`HT123+124(a,b)`, `HT94(a,b)`, `HT9(a,b)` — identified by the standard
GORILA recto/verso face-letter convention. Classified **PROBABLE SAME
ARTIFACT** (well-established scholarly convention, not individually
re-verified against primary plates by this project — full confirmation is
**DOMAIN-EXPERT DEPENDENT**). `HT123+124` additionally carries a "+"-joined
compound catalog number, meaning its underlying fragment-join judgment is
separately **DOMAIN-EXPERT DEPENDENT**. The remaining 24 tablets show no
candidate dependence pattern under base-ID grouping — classified
**DISTINCT** (best-supported, not proven with certainty).

**Outcome agreement within pairs, checked directly, not assumed:**

| pair | face outcomes | agree? |
|---|---|---|
| HT11 | a=MISMATCH, b=SUPPORT | **disagree** |
| HT122 | a=MISMATCH, b=MISMATCH | agree |
| HT123+124 | a=[untestable,MISMATCH], b=MISMATCH | agree |
| HT94 | a=SUPPORT, b=SUPPORT | agree |
| HT9 | a=MISMATCH, b=SUPPORT | **disagree** |

Two of five probable-same-artifact pairs show a genuine support/mismatch
disagreement between faces — collapsing these to one physical-object unit
each would classify them **MIXED**, not cleanly one-sided, at the
physical-object level.

## 4. Confidence limitations (predeclared strata, applied to all 37 KU-RO occurrences)

**DAMAGED/UNCERTAIN = 0, MISSING FRACTION INFORMATION = 5, SECURE = 21,
OTHER UNRESOLVED = 11** (the 11 are `NOT_TESTABLE`-excluded occurrences,
neither damaged nor fraction-involving). Zero damaged occurrences means the
damage dimension had no measurable effect on this result, one way or the
other — stated plainly, not silently omitted. The 5 fraction-involving
occurrences: `HT13`, `HT104` (both already-classified support, matching
Paper 1's own worked examples), `HT9a`, `HT46a`, `HT123+124a` (all three
already-classified mismatch).

## 5. Site concentration (tablet level, LEVEL 2, corroborating the occurrence-level finding)

| site | tablets | occurrences | testable | support | mismatch |
|---|---|---|---|---|---|
| Haghia Triada | 32 | 35 | 26 | 16 | 10 |
| Phaistos | 1 | 1 | 0 | 0 | 0 |
| Zakros | 1 | 1 | 0 | 0 | 0 |

**100% of arithmetically testable tablets and occurrences are from Haghia
Triada, confirmed at both levels** — not an occurrence-level double-counting
artifact.

## 6. Fraction-information sensitivity (Phase 7, all five predeclared views)

| view | N_testable | mismatch | rate |
|---|---|---|---|
| 1. All occurrence-level records (primary result) | 26 | 10 | **38.5%** |
| 2. Unique-tablet weighting (one row per tablet) | 26 | 10 | **38.5%** |
| 3. Secure-only subset | 21 | 7 | **33.3%** |
| 4. Excluding fraction-affected records | 21 | 7 | **33.3%** |
| 5. `HT9a` treated as unresolved (excluded, not mismatch) | 25 | 9 | **36.0%** |

**Every predeclared view remains above the 20% new-project-specific
arithmetic-falsification threshold — none were selected because they looked
favorable; all five are reported.** Views 3 and 4 coincide exactly in this
dataset (a consequence of zero damaged occurrences, not a computational
shortcut).

**Independent-unit collapse (LEVEL 3, physical-object level, using the
face-pair finding in §3):** collapsing the 5 probable-same-artifact pairs
to one unit each yields **29 defensible independent units** (13
ALL_SUPPORT, 6 ALL_MISMATCH, 2 MIXED, 8 UNTESTABLE). Mismatch rate under
every reasonable treatment of the 2 MIXED units:

| treatment of MIXED units | mismatch rate |
|---|---|
| excluded entirely | 31.6% |
| split 0.5/0.5 | 33.3% |
| counted as support (best case for H1) | **28.6%** |
| counted as mismatch (worst case for H1) | 38.1% |

**Even the most favorable-to-H1 treatment (28.6%) remains well above the
20% falsification threshold.**

## 7. Whether the FAILURE remains qualitatively robust

**Yes.** The arithmetic component's falsification (rate > 20%) survives
every predeclared sensitivity view in this audit — occurrence-level,
tablet-level, secure-only, fraction-excluded, HT9a-excluded, and
physical-object-collapsed-under-every-MIXED-treatment. The positional
component's falsification (non-terminal rate 37.84% vs. a 10% bar) was not
separately re-audited at the dependence level in this round, but is
untouched by anything found here.

## 8. Whether confidence in its magnitude changes

**Somewhat, modestly, and only in the direction of appearing less extreme,
never toward support.** The raw occurrence-level rate (38.5%) is the
highest figure across every predeclared view; secure-only and
fraction-excluded views both land at a materially lower but still-falsifying
33.3%; the most favorable physical-object-level treatment lands at 28.6%.
The magnitude of the mismatch rate is therefore somewhat sensitive to which
evidence-counting convention is used (a ~10-point range across all views,
38.5% down to 28.6%), but **the qualitative conclusion — falsification —
does not change under any of them.**

## 9. What cannot be resolved without domain expertise

Whether the 5 candidate same-artifact face-pairs are genuinely one physical
object each (standard convention, not individually re-verified against
GORILA plates); whether `HT123+124`'s fragment join is archaeologically
accepted; whether any specific `UNEXPLAINED_MISMATCH` case reflects damage
this project's bracket-parsing missed, a genuine scribal/metrological
discrepancy, or a mis-sectioned block; whether Haghia Triada's near-total
dominance of the testable sample reflects a genuine feature of KU-RO usage
or an artifact of this specific source's uneven site coverage (already
flagged in `results/H1_RESULT.md` §16, unresolved here too).
