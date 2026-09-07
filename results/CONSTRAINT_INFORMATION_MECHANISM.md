# Constraint accumulation V3 — mechanism discovery / asymmetric elimination audit

**This is a pure mathematics / theory round.** No real corpus data was
touched. No frozen H1, Candidate 1, V1, or V2 file was modified. Every
numeric example below is computed exactly (finite arithmetic, verified in
`src/constraint_information_mechanism.py` / `tests/test_constraint_information_mechanism.py`,
17/17 passing), not simulated or approximated.

## A. Provenance

| | |
|---|---|
| Commit at start of round | `e48e01c67b5a5023c8824364b4be1d1b1a38f5d0` |
| Git status at start | clean except two already-uncommitted V2 result files (pre-existing from the prior round, untouched here) |
| SHA-256 of frozen V2 files | recorded (protocol `b757d27e...`, module `5584dbeb...`, module tests `26cb8c51...`, harness `c7844fa7...`, harness tests `600e0fba...`, result JSON `1e4fb61d...`, result MD `1dc1a151...`) |
| Tests before this round | 312 passed |
| Tests after this round | 329 passed (17 new) |
| New files | `src/constraint_information_mechanism.py`, `tests/test_constraint_information_mechanism.py`, `results/constraint_information_mechanism.json`, `results/CONSTRAINT_INFORMATION_MECHANISM.md` |
| Files modified | none |
| Staged/committed | nothing — per instruction |

## B. Minimal theorem

**Setup.** A finite population of states, `n1` with `Y=1`, `n0` with
`Y=0`, uniform prior (weighting shown unnecessary below). A constraint
eliminates `e1` of the positives and `e0` of the negatives.
`p = n1/(n1+n0)`, `p' = (n1-e1)/((n1-e1)+(n0-e0))`.

**Theorem (Elimination Invariance).**

    p' = p   ⟺   e1/n1 = e0/n0   ⟺   r1 = r0

where `r1 = P(eliminated | Y=1)`, `r0 = P(eliminated | Y=0)`.

**Proof sketch.** Cross-multiply `p'=p`: `n(n1-e1) = n1(n-e1-e0)` where
`n=n1+n0`. Expanding and cancelling `n1·n` from both sides leaves
`n1·e0 = e1·(n-n1) = e1·n0`, i.e. `e1/n1 = e0/n0`. Every step is
reversible, so this is an **iff**, not merely a sufficient condition.
(`constraint_information_mechanism.theorem_p_prime_equals_p` checks this
identity computationally across a grid of `(n1,n0,e1,e0)` combinations —
`test_theorem_iff_holds_across_a_grid`, passing.)

**Generalization (no uniformity or finiteness required).** The same
derivation is exactly Bayes' rule applied to the event "survived
elimination": for *any* probability space and *any* event `E`,
`P(Y=1|E^c) = p` iff `P(E|Y=1) = P(E|Y=0)`. Uniform states were not
"mathematically necessary" (as Task 1 itself flagged as a possibility) —
they were not needed at all. **The theorem holds for arbitrary priors,
arbitrary (including continuous) state spaces, and does not require `Y`
to be a deterministic function of state.**
`src/constraint_information_mechanism.soft_reweighting_generalization`
verifies the further generalization to soft reweighting (not just hard
0/1 elimination): replacing `r1,r0` with expected weights
`E[w|Y=1], E[w|Y=0]` gives the identical iff condition.

**Is "removal changes information about Y iff removal is asymmetric wrt
Y" literally correct?** **Yes, exactly, as stated — no qualification is
needed beyond specifying which reference population the asymmetry is
measured against** (see §F — this is the one place a naive reading can
mislead, not because the theorem is wrong, but because "asymmetric"
must be evaluated *conditionally* on whatever is already fixed, not
*marginally* against some other population).

## C. Counterexamples (Task 2)

All four constructed exactly, verified computationally
(`test_example_A/B/C/D_*`, all passing):

| example | cardinality change | information change |
|---|---|---|
| **A** — 100 states (50/50) → eliminate 45 pos + 45 neg | **90% reduction** | **zero** (`r1=r0=0.9`, `p'=p=0.5` exactly) |
| **B** — 10,000 states (100 pos/9,900 neg) → eliminate 99 of 100 positives, 0 negatives | **0.99% reduction** | **large** (`p: 0.01→0.000101`, ~100× odds shift) |
| **C** — 100→90→80→70 states, 5 pos+5 neg removed every stage | **shrinks every stage** | **zero at every stage**, `p=0.5` throughout |
| **D** — 100→80→70→60 states, negatives-only removed every stage | **shrinks every stage** | **strictly increases every stage**, `p: 0.5→0.625→0.714→0.833` |

**Conclusion: state-space compression (`|S'|/|S|`) and target information
are fundamentally independent quantities.** Neither bounds the other in
either direction — Example A has enormous compression and zero
information; Example B has negligible compression and large information.
This is not approximately true or true "in most cases" — it is exactly,
constructively demonstrated to be unrelated: for any target compression
ratio you can construct both a zero-information and a large-information
example achieving it, simply by choosing `e1,e0` to satisfy or violate
`r1=r0`.

## D. Information theory (Task 3)

For elimination-indicator `C` (or any constraint variable), `I(C;Y)=0`
**exactly when** `C` and `Y` are independent — for the binary-binary
case this is *identical* to `r1=r0`
(`test_mutual_information_zero_for_independent`). This is not a new fact:
it is the standard definition/characterization of zero mutual information
for two variables.

**Can `|S_C|<|S|` (or more generally `I(C;X)>0`) coexist with `I(C;Y)=0`
when `Y=f(X)`?** **Yes — proven by explicit construction**
(`construction_IX_positive_IY_zero`, verified computationally):

- `X` uniform over `{a,b,c,d}`.
- `Y = f(X) = 1{X∈{a,b}}` (a 2-to-1 coarsening).
- `C = 1{X∈{a,c}}` (cuts *across* the `Y`-partition).

Result: **`I(C;Y) = 0` exactly** (`C` and `Y` are literally independent —
`P(C=1|Y=1)=P(C=1|Y=0)=0.5`), while **`I(C;X) = 1` bit** (`C` together
with `Y` exactly determines `X`). This is a direct instance of the **data
processing inequality**: `Y=f(X)` makes `C → X → Y` a Markov chain, so
`I(C;Y) ≤ I(C;X)` always — the inequality can be strict, including
strict-to-zero, exactly as constructed here. This does **not** require
`Y` to be deterministic given `X` — the same Markov-chain argument (and
therefore the same possible gap) survives if `Y|X` is noisy, as long as
`C`'s only channel to `Y` is through `X` (i.e. `C⊥Y|X`).

**This is a different phenomenon from the V1 mechanism** (§G) — it shows
a constraint *can* carry real information about the underlying state
while carrying none about a particular coarse summary of it; V1's
mechanism was the reverse kind of surprise (near-total information about
`Y` specifically, but for a definitional, not causal, reason).

## E. Elimination asymmetry (Task 4)

**Best definition:** `A = r1 - r0` (signed risk difference) is the most
directly interpretable elementary statistic; **mutual information `I(C;Y)`
itself is the canonically natural quantity**, because (a) it is symmetric
in `C`/`Y`, (b) it generalizes beyond binary `C` (odds ratio and risk
difference are specific to 2×2 tables), (c) it composes via the chain
rule (§F), and (d) **it is exactly what this project's own primary metric
(`ΔH_k`, held-out log-loss reduction) already estimates** — the entire
V1/V2 program has, in effect, been measuring elimination/conditioning
asymmetry all along, through a model-based, cross-validated estimator of
`I(C_k;Y|C_{<k})` rather than through the raw `r1,r0` contingency-table
lens. This is a genuine, useful unifying observation (see §J).

**Boxed question: `I(C;Y)>0 ⟺ r1≠r0`?** **True, but for the binary-`C`
case this is tautological**, not a new fact to prove: when `C` *is* the
elimination indicator itself, `r1` and `r0` are *by definition*
`P(C=1|Y=1)` and `P(C=1|Y=0)` — the standard characterization of
dependence between two binary variables (equivalently: nonzero
covariance, correlation, log-odds-ratio, or KL divergence between the two
conditional Bernoulli distributions — all of these share the *exact same
zero-set* `{r1=r0}`, differing only in how they scale the departure from
it). For **non-binary** constraints, the equivalence generalizes to "the
conditional distribution of `C` differs between `Y=0` and `Y=1`," which
is again just the definition of dependence — not a new result.

## F. Sequential theorem (Task 5)

**Chain rule (standard, Cover & Thomas):**
`I(C_1,...,C_k;Y) = Σ_j I(C_j;Y | C_1,...,C_{j-1})`.

Applying the single-step theorem (§B) *inside* each conditional term
gives: **step `j` contributes zero information iff its elimination is
independent of `Y` *given survival through stages `1..j-1`*** —
i.e. `r_{1,j} = r_{0,j}` evaluated on `S_{j-1}`, not on `S_0`.

**Is marginal (`S_0`-level) asymmetry the right thing to check?** **No —
proven insufficient and unnecessary by two explicit constructions:**

1. **`sequential_null_then_informative`**: an 8-state population where
   stage 1 is perfectly balanced (null, `r1=r0=0.5`) yet stage 2,
   conditioned on stage-1 survivors, is sharply asymmetric
   (`r1=0, r0=0.5`) — **a null step does not preclude a later
   informative step.**
2. **`simpson_marginal_balanced_conditional_asymmetric`**: two 20-state
   strata where a constraint has **opposite, large** effects within each
   stratum (`r1,r0 = 0.2,0.8` in stratum A; `0.8,0.2` in stratum B) that
   **exactly cancel when pooled** (`marginal r1=r0=0.5`, appearing
   perfectly uninformative). **Marginal symmetry can mask large,
   opposite-signed conditional asymmetry.**
3. **`confounded_proxy_marginal_asymmetric_conditionally_null`**: the
   mirror case — a constraint (`position=LATE`) that is *independent of
   `Y` within every stratum of a confounder (`site`)*, yet **appears
   asymmetric when evaluated marginally**, purely because it correlates
   with the confounder, which is itself genuinely informative. **Marginal
   asymmetry can be entirely spurious, a pure reflection of an earlier
   constraint's own effect.**

**Proposition (Sequential Elimination Criterion).** For nested constraints
`S_0⊇S_1⊇...⊇S_k`, the total information `I(C_1..k;Y)` decomposes exactly
via the chain rule; genuine progressive accumulation (every used step
contributing strictly positive information) requires strict **conditional**
asymmetry (`r_{1,j}≠r_{0,j}` on `S_{j-1}`) at every step — **neither
necessary nor sufficient is asymmetry measured against `S_0`** (or any
other reference population than the one actually being conditioned on).
A step showing zero conditional information does **not** poison later
steps (each chain-rule term is independent of the others' values) — this
directly matches the empirical finding that M2's null result did not
preclude M4 from being tested on its own merits.

**Reassurance for the project's own methodology:** this project's
conditional-permutation null (`docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md`
§8, unchanged in V2) was **already** designed to condition on
`M_{k-1}`'s own predictors at every step — i.e., it was already computing
the mathematically correct, *conditional* asymmetry, not the naive,
potentially-misleading marginal version this section warns against. The
math developed here validates, after the fact, a design choice the
project made for other (also sound) reasons.

## G. V1 → V2 interpretation (Task 6/8)

**Candidate mechanisms, evaluated:**

1. Genuine target-specific constraint information — **not supported**:
   the effect vanished under a population change designed to remove a
   different, specific mechanism, and nothing else changed conceptually.
2. Construction-induced asymmetry (vague) — **too imprecise**; sharpened
   below.
3. Selection/collider effects — **explicitly not this**: as established
   in `docs/CONSTRAINT_ACCUMULATION_V2_BLOCKER_AUDIT.md` Phase 7 item 10,
   this is left-truncation of the magnitude scale, not a collider (no
   two-cause common-effect structure exists here).
4. **Deterministic encoding of the outcome — the best-supported, most
   precise mechanism.** `results/CONSTRAINT_ACCUMULATION_VALIDITY_AUDIT.md`
   §4–5 proves, from the adapter's source code (not from data), that
   `numeric_value is None ⟹ fraction_present is True` with **certainty**
   (100%, r=1, an extreme, degenerate case of the asymmetry condition
   in §B — not a subtle statistical association at all).
5. Another mechanism — no further candidate is needed once (4) is
   established this precisely.

`v1_v2_elimination_diagnostic` restates the already-published V1→V2
population change in exactly this round's vocabulary, using only
already-disclosed counts (no new data access): removing V2's excluded 17
rows from V1's 236-row population is an elimination with **`r1 = 17/38 =
0.447`, `r0 = 0/198 = 0`** — a large, exact asymmetry, entirely consistent
with (indeed, numerically explaining) why the `NO_INTEGER_VALUE` category
behaved as a near-perfect predictor of `Y` within V1's full population.

**What can be inferred:** the V1 M4 finding was not robust to removing
exactly the mechanism the validity audit identified *before* V2 was run;
the magnitude and direction of the collapse (Holm p: 0.0015 → 0.636) is
exactly what that a priori, code-level prediction implied. This is about
as strong as observational (non-experimental) corroboration gets — a
mechanism proven from source code, then empirically confirmed by its
predicted consequence.

**What cannot be inferred:** that no relationship between numeral
structure and fraction notation exists in Linear A generally (V2 tested
one specific operationalization); that mechanism 4 is proven with
deductive certainty to be the *sole* contributor (strong, well-corroborated
inference, not proof); anything about scribal cognition, semantics, or
historical intent (unchanged claim firewall).

## H. Existing-data audit (Task 7)

**Per-block classification — the theory is not forced onto blocks that
don't instantiate it:**

| block | classification | reasoning |
|---|---|---|
| **V1→V2 population change** (excluding `NO_INTEGER_VALUE`) | **DIRECT ELIMINATION MEASURE** | A literal state-space restriction, `S_0⊇S_1`, with directly computable `r1,r0` — the cleanest instantiation of the whole framework anywhere in this project. |
| **M3 (commodity, binary: LIQUID/DRY)** | **DIRECT ELIMINATION MEASURE** | Binary categorical = exactly the `C` used throughout this document; `r1,r0 = P(commodity=LIQUID\|Y=1,S_2), P(commodity=LIQUID\|Y=0,S_2)` is directly computable and is exactly what the conditional permutation test already estimates. |
| **M1 (site+support), M2 (position, 3 levels)** | **PLAUSIBLE PROXY** | Multi-level categorical blocks are not single binary elimination events; each *level* individually admits an elimination-style reading (level vs. its complement), but the *block* as tested aggregates across levels via the model's log-loss, not a single `r1,r0` pair. |
| **M4 (whole-component magnitude, continuous)** | **NOT AN ELIMINATION MEASURE** | A continuous variable has no natural elimination/survival partition without an arbitrary threshold — forcing one would be exactly the kind of post-hoc binning this project's own firewall (rightly) avoided. The mutual-information/log-loss framing (already used) is the correct lens for M4, not the elimination-set framing. |

## I. Adversarial audit (Task 8)

**Domain of validity:** the single-step theorem (§B) is **fully
general** — no finiteness, no uniformity, no determinism of `Y|X`
required; it is Bayes' rule. **It does not fail anywhere probed** —
nonuniform weights, correlated constraints (chain rule is unconditional),
noisy observables (DPI needs only the Markov structure, not determinism),
and soft reweighting (§B generalization) were all checked and the
identity survives unchanged in form.

**What *can* fail is naive, non-conditional *application*** — checking
`r1,r0` against the wrong reference population. Both Simpson-type
constructions (§F items 2–3) demonstrate this cleanly: marginal
asymmetry can be **spuriously present** (confounded proxy) or **spuriously
absent** (cancelling reversal) relative to the correct, conditional
quantity. This is not a counterexample to the theorem — the theorem is
still exactly true at whatever population it is evaluated against — it
is a counterexample to the informal slogan "just check whether removal
is balanced," which silently assumes the reference population is
unambiguous.

**Strongest counterexample overall:** the Simpson cancellation
(`simpson_marginal_balanced_conditional_asymmetric`) — a constraint that
is *maximally* informative within each stratum (near-complete separation,
`r1,r0=0.2,0.8` and `0.8,0.2`) yet appears **perfectly** uninformative
pooled. This is the sharpest illustration that cardinality/marginal
statistics alone can be maximally misleading.

**Weakest assumption in the whole framework:** that a "constraint" is
even well-modeled as a fixed, pre-specified elimination event at all. In
practice (this project included), constraints are *estimated* from a
finite sample, and searching over many candidate constraints for one
with large apparent `r1,r0` asymmetry is a *selection* problem the
population-level theorem says nothing about — exactly the concern this
project's own freeze-before-data, permutation, and Holm-correction
discipline exists to control, external to this round's mathematics.

## J. Verdict

Evaluating against the four offered options, honestly, without favoring
the more exciting one (per explicit instruction):

- The **single-constraint** statement (§B) is a direct, elementary
  restatement of Bayes' rule / the definition of independence — by
  itself, this would be **VERDICT 1 (trivial restatement)**.
- The **sequential** statement (§F) is an immediate corollary of two
  textbook facts (the mutual-information chain rule; the single-step
  theorem applied conditionally) — no new mathematics was derived beyond
  composing standard results.
- However, the **elimination vocabulary, the explicit `r1/r0` lens, and
  the conditional-vs-marginal distinction it forces into the open**
  provide genuine, non-vacuous interpretive value for *this project's
  own results*: it (a) gives a precise, provable diagnosis of the V1
  mechanism (deterministic encoding, `r=1` exactly — sharper than "some
  construction dependence"), (b) explains, in one identity, why V1's huge
  apparent effect was not a subtle statistical association but a
  near-tautology, (c) formally validates that the project's own
  conditional-permutation design (not a marginal one) was the
  mathematically correct choice, and (d) supplies a reusable, general
  checklist (§I) for auditing any future candidate constraint before
  trusting an apparent effect.

**VERDICT: USEFUL REFORMULATION.**

The mathematics is standard (Bayes' rule, mutual information, the chain
rule — nothing here is a new theorem in the sense of extending
information theory), but the elimination-asymmetry framing is a genuinely
useful, correctly-derived lens for interpreting constraint-accumulation
systems like this one, and it directly, precisely explains what actually
happened between V1 and V2.

### The final boxed question

> **What, precisely, must a constraint do to a state space before it
> becomes informative about an observable?**

**It must eliminate (or reweight) states unevenly across the observable's
own two classes — formally, `P(elimination | Y=1) ≠ P(elimination | Y=0)`
— evaluated relative to whatever population the constraint is actually
applied to (i.e., conditionally on every previously-applied constraint,
never marginally against some other, unconditioned population).**
Cardinality reduction, by itself, is neither necessary nor sufficient
(§C); only this conditional asymmetry is necessary and sufficient (§B,
§F). If the correct answer reduces to elementary statistical
independence stated in different words — it does, and that is stated
plainly here, not dressed up as more than it is.
