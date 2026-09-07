# Constraint-accumulation V1: formal feature–target construction-dependence audit

**This document does not modify, weaken, or reinterpret the V1 result**
(`results/CONSTRAINT_ACCUMULATION_RESULT.md`, commit
`d397f2e42ec0d7ed66300379430db5ebcd03c3ae`). V1's mechanical verdict
remains exactly **WEAK POSITIVE UPDATE**. This document formally classifies
the construction-dependence finding already disclosed in V1 §H, proving
its strength directly from the code, not merely observing it in the data.

## 1. How is `Y = FRACTION_SIGN_PRESENCE` constructed by the adapter?

`constraint_candidate1.fraction_present(token) = bool(token.fractions)` —
`Y=1` iff the associated numeral `Token`'s `.fractions` field (a list) is
non-empty. `.fractions` is populated exclusively in
`lineara_adapter.raw_tablet_to_record`'s fraction-glyph branch (`if
is_fraction_glyph(w): ...`).

## 2. How is integer-value availability constructed?

`numeric_value = q.value if q is not None else None`
(`constraint_accumulation.build_feature_rows`), where `q` is the
associated numeral `Token`. `.value` is set in exactly one place in the
entire adapter: `Token(kind="numeral", value=float(w), damaged=damaged)`,
in the `is_numeral_string(w)` branch — i.e., only when the raw word itself
is a plain decimal-digit string.

## 3. Under what raw token configurations does `NO_INTEGER_VALUE` occur?

Exactly when a fraction glyph token `w` is encountered and the
**immediately preceding token is NOT itself a numeral token**
(`lineara_adapter.py`, fraction-glyph branch, `else` case):

```python
else:
    tokens.append(Token(kind="numeral",
                         fractions=[{"value": value, "confidence": None}]))
```

This new `Token` is never given a `.value` (the dataclass default, `None`,
is never overwritten). This is the **only** code path in the entire
adapter that can produce a numeral token with `value=None`.

## 4. Is `NO_INTEGER_VALUE` mathematically/programmatically implied by fraction-only numeral representation?

**Yes, exactly and unconditionally.** There is no other branch anywhere in
`lineara_adapter.py` that constructs a numeral token with `value=None`.
Every numeral token in this representation has either (a) `value` set and
`fractions` empty/None (plain integer, `is_numeral_string` branch), (b)
`value` set and `fractions` non-empty (integer immediately followed by a
fraction glyph — the `tokens[-1].kind == "numeral"` merge case), or (c)
`value=None` and `fractions` non-empty (fraction glyph with no preceding
numeral — the case under audit). **There is no fourth case.** A numeral
token with `value=None` and empty/absent `fractions` cannot be constructed
by this code at all.

## 5. Is the implication `NO_INTEGER_VALUE ⟹ FRACTION_SIGN_PRESENCE` exact by adapter construction, or merely empirical?

**Exact by construction — proven directly from the code in §3–4, not
merely observed in the data.** Every numeral token with `value=None`
was, by the only code path that can produce it, given a non-empty
`fractions` list at the moment of its creation. It is not possible, given
this adapter's logic, for a row to have `numeric_value=None` and
`fraction_present=False` simultaneously. The empirical count (§7 below,
17/17) **corroborates** this proof; it does not substitute for it — the
proof holds even before inspecting any real corpus row.

**Deeper root cause (not an adapter bug):** this determinism ultimately
traces to a genuine, unavoidable fact about the Linear A numeral system
itself, already established in this project's own scholarship audit
(`docs/LINEAR_A_NUMERICAL_METROLOGY_AUDIT.md` item 1): the notation is
additive/positive-only with no zero digit. A quantity strictly between 0
and 1 whole unit **cannot** be written with any integer digits at all — it
can only be represented by a fraction glyph alone. So `NO_INTEGER_VALUE`
is best understood as identifying **"this recorded quantity is a
sub-unit amount (0 < true value < 1)"** — a real, coherent structural fact
about the quantity — which, by the logic of the numeral system, is
*necessarily* fraction-bearing. The determinism is real and provable, but
its cause is the numeral system's own structure, not an arbitrary
adapter/parsing quirk.

## 6. Is the reverse implication true? (`FRACTION_SIGN_PRESENCE ⟹ NO_INTEGER_VALUE`)

**No — false, both logically and empirically.** The merge case (b) in §4
(`tokens[-1].kind == "numeral"`) produces tokens with both a resolved
`value` **and** non-empty `fractions` — i.e., an integer-plus-fraction
quantity (e.g., "3 ½"), which has `fraction_present=True` but
`numeric_value` resolved, not `None`. Empirically (§7): 21 of the 38 total
V1 positives have a resolved integer value.

## 7. How many fraction-positive rows also contain an integer value?

**21** (of 38 total positives; 21/38 = 55.3%).

## 8. How many `NO_INTEGER_VALUE` rows are fraction-negative?

**0** (of 17 `NO_INTEGER_VALUE` rows; 0/17 = 0%), consistent with, and
required by, the proof in §4–5.

## 9. Could `NO_INTEGER_VALUE` arise for reasons unrelated to fraction-only notation?

**No, not within this adapter's representation** (§4: no other code path
produces `value=None`). A caveat, stated plainly: this is a fact about
**this specific adapter's representation choices**, not a claim that the
raw Linear A source could never have some other reason for an
unrecoverable integer value (e.g., physical damage obscuring digits). In
the current adapter, a fully illegible/damaged numeral is handled via the
`damaged` flag on a token that still has *some* parsed content, or the
occurrence is excluded upstream (`has_quantity=False`) if no numeral token
can be associated at all — neither of those paths produces the
`value=None, fractions=non-empty` combination audited here.

## 10. Is the dependence caused by raw corpus semantics, transcription convention, adapter representation, feature engineering, or some combination?

**A combination, with a specific division of responsibility:**

- **Raw corpus / numeral-system semantics (root cause, unavoidable):** a
  sub-unit quantity (0<value<1) can only be written as a fraction alone,
  per §5's deeper explanation. This part is a genuine fact about Linear A,
  not a defect.
- **Adapter representation (faithful, reasonable, not itself a bug):**
  representing "no integer part was written" as `value=None` on a numeral
  token that already carries `fractions` is a faithful, direct encoding of
  that raw fact.
- **Feature engineering (the actual point of failure):** `C_NUMERIC`'s
  decision (`constraint_accumulation.numeric_bin` / `numeric_bin_fold`) to
  fold "no integer value" in as a fourth category of what was intended to
  be a **magnitude** variable is what mechanically entangles a structural
  notation fact (sub-unit vs. whole-unit-or-more) with `Y`
  (`FRACTION_SIGN_PRESENCE`, itself read from the very same token's
  `.fractions` field) inside a single feature meant to test a different
  question (does size predict fraction use). **This is where the
  correction belongs, not in the adapter or the raw source.**

## Classification

Weighing the five candidate labels against §1–10:

- **EXACT TARGET LEAKAGE** — too strong for the *whole* `C_NUMERIC`
  feature: only its `NO_INTEGER_VALUE` category (1 of 4 levels) is
  affected; `SMALL`/`MEDIUM`/`LARGE` show no such property (§ V1 result
  §H: 10.8%/11.1%/6.8%, an ordinary empirical spread, not a determinism).
- **EMPIRICAL ASSOCIATION** — too weak: §4–5 is a **proof from code**, not
  an observed correlation that happens to be strong; the 17/17 figure is
  corroborating evidence, not the basis of the claim.
- **OPEN** — not justified: the mechanism is fully resolved and provable
  from the adapter source, not unresolved.
- **PARTIAL CONSTRUCTION DEPENDENCE** — close, and defensible as a
  secondary/scoping label (it correctly signals that only part of the
  feature is affected).

**Primary classification: DETERMINISTIC FEATURE–TARGET CONSTRUCTION
DEPENDENCE**, **scoped specifically to `C_NUMERIC`'s `NO_INTEGER_VALUE`
category** — deterministic and provable from the code (not merely
empirical), a genuine construction dependence (both `Y` and this specific
category are read from the same token object's fields, in a way that is
logically coupled for this subcase), and explicitly **not** a claim that
the entire `C_NUMERIC` feature, or any other V1 block, is compromised.

## 11. Can V1 M4 be interpreted as genuine magnitude evidence?

**Not cleanly, as constructed.** V1's M4 conflated two different
questions (formalized in
`docs/CONSTRAINT_ACCUMULATION_V2_DESIGN.md` §"Two questions"): whether a
quantity has *any* integer component at all (which, per §5, is
definitionally certain to co-occur with fraction presence for the
sub-unit subset) and whether, given an integer component, its *magnitude*
predicts fraction presence. The large observed `ΔH4` is very likely driven
substantially — plausibly predominantly — by the first, definitionally
certain sub-question, not by the second, genuinely open one. This is
restated from, not a change to, V1's own §H.

## 12. Does integer-component structure deserve its own future hypothesis?

**Plausibly yes — recorded as a candidate, not tested here.** "Does a
recorded quantity include a whole-number part at all" is a genuine,
non-arbitrary structural distinction in the notation (sub-unit vs.
whole-unit-or-more quantities) that may itself correlate with other
structural features (commodity, site, position) for reasons *other* than
its tautological relationship to `Y` as currently defined. A future,
separately-designed hypothesis — tentatively named `INTEGER_COMPONENT_
STRUCTURE` — could test this validly by choosing a **different target**
that is not itself definitionally derived from the same token field (e.g.,
predicting `commodity_class` or `site_block` from whether-integer-present,
rather than predicting `fraction_present`). **Not tested in this round**,
per this round's own instruction (Phase 4: "Do not test Question A
inferentially in this round").
