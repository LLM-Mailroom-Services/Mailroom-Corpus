<div align="center">

# ⚙️ Corpus EDA Scripts

**Utility scripts for the mailroom-corpus-eda package, organized by purpose.**

</div>

---

## Layout

| Directory | Purpose |
| :--- | :--- |
| [`build/`](build/) | Corpus build + publish (v9 `mailroom-dataset`) |
| [`publish/`](publish/) | Hub publish/verify helpers |
| [`audit/`](audit/) | Corpus audit & expansion-planning instruments |
| [`reports/`](reports/) | Report artifact generators |
| [`backfill/`](backfill/) | Label hydration CLIs |
| [`archive/`](archive/) | Frozen v8 + one-time v9-acquisition tooling (provenance) |
| [`_bootstrap.py`](_bootstrap.py) | Shared path bootstrap (repo root + `src/` on `sys.path`) |

`run_all.py` (repo root) remains the canonical P0–P6 pipeline entrypoint.

## Live scripts

| Script | Purpose |
| :--- | :--- |
| [`build/build_v9.py`](build/build_v9.py) | Build (and optionally publish) the v9 `mailroom-dataset` (stage-only by default; `--publish` uploads via `mailroom_eda.hf_interface`) |
| [`publish/verify_hf.py`](publish/verify_hf.py) | Byte-verify a local export against the Hub; list repo files |
| [`audit/baseline_audit.py`](audit/baseline_audit.py) | §4 / §85 P0 baseline audit → `docs/reports/audits/` |
| [`audit/coverage_matrix.py`](audit/coverage_matrix.py) | §40–§41 coverage matrix → `docs/reports/audits/docclass_coverage_matrix.*` |
| [`audit/expansion_priorities.py`](audit/expansion_priorities.py) | §89 expansion backlog → `docs/reports/audits/docclass_expansion_priorities.*` |
| [`reports/generate_index.py`](reports/generate_index.py) | Regenerate `reports/index.html` dashboard (data-driven) |
| [`reports/generate_summary_md.py`](reports/generate_summary_md.py) | Regenerate `reports/SUMMARY_REPORT.md` (data-driven) |
| [`backfill/backfill_intent.py`](backfill/backfill_intent.py) | Correspondence intent hydration (issue #5) — checkpointed |

## Archived scripts

| Script | Purpose | Status |
| :--- | :--- | :--- |
| [`archive/v8/`](archive/v8/) | `build_v8.py`, `publish_hardened.py`, `reconcile_gt_v8.py`, `publish_docclass.py`, `export_docclass.py` | Frozen `mailroom-corpus` (v8) tooling — lineage only |
| [`archive/v9-acquisition/`](archive/v9-acquisition/) | `edgar_pull.py`, `edgar_ftsearch.py`, `draw_contract_v9.py` | One-time v9 sourcing — provenance only |

See [`archive/README.md`](archive/README.md) for the archive policy.

## Usage

```bash
cd Mailroom-Corpus-EDA
.venv/bin/python run_all.py                       # full pipeline P0-P6
.venv/bin/python run_all.py --phases P3 P4        # figures only
.venv/bin/python scripts/build/build_v9.py        # stage v9 under data/v9/stage
.venv/bin/python scripts/build/build_v9.py --publish   # stage + publish v1
.venv/bin/python scripts/backfill/backfill_intent.py --check
.venv/bin/python scripts/audit/coverage_matrix.py
.venv/bin/python scripts/reports/generate_summary_md.py
.venv/bin/python scripts/reports/generate_index.py
.venv/bin/python scripts/publish/verify_hf.py --repo Lucius-Morningstar/mailroom-dataset
```

> Note: `generate_figures.py` / `gen_interactive_charts.py` (documented in
> earlier revisions) no longer exist; P3/P4 entrypoints are the `__main__`
> blocks of `src/mailroom_eda/visualizations.py` and
> `src/mailroom_eda/visualizations_interactive.py`, invoked via `run_all.py`.

## Path bootstrap

Every script locates the repo root through [`_bootstrap.py`](_bootstrap.py)
(the first ancestor carrying `.git`), so the CLIs run identically from any
bucket depth (`scripts/`, `scripts/audit/`, `scripts/archive/v8/`, …). Never
derive repo paths from `__file__.parents[n]` in a script.

## Related Files

- `reports/` — Generated reports and figures
- `src/` — Source code
- `tests/` — Test suites
