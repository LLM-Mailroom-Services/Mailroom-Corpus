# AGENTS.md — Mailroom-Corpus-EDA

Exploratory data analysis (and the centralized HF upload helpers) for the
[`Lucius-Morningstar/mailroom-dataset`](https://huggingface.co/datasets/Lucius-Morningstar/mailroom-dataset)
corpus (v1, canonically **v9** of the mailroom corpus family) — **3,302** legal
documents across 5 doc_types (insurance_claim, merger_agreement, contract,
correspondence, corporate_record), 55 strata. Pinned at tip `46a4d3c2…` (mailroom-dataset v9);
standalone successor of the frozen v8 `mailroom-corpus` baseline (2,000 rows,
`eafe1ab4` — never destroyed).

Mirror of the standalone `Exios66/Mailroom-Corpus-EDA` repo; in the monorepo
it lives at `packages/mailroom-corpus-eda` as a virtual uv member (no build).

## Monorepo development & sync (Digital-Mailroom)

- **Dev source of truth**: the monorepo
  (`LLM-Mailroom-Services/Digital-Mailroom`) is where active development
  happens; this package is the subtree mirror of `Exios66/Mailroom-Corpus-EDA`.
- **Sync contract**: never edit the mirror from both places in one session.
  Changes flow ONE way at a time through `scripts/sync_packages.py`
  (monorepo root): `pull --squash` imports standalone work monorepo-ward,
  `push` (content-only) / `push --all --patch` (release-train sweep)
  publishes monorepo deltas upstream, `snapshot` re-baselines the cursor.
  Never hand-edit the mirror and never push to the standalone repo
  directly.
- **Releases**: this package ships upstream (`Exios66/Mailroom-Corpus-EDA`)
  as a standalone repo; its corpus releases (e.g. `mailroom-dataset` v9)
  are published via the centralized HF helpers below and propagated
  monorepo-ward by the sync pass. Full law: root `AGENTS.md` §Sub-package
  sync + `docs/wiki/Sub-Package-Sync.md` + `docs/wiki/Releases.md`.

## Layout

- `src/mailroom_eda/` — the EDA + HF library (imports as `mailroom_eda`)
  - `config.py` — paths, doc types, colors, token budgets, matplotlib setup
  - `download.py` — corpus acquisition (HF snapshot) + manifest parsing
  - `integrity.py` — P1 structural integrity & provenance audit
  - `composition.py` — P2 strata / imbalance / provenance / metadata coverage
  - `visualizations.py` — P3 static PNG figures (30) + EDA tables
  - `visualizations_interactive.py` — P4 Plotly HTML figures (18)
  - `hf_interface.py` — centralized Hub client (upload, sha256 verify)
  - `dataset_export.py` — cast-safe JSONL (KANBAN-076/088), parquet staging, manifests
  - `docclass_uploader.py` — docclass v7 publish, surgical card render, leak guard
  - `intent_backfill.py` — correspondence intent hydration (issue #5):
    cross-walk, Enron/AESLC sha256 join, constrained LLM pass, provenance
  - `token_budget.py` — token estimation & budget coverage
  - `identity.py` — P0 document identity (document_id, content hashes,
    source provenance — cast-safe, absence is '')
  - `eval_contract.py` — P1 evaluation-contract derivations (§59 routing,
    §57–58 stage, §31 review/retry, §43 provenance) + closed vocabularies
    (fixture kinds, calibration quartet, matter/group, failure stages)
  - `matter.py` — P2 grouping derivations (§14A: header threads — verified
    absent here; subject+custodian+window reconstruction; never-mix guard)
  - `bundles.py` — P2 §14 synthetic bundle-family generator (flagged
    scaffold over real anchors; publish rides §84)
  - `fixtures.py` — §68–§72A fixture content (calibration quartet at live
    bands, arbiter scenarios, failure-stage matrix; publish rides §84)
- `scripts/` — CLI wrappers, organized by purpose:
  - `build/build_v9.py` — build + publish the v9 `mailroom-dataset`
  - `publish/verify_hf.py` — byte-verify a local export against the Hub
  - `audit/` — `baseline_audit.py`, `coverage_matrix.py` (→
    `docs/reports/audits/docclass_coverage_matrix.*`), `expansion_priorities.py`
    (→ `docs/reports/audits/docclass_expansion_priorities.*`)
  - `reports/` — `generate_index.py`, `generate_summary_md.py` (data-driven
    report generators)
  - `backfill/backfill_intent.py` — correspondence intent hydration (issue #5)
  - `archive/v8/` — frozen `mailroom-corpus` tooling (build_v8,
    publish_hardened, reconcile_gt_v8, publish_docclass, export_docclass)
  - `archive/v9-acquisition/` — one-time v9 EDGAR/draw sourcing
  - `_bootstrap.py` — shared repo-root + `src/` path bootstrap for all CLIs
- `run_all.py` — 7-phase pipeline (P0 download → P6 intent coverage audit)
- `reports/` — generated artifacts (figures/, figures_interactive/, tables/, SUMMARY_REPORT.md)
  - ALL of `reports/` is tracked in full per human directive (HUB-008) — never
    prune it and never commit regenerated variants of `figures_interactive/`:
    each Plotly HTML embeds a random per-render div UUID, so regenerated
    figures can never be byte-identical. The committed files are the canonical
    upstream bytes; treat local regeneration as scratch output only.

## Commands

```bash
.venv/bin/python run_all.py                      # full pipeline P0-P6
.venv/bin/python run_all.py --phases P3 P4       # figures only
.venv/bin/python scripts/backfill/backfill_intent.py --check
.venv/bin/python scripts/build/build_v9.py --help
.venv/bin/python scripts/audit/coverage_matrix.py --check
```

**Summary writes**: `reports/SUMMARY_REPORT.json` is written only by a
full-pipeline run (all seven phases). `--phases` subset runs — and
`--no-interactive`, whose summary would be missing the P4 section — leave the
summary untouched; per-phase results print to stdout only. (HUB-009: subset
runs used to clobber the full-corpus summary with phase-partial stats.)

## Conventions

- **Data never commits**: `data/` and `.venv/` are gitignored; `data/parquet`
  is re-fetched from the Hub by `download.py`.
- **HF uploads** use the centralized modules in `mailroom_eda.hf_interface`
  / `dataset_export` / `docclass_uploader` — never ad-hoc upload code.
  Metadata must be cast-safe (uniform keys, string-typed), JSONL must be
  line-boundary-safe (U+2028/U+2029/NEL), and labels NEVER ride in the blind
  `default` config.
- **Interactive HTML figures** are TRACKED IN FULL per human directive
  (HUB-008): each Plotly HTML embeds a random per-render div UUID, so
  regenerating can never be byte-identical — the committed files are the
  canonical upstream bytes; treat local regeneration as scratch only.
- **Intent backfill** (issue #5): never hand-edit `data/backfill/intent_labels.jsonl`;
  re-run `scripts/backfill/backfill_intent.py` (checkpointed — the LLM pass skips rows
  already in the sidecar). The canonical vocabulary is the closed 8-class set
  in `intent_backfill.CANONICAL_INTENTS`; `other` is the explicit fallback,
  never null.
- **Split rule**: md5(filename) % 10 == 0 → test (90/10), stable across rebuilds.
- **Determinism**: `RANDOM_STATE = 42`; rebuilds of JSONL/parquet must be
  byte-identical (sorted rows, deterministic order).

## HF facts (verified 2026-09-13, dataset v1 / corpus v9)

- Repo: `Lucius-Morningstar/mailroom-dataset` (v1, canonically v9; data tip
  `46a4d3c2…`). 3,302 rows (train 2,979 / test 323): insurance_claim 1,100
  (carrier/inpatient/outpatient/pde 600 CMS DE-SynPUF + property 200 GNOTHEIA
  + auto 150 BDR motor + 150 INSURBIAS/§36), correspondence 1,000,
  contract 600 (509 CUAD + 91 SEC EDGAR EX-10), corporate_record 450,
  merger_agreement 152 — 55 strata. Lineage: standalone successor of
  `Lucius-Morningstar/mailroom-corpus` (frozen v8 baseline, 2,000 rows,
  `eafe1ab4` — never destroyed); old `docclass-merged` repo DELETED.
- Configs: `default` (blind, 4 cols) + `ground_truth` (36 top-level cols incl.
  identity/provenance/matter + a `gt_fields` JSON column carrying the 29-key
  §84 complete-GT label set — the EDA layer expands it via
  `download._expand_gt_fields`) + `bundles` (50) + `streams` (62) +
  `fixtures` (32). Sidecars: `ground_truth_hardened.jsonl`,
  `bundles.jsonl`, `streams.jsonl`, `fixtures.jsonl`, `manifest.txt`.
- Split: train 2,979 / test 323 on both configs; filename sets equal.
- v9 expansion (tracking epic #18): correspondence +650 (intent hydrated via
  §20/§43 subject-line heuristics — new `intent_source = heuristic`
  provenance), corporate records +411, contract +91 (EX-10 — no CUAD
  clause annotations), insurance +150 (INSURBIAS narratives + §36 workflow
  docs). The v8 synthetic LOB expansion (property/auto) and the §84 hardened
  columns carry over.
- Correspondence intent (issue #5 + v9): 1,000/1,000 rows carry a canonical
  8-class intent; sources 637 llm_zero_shot + 162 aeslc_join + 105 heuristic
  + 96 manual; 25 flagged_review; all 8 classes in the test split (85 rows).
- Related: `enron-correspondence-dedup`, `mailroom-cuad-contracts-full`,
  `mailroom-s1-corporate-records`, `mailroom-maud-contracts`.

License note: the corpus card is CC-BY-4.0; v8 additions are Apache-2.0
(GNOTHEIA) + MIT (BDR); INSURBIAS is CC-BY-4.0. XpertSystems ins001/ins007/
hlt015 samples are CC-BY-NC-4.0 and were excluded.

## HF facts (verified 2026-09-02, schema v8 — historical baseline)

The v8 facts below describe the frozen baseline repo
(`Lucius-Morningstar/mailroom-corpus`), which remains pinned at `eafe1ab4`
for lineage and is superseded by `mailroom-dataset` above.

- Repo: `Lucius-Morningstar/mailroom-corpus` (v8, 2,000 rows; data tip
  `bba2f750`; hardened release rebuilt on v8 at `eafe1ab4`).
- Composition: insurance_claim 950 (carrier/inpatient/outpatient/pde 600 CMS
  DE-SynPUF + property 200 GNOTHEIA + auto 150 BDR motor),
  contract 509, correspondence 350, merger_agreement 152,
  corporate_record 39.
- Configs: `default` (blind, 4 cols) + `ground_truth` (60 cols incl. labels,
  intent provenance `intent_source`/`intent_confidence`/`intent_status`, AND
  the §84 hardened columns — identity/hashes, evaluation contract,
  matter/group) + `bundles` (38 cols, 50 rows) + `streams` (39 cols, 62 rows
  — §27–§29/§48 STREAM tier: `RUN-SIM-001` interleaved ingress stream over
  the bundle matters, 12 no-matter distractors) + `fixtures` (30 cols, 32
  rows). Built via `scripts/archive/v8/publish_hardened.py` (HUB-022) on
  the v8 base:
  v7 `document_id`s unchanged (0 drift), v8 LOB rows carry their own
  `source_corpus`/`annotation_source` (GNOTHEIA/BDR) + pinned
  `source_revision` via `metadata.source_dataset` / `.source_revision`
  (identity / eval_contract precedence: class map stays authoritative except
  the insurance LOB override — never churn published document_ids).
- Split: train 1,792 / test 208 on both configs; filename sets equal.
- v8 insurance LOB expansion (HUB-028): property rows from
  `gratex/GNOTHEIA-synthetic-insurance-dataset` (Apache-2.0) — FNOL bundles
  stratified by loss event, determination `pending` (no adjudication in
  source); auto rows from
  `bdr-ai-org/insurance-motor-claims-decision-v1` (MIT) — decision letters
  stratified by accident type × APPROVE/REVIEW/REJECT (all reject rows
  included), feature-grounded denial reasons, adjuster pseudonyms. Full GT
  conformance: all 950 insurance rows carry intent/subject/keywords +
  provenance (CMS template-derived backfill); claimed_amount recovered from
  doc text on 10 v7 gap rows; 3 train-only outpatient `:2` date gaps
  documented as source-N/A; test-split nullification enforced (zero empty
  class-relevant keys).
- v7 intent hydration (issue #5): 350/350 correspondence rows carry a
  canonical 8-class intent (payment_demand, notice, analysis, request, update,
  meeting_invite, press_communication, other); 96 manual + 254 llm_zero_shot
  (deepseek-chat, OpenRouter), 162 sha256-exact-body AESLC/Enron joins,
  1 flagged_review. All 8 classes present in the test split.
- Related: `enron-correspondence-dedup`, `mailroom-cuad-contracts-full`,
  `mailroom-s1-corporate-records`, `mailroom-maud-contracts`.

License note: the corpus card is CC-BY-4.0; v8 additions are Apache-2.0
(GNOTHEIA) + MIT (BDR). XpertSystems ins001/ins007/hlt015 samples are
CC-BY-NC-4.0 and were excluded; INSURBIAS (CC-BY-4.0) is deferred to v9
(narratives only, no decision GT).

See the `huggingface` opencode skill for the full Hub-interfacing workflow.