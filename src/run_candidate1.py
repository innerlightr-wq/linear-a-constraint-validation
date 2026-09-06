"""
Candidate 1 real-data driver.

Uses ONLY src/lineara_adapter.py (already frozen, H1 corpus lineage) and
src/constraint_candidate1.py (frozen at commit
f86e4a1af9014cc6b0a18a7ccc0b7affcc7555e2, docs/CANDIDATE1_PROTOCOL.md) --
no classification/statistical logic is reimplemented here. This file's job
is exactly: load the same primary mwenge corpus already used by src/run_h1.py,
adapt each tablet, build the frozen Level A/B tables, apply the frozen
adequacy gate, and (only if it passes) run the frozen permutation test.

DETERMINISTIC SEED: CANDIDATE1_PROTOCOL.md did not freeze a specific integer
seed (only that an rng be supplied). Per this round's own instruction, seed
20260906 is used, labeled an ENGINEERING REPRODUCIBILITY CHOICE, not a
scientific tuning parameter -- changing it would not change which stratum
labels are exchangeable, only which specific permutation draws are sampled.
"""
from __future__ import annotations

import json
import os
import random
import statistics
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lineara_adapter as la  # noqa: E402
import constraint_candidate1 as c1  # noqa: E402

SEED = 20260906  # ENGINEERING REPRODUCIBILITY CHOICE, not a scientific tuning parameter
B = 2000
ALPHA = 0.05
MIN_N = 10

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                          "data", "generated", "lineara_extracted.json")


def load_raw(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_tablet_table(raw_records: list[dict]) -> dict:
    """One pass over the corpus. Returns a dict with every Level A/B table
    and metadata needed by every later phase -- no rate, Δ, or p-value is
    computed in this function."""
    per_tablet_meta = {}       # tablet_id -> {site, support, base_key}
    level_a_rows = []          # list[RawOccurrence]
    level_b_rows = []          # list[TabletObservation]

    for raw in raw_records:
        tablet_id = raw["name"]
        site = raw.get("site")
        support = raw.get("support")
        per_tablet_meta[tablet_id] = {
            "site": site,
            "support": support,
            "base_key": c1.physical_artifact_key(tablet_id),
        }
        record = la.raw_tablet_to_record(raw)
        level_a_rows.extend(c1.find_commodity_occurrences(record))
        level_b_rows.extend(c1.tablet_level_observations(record))

    return {
        "meta": per_tablet_meta,
        "level_a": level_a_rows,
        "level_b": level_b_rows,
    }


def rows_by_stratum_for(level_b_rows: list, meta: dict, restrict_tablets=None,
                         restrict_sign_no_ligature=None) -> dict:
    """Builds the rows_by_stratum structure constraint_candidate1's
    exchangeability/permutation/delta functions expect: stratum_key ->
    list[(class, is_fraction_present_bool)], usable rows only.

    `restrict_tablets`, if given, is a set of tablet_ids to include (used by
    Sensitivity D, Haghia Triada only). `restrict_sign_no_ligature` is unused
    here -- Sensitivity E rebuilds level_b_rows itself from a filtered Level A
    set (see sensitivity_E), since bare-sign-only requires re-running the
    tablet-level first-occurrence rule over a restricted occurrence set, not
    filtering already-aggregated Level B rows.
    """
    rbs = defaultdict(list)
    for obs in c1.usable_rows(level_b_rows):
        if restrict_tablets is not None and obs.tablet_id not in restrict_tablets:
            continue
        m = meta[obs.tablet_id]
        key = c1.stratum_key(m["site"], m["support"])
        rbs[key].append((obs.commodity_class, obs.outcome == "FRACTION_PRESENT"))
    return dict(rbs)


def counts(rows_by_class: list[tuple]) -> dict:
    liquid = [p for cls, p in rows_by_class if cls == "LIQUID"]
    dry = [p for cls, p in rows_by_class if cls == "DRY"]
    return {
        "n_l": len(liquid), "present_l": sum(liquid),
        "n_d": len(dry), "present_d": sum(dry),
        "p_l": (sum(liquid) / len(liquid)) if liquid else None,
        "p_d": (sum(dry) / len(dry)) if dry else None,
    }


def rate_ratio(p_l, p_d):
    if p_l is None or p_d is None or p_d == 0:
        return None
    return p_l / p_d


def odds_ratio(n_l, present_l, n_d, present_d):
    a, b = present_l, n_l - present_l
    c, d = present_d, n_d - present_d
    if 0 in (a, b, c, d):
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
        corrected = True
    else:
        corrected = False
    if b == 0 or c == 0:
        return None, corrected
    return (a * d) / (b * c), corrected


def run_primary_test(rbs: dict, seed: int, B: int):
    delta_obs = c1.observed_delta(rbs)
    if delta_obs is None:
        return None
    rng = random.Random(seed)
    result = c1.run_stratified_permutation_test(rbs, B=B, rng=rng)
    return result


def quantiles(values):
    if not values:
        return {}
    values = sorted(values)
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "q1": statistics.quantiles(values, n=4)[0] if len(values) >= 4 else None,
        "q3": statistics.quantiles(values, n=4)[2] if len(values) >= 4 else None,
    }


def main():
    raw = load_raw(DATA_PATH)
    table = build_tablet_table(raw)
    meta = table["meta"]
    level_a = table["level_a"]
    level_b = table["level_b"]

    report = {}

    # --- Phase 5: extraction / adequacy diagnostics -----------------------
    report["raw_occurrences_total"] = len(level_a)
    report["raw_occurrences_liquid"] = sum(1 for o in level_a if o.commodity_class == "LIQUID")
    report["raw_occurrences_dry"] = sum(1 for o in level_a if o.commodity_class == "DRY")
    report["usable_occurrences_liquid"] = sum(1 for o in level_a if o.commodity_class == "LIQUID" and o.has_quantity)
    report["usable_occurrences_dry"] = sum(1 for o in level_a if o.commodity_class == "DRY" and o.has_quantity)
    report["excluded_occurrences_liquid"] = report["raw_occurrences_liquid"] - report["usable_occurrences_liquid"]
    report["excluded_occurrences_dry"] = report["raw_occurrences_dry"] - report["usable_occurrences_dry"]

    liquid_tablets = {o.tablet_id for o in level_b if o.commodity_class == "LIQUID"}
    dry_tablets = {o.tablet_id for o in level_b if o.commodity_class == "DRY"}
    report["unique_liquid_tablets"] = len(liquid_tablets)
    report["unique_dry_tablets"] = len(dry_tablets)
    report["tablets_both_classes"] = len(liquid_tablets & dry_tablets)

    usable_b = c1.usable_rows(level_b)
    report["usable_tablet_obs_liquid"] = sum(1 for o in usable_b if o.commodity_class == "LIQUID")
    report["usable_tablet_obs_dry"] = sum(1 for o in usable_b if o.commodity_class == "DRY")
    report["ambiguous_tablet_obs"] = sum(1 for o in level_b if o.outcome == "AMBIGUOUS_UNUSABLE")

    site_dist = defaultdict(int)
    support_dist = defaultdict(int)
    for o in usable_b:
        m = meta[o.tablet_id]
        site_dist[(m["site"] or "UNKNOWN")] += 1
        support_dist[(m["support"] or "UNKNOWN")] += 1
    report["site_distribution"] = dict(site_dist)
    report["support_distribution"] = dict(support_dist)

    rbs_primary = rows_by_stratum_for(level_b, meta)
    exch, non_exch = c1.exchangeable_strata(rbs_primary)
    report["n_strata_total"] = len(rbs_primary)
    report["n_strata_exchangeable"] = len(exch)
    report["n_strata_nonexchangeable"] = len(non_exch)

    retained = sum(len(rbs_primary[k]) for k in exch)
    excluded_nonexch = sum(len(rbs_primary[k]) for k in non_exch)
    report["obs_retained_exchangeable"] = retained
    report["obs_excluded_nonexchangeable"] = excluded_nonexch

    exch_rows = [row for k in exch for row in rbs_primary[k]]
    prim_counts = counts(exch_rows)
    report["primary_counts"] = prim_counts

    # --- Phase 6: adequacy gate --------------------------------------------
    delta_obs = c1.observed_delta(rbs_primary)
    gate_pass = (
        delta_obs is not None
        and prim_counts["n_l"] >= MIN_N
        and prim_counts["n_d"] >= MIN_N
    )
    report["adequacy_gate_pass"] = gate_pass

    # --- Phase 7: primary test (only if gate passes) -----------------------
    if gate_pass:
        primary_result = run_primary_test(rbs_primary, SEED, B)
        report["primary_result"] = primary_result
        report["seed"] = SEED
    else:
        report["primary_result"] = None
        report["verdict"] = "INCONCLUSIVE"

    # --- Phase 8: effect sizes ----------------------------------------------
    if gate_pass:
        rr = rate_ratio(prim_counts["p_l"], prim_counts["p_d"])
        orv, or_corrected = odds_ratio(prim_counts["n_l"], prim_counts["present_l"],
                                        prim_counts["n_d"], prim_counts["present_d"])
        report["rate_ratio"] = rr
        report["odds_ratio"] = orv
        report["odds_ratio_corrected"] = or_corrected

    # --- Phase 9: sensitivities ----------------------------------------------
    sens = {}

    # Sensitivity A: raw occurrence level (descriptive only)
    a_rows = [(o.commodity_class, o.fraction_present) for o in level_a if o.has_quantity]
    sens["A_raw_occurrence"] = {**counts(a_rows), "label": "DESCRIPTIVE ONLY"}

    # Sensitivity B: primary tablet-level (restate)
    sens["B_primary_tablet"] = {**prim_counts, "delta": delta_obs,
                                  "p_perm": report["primary_result"]["p_value"] if gate_pass else None}

    # Sensitivity C: probable-same-artifact collapse
    grouped = defaultdict(list)
    for o in usable_b:
        m = meta[o.tablet_id]
        grouped[(m["base_key"], o.commodity_class)].append(o.outcome)
    collapsed_rows = []
    conflicts = 0
    for (base_key, cls), outcomes in grouped.items():
        uniq = set(outcomes)
        if len(uniq) == 1:
            collapsed_rows.append((cls, uniq.pop() == "FRACTION_PRESENT"))
        else:
            conflicts += 1
    # restrict to exchangeable strata analog: recompute using same site/support
    # keyed by one representative tablet per base_key (site/support assumed
    # identical across faces of the same physical object)
    rbs_c = defaultdict(list)
    seen_keys = set()
    for o in usable_b:
        m = meta[o.tablet_id]
        gk = (m["base_key"], o.commodity_class)
        if gk in seen_keys:
            continue
        outcomes = grouped[gk]
        if len(set(outcomes)) != 1:
            continue
        seen_keys.add(gk)
        key = c1.stratum_key(m["site"], m["support"])
        rbs_c[key].append((o.commodity_class, outcomes[0] == "FRACTION_PRESENT"))
    rbs_c = dict(rbs_c)
    exch_c, _ = c1.exchangeable_strata(rbs_c)
    rows_c = [row for k in exch_c for row in rbs_c[k]]
    c_counts = counts(rows_c)
    c_gate = c_counts["n_l"] >= MIN_N and c_counts["n_d"] >= MIN_N and c1.observed_delta(rbs_c) is not None
    c_result = run_primary_test(rbs_c, SEED, B) if c_gate else None
    sens["C_artifact_collapse"] = {**c_counts, "conflicts_excluded": conflicts,
                                     "delta": c1.observed_delta(rbs_c),
                                     "p_perm": c_result["p_value"] if c_result else None,
                                     "label": "INFERENTIAL" if c_gate else "DESCRIPTIVE ONLY (adequacy gate failed)"}

    # Sensitivity D: Haghia Triada only
    ht_tablets = {tid for tid, m in meta.items() if (m["site"] or "").strip().casefold() == "haghia triada"}
    rbs_d = rows_by_stratum_for(level_b, meta, restrict_tablets=ht_tablets)
    exch_d, _ = c1.exchangeable_strata(rbs_d)
    rows_d = [row for k in exch_d for row in rbs_d[k]]
    d_counts = counts(rows_d)
    d_gate = d_counts["n_l"] >= MIN_N and d_counts["n_d"] >= MIN_N and c1.observed_delta(rbs_d) is not None
    d_result = run_primary_test(rbs_d, SEED, B) if d_gate else None
    sens["D_haghia_triada_only"] = {**d_counts, "delta": c1.observed_delta(rbs_d),
                                      "p_perm": d_result["p_value"] if d_result else None,
                                      "label": "INFERENTIAL" if d_gate else "DESCRIPTIVE ONLY (adequacy gate failed)"}

    # Sensitivity E: bare base-sign only (no ligature)
    level_a_bare = [o for o in level_a if o.sign_id == c1.base_sign(o.sign_id)]
    tablet_ids_e = {o.tablet_id for o in level_a_bare}
    rbs_e = defaultdict(list)
    for tid in tablet_ids_e:
        bare_occs = [o for o in level_a_bare if o.tablet_id == tid]
        m = meta[tid]
        for cls in ("LIQUID", "DRY"):
            cls_occs = [o for o in bare_occs if o.commodity_class == cls]
            usable = [o for o in cls_occs if o.has_quantity]
            if not usable:
                continue
            first = usable[0]
            key = c1.stratum_key(m["site"], m["support"])
            rbs_e[key].append((cls, first.fraction_present))
    rbs_e = dict(rbs_e)
    exch_e, _ = c1.exchangeable_strata(rbs_e)
    rows_e = [row for k in exch_e for row in rbs_e[k]]
    e_counts = counts(rows_e)
    e_gate = e_counts["n_l"] >= MIN_N and e_counts["n_d"] >= MIN_N and c1.observed_delta(rbs_e) is not None
    e_result = run_primary_test(rbs_e, SEED, B) if e_gate else None
    sens["E_bare_sign_only"] = {**e_counts, "delta": c1.observed_delta(rbs_e),
                                  "p_perm": e_result["p_value"] if e_result else None,
                                  "label": "INFERENTIAL" if e_gate else "DESCRIPTIVE ONLY (adequacy gate failed)"}

    report["sensitivities"] = sens

    # --- Phase 10: opportunity-bias diagnostic -------------------------------
    per_tablet_class_counts = defaultdict(lambda: defaultdict(int))
    for o in level_a:
        per_tablet_class_counts[o.tablet_id][o.commodity_class] += 1
    liquid_counts = [v["LIQUID"] for v in per_tablet_class_counts.values() if v.get("LIQUID")]
    dry_counts = [v["DRY"] for v in per_tablet_class_counts.values() if v.get("DRY")]
    report["opportunity_bias"] = {
        "liquid_occurrences_per_tablet": quantiles(liquid_counts),
        "dry_occurrences_per_tablet": quantiles(dry_counts),
    }

    # --- Phase 11: site-dominance diagnostic --------------------------------
    ht_liquid = sum(1 for o in usable_b if o.commodity_class == "LIQUID"
                    and (meta[o.tablet_id]["site"] or "").strip().casefold() == "haghia triada")
    ht_dry = sum(1 for o in usable_b if o.commodity_class == "DRY"
                 and (meta[o.tablet_id]["site"] or "").strip().casefold() == "haghia triada")
    report["site_dominance"] = {
        "ht_fraction_of_liquid": ht_liquid / prim_counts["n_l"] if prim_counts["n_l"] else None,
        "ht_fraction_of_dry": ht_dry / prim_counts["n_d"] if prim_counts["n_d"] else None,
        "ht_liquid_n": ht_liquid, "ht_dry_n": ht_dry,
    }

    # --- verdict --------------------------------------------------------------
    if gate_pass:
        p = report["primary_result"]["p_value"]
        report["verdict"] = "CANDIDATE 1 SUPPORTED" if p < ALPHA else "CANDIDATE 1 NOT SUPPORTED"

    return report


if __name__ == "__main__":
    import pprint
    r = main()
    pprint.pprint(r, width=120, sort_dicts=False)
