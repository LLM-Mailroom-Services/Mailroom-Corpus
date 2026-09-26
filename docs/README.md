# Mailroom Dataset — Source Dataset Cards

Documentation for the five source corpora integrated into
[`Lucius-Morningstar/mailroom-dataset`](https://huggingface.co/datasets/Lucius-Morningstar/mailroom-dataset)
(v1, canonically v9 of the corpus family, 3,302 rows, published 2026-09-12;
lineage parent the frozen v8 `mailroom-corpus`, 2,000 rows). Each card
records the full context, source material, attribution, and the purpose the
corpus serves inside the merged classification surface. All numbers are
reproducible from this repo's EDA pipeline (`run_all.py`) and the tables
under [`reports/tables/`](../reports/tables/).

## The five corpora

| Card | doc_type | Rows | Share | License | Upstream origin |
|---|---:|---:|---|---|
| [CUAD contracts](dataset-cards/cuad-contracts.md) | `contract` | 600 | 18.2% | CC BY 4.0 | CUAD v1 — The Atticus Project (+ SEC EDGAR EX-10) |
| [MAUD merger agreements](dataset-cards/maud-merger-agreements.md) | `merger_agreement` | 152 | 4.6% | CC BY 4.0 | MAUD v1 — The Atticus Project (Zenodo 7500064) |
| [S-1 corporate records](dataset-cards/s1-corporate-records.md) | `corporate_record` | 450 | 13.6% | Public domain (US gov works) | SEC EDGAR S-1/8-K exhibits |
| [Enron correspondence](dataset-cards/enron-correspondence.md) | `correspondence` | 1000 | 30.3% | Research use (inherited from CMU Enron) | CMU Enron Email Dataset via `enron-correspondence-dedup` |
| [CMS DE-SynPUF insurance claims](dataset-cards/cms-desynpuf-insurance-claims.md) | `insurance_claim` | 1100 | 33.3% | CMS public-use (synthetic) | CMS DE-SynPUF 2008–2010 Sample 1 via `claims-data-eda` (+ GNOTHEIA/BDR/INSURBIAS LOB lines) |
| **Total** | 5 doc_types | **3,302** | 100% | mixed — see per-card terms | 55 strata (`expected` × `expected_subclass`) |

## How each corpus entered the merge

| Corpus version | Schema | Added | Mechanics |
|---|---|---|---|
| v1–v3 (legacy 700 rows) | v1–v3 | contract 509 + merger_agreement 152 + corporate_record 39 | built by `llm-entity-extraction` `build_docclass_merged.py` (KANBAN-071/073/074) |
| v4 | two-config blind/GT layout | +110 correspondence | deterministic stratified sha256(filename) draw from `enron-correspondence-dedup` |
| v5 (KANBAN-084) | + clause-level GT | +400 insurance_claim | DE-SynPUF EOB renders with verbatim GT contract; `cuad_clause_labels` / `maud_clause_labels` joined |
| v6 (KANBAN-105) | blind-surface repair | +240 correspondence, +200 insurance_claim | stratified re-draw excluding existing filenames; DE-SynPUF re-render (record_id exclusion) |
| v7 (issue #5) | intent hydration | no row change | 350/350 correspondence rows carry canonical 8-class `intent` + provenance columns |
| v8 (2026-09-02) | frozen baseline | 1,650 → 2,000 | `mailroom-corpus` — insurance LOB expansion (property/auto) + full GT conformance; never destroyed |
| v9 (2026-09-12) | standalone successor | 2,000 → 3,302 | `mailroom-dataset` v1 — §84 hardened GT (identity/provenance/matter): correspondence +650, corporate_record +411, contract +91 (EX-10), insurance +150 (INSURBIAS) |

## Row-level provenance

Every row self-identifies its origin through two cast-safe string fields in
the blind config's `metadata` struct. These are the authoritative join keys
to the cards above:

| doc_type | `metadata.source` | `metadata.source_dataset` |
|---|---|---|
| contract | `cuad_v1` | `mailroom-cuad-contracts-full` |
| merger_agreement | `maud_v1` | `data/maud/contracts.jsonl` |
| corporate_record | `edgar_s1` | `data/s1_corporate_records/corporate-records.jsonl` |
| correspondence | `cmu_enron_maildir` | `Lucius-Morningstar/enron-correspondence-dedup` |
| insurance_claim | `""` (synthetic render — the render is the original) | `cms-de-synpuf-2008-2010-sample1` |

Correspondence rows additionally record their exact draw in
`metadata.sample_method` (e.g. `stratified sha256(filename) deterministic
draw of 240 from 247413 (KANBAN-105 v6 append; quota 30)`), and Enron rows
carry `metadata.license = "Enron corpus — released for research use"`.

## License matrix (summary)

- **CC BY 4.0** — the CUAD and MAUD portions (The Atticus Project; Wang et
  al. 2023). Attribution required; see the citation blocks in each card.
- **Public domain** — S-1 corporate records are US SEC EDGAR filings (US
  government works).
- **Research use only** — the Enron correspondence subset inherits the CMU
  Enron Email Dataset terms and contains real PII of Enron employees. No
  redistribution of raw PII outside research contexts; no production use.
- **Synthetic / CMS public-use** — insurance claims are rendered from the
  fully synthetic CMS DE-SynPUF ("very limited inferential research utility"
  per CMS). No real PHI exists; evaluation substrate, not epidemiology.

## Splits

Per-row `split` follows the family rule `md5(filename) % 10 == 0 → test`
(~10%), deterministic and stable across rebuilds; identical to the rule used
by every sibling dataset in the family. Current counts: train 2,979 / test
323 (contract 540/60, merger_agreement 135/17, corporate_record 403/47,
correspondence 915/85, insurance_claim 986/114).

## Two-config layout reminder

`default` (blind) carries no label columns; all gold labels —
`expected`, `expected_subclass`, clause GT, sentiment/topic/intent — live in
the `ground_truth` config, keyed 1:1 on `filename`. See the
[live dataset card](https://huggingface.co/datasets/Lucius-Morningstar/mailroom-dataset)
for the full row shape and config contract.

## Plans

| Plan | Scope |
|---|---|
| [v9.1 data-quality HF revision](plans/v9.1-data-quality-hf-revision.md) | Evidence-based Hub revision on the 3,302-row v9 tip — Modal insights, LLM-ingestion formatting, EX-10 close-out, eval floors (tracked as [mailroom-issues#196](https://github.com/LLM-Mailroom-Services/mailroom-issues/issues/196)) |

## Related family repos

The family is cataloged in the public
[**Mailroom Corpus Family** collection](https://huggingface.co/collections/Lucius-Morningstar/mailroom-corpus-family-6aa715cce29d415b0db92473)
on Hugging Face:

- [`enron-correspondence-dedup`](https://huggingface.co/datasets/Lucius-Morningstar/enron-correspondence-dedup) — the 247K-row deduplicated Enron corpus the correspondence sample was drawn from
- [`mailroom-cuad-contracts-full`](https://huggingface.co/datasets/Lucius-Morningstar/mailroom-cuad-contracts-full) — byte-verified CUAD mirror used at ingestion
- [`cms-desynpuf-insurance-claims`](https://huggingface.co/datasets/Lucius-Morningstar/cms-desynpuf-insurance-claims) — the v5-era rendered-EOB claims corpus (v6 re-rendered from source)
- [`LLM Mailroom`](https://github.com/Exios66/llm-mailroom) — the agentic triage system evaluated against this benchmark
