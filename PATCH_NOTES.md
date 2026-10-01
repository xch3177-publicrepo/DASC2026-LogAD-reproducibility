# Path-only legacy portability patches

The six recovered scripts retain their algorithm settings and computations.
Three files have only the following input/output-path changes:

1. `build_hdfs.py`: allow `LOGAD_RAW_ROOT` and `LOGAD_PROC_DIR`; default layout
   remains the legacy `raw/HDFS_v1/preprocessed` and `proc` layout.
2. `build_bgl.py`: allow the same variables; default BGL layout remains
   `raw/BGL/BGL.log`.
3. `log_experiments.py`: allow `LOGAD_PROC_DIR` and `LOGAD_OUT_DIR`.

The new CLI supplies those variables so new runs cannot overwrite the archived
CSV. It requires explicit opt-in for data processing/model training and refuses
to overwrite an existing output directory. No algorithm hyperparameters,
thresholds, randomness, epochs, or truncation lengths were changed. Exact
old/new replacement strings and original source hashes are in `provenance.json`.
The verifier reverses every declared patch in memory and checks the resulting
bytes against the original archive entry hash.

`drain.py`, `log_features.py`, `lstm_model.py`, and the historical CSV are
byte-identical to recovered archive entries. The archived plotting script,
paper, figures, template catalogs, and narrative README are excluded; see
`MISSING_ASSETS.md` for the missing plotting dependency.

All files in `tools/` and `tests/`, and all documentation in this package, were
written for this support release. They must not be cited as recovered original
experiment implementations.
