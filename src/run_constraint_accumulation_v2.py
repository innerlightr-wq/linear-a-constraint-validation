"""
Constraint accumulation V2 real-data execution harness.

THIN WRAPPER around the frozen implementation in
src/constraint_accumulation_v2.py (frozen at commit
931fd5905ec3c67f526b108452ec9c355c1b0048,
docs/CONSTRAINT_ACCUMULATION_V2_PROTOCOL.md) and the reused,
also-frozen src/constraint_accumulation.py. Introduces NO new scientific
decision -- every category set, model block, adequacy threshold, CV rule,
null definition, p-value formula, and verdict rule is read from those two
modules / the frozen V2 protocol document unchanged. sklearn's
GroupKFold and LogisticRegression are used only as mechanical
implementations of the protocol's already-fixed specification, exactly as
in src/run_constraint_accumulation.py (V1's own harness).

THIS ROUND'S FIREWALL (docs/CONSTRAINT_ACCUMULATION_V2_PROTOCOL.md §14 /
this round's own instructions): this module's __main__ entry point, when
run against the real corpus, performs ONLY provenance/adequacy checks --
marginal counts, never crossed with any conditional Y-vs-predictor
relationship. It does NOT fit any model, run any CV fold, compute any
log-loss/H_hat/ΔH, run any permutation, or compute any p-value/Holm-
adjusted-p/verdict against real data.

`run_full_pipeline_v2` (the complete scientific pipeline) IS fully
implemented below and IS exercised end-to-end by
tests/test_run_constraint_accumulation_v2.py -- but ONLY against
hand-built synthetic fixtures, NEVER against
data/generated/lineara_extracted.json. Invoking it against the real
corpus is a separate, separately-authorized future step -- not taken in
this round.
"""
from __future__ import annotations

import json
import os
import random
import sys
from collections import defaultdict
from typing import Optional

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_constraint_accumulation as rca_v1  # noqa: E402 -- reused: build_corpus_rows, corpus_checksum, load_raw
import constraint_accumulation as ca  # noqa: E402
import constraint_accumulation_v2 as v2  # noqa: E402

SEED = 20260906
B = 2000
N_SPLITS = 5   # protocol §6: exactly 5, NO 3-fold fallback

PROTOCOL_FREEZE_SHA = "931fd5905ec3c67f526b108452ec9c355c1b0048"
DATA_PATH = rca_v1.DATA_PATH

_LEVEL_COLUMNS = {
    "site_support": (
        [("site_block", lvl) for lvl in ca._LEVELS["site_block"] if lvl != ca.REFERENCE_LEVELS["site_block"]]
        + [("support_block", lvl) for lvl in ca._LEVELS["support_block"] if lvl != ca.REFERENCE_LEVELS["support_block"]]
    ),
    "position": [("position_bucket", lvl) for lvl in ca._LEVELS["position_bucket"] if lvl != ca.REFERENCE_LEVELS["position_bucket"]],
    "commodity": [("commodity_class", lvl) for lvl in ca._LEVELS["commodity_class"] if lvl != ca.REFERENCE_LEVELS["commodity_class"]],
}


# =============================================================================
# ALLOWED AGAINST REAL DATA: provenance / row construction / marginal adequacy
# =============================================================================
def build_v2_corpus_rows(path: str) -> list:
    """Loads the primary corpus (reusing run_constraint_accumulation's
    already-frozen loader/row-builder unchanged) and restricts to the V2
    population via constraint_accumulation_v2.build_v2_rows, unchanged."""
    feature_rows = rca_v1.build_corpus_rows(path)
    return v2.build_v2_rows(feature_rows)


def compute_provenance_and_adequacy_v2(rows: list, freeze_sha: str, corpus_path: str) -> dict:
    """MARGINAL adequacy diagnostics only -- N, tablet count, positive/
    negative counts, per-category counts -- none crossed with any other
    field."""
    n_total = len(rows)
    tablets = v2.unique_tablets(rows)
    n_positive = sum(1 for r in rows if r.fraction_present)
    n_negative = n_total - n_positive

    return {
        "status": "PROVENANCE_AND_ADEQUACY_ONLY",
        "freeze_sha": freeze_sha,
        "corpus_path": corpus_path,
        "corpus_checksum_sha256": rca_v1.corpus_checksum(corpus_path) if os.path.exists(corpus_path) else None,
        "n_total": n_total,
        "n_tablets": len(tablets),
        "n_positive": n_positive,
        "n_negative": n_negative,
        "coarse_screen_pass": (n_total >= ca.ADEQUACY_MIN_TOTAL_N and len(tablets) >= ca.ADEQUACY_MIN_TABLETS),
        "site_counts": v2.population_cardinality(rows, "site_block"),
        "support_counts": v2.population_cardinality(rows, "support_block"),
        "position_counts": v2.population_cardinality(rows, "position_bucket"),
        "commodity_counts": v2.population_cardinality(rows, "commodity_class"),
        "note": ("No model was fit, no CV fold was run, no log loss/H_hat/ΔH was "
                 "computed, no permutation was run, no p-value or verdict was "
                 "computed. Marginal counts only. Per-fold/per-stratum adequacy "
                 "(criteria B/C, protocol §7) require fold construction and are "
                 "computed only inside run_full_pipeline_v2, never here."),
    }


# =============================================================================
# FULL SCIENTIFIC PIPELINE -- fully implemented, NOT invoked against real
# data this round. Exercised only by synthetic fixtures.
# =============================================================================
def _columns_for_blocks(blocks: list[str]) -> list[tuple]:
    cols = []
    for b in blocks:
        if b == "magnitude":
            cols.append(("magnitude", "WHOLE_COMPONENT_MAGNITUDE"))
        else:
            cols.extend(_LEVEL_COLUMNS[b])
    return cols


def _encode_matrix(rows: list, blocks: list[str]) -> list[list[float]]:
    cols = _columns_for_blocks(blocks)
    X = []
    for row in rows:
        indicators = {}
        if "site_support" in blocks:
            indicators.update(ca.encode_indicator("site_block", row.site_block))
            indicators.update(ca.encode_indicator("support_block", row.support_block))
        if "position" in blocks:
            indicators.update(ca.encode_indicator("position_bucket", row.position_bucket))
        if "commodity" in blocks:
            indicators.update(ca.encode_indicator("commodity_class", row.commodity_class))
        if "magnitude" in blocks:
            indicators["magnitude__WHOLE_COMPONENT_MAGNITUDE"] = row.whole_component_magnitude
        X.append([indicators.get(f"{f}__{lvl}", 0.0) for f, lvl in cols])
    return X


def _fit_predict(X_train, y_train, X_test, seed: int) -> list[float]:
    n_cols = len(X_train[0]) if X_train else 0
    if n_cols == 0:
        base_rate = sum(y_train) / len(y_train)
        return [base_rate] * len(X_test)
    clf = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, random_state=seed)
    clf.fit(X_train, y_train)
    return list(clf.predict_proba(X_test)[:, 1])


def _make_group_folds(tablet_ids: list, n_splits: int):
    n_groups = len(set(tablet_ids))
    if n_groups < n_splits:
        return None
    return list(GroupKFold(n_splits=n_splits).split(np.zeros(len(tablet_ids)), groups=tablet_ids))


def _folds_all_evaluable(folds, y):
    for train_idx, _ in folds:
        if not ca.fold_is_evaluable([y[i] for i in train_idx]):
            return False
    return True


def _folds_minority_adequate(folds, y) -> bool:
    """Protocol §7 criterion B: every TRAINING fold must have
    >= MIN_MINORITY_PER_TRAINING_FOLD positive rows."""
    for train_idx, _ in folds:
        if not v2.training_fold_minority_adequate([y[i] for i in train_idx]):
            return False
    return True


def _h_hat_for_model(rows: list, blocks: list[str], folds: list, y: list, seed: int) -> float:
    oof_pred = [None] * len(rows)
    X_all = _encode_matrix(rows, blocks)
    for train_idx, test_idx in folds:
        X_train = [X_all[i] for i in train_idx]
        X_test = [X_all[i] for i in test_idx]
        y_train = [y[i] for i in train_idx]
        preds = _fit_predict(X_train, y_train, X_test, seed)
        for idx, p in zip(test_idx, preds):
            oof_pred[idx] = p
    return ca.log_loss_bits(list(y), oof_pred)


def _strata_for_step(rows: list, y: list, step: str) -> dict:
    fields = v2.STEP_STRATUM_FIELDS_V2[step]
    rbs: dict = defaultdict(list)
    for i, r in enumerate(rows):
        key = tuple(getattr(r, f) for f in fields)
        rbs[key].append(y[i])
    return dict(rbs)


def run_full_pipeline_v2(rows: list, seed: int = SEED, B: int = B, *,
                         min_total_n: int = ca.ADEQUACY_MIN_TOTAL_N,
                         min_tablets: int = ca.ADEQUACY_MIN_TABLETS,
                         n_splits: int = N_SPLITS) -> dict:
    """FULLY IMPLEMENTED per docs/CONSTRAINT_ACCUMULATION_V2_PROTOCOL.md.
    NEVER invoked against the real corpus in this round -- exercised only
    by tests/test_run_constraint_accumulation_v2.py's synthetic fixtures.

    `min_total_n`/`min_tablets`/`n_splits` are keyword-only TEST-SUPPORT
    overrides (default to the frozen protocol constants) so tests can
    exercise rare edge paths against small synthetic datasets -- never
    used by this module's own real-data entry point."""
    n_total = len(rows)
    tablet_ids = [r.tablet_id for r in rows]
    y = [1 if r.fraction_present else 0 for r in rows]
    n_positive = sum(y)
    n_negative = n_total - n_positive
    n_tablets = len(set(tablet_ids))

    # criterion D: coarse feasibility screen
    if not (n_total >= min_total_n and n_tablets >= min_tablets):
        return {"status": "INCONCLUSIVE", "reason": "coarse N/tablet feasibility screen failed"}

    # protocol §6: exactly n_splits folds, NO fallback
    folds = _make_group_folds(tablet_ids, n_splits)
    if folds is None:
        return {"status": "INCONCLUSIVE", "reason": f"cannot construct {n_splits} grouped folds (too few tablet groups)"}

    # criterion A: hard CV evaluability
    if not _folds_all_evaluable(folds, y):
        return {"status": "INCONCLUSIVE", "reason": "criterion A failed: a training fold lacks both classes"}

    # criterion B: minority support per training fold
    if not _folds_minority_adequate(folds, y):
        return {"status": "INCONCLUSIVE", "reason": "criterion B failed: a training fold has < MIN_MINORITY_PER_TRAINING_FOLD positives"}

    # criterion C: mixed-strata fraction at the finest (M3->M4) conditioning
    m4_strata = _strata_for_step(rows, y, "M4")
    if not v2.strata_mixed_adequate(m4_strata):
        return {"status": "INCONCLUSIVE", "reason": "criterion C failed: < MIN_MIXED_STRATA_FRACTION of M3->M4 strata are mixed"}

    h_hat = {}
    for model_name, blocks in v2.MODEL_BLOCKS_V2.items():
        h_hat[model_name] = _h_hat_for_model(rows, blocks, folds, y, seed)

    delta_h = {
        "M1": ca.delta_h(h_hat["M0"], h_hat["M1"]),
        "M2": ca.delta_h(h_hat["M1"], h_hat["M2"]),
        "M3": ca.delta_h(h_hat["M2"], h_hat["M3"]),
        "M4": ca.delta_h(h_hat["M3"], h_hat["M4"]),
    }

    step_pvalues: dict[str, Optional[float]] = {}
    rng = random.Random(seed)

    for step in ("M2", "M3", "M4"):
        stratum_fields = v2.STEP_STRATUM_FIELDS_V2[step]
        perm_rows = [(tuple(getattr(r, f) for f in stratum_fields), y[i]) for i, r in enumerate(rows)]
        permutable, _ = ca.permutable_strata(perm_rows, lambda preds: preds)
        if not permutable:
            step_pvalues[step] = None
            continue

        blocks_prev = v2.MODEL_BLOCKS_V2[v2.STEP_PREV_MODEL_V2[step]]
        blocks_curr = v2.MODEL_BLOCKS_V2[step]
        delta_obs = delta_h[step]

        perm_deltas = []
        for _ in range(B):
            permuted = ca.conditional_permutation_delta(perm_rows, lambda preds: preds, rng)
            y_perm = [yp for _, yp in permuted]
            h_prev = _h_hat_for_model(rows, blocks_prev, folds, y_perm, seed)
            h_curr = _h_hat_for_model(rows, blocks_curr, folds, y_perm, seed)
            perm_deltas.append(ca.delta_h(h_prev, h_curr))
        step_pvalues[step] = ca.step_permutation_pvalue(delta_obs, perm_deltas, B)

    holm_adjusted = ca.holm_family(step_pvalues)

    step_verdicts = {}
    for step in ("M2", "M3", "M4"):
        holm_p = holm_adjusted.get(step)
        step_verdicts[step] = v2.classify_step_verdict(holm_p, delta_h[step])

    broad_verdict = v2.classify_broad_verdict(step_verdicts)

    return {
        "status": "COMPLETE",
        "n_splits": n_splits,
        "seed": seed,
        "B": B,
        "h_hat": h_hat,
        "delta_h": delta_h,
        "raw_p": step_pvalues,
        "holm_adjusted_p": holm_adjusted,
        "step_verdicts": step_verdicts,
        "broad_program_update": broad_verdict,
    }


# =============================================================================
# result serialization (plumbing)
# =============================================================================
def write_result_json(result: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)


if __name__ == "__main__":
    # PROVENANCE/ADEQUACY ONLY -- see module docstring. run_full_pipeline_v2
    # is deliberately NOT called here against real data this round.
    rows = build_v2_corpus_rows(DATA_PATH)
    result = compute_provenance_and_adequacy_v2(
        rows, freeze_sha=PROTOCOL_FREEZE_SHA, corpus_path=DATA_PATH,
    )
    import pprint
    pprint.pprint(result, width=120, sort_dicts=False)
