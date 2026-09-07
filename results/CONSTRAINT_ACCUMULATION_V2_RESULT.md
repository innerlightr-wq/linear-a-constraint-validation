# Constraint accumulation V2 result (real, primary corpus)

**This is the real result of the frozen V2 experiment, run exactly
once.** Protocol frozen at
`docs/CONSTRAINT_ACCUMULATION_V2_PROTOCOL.md`, commit
`931fd5905ec3c67f526b108452ec9c355c1b0048`
(`CONSTRAINT_ACCUMULATION_V2_PRE_RESULT_FREEZE`); harness archived at
commit `e48e01c67b5a5023c8824364b4be1d1b1a38f5d0`
(`CONSTRAINT_ACCUMULATION_V2_HARNESS_COMMIT`). V2 is scientifically
independent of, and does not reinterpret, weaken, or rescue: the frozen
KU-RO H1 **FAILURE**, the frozen Candidate 1 **NOT SUPPORTED** result, or
the frozen V1 accumulation result (mechanical **WEAK POSITIVE UPDATE**,
scientifically qualified as substantially compromised by deterministic
construction dependence — `results/CONSTRAINT_ACCUMULATION_RESULT.md`).

## Provenance

| | |
|---|---|
| V2 protocol freeze SHA | `931fd5905ec3c67f526b108452ec9c355c1b0048` |
| V2 harness commit SHA | `e48e01c67b5a5023c8824364b4be1d1b1a38f5d0` |
| Corpus path | `data/generated/lineara_extracted.json` |
| Corpus SHA-256 | `219b52569cab75b58e95afb0a969689c6c50f753ce690321f20abbaff3a8eff8` (identical to V1's — same corpus lineage, confirmed, not assumed) |
| Seed | `20260906` |
| B | `2000` |
| CV folds | `5` (protocol §6 — no 3-fold fallback exists for V2) |
| Timestamp (UTC) | `2026-09-07T00:38:29Z` |

## Population

Include row iff `numeric_value is not None` (checked without ever reading
`.fractions`) — a **conditional population** (quantities ≥1 whole unit),
not compared inferentially to the excluded fraction-only rows.

| | |
|---|---|
| N | **219** |
| Unique tablets | **89** |
| Positives (Y=1) | **21** |
| Negatives (Y=0) | **198** |
| Positive tablets | 16 (unchanged from the blocker audit — same population) |
| Haghia Triada proportion | **157/219 = 71.7%** |
| Site counts | Haghia Triada 157, OTHER 62 |
| Support counts | Tablet 214, OTHER 5 |
| Position counts | FIRST 87, SECOND 41, THIRD_OR_LATER 91 |
| Commodity counts | LIQUID 114, DRY 105 |
| `WHOLE_COMPONENT_MAGNITUDE` range | **[1.0, 9.932]** bits (integer values 1–976) |

## Adequacy (all four frozen criteria)

| criterion | classification | result |
|---|---|---|
| A — every training fold has both classes | MATHEMATICAL/ENGINEERING REQUIREMENT | **PASS** |
| B — ≥5 minority rows per training fold | PROJECT-SPECIFIC SAFEGUARD (power) | **PASS** (min training-fold positives: 15) |
| C — ≥50% mixed strata at M3→M4 | PROJECT-SPECIFIC SAFEGUARD (power) | **PASS** (10/14 = 71.4% mixed) |
| D — coarse N/tablet screen | PROJECT-SPECIFIC SAFEGUARD (weak) | **PASS** (219≥150, 89≥50) |

**Overall adequacy: PASS.** 5-fold `GroupKFold` used, exactly as frozen —
no fallback needed or available.

**Fold-level support (descriptive):**

| fold | train N | train pos | train neg | test N | test pos | test neg |
|---|---|---|---|---|---|---|
| 0 | 175 | 15 | 160 | 44 | 6 | 38 |
| 1 | 175 | 18 | 157 | 44 | 3 | 41 |
| 2 | 175 | 15 | 160 | 44 | 6 | 38 |
| 3 | 175 | 18 | 157 | 44 | 3 | 41 |
| 4 | 176 | 18 | 158 | 43 | 3 | 40 |

(Identical to the blocker audit's pre-registered diagnostic — confirms no
drift between design-time and run-time population.)

## Model performance (`H_hat`, bits)

| model | H_hat |
|---|---|
| H0 | 0.461096 |
| H1 | 0.467832 |
| H2 | 0.483787 |
| H3 | 0.500792 |
| H4 | 0.501364 |

## Increments (`ΔH`, bits)

| step | ΔH | direction |
|---|---|---|
| ΔH1 (M0→M1) | −0.006736 | HARMS *(descriptive — M1 baseline, not evidentiary)* |
| ΔH2 (M1→M2, position) | −0.015956 | HARMS |
| ΔH3 (M2→M3, commodity) | −0.017005 | HARMS |
| ΔH4 (M3→M4, whole-component magnitude) | **−0.000572** | **HARMS (essentially zero)** |

**Critical observation: `ΔH4` is negative and negligibly small in
magnitude (~0.0006 bits) — the opposite of, and utterly unlike, V1's
`ΔH4 = +0.1766`.** Once the deterministic `NO_INTEGER_VALUE` construction
channel is removed by design (not by post-hoc exclusion — it was never
part of the V2 population to begin with), the magnitude predictor shows
**no meaningful signal at all**.

## Permutation inference

Frozen conditional permutation (B=2000, seed=20260906), unconditional on
sign — every step received a real p-value.

| step | ΔH_obs | raw p | Holm-adjusted p | verdict |
|---|---|---|---|---|
| M2 (position) | −0.015956 | 0.919040 | 1.000000 | **NOT SUPPORTED** |
| M3 (commodity) | −0.017005 | 0.985507 | 1.000000 | **NOT SUPPORTED** |
| M4 (magnitude) | −0.000572 | 0.211894 | 0.635682 | **NOT SUPPORTED** |

α = 0.05. Holm family = {M2, M3, M4}, all evaluable, all three retained
regardless of sign — none reaches significance.

## Frozen V2 verdict

**BROAD PROGRAM UPDATE: NEGATIVE UPDATE**

- Did M2 qualify? **No.**
- Did M4 qualify? **No.**
- Did the accumulation criterion (M2 **and** M4 both `SUPPORTED`) fire?
  **No — neither individually qualifies, so the joint criterion cannot
  fire.**

Mechanically exact application of the frozen rule
(`docs/CONSTRAINT_ACCUMULATION_V2_PROTOCOL.md` §11): adequate, valid
experiment; among the evaluable blocks, none is `SUPPORTED`.

## Information-type interpretation

- **M1 (site/support):** archival/context baseline, never evidentiary —
  itself slightly harmed held-out prediction (`ΔH1 = −0.0067`).
- **M2 (position):** DERIVED STRUCTURAL INFORMATION — **NOT SUPPORTED**;
  adds no held-out information about fraction presence within this
  population.
- **M3 (commodity):** EXTERNAL MODEL INFORMATION — **NOT SUPPORTED**;
  consistent with, and now triply cross-validated against, Candidate 1's
  own marginal null (p=0.194) and V1's own conditional null.
- **M4 (whole-component magnitude):** POTENTIALLY INDEPENDENT NUMERICAL
  INFORMATION — **NOT SUPPORTED**; `log2(1 + integer_value)` carries
  essentially no predictive information about fraction-sign presence
  among quantities ≥1 whole unit.

## V1 → V2 comparison (the most important cross-check of this round)

**Did the apparent magnitude signal survive removal of the
`NO_INTEGER_VALUE` construction channel? No — it collapsed almost
entirely.** V1's M4: `ΔH4 = +0.176632`, Holm p = 0.0015, `SUPPORTED`.
V2's M4 (same underlying magnitude concept, cleaned population):
`ΔH4 = −0.000572`, Holm p = 0.636, `NOT SUPPORTED`. This is exactly the
outcome `results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md` predicted on
structural grounds (the flat, non-monotonic SMALL/MEDIUM/LARGE marginal
rates already found in V1, 10.8%/11.1%/6.8%) — now confirmed by an
independent, prospectively-designed, differently-scoped experiment, not
merely inferred descriptively. **The raw `ΔH` magnitudes are not
directly comparable as if the two populations were identical — V1's
N=236/38-positive population and V2's N=219/21-positive population are
different estimands (V2 excludes the 17 rows that were, by construction,
100% positive) — but the qualitative conclusion is unambiguous: whatever
predictive power V1's `C_NUMERIC` appeared to carry was not a genuine
magnitude effect.**

## Limitations

- **Scope:** this result is scoped to quantities ≥1 whole unit
  (protocol §2) — it says nothing about fraction-only (sub-unit)
  expressions, which remain a distinct, untested population.
- **Haghia Triada concentration:** 71.7% of the population — no
  cross-site generalization claim is made.
- **`support_block=OTHER` thinness:** 1 positive in 5 rows (unchanged
  from V1/the blocker audit) — affects only M1 (baseline, non-evidentiary).
- **Artifact-dependence sensitivity: PENDING — PREDECLARED, NOT PART OF
  THIS PRIMARY RUN.** Not implemented after seeing this result, per this
  round's own explicit instruction; does not alter the primary verdict.
- **M4 naming:** `WHOLE_COMPONENT_MAGNITUDE` measures only the resolvable
  whole-number part, never the total value of an integer+fraction
  expression (unchanged limitation, now moot in practice since M4 shows
  no signal to further qualify).

## Adversarial audit (interpretive only — does not alter the verdict above)

1. **Did M1 improve prediction?** No (`ΔH1 < 0`).
2. **Did M2 improve prediction?** No (`ΔH2 < 0`).
3. **Did M3 improve prediction?** No (`ΔH3 < 0`).
4. **Did M4 improve prediction?** No, negligibly negative (`ΔH4 ≈ 0`).
5. **Are any values practically meaningful or all tiny?** All four
   increments are small in absolute bits terms; none is both large and
   significant — there is no "practically meaningful but narrowly
   missed significance" case here to worry about.
6. **Are signs reasonably stable across folds?** Not separately
   re-instrumented this round (would require a new per-fold ΔH
   breakdown not exposed by the frozen pipeline's output) — not claimed
   either way; the aggregate out-of-fold result is what is reported.
7. **Is one tablet dominating positive cases?** No — max single-tablet
   share is 4/21 (19%), unchanged from the blocker audit's pre-registered
   check.
8. **Is HT concentration still ~72%?** Yes, confirmed directly: 71.7%.
9. **Does `support=OTHER` remain nearly devoid of positives?** Yes,
   confirmed: 1/5.
10. **Could M3 success merely reflect external semantic assumptions?**
    Moot — M3 was NOT SUPPORTED.
11. **Does M4 (non-)success mean whole-component magnitude carries no
    information, or is there another construction dependence?** No
    further construction dependence is evident — M4's population and
    transform were both independently audited and proven Y-independent
    (`docs/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md`,
    `docs/CONSTRAINT_ACCUMULATION_V2_BLOCKER_AUDIT.md`) before this run;
    the honest reading is that magnitude, cleanly measured, simply
    carries little to no signal about fraction presence in this corpus.
12. **Does any successful block merely recover record-format structure?**
    No block succeeded, so this does not arise.
13. **Are conditional permutation strata sufficiently mixed?** Yes — the
    finest step (M3→M4) had 71.4% mixed strata, comfortably above the
    frozen 50% criterion.
14. **Does the result truly satisfy the frozen accumulation criterion?**
    No — and it transparently, mechanically does not; there is no
    ambiguity in this determination.
15. **Strongest skeptical interpretation:** the entire V1→V2 program can
    be read as a single, informative negative-control exercise: V1's
    apparent signal was a data-representation artifact; once removed,
    nothing in this corpus's available structural features (site,
    support, position, commodity, magnitude) predicts fraction-sign
    presence beyond chance, under this frozen methodology.

## Claim firewall

This `NEGATIVE UPDATE` result establishes only: *within the conditional
V2 population (quantities ≥1 whole unit), none of position, commodity, or
whole-component magnitude — individually or, since none is even
individually supported, in combination — provides Holm-significant
held-out information about fraction-sign presence, beyond the (also
non-informative) site/support baseline.* It does **not** establish, rule
out, or speak to: decipherment, Minoan cognition, metrological intent,
arithmetic sophistication, causal scribal behavior, commodity semantics,
or cross-site universality.
