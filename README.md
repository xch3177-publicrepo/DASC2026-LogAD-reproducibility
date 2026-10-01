# DASC 2026 reproduction support artifact

**Partial legacy rerun support + published aggregate-table reconstruction.**

This is not a complete replication package for the final paper's experiments.
It contains recovered July 2026 baseline code, historical baseline aggregates,
and final-paper table values. The final five-seed experiment implementations,
split indices, per-seed predictions, and timing records were not recovered.
New support tools and synthetic tests were written on 2026-10-01; they are not
original experiment code or additional experimental evidence.

## What can be verified offline

Python 3.10 or later is sufficient; no third-party package or dataset is needed:

```bash
python3 tools/verify_artifact.py
python3 tools/reconstruct_tables.py --check
python3 -B -m unittest discover -s tests -v
python3 tools/scan_public.py
```

These commands verify artifact checksums, eight exported tables, the ordered
344 visible numeric tokens and 134 mean/standard-deviation pairs, deterministic
Markdown reconstruction, and synthetic parser/utility behavior. They do not
recompute published model scores or infer missing seed-level measurements.

The earlier manuscript gate's 348-token count also included four `0.6em`
spacing parameters. Both the 348-token source audit and the 344-token visible
table ledger are preserved separately; layout numbers are not experimental data.

To regenerate the table presentation, run:

```bash
python3 tools/reconstruct_tables.py
```

The JSON and Markdown are transcribed/exported aggregate results, not raw
experimental outputs. See `PROVENANCE.md` and `MISSING_ASSETS.md`.

## Package layout

- `legacy_baseline/src/`: six recovered baseline scripts, with path-only
  portability changes documented in `PATCH_NOTES.md`.
- `legacy_baseline/results/log_results.csv`: the recovered 16-row historical
  aggregate CSV, byte-identical to the archive entry. It is not a final-paper
  five-seed result table.
- `published_tables/tables.json`: final-paper table values, including context,
  access regimes, headers, grouped rows, and printed precision.
- `published_tables/numeric_ledger.json`: independently extracted numeric
  ledger and mean/SD sequence used to audit the export.
- `published_tables/reconstructed_tables.md`: generated presentation.
- `tools/`: newly written verification, reconstruction, and execution helpers.
- `tests/`: newly written synthetic tests; no benchmark examples or results.
- `data/README.md`: official dataset entry points and expected local layout.

## Optional legacy rerun

Full legacy training **was not executed for this release**: the available
runtime lacked SciPy, scikit-learn, XGBoost, Gensim, and PyTorch. No packages
were installed and no new benchmark result is represented as a reproduced
historical measurement. NumPy/Pandas preprocessing is separately documented
in `VALIDATION.md`. The CLI and core preprocessing/parser utilities have
synthetic smoke coverage.

Use a separate virtual environment and install `requirements-legacy.txt`.
That file identifies package names, not a recovered historical environment
lock or a promise of exact replay. Library compatibility must be checked in
the environment used for a real rerun.

```bash
python3 tools/run_legacy.py --check-dependencies
# Download the datasets from their official entry points first; see data/README.md.
python3 tools/run_legacy.py --raw-root ./local_data \
  --work-dir ./new_runs/example --stage all --allow-full-run
```

The execution wrapper writes new outputs to the chosen empty work directory,
never to `legacy_baseline/results/`. It does not change algorithm parameters,
add seeds, create final-paper protocols, or assert that a new result matches
the archived values. Original randomness includes an unseeded NumPy shuffle
and multi-worker Word2Vec, so bitwise replay is not supported.

## Scope, privacy, and permissions

The package excludes the manuscript, review records, identities/contact
details, private repository history, credentials, machine-specific paths,
raw logs, and copied template catalogs. Dataset downloads remain subject to
their upstream terms. See `NOTICE.md`; no new license is granted over the
recovered code or dataset material. This artifact is intended to make the
available evidence inspectable without overstating its completeness.
