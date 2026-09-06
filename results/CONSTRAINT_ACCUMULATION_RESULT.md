# Constraint-accumulation result — SCHEMA TEMPLATE, NOT A REAL RESULT

**This entire document is a SYNTHETIC FIXTURE TEMPLATE.** Every number
below comes from `results/constraint_accumulation_result.json`, itself
generated from hand-built synthetic rows (30 fake tablets, 60 fake rows)
with a reduced `B=5` (the frozen protocol's `B=2000` is unchanged as the
module default — reduced only for template-generation speed). **No row in
this document reflects `data/generated/lineara_extracted.json` or any
other real corpus data.** Its only purpose is to fix the result schema
(Phase 8) before any real inference is run, exactly as the task requires:
*"Design the result output now, before real inference... DO NOT populate
them with real performance yet. A synthetic fixture/template is fine."*

When a real run is authorized, this file is regenerated from the real
`results/constraint_accumulation_result.json` and this notice is removed.

## A. Provenance

| | |
|---|---|
| Freeze commit (`CONSTRAINT_ACCUMULATION_PRE_RESULT_FREEZE`) | `2f58a7c80c173f538c758596ce94aa353d1ca07c` |
| Corpus source | `data/generated/lineara_extracted.json` *(template used synthetic rows instead)* |
| Corpus checksum (SHA-256) | *(not applicable — template run)* |
| Execution timestamp | *(not applicable — template run)* |

## B. Adequacy

| | template value |
|---|---|
| N (usable rows) | 60 |
| Unique tablets | 30 |
| Positives | 30 |
| Negatives | 30 |
| Per-category support | *(see `compute_provenance_and_adequacy` output for the real run — not reproduced here)* |
| Chosen fold count | 5 |
| Evaluable steps | M2, M3, M4 |

## C. Model performance (`H_hat`, bits)

| model | H_hat |
|---|---|
| H0 | 1.000000 |
| H1 | 1.000000 |
| H2 | 1.011054 |
| H3 | 1.011147 |
| H4 | 1.013109 |

## D. Increments (`ΔH`, bits)

| step | ΔH |
|---|---|
| ΔH_1 (M0→M1) | 0.000000 |
| ΔH_2 (M1→M2) | −0.011054 |
| ΔH_3 (M2→M3) | −0.0000929 |
| ΔH_4 (M3→M4) | −0.001962 |

## E. Inference

| step | raw permutation p | Holm-adjusted p |
|---|---|---|
| M2 | 0.3333 | 0.6667 |
| M3 | 0.1667 | 0.5000 |
| M4 | 1.0000 | 1.0000 |

*(Template used B=5, so these p-values are not meaningful in themselves —
only their presence/schema position matters here.)*

## F. Verdicts

| step | verdict |
|---|---|
| M2 | NOT SUPPORTED |
| M3 | NOT SUPPORTED |
| M4 | NOT SUPPORTED |

**Broad program (template):** NEGATIVE UPDATE

*(Template values only — under the corrected Phase 1 rule, a step's
raw/Holm p-value is always computed and it always remains in the Holm
family whenever it is evaluable, regardless of its sign — this template
run happens to show all three as evaluable and all three as
NOT SUPPORTED, which is one possible schema shape, not a prediction of
the real outcome.)*

## G. Limitations (carried forward from the frozen protocol, restated for template completeness)

- Haghia-Triada / `Tablet`-support dominance (`docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md` §12) — no cross-site generalization claim will be made regardless of outcome.
- External semantic dependence of M3 (`C_COMMODITY` = LIQUID/DRY, EXTERNAL DOMAIN MODEL INPUT, §4/§14) — a positive M3 result supports conditional predictive usefulness of the imported label only, not an independently discovered Linear-A semantic constraint.
- Artifact dependence (§13) — the primary result uses tablet-level grouping, not physical-artifact grouping; the artifact-collapse sensitivity is predeclared but not part of the primary verdict.
- Sparse M4 null risk (§8, §9, §20 item 2) — M4's conditional null strata may be sparse enough to render M4 `NOT_EVALUABLE` in the real run; this is a valid, informative outcome under the frozen protocol, not a failure to fix.
