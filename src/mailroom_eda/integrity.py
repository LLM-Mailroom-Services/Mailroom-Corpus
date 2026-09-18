"""P1 — structural integrity & provenance audit (full, no sampling)."""
from __future__ import annotations

import logging

import json
from collections import Counter

import numpy as np
import pandas as pd

from .config import TABLE_DIR, split_rule
from .download import load_default, load_ground_truth, load_jsonl


def _meta_series(blind: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([dict(m) for m in blind["metadata"]])


def audit_config_join(blind: pd.DataFrame, gt: pd.DataFrame) -> dict:
    return {
        "blind_rows": int(len(blind)),
        "gt_rows": int(len(gt)),
        "blind_unique_filenames": bool(blind["filename"].is_unique),
        "gt_unique_filenames": bool(gt["filename"].is_unique),
        "filename_sets_equal": set(blind["filename"]) == set(gt["filename"]),
        "blind_split_counts": blind["split"].value_counts().to_dict(),
        "gt_split_counts": gt["split"].value_counts().to_dict(),
        "split_agreement": bool(
            blind.set_index("filename")["split"].sort_index().equals(
                gt.set_index("filename")["split"].sort_index()
            )
        ),
    }


def audit_split_rule(blind: pd.DataFrame, gt: pd.DataFrame) -> dict:
    out = {}
    for name, df in (("default", blind), ("ground_truth", gt)):
        recomputed = df["filename"].map(split_rule)
        mism = df.loc[recomputed != df["split"], "filename"].tolist()
        out[name] = {
            "rule": "md5(filename utf-8) % 10 == 0 -> test",
            "mismatches": len(mism),
            "mismatch_examples": mism[:5],
        }
    claims = gt[gt["expected"] == "insurance_claim"].copy()
    meta = _meta_series(blind.loc[claims.index])
    rid = meta["record_id"]
    moved = 0
    checked = 0
    for (r, s) in zip(rid, claims["split"]):
        if isinstance(r, str) and r:
            checked += 1
            src = "test" if int(__import__("hashlib").md5(r.encode()).hexdigest(), 16) % 10 == 0 else "train"
            if src != s:
                moved += 1
    out["claims_source_rule"] = {
        "rule": "md5(record_id) % 10 (source placement)",
        "checked": checked,
        "rows_moved_by_family_rule": moved,
        # v9 note: the family split rule (md5(filename)) is authoritative; this
        # counter records how many claims landed in a different split than their
        # source record_id placement would imply (informational, not an error).
        "manifest_claim": f"{moved}/{checked} rows differ from source placement",
    }
    return out


def _norm_md(d) -> dict:
    if isinstance(d, str):
        d = json.loads(d)
    return {k: ("" if v is None else v) for k, v in dict(d).items() if v not in (None, "")}


def audit_jsonl_parity(blind: pd.DataFrame, gt: pd.DataFrame) -> dict:
    jl = load_jsonl()
    out = {"jsonl_rows": int(len(jl)), "jsonl_columns": list(jl.columns)}
    b = blind.set_index("filename")
    g = gt.set_index("filename")
    joined = jl.set_index("filename")
    common = joined.index.intersection(b.index)
    out["jsonl_rows_in_blind"] = int(len(common))
    out["jsonl_rows_not_in_blind"] = int(len(joined) - len(common))
    if len(common):
        dt_eq = (joined.loc[common, "doc_text"].astype(str) == b.loc[common, "doc_text"].astype(str))
        out["doc_text_byte_equal_rate"] = float(dt_eq.mean())
        md_eq = sum(
            _norm_md(joined.loc[i, "metadata"]) == _norm_md(b.loc[i, "metadata"]) for i in common
        )
        out["metadata_equal_after_null_normalization"] = md_eq / len(common)
        diffs = Counter()
        for i in common:
            a, c = _norm_md(joined.loc[i, "metadata"]), _norm_md(b.loc[i, "metadata"])
            for k in sorted(set(a) | set(c)):
                if a.get(k) != c.get(k):
                    diffs[k] += 1
        out["metadata_field_diff_counts"] = dict(diffs.most_common(10))
        if "expected" in joined.columns:
            lab_eq = (joined.loc[common, "expected"].astype(str) == g.loc[common, "expected"].astype(str))
            out["expected_label_equal_rate"] = float(lab_eq.mean())
    return out


def audit_schema(blind: pd.DataFrame, gt: pd.DataFrame) -> dict:
    null_gt = gt.isna().sum()
    null_gt = null_gt[null_gt > 0].sort_values(ascending=False)
    out = {
        "blind_columns": list(blind.columns),
        "gt_columns": list(gt.columns),
        "gt_nonuniform_null_columns": {k: int(v) for k, v in null_gt.items()},
        "prompt_all_empty": bool((blind["prompt"] == "").all()),
        "doc_text_nulls": int(blind["doc_text"].isna().sum()),
    }
    meta = _meta_series(blind)
    out["metadata_key_union_n"] = int(meta.notna().any().sum())
    out["metadata_all_string_like"] = bool(
        all(isinstance(v, str) for row in blind["metadata"] for v in row.values())
    )
    return out


def metadata_coverage(blind: pd.DataFrame, gt: pd.DataFrame) -> pd.DataFrame:
    meta = _meta_series(blind)
    cov = pd.concat([gt["expected"].rename("doc_type"), meta], axis=1)
    tbl = cov.set_index("doc_type").groupby(level=0).apply(
        lambda g: g.notna().mean().T
    )
    return tbl


def _parse_labels(v):
    if isinstance(v, str) and v.strip():
        return json.loads(v)
    return v if isinstance(v, dict) else {}


def audit_cuad_clause_offsets(blind: pd.DataFrame, gt: pd.DataFrame) -> dict:
    text_by_fn = blind.set_index("filename")["doc_text"]
    total = 0
    ok = 0
    fails = []
    spans_per_contract = []
    for fn, labels in zip(gt["filename"], gt["cuad_clause_labels"]):
        labels = _parse_labels(labels)
        if not labels:
            continue
        txt = text_by_fn[fn]
        n = 0
        for clause, spans in labels.items():
            for sp in spans:
                total += 1
                n += 1
                t, s = sp.get("text", ""), sp.get("start")
                if isinstance(s, int) and 0 <= s and s + len(t) <= len(txt) and txt[s : s + len(t)] == t:
                    ok += 1
                elif len(fails) < 20:
                    fails.append({"filename": fn, "clause": clause, "start": s, "text_head": t[:60]})
        spans_per_contract.append(n)
    return {
        "rows_with_labels": int(sum(1 for v in gt["cuad_clause_labels"] if _parse_labels(v))),
        "total_spans": total,
        "exact_offset_matches": ok,
        "match_rate": ok / total if total else None,
        "spans_per_contract_mean": float(np.mean(spans_per_contract)) if spans_per_contract else None,
        "fail_examples": fails,
    }


def audit_maud_labels(blind: pd.DataFrame, gt: pd.DataFrame) -> dict:
    n = 0
    task_counts = Counter()
    label_counts = []
    meta_counts_ok = 0
    meta_checked = 0
    meta_series = _meta_series(blind)
    for i, raw in enumerate(gt["maud_clause_labels"]):
        labels = _parse_labels(raw)
        if not labels:
            continue
        n += 1
        task_counts.update(labels.keys())
        label_counts.append(len(labels))
        mc = meta_series.iloc[i].get("maud_label_count")
        cats = meta_series.iloc[i].get("maud_categories")
        try:
            cat_sum = sum(json.loads(cats).values()) if isinstance(cats, str) and cats.strip() else None
        except Exception:
            cat_sum = None
        if cat_sum is not None:
            meta_checked += 1
            try:
                if int(float(str(cat_sum))) == int(float(str(mc))) and int(float(str(mc))) >= len(labels):
                    meta_counts_ok += 1
            except Exception as exc:
                logging.getLogger(__name__).warning(
                    "MAUD meta-count comparison skipped for row %s (cat_sum=%r mc=%r): %s",
                    i,
                    cat_sum,
                    mc,
                    exc,
                )
    return {
        "rows_with_labels": n,
        "distinct_tasks": len(task_counts),
        "labels_per_row_mean": float(np.mean(label_counts)) if label_counts else None,
        "labels_per_row_min_max": (int(min(label_counts)), int(max(label_counts))) if label_counts else None,
        "task_frequency_top10": dict(task_counts.most_common(10)),
        "metadata_count_semantics": "maud_label_count == sum(maud_categories) == upstream annotation count; >= per-task GT column size",
        "metadata_count_consistency_ok": meta_counts_ok,
        "metadata_count_checked": meta_checked,
    }


def audit_metadata_label_consistency(blind: pd.DataFrame, gt: pd.DataFrame) -> dict:
    meta = _meta_series(blind)
    if "expected_doc_type" not in meta.columns:
        return {"available": False}
    m = meta["expected_doc_type"].astype(str).str.strip().str.lower()
    e = gt["expected"].astype(str).str.strip().str.lower()
    mask = m.isin(["contract", "merger_agreement", "corporate_record", "correspondence", "insurance_claim"])
    return {
        "available": True,
        "rows_with_expected_doc_type": int(mask.sum()),
        "agree_rate_on_filled": float((m[mask] == e[mask]).mean()) if mask.any() else None,
    }


def run(save: bool = True) -> dict:
    blind = load_default()
    gt = load_ground_truth()
    report = {}
    report["config_join"] = audit_config_join(blind, gt)
    report["split_rule"] = audit_split_rule(blind, gt)
    report["jsonl_parity"] = audit_jsonl_parity(blind, gt)
    report["schema"] = audit_schema(blind, gt)
    report["cuad_offsets"] = audit_cuad_clause_offsets(blind, gt)
    report["maud_labels"] = audit_maud_labels(blind, gt)
    report["metadata_label_consistency"] = audit_metadata_label_consistency(blind, gt)
    cov = metadata_coverage(blind, gt)
    if save:
        TABLE_DIR.mkdir(parents=True, exist_ok=True)
        cov.to_csv(TABLE_DIR / "metadata_coverage_by_type.csv")
        with open(TABLE_DIR / "integrity_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
    return report
