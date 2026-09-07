# Constraint-accumulation: null model, program-update rule, adversarial audit

**Status: DESIGN ONLY.** No permutation has been run against real data; no
`ΔH_k`, held-out score, or p-value of any kind exists in this repository
for this design. Companion to `docs/CONSTRAINT_ACCUMULATION_DESIGN.md` and
`docs/CONSTRAINT_ACCUMULATION_CANDIDATES.md`.

## Phase 9 — null model for accumulation

**Not a trivial global shuffle** (Phase 9's own warning: given known
site/support structure, a fully-randomized null would be too easy to
reject and would not isolate what a given *added block* contributes).

**Frozen null, per accumulation step k:** within each `(site, support)`
stratum (reusing the exact NULL 3 stratification concept already frozen in
`docs/CONSTRAINT_NULL_MODELS.md` and operationalized in
`constraint_candidate1.py`), permute `Y` among that stratum's rows —
**preserving** site/support composition, stratum sizes, and the marginal
distribution of every predictor block; **destroying** the pairing between
`Y` and every predictor **downstream of and including** the block under
test. Re-fit `M_{k-1}` and `M_k` on this permuted `Y`, recompute
`ΔH_k^{perm}` via the same grouped-CV procedure, repeat **B=2000** times.

**One-sided by construction, not two-sided:** the scientific question at
each step is "does adding this block reduce held-out uncertainty more than
chance would predict" — a directional question. If `ΔH_k^{obs} ≤ 0`, that
step already fails to show accumulation without needing a permutation
p-value (a negative or zero observed improvement cannot be "significantly
positive"). Where `ΔH_k^{obs} > 0`, compute:

    p_k = (count(ΔH_k^{perm} >= ΔH_k^{obs}) + 1) / (B + 1)

against **α = 0.05**, per this project's established finite-permutation
convention (`constraint_candidate1.finite_permutation_pvalue`, reused
unchanged in form).

**What this null preserves:** total N, tablet-group structure (permutation
is within stratum, not within tablet, so grouped-CV fold assignment is
unaffected by the permutation itself), every predictor's own marginal
distribution, `(site, support)` stratum composition.

**What this null destroys:** the specific pairing between `Y` and the
block(s) whose contribution is being tested.

## Phase 17 — broader program update rule (restated, unchanged from instruction)

- **NO UPDATE** — design blocked or inadequate sample.
- **NEGATIVE UPDATE** — adequate test, no reproducible accumulation.
- **WEAK POSITIVE UPDATE** — one additional independent constraint improves
  held-out information.
- **MODERATE POSITIVE UPDATE** — multiple sequential constraint blocks add
  reproducible held-out information.
- **STRONG POSITIVE UPDATE** — multiple blocks add information, effects
  survive dependence/site sensitivities, and at least one nontrivial
  conditional contribution is independently reproduced.

No single execution of this design may be described as "proving" the
broader constraint-accumulation framework, regardless of outcome.

## Phase 20 — adversarial audit

1. **Is Y partially defined by any predictor?** No — `fraction_present`
   reads only the associated numeral token's own field; none of C_SITE,
   C_SUPPORT, C_POSITION, C_COMMODITY, or C_NUMERIC reads that field.
2. **Is there train/test leakage through same-tablet observations?**
   Addressed by GroupKFold-by-tablet; not eliminated by aggregation (a
   disclosed, deliberate design choice, see design doc), but structurally
   prevented from crossing the train/test boundary.
3. **Is site doing all the predictive work?** Unknown until run — this is
   exactly what the M1→M2/M3/M4 comparison is designed to reveal; flagged
   as the single most important thing to watch for, given known HT
   concentration.
4. **Are support types proxies for site?** Plausibly, given `Tablet` ≈ 96%
   dominance and likely correlation with findspot conventions — this is
   why C_SITE and C_SUPPORT are bundled into a single M1 block rather than
   split across two steps: if they are highly collinear, splitting them
   would produce an uninterpretable, order-dependent artifact rather than
   real information about two independent sources.
5. **Is commodity identity imported semantically?** Yes, disclosed
   plainly (§ C_COMMODITY scope note, `docs/CONSTRAINT_ACCUMULATION_CANDIDATES.md`)
   — unchanged from Candidate 1's own audited status.
6. **Are fraction signs embedded in commodity ligatures creating leakage?**
   No — `fraction_present` never inspects the commodity token's own
   sign-id string, exactly as tested and resolved in Candidate 1
   (`test_ligature_suffix_does_not_leak_into_fraction_presence`); this
   design reuses that same function unchanged.
7. **Are numerical bins arbitrary?** Tertile cut-points are a convention,
   not a natural law — disclosed as a limitation, not hidden; they were
   fixed from a marginal (Y-blind) quantile check before any relationship
   to Y was inspected.
8. **Does model complexity exceed sample size?** A real risk with the full
   site/support cardinality (53/19 raw levels against N≈236) — mitigated,
   not eliminated, by the predeclared HT-vs-OTHER and Tablet-vs-OTHER
   collapses; even so, M4's full one-hot design matrix (2+2+3+4-ish binary
   columns before dropping reference levels) against N≈236 with only 38
   positives warrants caution, disclosed as a limitation of this design,
   not resolved by adding yet more data-dependent simplification now.
9. **Is CV unstable because one site dominates?** Likely, given ≈70–80%
   HT concentration — GroupKFold folds will each be HT-heavy by
   construction; this is a real limitation of what generalization claims
   this design can support (see design doc, leave-one-site-out
   infeasibility).
10. **Could apparent accumulation be caused by progressively adding
    proxies for the same latent variable?** A genuine risk if, e.g., site
    and support and commodity all partly reflect "which archive/room this
    came from" — this is exactly why blocks are added in a fixed,
    theory-motivated order (context → structure → content → magnitude)
    rather than a data-driven order, and why `ΔH_k` at each step is
    reported individually rather than only a single end-to-end
    M0-vs-M4 comparison.
11. **Are repeated observations pseudo-replication?** Addressed by
    grouped CV (§ observational unit above) — a disclosed, deliberate
    substitute for Candidate 1's tablet-level dedup, appropriate to this
    design's predictive framing, not an oversight.
12. **Is the proposed null exchangeable?** Yes, by construction — the
    within-`(site, support)`-stratum permutation only reassigns `Y` among
    rows already sharing identical site/support block values, so C_SITE
    and C_SUPPORT (M1) remain perfectly predictive of themselves under the
    null (as they must — they aren't the thing being tested at that
    stratification level); strata containing only one row, if any exist
    under this broader occurrence-level universe, would need the same
    "excluded, retained descriptively" handling already frozen in
    `constraint_candidate1.exchangeable_strata` — reused, not reinvented,
    if this design is executed.
13. **Does each added constraint truly represent a distinct information
    source?** As distinct as the corpus allows to be checked without
    inventing new fields — C_SITE/SUPPORT (archival), C_POSITION
    (syntactic), C_COMMODITY (semantic), C_NUMERIC (quantitative) are
    conceptually distinct categories of information, though empirically
    they may still correlate with each other in this specific corpus
    (item 10 above) — that possibility is a limitation to interpret
    carefully, not a design flaw that blocks the test.
14. **Is the proposed test capable of producing a negative result?**
    **Yes, explicitly.** `ΔH_k ≤ 0` at any step is recorded plainly as
    failed accumulation at that step, not reinterpreted, not grounds to
    reorder or drop the block, and not smoothed into an aggregate score
    that could paper over it; the overall falsification criterion (Phase
    16, design doc) is written to trigger a **NEGATIVE UPDATE** verdict
    under the plausible, real scenario that M2/M3/M4 all fail to clear
    their null — this is not a test rigged only to be able to say
    "positive" or "inconclusive." **Design is NOT blocked on this
    question.**
