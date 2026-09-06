# H1 Protocol — KU-RO Positional and Arithmetic Behavior

**Status: FROZEN before any corpus statistic has been computed.** This
document is written before this project has looked at, queried, or computed
anything from real Linear A data. Every definition, exclusion rule, and
success/failure criterion below is declared now. If the real result looks
unfavorable to any prior claim, **this document is not to be edited to
accommodate it.** A dated addendum, not a silent rewrite, is the only
permitted mechanism for changing anything here after real data has been
examined.

## Core scientific rule

**Observed rate ≠ target threshold ≠ falsification threshold.** The original
paper's stated values (90%, ±5%) are *prior proposed thresholds*, not
empirical results, until independently reconstructed here. This protocol
treats them exactly that way throughout.

Three distinct kinds of number appear in this document and must never be
conflated:

- **OBSERVED RATE** — a number this project computes from reconstructed
  corpus data.
- **ORIGINAL PAPER TARGET** — a number Paper 1 itself states (e.g. ≥90%,
  ±5%). Attributed to the paper, never presented as this project's own
  finding or decision.
- **NEW PROJECT-SPECIFIC DECISION RULE** — a number *this project* declares,
  where Paper 1 supplies none. Labeled as such, prominently, everywhere it
  appears (see §10, §11).

## Scope: the H1 verdict concerns KU-RO only

**KU-RO is the sole PRIMARY H1 TARGET.** KI-RO and PO-TO-KU-RO are tracked
throughout this protocol for good scientific reasons (KI-RO as a negative
comparator, PO-TO-KU-RO as a separate nested-total exploratory target — see
§1), but **neither ever contributes to the H1 SUPPORT / WEAKENING / FAILURE /
INCONCLUSIVE verdict** (§11). Each of the three sequences gets its own,
separately-computed positional sample and arithmetically testable sample
(§9); only KU-RO's own samples feed §11's table. This restriction is stated
here, at the top, and repeated at the point of use (§9, §11) precisely
because pooling three sequences with different scientific roles into one
verdict would be a silent scope error.

---

## 1. What counts as a KU-RO occurrence?

A sign-group token whose resolved sign-identity sequence matches one of three
**declared target sequences**, tested and reported **separately, never
pooled**:

| label | role | GORILA sign-identifier sequence |
|---|---|---|
| `KU-RO` | claimed summation operator (the object of H1) | `AB081, AB002` |
| `KI-RO` | contrast/control — claimed **not** to total (per the external foundation's own use of this as a negative control, independently adopted here as good practice, not copied) | `AB067, AB002` |
| `PO-TO-KU-RO` | hierarchical extension (nested-total claim, tracked separately per the earlier feasibility audit's instruction to keep nested-total claims distinct from H1 proper) | `AB011, AB005, AB081, AB002` |

**Preferred matching:** by GORILA canonical sign identifier, not by ASCII
transliteration string — a transliteration is a lossy derivative of the
sign-identity resolution, and matching on it risks conflating genuinely
distinct sign-groups that happen to transliterate similarly. **Declared
fallback:** if a candidate corpus source does not preserve GORILA sign IDs at
the token level, a documented string-match rule against the transliteration
will be substituted, and this fact will be logged per-tablet, not silently
absorbed.

**Sign-identity uncertainty:** if the source data flags the sign-group's own
identity as disputed/uncertain (not the same as a damaged numeral — see §6),
the occurrence is retained in the **positional sample** (§9) but marked
`sign_identity_uncertain = true`, and is excluded from the **arithmetically
testable sample** under the AMBIGUOUS category (§6).

---

## 2. Terminal / near-terminal / non-terminal

This operationalizes Paper 1's Constraint 4.1 ("occurs at or near the
terminus of administrative tablets"), which is a **tablet-level** claim,
distinct from the block-level sectioning needed for the arithmetic side (§4).

Let a tablet's record be the ordered sequence of sign-group tokens (ignoring
non-sign-group tokens such as rulings) in that tablet.

- **TERMINAL:** the KU-RO/KI-RO/PO-TO-KU-RO token is the **last** sign-group
  token in the tablet's record (its own associated numeral, §3, does not
  count as a following sign-group).
- **NEAR-TERMINAL:** the token is followed by **at most 2** further
  sign-group tokens before the record ends. **The threshold is 2, declared
  now.** It is not tuned after inspecting how many occurrences would qualify
  under different thresholds — that would be exactly the kind of
  after-the-fact permissive redefinition this protocol exists to prevent.
- **NON-TERMINAL:** anything not TERMINAL or NEAR-TERMINAL by the above.

This classification is computed for **every** occurrence in the positional
sample, independent of whether that occurrence is later usable for the
arithmetic test.

---

## 3. What counts as an associated numeral?

The **first** numeral-bearing token following the KU-RO/KI-RO/PO-TO-KU-RO
token, before the next sign-group token (i.e., strictly within the same
"slot"). A numeral value is extracted as:

1. a whole-number label, if the token carries one directly, **or**
2. the sum of fractional-sign values graded at a declared confidence level —
   **only `secure` and `derived` grades are admitted**, following Corazza et
   al. (2021)'s own published confidence grading, cited by number and
   independently adopted here (not copied code). A fraction graded below
   `derived` (e.g. contested/open) does **not** contribute a value; if it is
   the *only* candidate value present, the numeral is treated as absent (see
   §6, MISSING).

If neither yields a value, no associated numeral exists for that occurrence,
and it is excluded from the arithmetically testable sample (§6, MISSING).

---

## 4. What constitutes a preceding arithmetic block?

The maximal contiguous run of sign-group tokens strictly before the KU-RO
occurrence, within the same tablet, bounded backward by the **first**
of:

- a horizontal ruling marker, or
- a prior KU-RO/KI-RO/PO-TO-KU-RO token (a previous total closes its own
  block), or
- the start of the tablet's record.

**Two block-boundary rules are declared and will be reported side by side,**
following the same good practice the external foundation used (§ see
`EXTERNAL_FOUNDATION_AUDIT.md`) of reporting a result both with and without a
refinement rather than silently picking one:

- **Rule A (ruling/prior-total only).**
- **Rule B (Rule A, plus additionally bounded by a commodity-heading
  token)** — a commodity-ideogram token **not** immediately followed by a
  numeral is treated as a list heading and also closes the block backward at
  that point. ("Immediately followed by a numeral" = inline entry, counted;
  "not followed by a numeral before the next sign-group" = heading,
  boundary.)

Both rules are computed for every arithmetically-eligible occurrence; the
result is reported under both, never only under whichever looks more
favorable.

---

## 5. Eligible tablets/records for arithmetic testing

A KU-RO/KI-RO/PO-TO-KU-RO occurrence enters the **arithmetically testable
sample** only if, after §3–§4:

1. it has an associated numeral (§3), **and**
2. its preceding block (§4, either rule) contains at least one numeral.

Occurrences failing either condition remain in the positional sample (for
§2's terminal/near-terminal/non-terminal statistic) but are excluded from the
arithmetic test — see §9.

---

## 6. Exclusion categories (arithmetic test only)

Declared now, applied in this order, first match wins:

| category | operational definition |
|---|---|
| **AMBIGUOUS** | the sign-group's own identity is flagged disputed/uncertain in source data (§1) |
| **MISSING** | no associated numeral (§3), or the preceding block has zero numerals (§4/§5) |
| **DAMAGED** | the KU-RO token itself, its associated numeral, or **any** numeral in its preceding block carries a recorded damage/break/incompleteness flag |
| **NON_COMPARABLE** | Rule A and Rule B (§4) disagree on which numerals fall in the preceding block **and** that disagreement changes the arithmetic classification (§7) that would result — flagged rather than silently resolved by picking one rule |
| **NO_IDENTIFIABLE_TOTAL** | the tablet has sign-group tokens but zero KU-RO/KI-RO/PO-TO-KU-RO occurrences at all — a corpus-composition fact about the tablet, logged separately, not counted as a "failure" of anything |
| **OTHER** | any case not covered above; logged with a free-text reason, never silently dropped |

A record can carry more than one flag; the table above is evaluated in the
stated order for the purpose of the single **primary** exclusion reason
reported in summary statistics, but all applicable flags are retained in the
per-record output.

---

## 7. Arithmetic outcome categories

Applied, **in this fixed order**, only to occurrences that passed §5 and are
not excluded under §6:

1. **DAMAGED_OR_UNCERTAIN** — if the DAMAGED flag (§6) applies, classify here
   regardless of residual size. Damage-flag check happens *before* residual
   size is even examined, so a small residual on a damaged reading is never
   miscounted as a clean success.
2. **EXACT_CLOSURE** — `r = 0` within floating-point tolerance (`|r| <
   1e-9`).
3. **ROUNDING_COMPATIBLE** — `0 < |r|` and (`|r| ≤ 1.0` in the record's own
   numeral units, **or** `r_rel ≤ 0.05` when `T ≠ 0`) — the first branch
   reflects ordinary rounding to the nearest whole unit (matching, as a
   sanity check only, Paper 1's own worked example HT9: computed 25.83 vs.
   recorded 26, difference 0.17); the second branch is Paper 1's own stated
   ±5% Constraint 4.2 tolerance. **Declared as an OR of both, now, not
   selected after seeing which is more generous on real data.**
4. **UNEXPLAINED_MISMATCH** — everything else: `|r|` exceeds both rounding
   allowances and no damage flag applies.

Occurrences excluded under §6 are classified **NOT_TESTABLE** and never enter
the EXACT_CLOSURE / ROUNDING_COMPATIBLE / UNEXPLAINED_MISMATCH counts.

---

## 8. Residual definition

```
r     = T - sum_i(x_i)                  (signed)
r_rel = |r| / |T|                        (only defined when T != 0)
```
where `T` is the associated numeral (§3) and `x_i` ranges over the numerals
in the preceding block (§4).

---

## 9. Positional sample vs. arithmetically testable sample

These are **two different denominators** and must never be silently
conflated. Both, in turn, are computed **separately per target sequence** —
KU-RO, KI-RO, and PO-TO-KU-RO each get their own pair of samples. **The three
targets' samples are never pooled with each other, at any point:**

- **KU-RO POSITIONAL SAMPLE** / **KU-RO ARITHMETICALLY TESTABLE SAMPLE** —
  every KU-RO occurrence, and the eligible subset thereof (§5, §6). **These,
  and only these, feed the §11 H1 verdict.**
- **KI-RO POSITIONAL SAMPLE** / **KI-RO ARITHMETICALLY TESTABLE SAMPLE** —
  computed identically in mechanics, but reported strictly as a **separate
  comparator**. KI-RO is claimed *not* to total; a KI-RO arithmetic rate
  resembling KU-RO's would be a reason to distrust the whole approach, and a
  KI-RO rate that looks nothing like KU-RO's supports (without proving) that
  KU-RO's behavior is not a corpus-wide numeral-adjacency artifact. **Never
  enters §11's table, in either direction.**
- **PO-TO-KU-RO POSITIONAL SAMPLE** / **PO-TO-KU-RO ARITHMETICALLY TESTABLE
  SAMPLE** — computed identically in mechanics, reported strictly as a
  **separate exploratory finding** about the nested-total claim (see the
  earlier feasibility audit's instruction to keep this distinct from H1
  proper). **Never enters §11's table.**

Every reported rate states explicitly which sample, and which of the three
targets, it is computed over.

---

## 10. The original paper's prior claims, stated separately, not assumed true

> **PRIOR TARGET (positional):** *ku-ro* terminal/near-terminal placement
> ≥ 90%, invariant across HT/KH/ZA. Falsification (paper's own words):
> "Discovery of *ku-ro* in non-terminal positions... at rates >10% would
> require revision of the operator interpretation."

> **PRIOR ARITHMETIC CLAIM (ORIGINAL PAPER TARGET, partial):** the numeral
> following *ku-ro* equals or approximates the sum of preceding entries,
> within ±5% tolerance attributable to scribal error, fractional rounding,
> or damaged entries. **Paper 1 does not state its own separate numeric
> consistency-rate (pass/fail) target for this specific constraint** (unlike
> H2/H3, which each state one, ≥85%/falsification >15%). The ±5% figure is
> an ORIGINAL PAPER TARGET (used directly in §7's ROUNDING_COMPATIBLE rule);
> the *pass-rate band* used to turn UNEXPLAINED_MISMATCH counts into a
> verdict (§11) is not.

> **⚠ NEW PROJECT-SPECIFIC DECISION RULE, not an original paper threshold:**
> Paper 1's general falsification framework (§3.4) states, for the paper as
> a whole, that counter-examples "exceeding the stated threshold, typically
> 10–20%" falsify a claim — but does not attach a specific number to H1's
> arithmetic-binding constraint the way it does for H1's positional
> constraint (≥90%/>10%) or for H2/H3. **This project therefore declares its
> own 10%/20% band for H1's arithmetic component (§11), borrowing only the
> paper's general "10–20%" language as a starting point, not a value the
> paper itself computed or verified for this constraint.** Every place this
> band is used below is labeled NEW PROJECT-SPECIFIC DECISION RULE, not
> ORIGINAL PAPER THRESHOLD — the two must never be presented as
> interchangeable in any future report.

**Neither of these is assumed true here.** Both are reconstructed
independently, below, and the result is reported however it comes out.

---

## 11. Verdict rule — declared before computing anything

**This verdict is computed from KU-RO's own positional sample and KU-RO's
own arithmetically testable sample ONLY (§9). KI-RO's and PO-TO-KU-RO's
rates are never substituted, averaged, or pooled into any number in this
section, in either direction.** They are reported alongside, as a
comparator and an exploratory finding respectively, in the eventual results
output — never inside this table.

Two components, evaluated **separately on KU-RO's own rates**, then
combined:

**Positional component** — uses ORIGINAL PAPER TARGET ≥90% / >10% directly,
since Paper 1 states this specific number itself:
- KU-RO non-terminal rate ≤ 10% → **positional: survives**
- KU-RO non-terminal rate > 10% → **positional: falsified** (per the paper's
  own stated criterion — no gray zone is invented here, because the paper
  didn't offer one for this specific number)

**Arithmetic component — uses the 10%/20% band declared in §10, which is a
NEW PROJECT-SPECIFIC DECISION RULE, not an ORIGINAL PAPER THRESHOLD:**
- KU-RO UNEXPLAINED_MISMATCH rate ≤ 10% → **arithmetic: survives**
- KU-RO UNEXPLAINED_MISMATCH rate in (10%, 20%] → **arithmetic: weakened**
- KU-RO UNEXPLAINED_MISMATCH rate > 20% → **arithmetic: falsified**

**Combined verdict:**

| positional | arithmetic | **overall** |
|---|---|---|
| survives | survives | **SUPPORT** |
| survives | weakened | **WEAKENING** |
| survives | falsified | **WEAKENING** (positional claim intact, arithmetic-binding claim is not) |
| falsified | any | **FAILURE** |

**INCONCLUSIVE overrides the table above** (both bullets below are, like the
10%/20% band, **NEW PROJECT-SPECIFIC DECISION RULEs, not ORIGINAL PAPER
THRESHOLDs** — Paper 1 states no minimum-sample or data-adequacy rule at
all) if either:
- KU-RO's arithmetically testable sample has fewer than **10** occurrences
  (declared minimum now — Paper 1's own "current evidence" cited only 4
  example tablets; 10 is chosen as a floor below which a rate is not
  informative, not tuned to whatever the real count turns out to be), or
- KU-RO's `NOT_TESTABLE` + `DAMAGED_OR_UNCERTAIN` together exceed **50%** of
  KU-RO's eligible positional sample — meaning the corpus itself cannot
  adequately test the arithmetic claim, a data-adequacy gate independently
  declared here, inspired by (not copied from) the external foundation's own
  adequacy-protocol concept.

No other outcome is possible: every real result maps to exactly one of
SUPPORT / WEAKENING / FAILURE / INCONCLUSIVE by this table, decided now.
