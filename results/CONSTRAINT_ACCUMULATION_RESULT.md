# Constraint-accumulation result (real, primary corpus)

**This is the real result of the frozen constraint-accumulation experiment,
run exactly once.** Protocol frozen at
`docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md`, commit
`2f58a7c80c173f538c758596ce94aa353d1ca07c`
(`CONSTRAINT_ACCUMULATION_PRE_RESULT_FREEZE`); harness archived at commit
`de3bc6159082c49ffce5adfcaa00e04ec4730be6`
(`CONSTRAINT_ACCUMULATION_HARNESS_COMMIT`). This experiment is
scientifically independent of, and does not reinterpret, weaken, or
rescue: the frozen KU-RO H1 **FAILURE** (`results/H1_RESULT.md`), or the
frozen Candidate 1 **NOT SUPPORTED** result
(`results/CANDIDATE1_RESULT.md`).

## A. Provenance

| | |
|---|---|
| Protocol freeze SHA | `2f58a7c80c173f538c758596ce94aa353d1ca07c` |
| Harness commit SHA | `de3bc6159082c49ffce5adfcaa00e04ec4730be6` |
| Corpus path | `data/generated/lineara_extracted.json` |
| Corpus SHA-256 | `219b52569cab75b58e95afb0a969689c6c50f753ce690321f20abbaff3a8eff8` |
| Seed | `20260906` (ENGINEERING REPRODUCIBILITY CHOICE) |
| B | `2000` |
| Timestamp (UTC) | `2026-09-06T23:55:01Z` |

**Pre-result implementation interpretation (recorded before this run, per
Phase 2 of this round):** per-step category adequacy
(`docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md` §11) is applied to the newly
introduced block at each incremental step (position for M2, commodity for
M3, numeric for M4); previously admitted blocks retain their prior
evaluability status and are not re-checked at later steps. Not a new
hypothesis; not altered after seeing results.

## B. Adequacy

| | |
|---|---|
| N (usable rows) | **236** |
| Unique tablets | **94** |
| Positives (Y=1) | **38** |
| Negatives (Y=0) | **198** |
| Primary adequacy gate | **PASS** (236≥150, 94≥50, 38≥30, 198≥30) |
| CV folds used | **5** (primary — evaluable, no fallback needed) |
| Site counts | Haghia Triada 169, OTHER 67 |
| Support counts | Tablet 231, OTHER 5 |
| Position counts | FIRST 94, SECOND 46, THIRD_OR_LATER 96 |
| Commodity counts | LIQUID 125, DRY 111 |
| M2 evaluable | **YES** |
| M3 evaluable | **YES** |
| M4 evaluable | **YES** |

No step was `NOT_EVALUABLE` in this run — all three non-baseline
increments produced a real p-value.

## C. Model performance (`H_hat`, bits, out-of-fold log loss)

| model | H_hat |
|---|---|
| H0 | 0.650660 |
| H1 | 0.672504 |
| H2 | 0.680827 |
| H3 | 0.692870 |
| H4 | **0.516238** |

## D. Increments (`ΔH`, bits)

| step | ΔH | direction |
|---|---|---|
| ΔH1 (M0→M1) | −0.021844 | HARMS *(descriptive only — M1 is baseline, not evidentiary)* |
| ΔH2 (M1→M2, position) | −0.008323 | HARMS |
| ΔH3 (M2→M3, commodity) | −0.012044 | HARMS |
| ΔH4 (M3→M4, numeric) | **+0.176632** | **IMPROVES** |

## E. Inference

| step | raw p | Holm-adjusted p | verdict |
|---|---|---|---|
| M2 (position) | 0.654173 | 1.000000 | **NOT SUPPORTED** |
| M3 (commodity) | 0.931034 | 1.000000 | **NOT SUPPORTED** |
| M4 (numeric) | 0.000500 | **0.001499** | **SUPPORTED** |

α = 0.05. Holm family = {M2, M3, M4}, all evaluable, all three retained
regardless of sign (per the Phase 1 correction — M2 and M3's negative
`ΔH` did not exempt them from the family or from receiving a real p-value).

## F. Primary scientific verdict

**BROAD PROGRAM UPDATE: WEAK POSITIVE UPDATE**

(exactly one non-baseline block — M4 — is Holm-supported; M2 and M3 are
not. Mechanically exact application of the frozen rule
(`docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md` §16). See §H below for why
this mechanical verdict requires a major, disclosed interpretive caveat.)

## G. Limitations

- **Haghia Triada concentration:** 169/236 (71.6%) of usable rows are from
  Haghia Triada. No cross-site generalization claim is made.
- **Artifact-dependence sensitivity:** **PENDING — PREDECLARED BUT NOT YET
  IMPLEMENTED** in the harness (`docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md`
  §13). The primary result stands under its frozen primary (tablet-grouped)
  design regardless of this pending follow-up.
- **M3 external-domain dependence:** `C_COMMODITY` (LIQUID/DRY) is EXTERNAL
  DOMAIN MODEL INPUT (provisional Linear-B homology). M3 was **NOT
  SUPPORTED** here — consistent with, and cross-validating, Candidate 1's
  own independent marginal-association null finding
  (`results/CANDIDATE1_RESULT.md`, p_perm=0.194).
- **M4 numeric-bin circularity — see §H, the most important finding of
  this round.**

## H. Critical interpretive finding: M4's significance is substantially a construction artifact, not (only) a magnitude effect

**This section does not change the mechanically-computed verdict above —
M4 is, and remains reported as, SUPPORTED under the frozen protocol. This
section reports what that verdict most likely means, per this round's own
required adversarial audit (Phase 16) and interpretation firewall (Phase
11, LEVEL 2).**

`C_NUMERIC`'s `NO_INTEGER_VALUE` category is **tautologically entangled**
with `Y` by construction of the underlying token representation
(`src/lineara_adapter.py`): a numeral token's `numeric_value` is `None`
**if and only if** it was created via the fraction-only code path, which
**always** carries a non-empty `.fractions` list. A purely descriptive,
marginal check (not a new inferential test, not crossed with any other
predictor) confirms this directly:

| | fraction_present=True | fraction_present=False |
|---|---|---|
| `numeric_value is None` (17 rows) | **17 (100%)** | 0 |
| `numeric_value` resolved (219 rows) | 21 | 198 |

**All 17 of 17** `NO_INTEGER_VALUE` rows have `fraction_present=True` — by
definition, not by any empirical corpus pattern — and these 17 rows alone
account for **17 of the 38 total positives (44.7%)**.

Restricted to the 219 rows that **do** have a resolvable integer value
(excluding `NO_INTEGER_VALUE` entirely), the marginal fraction-presence
rate is roughly **flat** across the remaining three bins:

| bin | fraction-present rate |
|---|---|
| SMALL | 10.8% (8/74) |
| MEDIUM | 11.1% (8/72) |
| LARGE | 6.8% (5/73) |

No clear magnitude gradient. **M4's large, Holm-significant `ΔH4` is
therefore very likely driven substantially — plausibly predominantly — by
this structural artifact of how the source represents fraction-only
numerals, not by a genuine "quantity magnitude predicts fraction usage"
relationship.**

The permutation test itself is not malfunctioning: it correctly detects
that the real pairing between `numeric_bin` (including its
`NO_INTEGER_VALUE` category) and `Y` is far stronger than any
within-stratum reshuffling of `Y` could produce by chance — because in the
real data that category is a near-perfect predictor of `Y`, by
construction. The p-value is mechanically correct; what it is measuring is
not what "numerical magnitude" was intended to capture.

**Per this round's explicit firewall, no rebinning, category merge,
conditioning change, or protocol modification was made in response to
this finding.** It is reported, not acted on. A future, separately
frozen protocol revision could define `C_NUMERIC` (or a replacement
feature) in a way that does not structurally entangle "no integer value"
with fraction presence — that is a design question for a future round,
not resolved here.

## I. Stacked-correlation audit (Phase 12, interpretive only — does not alter verdicts)

1. **Was M1 much stronger than later blocks?** No — M1 itself was
   slightly *negative* (ΔH1=−0.022): site/support alone did not help
   held-out prediction at all in this run.
2. **Did M2/M3/M4 add genuine incremental information?** M2 and M3: no
   (both negative, both non-significant). M4: apparently yes by the
   numbers, but see §H — likely substantially a construction artifact.
3. **Are positive increments extremely small?** No — M4's increment
   (+0.177 bits) is large relative to the other steps, which is itself
   part of why §H's explanation (a near-deterministic sub-category) is
   the more parsimonious account than a genuine graded magnitude effect.
4. **Does site/support concentration plausibly explain later features?**
   Not directly implicated here — the M4 effect traces to a token-
   representation artifact, not to site/support confounding.
5. **Are any later blocks nearly redundant?** M2 and M3 both slightly
   *hurt* held-out prediction relative to their predecessor — consistent
   with redundant or noise-adding blocks, not with genuine independent
   signal.
6. **Did a later block improve raw ΔH but fail its conditional null?**
   No — the pattern here is the reverse framing doesn't quite apply: M2
   and M3 both had *negative* raw ΔH (never "improved" to begin with).
7. **Progressive accumulation, stacked correlation, or something else?**
   **Neither, primarily.** This is best described as a **third pattern**:
   a **structural/construction artifact** in one feature's category
   definition, not genuine progressive accumulation (M2/M3 added nothing,
   and M4's apparent addition is mostly definitional) and not stacked
   correlation around archive/site context (site/support explained
   nothing either). The cleanest honest label for this run is: **no
   genuine accumulation demonstrated; one large but substantially
   artifactual association found and disclosed.**

## J. Adversarial result audit (Phase 16)

1. **Could a positive result be driven by HT concentration?** Checked:
   the M4 effect is not obviously HT-specific (no HT-vs-OTHER breakdown
   was computed this round beyond the marginal site counts already
   reported — this specific cross-check was not run, consistent with the
   firewall against generating new tests in this audit).
2. **Could M3 merely encode imported semantic assumptions?** M3 was **NOT
   SUPPORTED** — moot for M3 specifically in this run.
3. **Could conditional-null sparsity distort inference?** No sparsity was
   encountered — all three steps were fully evaluable; the concern that
   materialized instead was the §H artifact, a different issue from
   sparsity.
4. **Are effect sizes practically tiny despite significance?** The
   opposite concern applies here: the effect is large, and precisely
   *because* it is unexpectedly large for a "magnitude" feature, it
   warranted the scrutiny in §H that found the artifact.
5. **Did one fold dominate the average?** Not specifically checked this
   round (would require a new per-fold breakdown not computed here).
6. **Is the result stable in sign across folds?** Not specifically
   checked this round.
7. **Did M1 absorb nearly all predictable structure?** No — M1 itself
   added no held-out information (§I item 1).
8. **Are later blocks genuinely conditional additions?** M2/M3: yes, in
   the sense of being tested conditionally, but they added nothing. M4:
   the *test* is genuinely conditional; the *feature* itself is
   compromised (§H).
9. **Does any claim exceed the frozen target Y?** No claim beyond
   `FRACTION_SIGN_PRESENCE` is made anywhere in this document.
10. **Would a skeptical statistician agree the stated verdict follows from
    the protocol?** Yes for the mechanical verdict (WEAK POSITIVE UPDATE
    follows exactly from the frozen rule given these numbers) — and yes
    that the same skeptical statistician would immediately flag §H as the
    reason not to treat this as strong evidence for the broader
    constraint-accumulation hypothesis.

## K. Interpretation firewall (Phase 11) — explicit level statements

- **LEVEL 1 (predictive result):** Position added no held-out information
  (ΔH2<0). Commodity added no held-out information (ΔH3<0). Numeric
  magnitude showed a large, Holm-significant apparent improvement
  (ΔH4>0, p_holm=0.0015) — but see LEVEL 2.
- **LEVEL 2 (structural interpretation):** **NOT supported as a genuine
  "numerical magnitude constrains fraction usage" finding.** The
  apparent M4 effect is substantially attributable to a tautological
  sub-category (§H), not to a graded magnitude relationship — the
  residual signal among magnitude-resolved rows (SMALL/MEDIUM/LARGE) is
  small and non-monotonic (10.8%/11.1%/6.8%).
- **LEVEL 3 (external domain model input):** M3's LIQUID/DRY grouping was
  NOT SUPPORTED in this run — no claim of conditional predictive
  usefulness of the imported commodity grouping is made (the opposite:
  it appears to add no information here, beyond what Candidate 1 already
  found).
- **LEVEL 4 (cognitive/historical interpretation):** **Not made.** Nothing
  in this experiment licenses any claim about Minoan abstract arithmetic,
  inverse-number cognition, metrological intent, semantic decipherment,
  or administrative purpose.
