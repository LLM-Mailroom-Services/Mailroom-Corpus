# Mailroom Dataset (v9) — EDA Summary Report

Generated: 2026-09-13 · Pipeline: `run_all.py` (P0–P6) · Data: `Lucius-Morningstar/mailroom-dataset` v1 (canonically **v9** of the corpus family, pinned `a7067844`)

> v9 lineage (tracking epic #18): standalone successor of the frozen v8
> `Lucius-Morningstar/mailroom-corpus` baseline (2,000 rows, `eafe1ab4` —
> never destroyed). v9 expansion: correspondence +650, corporate records +411,
> contract +91 (SEC EDGAR EX-10), insurance +150 (INSURBIAS + §36 workflow
> docs), plus the v8 synthetic LOB expansion (property/auto) and the §84
> hardened evaluation-contract columns (identity, provenance, matter) on the
> `ground_truth` config.

## Executive Summary

The corpus is a **3,302-document** legal classification surface across
**five doc_types** and **55 strata** (doc_type × expected_subclass). The
dataset is fully joinable (blind ↔ ground_truth, 3,302/3,302
filename-set agreement), the split rule (md5(filename) % 10 → test) is
byte-exact with zero mismatches, and all annotation offsets validate (CUAD
13,753/13,753 span matches = 100%).

| insurance_claim | 1,100 | 33.3% | bdr-ai-org/insurance-motor-claims-decision-v1; cms-de-synpuf-2008-2010-sample1; feihuangfh/INSURBIAS |
| contract | 600 | 18.2% | cuad_v1 |
| correspondence | 1,000 | 30.3% | cmu_enron_maildir |
| merger_agreement | 152 | 4.6% | maud_v1 |
| corporate_record | 450 | 13.6% | edgar_s1 |

**Imbalance:** max/min ratio 7.2× at type
level, 557× at stratum level (min
stratum `merger_agreement/mixed_cash_stock_election` = 1 row).
Type entropy = 2.09 bits.

## Key Findings

### 1. Text & token geometry

- `merger_agreement` documents are by far the longest (mean ~89,048.5 chars
  ≈ 22,262.1 tokens; max 252,135 chars ≈ 63,033.8
  tokens) — **exceed common 32k/65k contexts**.
- Insurance claims are uniformly short (~691.5 chars, σ=952.6).
- Token budget coverage: 76.6% ≤4k 89.6% ≤16k 93.2% ≤32k 99.8% ≤128k.

### 2. CUAD annotations (509 contracts, 41 clause types)

- 13,753 spans with **100.0% exact offset match** against doc_text.
- Most-annotated: `Document Name` (509 docs, mean 1.0 spans), `Parties` (508 docs, mean 5.0 spans), `Agreement Date` (469 docs, mean 1.0 spans), `Governing Law` (436 docs, mean 1.1 spans).
- 91 v9 EX-10 contracts carry no CUAD clause annotations (source-native EDGAR
  exhibits; `cuad_clause_labels` = `{}`), so annotation density is computed
  over the 509 CUAD-v1 contracts.

### 3. MAUD annotations (152 merger agreements, 22 tasks)

- `Accuracy of Target R&W Closing Condition` on 152 agreements (100.0%)
- `MAE Definition` on 152 agreements (100.0%)
- `Tail Period & Acquisition Proposal Details` on 152 agreements (100.0%)
- `Ordinary course covenant` on 151 agreements (99.3%)
- Metadata count consistency: 152/152
  rows match `maud_label_count == sum(maud_categories) == upstream count`.

### 4. Insurance claims (1,100 rows)

- Claimed amount present on 1,062 rows (median $1,250); coverage
  determination & denial reasons fully populated → ready for
  coverage-classification supervision.
- 13/13 fields 100% filled across all 6 LOB subtypes
  (carrier/inpatient/outpatient/pde/property/auto).

### 5. Correspondence (1,000 rows)

- **Intent is 100% hydrated** (1,000/1,000
  rows): `intent_source` records the hydration path (disjoint, sums to 1,000):
  162 aeslc_join + 105 heuristic + 637 llm_zero_shot + 96 manual. v9 adds the `heuristic` provenance for the §20/§43
  subject-line-hydrated draws (105 rows,
  `intent_status = auto_labeled`); 25 rows flagged for review.
- Every canonical intent class appears in the 10% test split: `analysis`, `meeting_invite`, `notice`, `other`, `payment_demand`, `press_communication`, `request`, `update`.

### 6. Split integrity

- 90/10 train/test: 2,979/323. Per-stratum test shares deviate
  from 10% (0%–max); 10 strata have zero test rows and
  5 minority strata (<10 rows, 19 rows total) — flagged in
  `24_strata_imbalance_ratio.png` / `25_minority_strata.png`.

### 7. §84 hardened evaluation contract (ground_truth config)

- Ground truth carries 65 columns after `gt_fields` expansion:
  identity (`document_id`, `content_sha256`, `normalized_text_sha256`),
  provenance (`source_corpus`, `source_document_id`, `source_filename`,
  `source_revision`, `annotation_*`), and the evaluation contract
  (`expected_specialist`, `expected_stage`, `retry_expected`,
  `review_expected`, `review_reason`, `expected_post_retry_state`) plus the
  matter/group tier (`matter_id`, `matter_construction`, `group_id`,
  `group_role`, `thread_*`, `relationships`, `related_document_ids`).

## Artifacts

### Static figures — `reports/figures/` (30 PNGs)

| # | figure | insight |
| --- | --- | --- |
| 01–03 | type/subclass/strata/metadata heatmap | composition & coverage |
| 04–07 | text length violin, token budgets, ECDF, subclass lengths | context-window fit |
| 08–12 | CUAD presence/span/co-occurrence | annotation density & structure |
| 13–15 | MAUD frequency/answers/categories | task coverage |
| 16–19 | claim amounts, coverage, dates, subtype fill | claim supervision readiness |
| 20–22 | correspondence topic/intent/sentiment | Enron subset character |
| 23–25 | treemap, strata ratios, minority strata | imbalance risk map |
| 26–28 | temporal, source proportions, date spans | provenance & time |
| 29–30 | metadata correlation/cardinality | field structure |

> Static figure counts are nominal; regenerate with `run_all.py --phases P3`.

### Interactive figures — `reports/figures_interactive/` (18 HTML)

Plotly versions with hover/zoom: lengths, budgets, CUAD, MAUD, claims,
treemap, strata, timeline, sources, metadata.

### Tables — `reports/tables/` (17 files)

`integrity_report.json`, `strata_counts.csv`, `metadata_coverage_by_type.csv`,
`provenance_by_type.csv`, `imbalance_metrics.json`, `text_length_stats_by_type.csv`,
`token_budget_coverage.csv`, `cuad_clause_stats.csv`, `cuad_cooccurrence_matrix.csv`,
`maud_task_stats.csv`, `claim_amount_stats.csv`, `claim_field_coverage.csv`,
`correspondence_topic_intent.csv`, `strata_imbalance_detailed.csv`,
`minority_strata_report.csv`, `temporal_summary.csv`, `provenance_detailed.csv`.

## HF Interface (centralized)

- `src/mailroom_eda/hf_interface.py` — Hub client: upload, sha verify, repo mgmt
- `src/mailroom_eda/dataset_export.py` — KANBAN-076 cast-safe metadata,
  KANBAN-088 JSONL safety, parquet staging, manifests, splits
- `src/mailroom_eda/docclass_uploader.py` — docclass publish, surgical card
  render, blind-label strip, leak guard
- `src/mailroom_eda/intent_backfill.py` — correspondence intent hydration +
  provenance columns
- `scripts/backfill/backfill_intent.py` — intent hydration CLI
- `scripts/publish/verify_hf.py` — byte-verify a local export against the Hub
- `scripts/archive/v8/publish_docclass.py` / `export_docclass.py` — frozen
  v8 baseline docclass publish/export (archived)

## ML-readiness recommendations

1. **Long docs**: `merger_agreement` requires 131k+ context or chunking; most
   contract text fits 32k.
2. **Minority strata** (5 strata < 10 rows): consider
   stratification-aware sampling or class/subclass rollups for training
   stability.
3. **Zero-test strata** (10): add a per-stratum test floor for the
   next corpus revision.
4. **Sentiment/intent labels** cover all correspondence (1,000
   rows); intent is fully hydrated (canonical 8-class set with
   `intent_source` / `intent_confidence` / `intent_status` provenance) — a
   ready multi-task head target (intent + sentiment + topic).
5. **Claims block** spans six LOB subtypes (carrier/inpatient/outpatient/pde +
   property/auto) — synthetic-data caveats apply (PAID only, health LOB).
