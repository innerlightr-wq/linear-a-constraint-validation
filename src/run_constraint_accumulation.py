"""
Constraint-accumulation real-data execution harness.

THIN WRAPPER around the frozen implementation in src/constraint_accumulation.py
(frozen at commit 2f58a7c80c173f538c758596ce94aa353d1ca07c,
docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md). Introduces NO new scientific
decision -- every category set, cutoff-fitting rule, model hyperparameter,
CV rule, null definition, p-value formula, and adequacy threshold is read
from constraint_accumulation.py / the frozen protocol document unchanged.
sklearn's GroupKFold and LogisticRegression are used only as mechanical
implementations of already-frozen specifications (grouped-by-tablet 5-fold
CV with a 3-fold fallback; L2-regularized logistic regression with
C=1.0/lbfgs/max_iter=1000/random_state=20260906) -- choosing to use these
standard library primitives to implement an unambiguous, already-fixed
specification is plumbing, not a new scientific decision.

THIS ROUND'S FIREWALL (docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md Phase 12
/ this round's own instructions): this module's __main__ entry point, when
run against the real corpus, performs ONLY provenance/adequacy checks
(corpus checksum, row/tablet/positive/negative marginal counts, adequacy-
gate and category-adequacy pass/fail -- all marginal, none crossed with
any conditional Y-vs-predictor relationship). It does NOT fit any model,
run any CV fold, compute any log-loss/H_hat/ΔH, run any permutation, or
compute any p-value/Holm-adjusted-p/verdict against real data.

`run_full_pipeline` (the complete scientific pipeline) IS fully
implemented below and IS exercised end-to-end by
tests/test_run_constraint_accumulation.py -- but ONLY against hand-built
synthetic fixtures, NEVER against data/generated/lineara_extracted.json.
Invoking `run_full_pipeline` against the real corpus is a separate,
separately-authorized future step -- not taken in this round.
"""
from __future__ import annotations

import hashlib
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
import lineara_adapter as la  # noqa: E402
import constraint_accumulation as ca  # noqa: E402

SEED = 20260906   # ENGINEERING REPRODUCIBILITY CHOICE, reused from Candidate 1's own convention
B = 2000
PRIMARY_N_SPLITS = 5
FALLBACK_N_SPLITS = 3

PROTOCOL_FREEZE_SHA = "2f58a7c80c173f538c758596ce94aa353d1ca07c"

PRE_RESULT_IMPLEMENTATION_INTERPRETATION = (
    "Per-step category adequacy (docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md "
    "§11) is applied to the newly introduced block at each incremental "
    "step (position for M2, commodity for M3, numeric for M4); previously "
    "admitted blocks retain their prior evaluability status and are not "
    "re-checked at later steps. This is a disclosed, pre-result reading of "
    "an otherwise-underspecified scoping detail in the frozen protocol -- "
    "not a new hypothesis, and not altered after seeing results."
)

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                          "data", "generated", "lineara_extracted.json")

MODEL_BLOCKS = {
    "M0": [],
    "M1": ["site_support"],
    "M2": ["site_support", "position"],
    "M3": ["site_support", "position", "commodity"],
    "M4": ["site_support", "position", "commodity", "numeric"],
}
STEP_PREV_MODEL = {"M2": "M1", "M3": "M2", "M4": "M3"}
# M_{k-1}'s own predictor fields, for the conditional null (protocol §8)
STEP_STRATUM_FIELDS = {
    "M2": ("site_block", "support_block"),
    "M3": ("site_block", "support_block", "position_bucket"),
    "M4": ("site_block", "support_block", "position_bucket", "commodity_class"),
}
STEP_BLOCK_ADEQUACY_FIELD = {
    "M2": ("position_bucket", ca.ADEQUACY_MIN_CATEGORY_ROWS),
    "M3": ("commodity_class", ca.ADEQUACY_MIN_CATEGORY_TABLETS),
    "M4": ("numeric_bin", ca.ADEQUACY_MIN_CATEGORY_ROWS),
}

_LEVEL_COLUMNS = {
    "site_support": (
        [("site_block", lvl) for lvl in ca._LEVELS["site_block"] if lvl != ca.REFERENCE_LEVELS["site_block"]]
        + [("support_block", lvl) for lvl in ca._LEVELS["support_block"] if lvl != ca.REFERENCE_LEVELS["support_block"]]
    ),
    "position": [("position_bucket", lvl) for lvl in ca._LEVELS["position_bucket"] if lvl != ca.REFERENCE_LEVELS["position_bucket"]],
    "commodity": [("commodity_class", lvl) for lvl in ca._LEVELS["commodity_class"] if lvl != ca.REFERENCE_LEVELS["commodity_class"]],
    "numeric": [("numeric_bin", lvl) for lvl in ca._LEVELS["numeric_bin"] if lvl != ca.REFERENCE_LEVELS["numeric_bin"]],
}


# =============================================================================
# ALLOWED AGAINST REAL DATA: provenance / row construction / marginal adequacy
# =============================================================================
def corpus_checksum(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_raw(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_corpus_rows(path: str) -> list[ca.FeatureRow]:
    """Loads the primary corpus and builds feature rows via the frozen
    constraint_accumulation.build_feature_rows, unchanged. No filtering,
    binning, or classification rule introduced here beyond what that
    frozen function already does."""
    raw = load_raw(path)
    rows: list[ca.FeatureRow] = []
    for r in raw:
        record = la.raw_tablet_to_record(r)
        rows.extend(ca.build_feature_rows(record, site=r.get("site"), support=r.get("support")))
    return rows


def compute_provenance_and_adequacy(rows: list, freeze_sha: str, corpus_path: str) -> dict:
    """MARGINAL adequacy diagnostics only -- N, tablet count, positive/
    negative counts, per-category counts -- none crossed with any other
    field. Matches this round's explicit allowance: 'if validating row
    construction would reveal target/predictor marginal counts already
    known from previous rounds, that is acceptable. Do not inspect new
    conditional relationships' -- nothing here is conditional."""
    n_total = len(rows)
    tablets = ca.unique_tablets(rows)
    n_positive = sum(1 for r in rows if r.fraction_present)
    n_negative = n_total - n_positive

    def tablets_per_category(field):
        d = defaultdict(set)
        for r in rows:
            d[getattr(r, field)].add(r.tablet_id)
        return {k: len(v) for k, v in d.items()}

    category_adequacy = {
        "site_block": ca.category_adequacy(tablets_per_category("site_block"), ca.ADEQUACY_MIN_CATEGORY_TABLETS),
        "support_block": ca.category_adequacy(tablets_per_category("support_block"), ca.ADEQUACY_MIN_CATEGORY_TABLETS),
        "commodity_class": ca.category_adequacy(tablets_per_category("commodity_class"), ca.ADEQUACY_MIN_CATEGORY_TABLETS),
        "position_bucket": ca.category_adequacy(ca.cardinality(rows, "position_bucket"), ca.ADEQUACY_MIN_CATEGORY_ROWS),
        "numeric_bin": ca.category_adequacy(ca.cardinality(rows, "numeric_bin"), ca.ADEQUACY_MIN_CATEGORY_ROWS),
    }

    return {
        "status": "PROVENANCE_AND_ADEQUACY_ONLY",
        "freeze_sha": freeze_sha,
        "corpus_path": corpus_path,
        "corpus_checksum_sha256": corpus_checksum(corpus_path) if os.path.exists(corpus_path) else None,
        "n_total": n_total,
        "n_tablets": len(tablets),
        "n_positive": n_positive,
        "n_negative": n_negative,
        "primary_adequacy_gate_pass": ca.primary_adequacy_gate(n_total, len(tablets), n_positive, n_negative),
        "site_counts": ca.cardinality(rows, "site_block"),
        "support_counts": ca.cardinality(rows, "support_block"),
        "position_counts": ca.cardinality(rows, "position_bucket"),
        "commodity_counts": ca.cardinality(rows, "commodity_class"),
        "category_adequacy": category_adequacy,
        "pre_result_implementation_interpretation": PRE_RESULT_IMPLEMENTATION_INTERPRETATION,
        "note": ("No model was fit, no CV fold was run, no log loss/H_hat/ΔH was "
                 "computed, no permutation was run, no p-value or verdict was "
                 "computed. Marginal counts only."),
    }


# =============================================================================
# FULL SCIENTIFIC PIPELINE -- fully implemented, NOT invoked against real
# data this round. Exercised only by synthetic fixtures (see
# tests/test_run_constraint_accumulation.py).
# =============================================================================
def _columns_for_blocks(blocks: list[str]) -> list[tuple]:
    cols = []
    for b in blocks:
        cols.extend(_LEVEL_COLUMNS[b])
    return cols


def _encode_matrix(rows: list, blocks: list[str], numeric_cutoffs: Optional[tuple]) -> list[list[float]]:
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
        if "numeric" in blocks:
            nb = ca.numeric_bin_fold(row.numeric_value, numeric_cutoffs[0], numeric_cutoffs[1])
            indicators.update(ca.encode_indicator("numeric_bin", nb))
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
    """Returns list of (train_idx, test_idx) or None if GroupKFold cannot
    construct `n_splits` groups at all, or if any TRAINING fold is not
    evaluable (fold_is_evaluable) for the given y."""
    n_groups = len(set(tablet_ids))
    if n_groups < n_splits:
        return None
    return list(GroupKFold(n_splits=n_splits).split(np.zeros(len(tablet_ids)), groups=tablet_ids))


def _folds_all_evaluable(folds, y):
    for train_idx, _ in folds:
        if not ca.fold_is_evaluable([y[i] for i in train_idx]):
            return False
    return True


def _h_hat_for_model(rows: list, blocks: list[str], folds: list, y: list, seed: int) -> float:
    """Out-of-fold log loss (bits) for one model (block set), across the
    already-chosen `folds`. Numeric-bin cutoffs, if `numeric` is among
    `blocks`, are fit fresh inside each TRAINING fold only (protocol §4a)."""
    oof_pred = [None] * len(rows)
    for train_idx, test_idx in folds:
        numeric_cutoffs = None
        if "numeric" in blocks:
            train_values = [rows[i].numeric_value for i in train_idx]
            numeric_cutoffs = ca.fit_numeric_bin_cutoffs(train_values)
        X_all = _encode_matrix(rows, blocks, numeric_cutoffs)
        X_train = [X_all[i] for i in train_idx]
        X_test = [X_all[i] for i in test_idx]
        y_train = [y[i] for i in train_idx]
        preds = _fit_predict(X_train, y_train, X_test, seed)
        for idx, p in zip(test_idx, preds):
            oof_pred[idx] = p
    y_true = list(y)
    return ca.log_loss_bits(y_true, oof_pred)


def run_full_pipeline(rows: list, seed: int = SEED, B: int = B, *,
                      min_total_n: int = ca.ADEQUACY_MIN_TOTAL_N,
                      min_tablets: int = ca.ADEQUACY_MIN_TABLETS,
                      min_positive: int = ca.ADEQUACY_MIN_POSITIVE,
                      min_negative: int = ca.ADEQUACY_MIN_NEGATIVE,
                      n_splits_primary: int = PRIMARY_N_SPLITS,
                      n_splits_fallback: int = FALLBACK_N_SPLITS) -> dict:
    """FULLY IMPLEMENTED per docs/CONSTRAINT_ACCUMULATION_PROTOCOL.md.
    NEVER invoked against the real corpus in this round -- exercised only
    by tests/test_run_constraint_accumulation.py's synthetic fixtures.

    The keyword-only `min_*`/`n_splits_*` parameters exist ONLY so tests
    can exercise rare edge paths (INCONCLUSIVE, 3-fold fallback, sparse-
    strata NOT_EVALUABLE) against small synthetic datasets without needing
    150+ rows -- they default to the exact frozen protocol constants and
    are NEVER overridden by this module's own real-data entry point
    (`__main__`, which does not call this function at all this round)."""
    n_total = len(rows)
    tablet_ids = [r.tablet_id for r in rows]
    y = [1 if r.fraction_present else 0 for r in rows]
    n_positive = sum(y)
    n_negative = n_total - n_positive
    n_tablets = len(set(tablet_ids))

    adequate = (n_total >= min_total_n and n_tablets >= min_tablets
                and n_positive >= min_positive and n_negative >= min_negative)
    if not adequate:
        return {"status": "INCONCLUSIVE", "reason": "primary adequacy gate failed"}

    folds = _make_group_folds(tablet_ids, n_splits_primary)
    chosen_n_splits = n_splits_primary
    if folds is None or not _folds_all_evaluable(folds, y):
        folds = _make_group_folds(tablet_ids, n_splits_fallback)
        chosen_n_splits = n_splits_fallback
        if folds is None or not _folds_all_evaluable(folds, y):
            return {"status": "INCONCLUSIVE", "reason": "no evaluable grouped CV split at primary or fallback fold count"}

    h_hat = {}
    for model_name, blocks in MODEL_BLOCKS.items():
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
        stratum_fields = STEP_STRATUM_FIELDS[step]
        adequacy_field, min_count = STEP_BLOCK_ADEQUACY_FIELD[step]
        cat_counts = ca.cardinality(rows, adequacy_field)
        cat_ok = ca.category_adequacy(cat_counts, min_count)
        if not all(cat_ok.values()):
            step_pvalues[step] = None  # NOT_EVALUABLE: category adequacy failed
            continue

        perm_rows = [(tuple(getattr(r, f) for f in stratum_fields), y[i]) for i, r in enumerate(rows)]
        permutable, _ = ca.permutable_strata(perm_rows, lambda preds: preds)
        if not permutable:
            step_pvalues[step] = None  # NOT_EVALUABLE: no permutable strata
            continue

        blocks_prev = MODEL_BLOCKS[STEP_PREV_MODEL[step]]
        blocks_curr = MODEL_BLOCKS[step]
        delta_obs = delta_h[step]

        try:
            perm_deltas = []
            for _ in range(B):
                permuted = ca.conditional_permutation_delta(perm_rows, lambda preds: preds, rng)
                y_perm = list(y)
                for i, (_, y_p) in enumerate(permuted):
                    y_perm[i] = y_p
                h_prev = _h_hat_for_model(rows, blocks_prev, folds, y_perm, seed)
                h_curr = _h_hat_for_model(rows, blocks_curr, folds, y_perm, seed)
                perm_deltas.append(ca.delta_h(h_prev, h_curr))
            step_pvalues[step] = ca.step_permutation_pvalue(delta_obs, perm_deltas, B)
        except ValueError:
            step_pvalues[step] = None  # NOT_EVALUABLE: e.g. numeric cutoff fitting failed on a permuted fold

    holm_adjusted = ca.holm_family(step_pvalues)

    verdicts = {}
    for step in ("M2", "M3", "M4"):
        if step_pvalues[step] is None:
            verdicts[step] = "NOT_EVALUABLE"
        elif holm_adjusted[step] < 0.05 and delta_h[step] > 0:
            verdicts[step] = "SUPPORTED"
        else:
            verdicts[step] = "NOT SUPPORTED"

    supported_count = sum(1 for v in verdicts.values() if v == "SUPPORTED")
    any_evaluable = any(v != "NOT_EVALUABLE" for v in verdicts.values())
    if not any_evaluable:
        broad_verdict = "NO UPDATE"
    elif supported_count == 0:
        broad_verdict = "NEGATIVE UPDATE"
    elif supported_count == 1:
        broad_verdict = "WEAK POSITIVE UPDATE"
    else:
        broad_verdict = "MODERATE POSITIVE UPDATE"

    return {
        "status": "COMPLETE",
        "chosen_n_splits": chosen_n_splits,
        "seed": seed,
        "B": B,
        "h_hat": h_hat,
        "delta_h": delta_h,
        "raw_p": step_pvalues,
        "holm_adjusted_p": holm_adjusted,
        "step_verdicts": verdicts,
        "broad_program_update": broad_verdict,
        "pre_result_implementation_interpretation": PRE_RESULT_IMPLEMENTATION_INTERPRETATION,
    }


# =============================================================================
# result serialization (plumbing)
# =============================================================================
def write_result_json(result: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)


if __name__ == "__main__":
    # PROVENANCE/ADEQUACY ONLY -- see module docstring. run_full_pipeline
    # is deliberately NOT called here against real data this round.
    rows = build_corpus_rows(DATA_PATH)
    result = compute_provenance_and_adequacy(
        rows,
        freeze_sha=PROTOCOL_FREEZE_SHA,
        corpus_path=DATA_PATH,
    )
    import pprint
    pprint.pprint(result, width=120, sort_dicts=False)
