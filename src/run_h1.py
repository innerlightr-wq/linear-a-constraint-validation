"""
H1 corpus-wide driver.

Uses ONLY src/lineara_adapter.py and src/kuro_protocol.py for all
classification logic -- this file contains no reimplementation of the H1
protocol. Its job is exactly: iterate every corpus record, adapt it,
identify occurrences of each of the three targets separately, classify each
occurrence using the frozen protocol functions, and aggregate only after
every occurrence has been classified.

RULE B REMAINS BLOCKED. No commodity_ids are supplied anywhere in this
file; every preceding_block call below uses rule="A" only.

KI-RO and PO-TO-KU-RO are processed through the exact same functions as
KU-RO (for a fair, non-cherry-picked comparator/exploratory computation) but
their aggregate results are never passed to kuro_protocol.verdict() -- only
KU-RO's are, per H1_PROTOCOL.md #9/#11.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import kuro_protocol as kp  # noqa: E402
import lineara_adapter as la  # noqa: E402

TARGETS = ("KU-RO", "KI-RO", "PO-TO-KU-RO")


def load_raw(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_occurrence_rows(raw_records: list[dict]) -> list[dict]:
    """Occurrence-level rows for ALL three targets. Aggregation happens
    strictly after this function returns -- nothing here computes a rate,
    a sample total, or a verdict."""
    rows = []
    fallback_log: list = []

    for raw in raw_records:
        site = raw.get("site")
        record = la.raw_tablet_to_record(raw, fallback_log=fallback_log)

        for target in TARGETS:
            occs = kp.find_occurrences(record, target)
            for occ_index, idx in enumerate(occs):
                occ_token = record.tokens[idx]
                position = kp.classify_position(record, idx)
                total_token = kp.associated_numeral(record, idx)
                block_a = kp.preceding_block(record, idx, rule="A")

                numeral_present = total_token is not None
                exclusion = kp.classify_exclusion(occ_token, total_token, block_a,
                                                   block_tokens_b=None)

                # Independent boolean flags (all-exclusion-flags view), computed
                # from the same already-frozen primitives kuro_protocol exposes
                # -- not a second implementation of the exclusion logic, just
                # exposing its inputs individually for the audit table.
                flag_ambiguous = occ_token.sign_identity_uncertain
                total_value = kp.numeral_value(total_token) if total_token else None
                block_values = [v for v in (kp.numeral_value(t) for t in block_a) if v is not None]
                flag_missing = total_value is None or not block_values
                flag_damaged = occ_token.damaged or (total_token.damaged if total_token else False) \
                    or any(t.damaged for t in block_a)

                eligible = numeral_present and bool(block_values)

                row = {
                    "tablet_id": record.tablet_id,
                    "target": target,
                    "occurrence_index": occ_index,
                    "site": site,
                    "position_class": position,
                    "numeral_present": numeral_present,
                    "arithmetically_eligible": eligible,
                    "primary_exclusion_reason": exclusion,
                    "flag_ambiguous": flag_ambiguous,
                    "flag_missing": flag_missing,
                    "flag_damaged": flag_damaged,
                    "n_preceding_entries": len(block_values),
                    "computed_sum": sum(block_values) if block_values else None,
                    "recorded_total": total_value,
                    "residual": None,
                    "relative_residual": None,
                    "arithmetic_outcome": "NOT_TESTABLE",
                    "sectioning_rule": "A",
                }

                if exclusion is None and eligible:
                    r, r_rel = kp.residual(total_value, block_values)
                    outcome = kp.classify_arithmetic(r, r_rel, damaged=flag_damaged)
                    row["residual"] = r
                    row["relative_residual"] = r_rel
                    row["arithmetic_outcome"] = outcome
                elif flag_damaged and eligible:
                    # eligible but excluded specifically for DAMAGED -- still
                    # compute the residual for transparency, outcome forced
                    # to DAMAGED_OR_UNCERTAIN by classify_arithmetic itself.
                    r, r_rel = kp.residual(total_value, block_values)
                    outcome = kp.classify_arithmetic(r, r_rel, damaged=True)
                    row["residual"] = r
                    row["relative_residual"] = r_rel
                    row["arithmetic_outcome"] = outcome

                rows.append(row)

    return rows, fallback_log


def aggregate(rows: list[dict], target: str) -> dict:
    """Raw integer counts ONLY -- no rate, no verdict. Computed strictly
    from already-classified occurrence rows."""
    sub = [r for r in rows if r["target"] == target]
    n_positional = len(sub)
    pos_counts = Counter(r["position_class"] for r in sub)

    testable = [r for r in sub if r["arithmetic_outcome"] != "NOT_TESTABLE"]
    not_testable = [r for r in sub if r["arithmetic_outcome"] == "NOT_TESTABLE"]
    outcome_counts = Counter(r["arithmetic_outcome"] for r in sub)
    exclusion_counts = Counter(r["primary_exclusion_reason"] for r in not_testable)

    return {
        "target": target,
        "n_positional": n_positional,
        "terminal": pos_counts.get("TERMINAL", 0),
        "near_terminal": pos_counts.get("NEAR_TERMINAL", 0),
        "non_terminal": pos_counts.get("NON_TERMINAL", 0),
        "n_arithmetically_testable": len(testable),
        "exact_closure": outcome_counts.get("EXACT_CLOSURE", 0),
        "rounding_compatible": outcome_counts.get("ROUNDING_COMPATIBLE", 0),
        "damaged_or_uncertain": outcome_counts.get("DAMAGED_OR_UNCERTAIN", 0),
        "unexplained_mismatch": outcome_counts.get("UNEXPLAINED_MISMATCH", 0),
        "not_testable": len(not_testable),
        "exclusion_breakdown": dict(exclusion_counts),
        "sites": sorted({r["site"] for r in sub if r["site"]}),
    }


def sanity_check(agg: dict) -> list[str]:
    problems = []
    pos_sum = agg["terminal"] + agg["near_terminal"] + agg["non_terminal"]
    if pos_sum != agg["n_positional"]:
        problems.append(
            f"{agg['target']}: TERMINAL+NEAR_TERMINAL+NON_TERMINAL={pos_sum} "
            f"!= n_positional={agg['n_positional']}")

    testable_sum = (agg["exact_closure"] + agg["rounding_compatible"]
                     + agg["damaged_or_uncertain"] + agg["unexplained_mismatch"])
    if testable_sum != agg["n_arithmetically_testable"]:
        problems.append(
            f"{agg['target']}: arithmetic outcome categories sum to {testable_sum} "
            f"!= n_arithmetically_testable={agg['n_arithmetically_testable']}")

    total_check = agg["n_arithmetically_testable"] + agg["not_testable"]
    if total_check != agg["n_positional"]:
        problems.append(
            f"{agg['target']}: testable({agg['n_arithmetically_testable']}) + "
            f"not_testable({agg['not_testable']}) = {total_check} "
            f"!= n_positional={agg['n_positional']}")
    return problems


if __name__ == "__main__":
    raw = load_raw(sys.argv[1] if len(sys.argv) > 1 else "data/generated/lineara_extracted.json")
    rows, fallback_log = build_occurrence_rows(raw)

    print(f"corpus records: {len(raw)}")
    print(f"total occurrences (all 3 targets): {len(rows)}")
    print(f"fallback-log entries (tablets adapted): {len(fallback_log)}")
    print()

    aggs = {}
    all_problems = []
    for target in TARGETS:
        agg = aggregate(rows, target)
        aggs[target] = agg
        problems = sanity_check(agg)
        all_problems.extend(problems)
        print(f"=== {target} ===")
        for k, v in agg.items():
            print(f"  {k}: {v}")
        print()

    if all_problems:
        print("SANITY CHECK FAILURES:")
        for p in all_problems:
            print(" -", p)
    else:
        print("All sanity checks passed.")

    # Occurrence-level audit table (Phase 4): redistribution-safe -- no raw
    # transliteration/transcription text, only tablet IDs (ordinary
    # scholarly citation), site metadata, and derived/computed fields.
    import csv
    fieldnames = list(rows[0].keys()) if rows else []
    with open("results/h1_occurrence_audit.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"\nwrote results/h1_occurrence_audit.csv ({len(rows)} rows)")
