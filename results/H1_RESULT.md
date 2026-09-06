# H1 Result — KU-RO Positional and Arithmetic Behavior

**Labels used throughout:** PREDECLARED RULE, ORIGINAL PAPER TARGET, NEW
PROJECT-SPECIFIC DECISION RULE, NEW EMPIRICAL RESULT, CORPUS LIMITATION,
DOMAIN-EXPERT DEPENDENT, OPEN.

## 1. Protocol freeze hash

`5aae796f71245e359c2fb72d5b01b81f72d44288` — confirmed unchanged (byte-identical) at the time of this run.

## 2. Ingestion freeze hash

`98d6379dffdd886463451a994b5f876946b055d2`

## 3. Corpus provenance / checksum

Source: `mwenge/lineara.xyz` @ `43fe7cf1abc8e6bb1ea3228c3a1bd5938709620a` (see `docs/CORPUS_PROVENANCE.md`). Extraction: `node src/extract_raw_js.js data/raw/lineara_xyz/LinearAInscriptions.js`, run 2026-09-06T21:30:03Z, produced `data/generated/lineara_extracted.json` (gitignored, not committed), sha256 `219b52569cab75b58e95afb0a969689c6c50f753ce690321f20abbaff3a8eff8`, **NEW EMPIRICAL RESULT: 1721 parsed tablet/document records, 0 duplicate names, 0 malformed entries, 9 records with empty/missing `transliteratedWords`.** (1721 independently matches the external foundation project's own reported record count for the same upstream lineage — a useful cross-check, not itself an H1 statistic.)

## 4. Exact sample construction

Per `docs/H1_PROTOCOL.md` §9: three separate positional/arithmetic sample pairs, one per target (KU-RO, KI-RO, PO-TO-KU-RO), never pooled. Built by `src/run_h1.py`, which calls only `src/lineara_adapter.py` (raw → frozen `Record`/`Token`) and `src/kuro_protocol.py` (all classification) — no H1 logic is reimplemented in the driver. **Rule A only; Rule B remains BLOCKED** (no `commodity_ids` supplied anywhere).

**CORPUS LIMITATION, found and fixed during this run (see §15):** the adapter's original mapping of `"\n"` to a `ruling` boundary was found to be wrong against real data (this source places `"\n"` between every entry, not only true section boundaries) and was corrected to drop `"\n"` entirely, exactly like the word separator. This is an adapter fix, not a protocol change — `docs/H1_PROTOCOL.md`, `src/kuro_protocol.py`, and `tests/test_kuro_protocol.py` remain byte-identical to the freeze commit.

## 5. Raw integer counts

| | KU-RO | KI-RO (comparator) | PO-TO-KU-RO (exploratory) |
|---|---|---|---|
| POSITIONAL SAMPLE N | **37** | 16 | 2 |
| TERMINAL | 11 | 3 | 2 |
| NEAR_TERMINAL | 12 | 2 | 0 |
| NON_TERMINAL | 14 | 11 | 0 |
| ARITHMETICALLY TESTABLE N | **26** | 3 | 1 |
| EXACT_CLOSURE | 10 | 0 | 0 |
| ROUNDING_COMPATIBLE | 6 | 0 | 0 |
| DAMAGED_OR_UNCERTAIN | 0 | 0 | 0 |
| UNEXPLAINED_MISMATCH | 10 | 3 | 1 |
| NOT_TESTABLE | 11 | 13 | 1 |

Sanity check (Phase 5, `src/run_h1.py:sanity_check`): TERMINAL+NEAR_TERMINAL+NON_TERMINAL = POSITIONAL SAMPLE, and ARITHMETICALLY_TESTABLE+NOT_TESTABLE = POSITIONAL SAMPLE, for all three targets — **all passed, no discrepancy.**

## 6. Exclusions

All three targets: **100% of NOT_TESTABLE occurrences fall under MISSING** (no other exclusion category — AMBIGUOUS, DAMAGED, NON_COMPARABLE, NO_IDENTIFIABLE_TOTAL, OTHER — was triggered at all in this run). This is a **NEW EMPIRICAL RESULT**, not assumed: it reflects that the most common reason an occurrence is untestable in this source is the absence of either a resolvable associated numeral or any numeral in the preceding block, not damage or ambiguity. **DAMAGED never fired** in this run (0 across all three targets) — meaning bracket/`?`-marked damage did not affect this particular result set, positively or negatively (see adversarial audit §10-equivalent below).

## 7. Rates

**KU-RO** (the only target feeding the verdict):
- Positional: non-terminal rate = 14/37 = **37.84%**
- Arithmetic: unexplained-mismatch rate = 10/26 = **38.46%**

## 8. Original-paper target comparison

**ORIGINAL PAPER TARGET (positional):** ≥90% terminal/near-terminal, falsification at >10% non-terminal. **Observed KU-RO non-terminal rate: 37.84% — exceeds 10% by a wide margin.** Per the paper's own stated criterion (`H1_PROTOCOL.md` §11), this **falsifies** the positional component.

## 9. New-project decision-rule comparison

**NEW PROJECT-SPECIFIC DECISION RULE (not an original-paper threshold):** ≤10% survives, (10%,20%] weakened, >20% falsified. **Observed KU-RO unexplained-mismatch rate: 38.46% — exceeds 20%.** This **falsifies** the arithmetic component under the project's own declared (not paper-derived) band.

## 10. Adequacy-gate result

`H1_PROTOCOL.md` §11 INCONCLUSIVE gates, checked before the combined verdict: arithmetically testable N = 26 (≥10, does not trigger small-sample INCONCLUSIVE); NOT_TESTABLE+DAMAGED_OR_UNCERTAIN = 11+0 = 11/37 = 29.7% (≤50%, does not trigger data-inadequacy INCONCLUSIVE). **Neither gate fires.**

## 11. Final frozen-protocol verdict

Computed by calling `kuro_protocol.verdict()` unmodified (not hand-derived):

```
non_terminal_rate = 0.3784
unexplained_mismatch_rate = 0.3846
n_arithmetically_testable = 26
not_testable_or_damaged_fraction = 0.2973
```

# PRIMARY-CORPUS H1 VERDICT: **FAILURE**

Both components independently falsify (positional per the paper's own criterion; arithmetic per this project's own declared band). Per `H1_PROTOCOL.md` §11's table, `falsified | any → FAILURE`.

**Scope of this verdict, stated exactly:** this is **FAILURE UNDER THIS FROZEN PROTOCOL, ON THIS GORILA→`mwenge/lineara.xyz` CORPUS LINEAGE**. It is **not**, and must not be read as, a **UNIVERSAL FALSIFICATION ACROSS ALL LINEAR A TRANSCRIPTIONS** — no other corpus lineage (SigLA in particular) has yet been tested under this protocol. That replication is the next phase, not part of this result.

## 12. Comparator KI-RO result — **NEVER used in the verdict above**

N=16 positional, only 3 arithmetically testable (13 MISSING), **all 3 testable cases UNEXPLAINED_MISMATCH (100%)**. One case (HT15) inspected directly: block-sum 1254 vs. recorded value 400. **KI-RO is directionally consistent with the intended negative-control behavior, but the arithmetic sample is too small for a strong inference** — n=3 does not support a claim that the comparator design has been validated; it is consistent with, not confirmatory of, that design.

## 13. Exploratory PO-TO-KU-RO result — **NEVER used in the verdict above**

N=2 positional (both TERMINAL), only 1 arithmetically testable, that one case UNEXPLAINED_MISMATCH (sum 32 vs. total 452). n=1 is not informative; reported only for the record, per its exploratory-only status.

## 14. Secondary sensitivity analyses (never replace the primary result above)

- **TERMINAL only vs. TERMINAL+NEAR_TERMINAL:** strict-terminal-only non-success rate = (NEAR_TERMINAL+NON_TERMINAL)/N = 26/37 = **70.3%**; the frozen (near-terminal-inclusive) definition's non-terminal rate is the already-reported 37.8%. The frozen, more generous definition substantially improves the apparent rate relative to a strict reading, but **both fall far short of the ≤10% bar** — this sensitivity does not change the positional falsification.
- **Exact closure vs. exact+rounding-compatible:** exact-only success = 10/26 = 38.5%; exact+rounding = 16/26 = **61.5%**. The rounding tolerance does real work (+23 points), but even the generous view leaves 38.5% unexplained mismatch, which still exceeds the new-project-specific >20% falsification bar. **16/26 cases were exact or rounding-compatible under the frozen protocol. Whether this exceeds an appropriate null expectation is OPEN and was not tested in this analysis** — no null model (e.g. random pairing of totals with sections, as prior independent work on this exact question has used) has been run here; this figure is reported as an observed rate only, not as evidence of a real effect size.
- **Inclusion/exclusion of damaged records:** **no effect measurable** — 0 DAMAGED_OR_UNCERTAIN cases occurred in this run for any target, so this sensitivity dimension is empty, not favorable or unfavorable.
- **Tablets with multiple target occurrences:** 34 distinct KU-RO-bearing tablets contribute 37 occurrences; three tablets (`HT25b`, `HT123+124a`, `HT127b`) each contribute 2. `HT123+124a`'s name suggests a joined/reconstructed tablet from two fragments — whether that reconstruction is archaeologically accepted is **DOMAIN-EXPERT DEPENDENT**, not resolved here.

## 15. Implementation limitations

- **Single-source corpus**, GORILA→`mwenge/lineara.xyz` lineage only; SigLA cross-check not yet performed (out of scope this round).
- **Fraction confidence grading is MISSING from this source** (per `docs/DATA_ADEQUACY_AUDIT.md`), and this measurably affects results: tablet **HT9a**, inspected directly, computes UNEXPLAINED_MISMATCH (sum 29 vs. total 31, whole-number-only) but its full attested fractional entries (5¾, 2½, 2½, 4¼ in the block; ¾ on the total) sum exactly to 31.0 vs. 31.75 — a residual of 0.75, which **would** classify ROUNDING_COMPATIBLE under the frozen tolerance. This is a concrete, demonstrated instance of the fraction-confidence gap changing an outcome category, not a hypothetical concern.
- **Rule A's ruling signal is MISSING from this source** (§4 above) — corrected to rely on prior-total/start-of-tablet only, a valid but narrower instantiation of Rule A than the protocol's full three-condition definition allows for sources that do encode true rulings.
- **Rule B remains BLOCKED** — no commodity-ID inventory was supplied or invented; NON_COMPARABLE could not be computed.
- **Entry-level transcription discrepancy observed, unresolved:** this source's HT13 entries (RE-ZA 5½, TE-TU 56, TE-KI 27½, KU-ZU-NI 18, DA-SI-*118 19, I-DU-NE-SI 5) do not match Paper 1's own cited HT13 breakdown (which lists a 28½ and a 16½ this source does not show, and does not list an 18-entry this source does show) — despite both arriving at the same whole-number total (130). **OPEN**, DOMAIN-EXPERT DEPENDENT — this project cannot adjudicate which transcription is correct.
- **KI-RO comparator underpowered** — n=3 arithmetically testable; directionally consistent with the intended negative-control role (§12) but not a strong inference on its own.
- **Site concentration** — see §16a: 35/37 KU-RO occurrences and 100% of arithmetically testable cases are from Haghia Triada; not yet tested as a hypothesis.
- **SigLA replication not yet performed** — this result reflects only the GORILA→`mwenge/lineara.xyz` lineage; see §11's scope statement.

## 16a. Site concentration — **NEW EMPIRICAL RESULT**

Reported descriptively only, not as a tested hypothesis:

- 35/37 KU-RO positional occurrences are from Haghia Triada.
- 26/26 (100%) of arithmetically testable KU-RO cases are from Haghia Triada.
- Khania contributes zero KU-RO occurrences in this source.

**Any hypothesis that KU-RO behavior is archive-, site-, or genre-conditioned
would be a NEW post-H1 hypothesis and requires a separately frozen protocol.**
No such hypothesis is proposed, tested, or implied here.

## 16. Domain-expert dependencies

Whether `HT123+124a`'s tablet-join is accepted; whether the HT13 entry-level discrepancy against Paper 1's citation reflects a genuine source difference, a transcription error in either source, or a scribal/collation subtlety; whether the 94.6%-Haghia-Triada concentration reflects genuine cross-site variation in KU-RO usage or an artifact of this source's uneven site coverage (Khania contributes **zero** KU-RO occurrences here at all, despite being one of Paper 1's own four selected sites); whether any specific UNEXPLAINED_MISMATCH case (e.g. HT46a: sum 1 vs. total 43, HT109: sum 8 vs. total 129) reflects damage, mis-sectioning, or a genuine counterexample — none of these are resolved by this project.
