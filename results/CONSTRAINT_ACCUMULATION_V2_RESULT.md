# Constraint accumulation V2 result — SCHEMA TEMPLATE, NOT A REAL RESULT

**This entire document is a SYNTHETIC FIXTURE TEMPLATE.** Every number
below comes from `results/constraint_accumulation_v2_result.json`, itself
generated from hand-built synthetic rows (60 fake tablets, 120 fake rows,
no real predictor–outcome relationship) with a reduced `B=30` (the frozen
protocol's `B=2000` is unchanged as the module default — reduced only for
template-generation speed). **No row in this document reflects
`data/generated/lineara_extracted.json` or any other real corpus data.**
Its only purpose is to fix the V2 result schema before any real inference
is run, per `docs/CONSTRAINT_ACCUMULATION_V2_PROTOCOL.md` §14. When a real
run is authorized, this file is regenerated from the real
`results/constraint_accumulation_v2_result.json` and this notice is
removed.

## A. Provenance

| | |
|---|---|
| V2 protocol freeze SHA | `931fd5905ec3c67f526b108452ec9c355c1b0048` |
| Corpus source | `data/generated/lineara_extracted.json` *(template used synthetic rows instead)* |
| Corpus checksum | *(not applicable — template run)* |
| Execution timestamp | *(not applicable — template run)* |
| Seed | `1` *(template only — real run uses `20260906`)* |
| B | `30` *(template only — real run uses `2000`)* |
| CV folds | `5` (protocol §6 — no 3-fold fallback exists for V2) |

## B. Adequacy (template values)

| | |
|---|---|
| N | 120 |
| Unique tablets | 60 |
| Criterion A (fold class presence) | PASS |
| Criterion B (≥5 minority/training fold) | PASS |
| Criterion C (≥50% mixed M3→M4 strata) | PASS |
| Criterion D (coarse N/tablet screen) | PASS (using template's relaxed override thresholds) |

## C. Model performance (`H_hat`, bits)

| model | H_hat |
|---|---|
| H0 | 0.896579 |
| H1 | 0.903816 |
| H2 | 0.923704 |
| H3 | 0.946016 |
| H4 | 0.979286 |

## D. Increments (`ΔH`, bits)

| step | ΔH |
|---|---|
| ΔH1 (M0→M1) | −0.007237 |
| ΔH2 (M1→M2) | −0.019888 |
| ΔH3 (M2→M3) | −0.022312 |
| ΔH4 (M3→M4) | −0.033270 |

## E. Inference

| step | raw p | Holm-adjusted p | verdict |
|---|---|---|---|
| M2 | 0.6774 | 1.0000 | NOT SUPPORTED |
| M3 | 1.0000 | 1.0000 | NOT SUPPORTED |
| M4 | 0.9355 | 1.0000 | NOT SUPPORTED |

## F. Broad verdict (template)

**NEGATIVE UPDATE**

*(Expected and correct for this template: the synthetic data has no real
predictor–outcome relationship by construction, so a clean negative
result here is a validity check on the machinery, not a finding.)*

## G. Limitations (carried forward from the frozen protocol, restated for template completeness)

- **Scope:** any real V2 result is scoped to quantities ≥1 whole unit
  (protocol §2) — never generalized to fraction-only expressions.
- **M4 naming:** `WHOLE_COMPONENT_MAGNITUDE` measures only the resolvable
  whole-number part, never the total value of an integer+fraction
  expression (protocol §5).
- **M3 (commodity):** EXTERNAL MODEL INFORMATION — remains part of the
  statistical testing family but never counts toward ACCUMULATION
  EVIDENCE on its own (protocol §11).
- **Adequacy criteria B/C:** disclosed, project-specific, mechanism-linked
  safeguards, not universal theorems (protocol §7).
- **Claim firewall:** even ACCUMULATION EVIDENCE would establish only a
  narrow, corpus-internal predictive claim — never decipherment, semantics,
  cognition, or cross-site universality (protocol §12).
