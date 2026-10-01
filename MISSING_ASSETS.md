# Recovered coverage and missing assets

## Recovered legacy implementation

The July baseline implements two datasets, six within-system configurations
(count LR/RF/XGBoost, sequence LSTM, semantic LR/XGBoost), and semantic LR/XGBoost
in both cross-system directions. The archived CSV has 12 within-system rows
and four cross-system rows. These are single-configuration aggregate outputs,
not the final manuscript's mean/SD tables.

Its classifier/split random state is 0; PyTorch is initialized with 0;
Word2Vec defaults to seed 1 and uses two workers. NumPy training-order shuffle
is not seeded. Word2Vec uses 30 epochs, matching the final table on that one
parameter, but lacks the final protocol's one-worker/process-independent hash
setup. Both legacy LSTM datasets use a 50-event truncation and three epochs.
The classification threshold is 0.5, without a validation-selected threshold.

## Not recovered for the final experiments

- The five exact experiment seeds, split/group-assignment indices, and
  validation choices; the final group-disjoint and chronological drivers.
- Frozen parser/vocabulary state and the final BGL temporal evaluation code.
- Parser-setting and rolling-origin experiment drivers and per-run outputs.
- The full two-by-two corpus/IDF ablation implementation and final predictions.
- Tie-aware review-budget experiment results below the published aggregates.
- Per-example predictions, per-seed metric tables, model checkpoints, and
  raw component-timing logs supporting the final Tables 4-8.
- The original environment lock and recorded SD normalization convention.
- The external `plotstyle` dependency used by the archived plotting script.

## Interpretation

The published table export supports aggregate reconstruction and consistency
checking only. It cannot establish experimental replay, recompute a p-value,
recover a confidence interval, or identify missing standard-deviation
normalization. The historical baseline cannot substitute for final protocols.
New synthetic test results are software checks, not scientific measurements.

The archival plotting script is excluded from the runnable source because its
style dependency is missing and it adds a hard-coded representation-cost value.
Neither that script nor its historical charts are used to regenerate final
paper results.
