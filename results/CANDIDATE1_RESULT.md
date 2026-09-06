# Candidate 1 result: commodity class → fraction-sign presence

**This result is scientifically independent of the frozen KU-RO H1
FAILURE** (`results/H1_RESULT.md`, commit `df2916485fbd97070d869c1fdefd54fdbd4798bd`,
re-verified byte-identical before this run). Nothing here reinterprets,
weakens, or modifies that verdict, and nothing here is a rescue attempt.

## 1. Pre-result freeze commit hash

`f86e4a1af9014cc6b0a18a7ccc0b7affcc7555e2` — **CANDIDATE1_PRE_RESULT_FREEZE**
(`docs/CANDIDATE1_PROTOCOL.md`, `src/constraint_candidate1.py`,
`tests/test_constraint_candidate1.py`; 154/154 synthetic tests passing at
freeze time, re-confirmed byte-identical immediately before this run).

## 2. Corpus provenance

Same primary corpus lineage already used by the frozen H1 run:
`data/generated/lineara_extracted.json` (1721 tablets), via
`src/lineara_adapter.py` (unmodified). No new extraction, no new corpus
source.

## 3. Observational unit

LEVEL B (tablet × commodity class), first-qualifying-occurrence rule, per
`docs/CANDIDATE1_PROTOCOL.md` §2.

## 4. Class definitions

LIQUID = base sign `VIN`/`OLE` (+ligature variants); DRY = base sign
`GRA`/`OLIV` (+ligature variants). Unchanged from the frozen protocol.

## 5. Fraction-presence definition

Associated numeral token's `.fractions` non-empty, confidence-independent.
Unchanged from the frozen protocol.

## 6. Commodity ↔ quantity rule

First following numeral token before an intervening signgroup. Unchanged
from the frozen protocol.

## 7. Adequacy counts (Phase 5 — before any inferential computation)

| | count |
|---|---|
| Raw qualifying commodity occurrences (Level A, all) | 322 |
| — LIQUID | 190 |
| — DRY | 132 |
| Usable occurrences (has resolvable quantity) — LIQUID | 125 |
| Usable occurrences — DRY | 111 |
| Excluded/no-associated-quantity — LIQUID | 65 |
| Excluded/no-associated-quantity — DRY | 21 |
| Unique LIQUID tablets (class represented at all) | 88 |
| Unique DRY tablets | 77 |
| Tablets containing both classes | 32 |
| Tablet-level usable observations (Level B) — LIQUID | 54 |
| Tablet-level usable observations — DRY | 64 |
| Tablet-level `AMBIGUOUS_UNUSABLE` (both classes) | 47 |

Site distribution (usable tablet-level observations): Haghia Triada 82,
Zakros 12, Khania 10, Arkhalkhori 4, Knossos 3, Tylissos 3, Phaistos 2,
Malia 1, Petras 1.

Support/document-type distribution (usable tablet-level observations):
`Tablet` 113, `Clay vessel` 3, `Roundel` 2.

## 8. Exchangeability diagnostics

12 total `(site, support)` strata populated; **5 exchangeable** (both
classes present), **7 nonexchangeable** (single class only). 110 of 118
usable tablet-level observations fall in an exchangeable stratum; **8
excluded** from the primary inferential computation as nonexchangeable
(retained here only descriptively, per `docs/CANDIDATE1_PROTOCOL.md` §12's
predeclared choice — not reassigned, not merged into another stratum).

## 9. Primary numerator/denominator counts

Within exchangeable strata:

| | fraction-present | usable N | rate |
|---|---|---|---|
| LIQUID | 10 | 49 | 0.2041 |
| DRY | 6 | 61 | 0.0984 |

## 10. p_L

**0.20408163265306123** (10/49)

## 11. p_D

**0.09836065573770492** (6/61)

## 12. Δ_obs

**0.10572097691535631** (p_L − p_D)

## 13. Permutation procedure

Site×support-stratified class-label permutation (NULL 3), within the 5
exchangeable strata only, B=2000, two-sided, `p = (extreme + 1)/(B + 1)`.

## 14. Deterministic seed

**20260906** — **ENGINEERING REPRODUCIBILITY CHOICE**, not a scientific
tuning parameter (`docs/CANDIDATE1_PROTOCOL.md` did not freeze a specific
integer; the choice of seed cannot change which strata are exchangeable or
which rows are usable, only which of the equally-valid permutation draws
are sampled).

## 15. Permutation p-value

**p_perm = 0.19390304847576212**

## 16. Effect sizes

- **Primary:** Δ_obs = **+0.1057** (10.6 percentage points, LIQUID higher)
- Rate ratio (p_L / p_D): **2.075**
- Odds ratio: **2.350** (all four cells nonzero, no correction needed)

## 17. Sensitivity analyses

| sensitivity | N_L | N_D | p_L | p_D | Δ | p_perm | status |
|---|---|---|---|---|---|---|---|
| A — raw occurrence-level | 125 | 111 | 0.184 | 0.135 | +0.049 | — | DESCRIPTIVE ONLY (not predeclared for inference — pseudo-replication risk) |
| B — primary tablet-level | 49 | 61 | 0.204 | 0.098 | +0.106 | 0.194 | primary result (restated) |
| C — probable-same-artifact collapse | 42 | 49 | 0.190 | 0.102 | +0.088 | 0.381 | INFERENTIAL (3 tablet-pairs excluded as within-artifact outcome conflicts) |
| D — Haghia Triada only | 39 | 43 | 0.179 | 0.093 | +0.086 | 0.304 | INFERENTIAL |
| E — bare base-sign only (no ligature) | 30 | 44 | 0.200 | 0.091 | +0.109 | 0.299 | INFERENTIAL |

Direction (LIQUID > DRY) is consistent across every sensitivity, including
the descriptive one; magnitude is fairly stable (Δ ≈ 0.05–0.11); no
sensitivity reaches p < 0.05.

**Sensitivity C collapse rule (engineering completion of an already-frozen
concept, disclosed explicitly, not a new tunable choice):**
`docs/CANDIDATE1_PROTOCOL.md` froze `physical_artifact_key` but not an
explicit multi-face-outcome-agreement rule. Applied here: group usable
Level-B observations by (physical-artifact key, class); if all faces agree
on outcome, use that outcome as the one collapsed unit; if faces disagree,
exclude the pair from Sensitivity C (3 such conflicts found, reported, not
hidden). This rule is mechanical and outcome-blind-until-collapse (it
checks agreement, it does not pick whichever outcome is convenient).

## 18. Opportunity-bias diagnostic (Phase 10)

Occurrence-count per tablet, by class (Level A, all tablets with ≥1
occurrence of that class, not restricted to usable/exchangeable):

| | N tablets | mean | median | Q1 | Q3 | max |
|---|---|---|---|---|---|---|
| LIQUID | 88 | 2.16 | 1.0 | 1.0 | 3.0 | 13 |
| DRY | 77 | 1.71 | 1.0 | 1.0 | 2.0 | 7 |

LIQUID tablets carry somewhat more occurrences per tablet on average (2.16
vs. 1.71; max 13 vs. 7) — this is exactly the kind of asymmetry that would
have inflated a naive "ANY-occurrence" rule's LIQUID rate relative to DRY
purely from opportunity count. The frozen first-qualifying-occurrence rule
appears to have been a materially important design choice, not a
theoretical nicety: given this asymmetry, an ANY-based rule would likely
have produced an even larger, and less trustworthy, apparent Δ_obs than the
one actually observed. This diagnostic does not change the frozen result.

## 19. Site-dominance diagnostic (Phase 11)

Of the 49 usable exchangeable-stratum LIQUID observations, **39 (79.6%)**
are from Haghia Triada; of the 61 DRY observations, **43 (70.5%)** are from
Haghia Triada. Both classes are HT-dominated, to a broadly similar degree.
Sensitivity D (HT-only: Δ=0.086, p=0.304) shows the effect direction
persists but does not strengthen when restricted to HT alone — **the
primary result is not simply an artifact of one class being HT-heavy while
the other is not**, since both are comparably HT-heavy; it also cannot be
said to generalize confidently beyond HT, since HT supplies the large
majority of both classes' usable observations.

## 20. Physical-object dependence sensitivity

See Sensitivity C (§17): Δ narrows from 0.106 to 0.088 and p rises from
0.194 to 0.381 under artifact-level collapse — consistent with, not
contradicting, a null association; collapsing reduces N substantially
(49→42 LIQUID, 61→49 DRY), which alone would widen a permutation p-value
even under an unchanged true effect.

## 21. Ligature sensitivity

See Sensitivity E (§17): restricting to bare base-sign forms only
(excluding all `+`-ligature variants) leaves Δ_obs essentially unchanged
(0.109 vs. 0.106) and p_perm unchanged in substance (0.299 vs. 0.194,
both far from significance) despite a large drop in N (79 vs. 110 usable
rows) — no evidence that ligature-variant inclusion drives the result.

## 22. Circularity / external-model audit (Phase 13)

**Classification: PARTIAL EVIDENTIAL DEPENDENCE.**

The LIQUID/DRY commodity-*identity* assignment (`VIN`=wine, `OLE`=oil,
`GRA`=grain, `OLIV`=olive) rests on sign-shape and functional homology with
Linear B (`docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md` item 7) — this part
is genuinely independent of any Linear-A-internal fraction/arithmetic
pattern; it was established from Linear B's own bilingual/administrative
context, not from observing Linear A numerals.

However, the broader *expectation* that liquid and dry commodities use
distinguishable measurement/fractional conventions (the reason Candidate 1
was considered worth testing at all, per `docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md`
items 3–6, 8) is itself partly derived from observing exactly this kind of
differential fractional/subunit notation in the sibling, deciphered script
Linear B, then imported to Linear A "by provisional homology." A positive
Candidate 1 result would therefore be **partly a rediscovery of an
already-known cross-script typological pattern**, not a fully independent
new finding — this is a real, disclosed dependency, not a fatal one (it
does not reach SUBSTANTIAL CIRCULARITY or CIRCULAR — the commodity
identity itself does not depend on Linear A's fraction data, and no
feedback loop exists within this corpus), but it means a significant
result here should not be read as strong independent confirmation of the
broader constraint-intersection hypothesis on its own. **This audit was
performed regardless of the (non-significant) outcome, per instruction.**

## 23. Epistemic interpretation

**Constraint-intersection level supported: LEVEL 0** — no detectable
constraint from this specific test (p_perm = 0.194 ≥ α = 0.05). The
observed direction (LIQUID somewhat higher fraction-presence than DRY) is
consistent across every predeclared sensitivity, which is worth noting
descriptively, but consistency-in-direction-without-significance does not
establish even LEVEL 1 ("individual structural association detected") —
that requires crossing the predeclared inferential threshold, which did
not happen in any of the five predeclared analyses.

## 24. Limitations

- The first-qualifying-occurrence rule, while resistant to opportunity
  bias (§18 confirms the bias it guards against was real), discards
  most of the corpus's raw occurrence information (322 raw occurrences →
  110 exchangeable tablet-level observations); Sensitivity A (raw
  occurrence-level, descriptive) shows a smaller Δ (0.049), consistent
  with — not contradicting — the tablet-level null result.
- 7 of 12 site×support strata (8 of 118 usable observations) could not
  contribute to inference at all (single-class strata) — a modest but
  real loss of usable evidence, predeclared as the correct handling
  rather than tuned after the fact.
- Both classes are heavily Haghia-Triada-dominated (~70–80%); this project
  cannot speak to whether the (null) result would hold at other sites with
  adequate power — no other site individually meets the ≥10/≥10 adequacy
  gate.
- Per §22, a hypothetical significant result here would itself carry a
  disclosed partial circularity; this limitation is reported even though
  it did not end up being decisive, since the audit was required
  regardless of outcome.

## 25. Exact verdict

**CANDIDATE 1 NOT SUPPORTED**

(p_perm = 0.194 ≥ α = 0.05; adequacy gate passed, so this is not
INCONCLUSIVE — the test was adequately powered by its own predeclared
standard and did not cross the predeclared significance threshold.)

---

## Broader constraint-program update (Phase 18)

**BROAD CONSTRAINT PROGRAM: NO UPDATE**

Candidate 1 is one of five preregistered candidates
(`docs/CONSTRAINT_HYPOTHESIS_CANDIDATES.md`); it returned a non-significant
result, consistent in direction but not reaching the predeclared threshold
in any of five sensitivities, over an adequately powered primary sample.
This provides no positive evidence for the broader constraint-intersection
program, but — per the same discipline already applied to the KU-RO
FAILURE — it also does not, by itself, falsify the broader program: it
falsifies only this one specific, narrow candidate constraint. The four
other predeclared candidates (`docs/CONSTRAINT_HYPOTHESIS_CANDIDATES.md`
§ shortlist) remain untested and are not affected by this result.

## Information-theoretic description (Phase 15 — SECONDARY DESCRIPTIVE)

Computed only as a secondary descriptive quantity, over the same primary
110-row exchangeable-stratum 2×2 table (§9), unconditional (no
stratification, no conditional entropy, no higher-order interaction — none
of that is introduced in this round, per instruction):

**I(COMMODITY_CLASS ; FRACTION_PRESENCE) ≈ 0.0160 bits**, versus
H(FRACTION_PRESENCE) ≈ 0.598 bits — commodity class accounts for
**≈2.7%** of the entropy in fraction-presence in this sample. This is a
small quantity, consistent with the non-significant permutation result;
it is descriptive only and played no role in the primary p-value.

## Adversarial result audit (Phase 19)

**Strongest argument AGAINST treating this as evidence for the constraint
program:** it isn't evidence for the program at all — p_perm=0.194 is a
null result under the study's own predeclared standard; the consistent
positive direction across sensitivities is a weak, non-dispositive
descriptive observation, not a finding, and could easily be residual
confounding by unmeasured factors (scribal practice, tablet condition,
specific transaction size) that happen to correlate loosely with commodity
class without any real class→fraction constraint existing.

**Strongest argument FOR treating this as evidence (of something, not of
the broad program):** the direction is unusually consistent — the same
sign, roughly the same magnitude, across the raw-occurrence level, the
primary tablet level, artifact-collapsed data, HT-restricted data, and
ligature-restricted data — five independent slices of the same
underlying pattern, which is at least suggestive that the tablet-level
sample (N=110) may simply be underpowered to detect a real but modest
effect (Δ≈0.09–0.11), rather than the null being exactly true; a larger or
differently-stratified future sample could resolve this, though that is a
statement about statistical power, not a claim this study is entitled to
make as a result.

Neither argument is privileged over the other in this document.
