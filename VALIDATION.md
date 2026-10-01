# Validation record

Validation date: 2026-10-01. This record describes software/support-artifact
checks, not a replication of the final experiments.

| Check | Result |
| --- | --- |
| Recovered source syntax | Six included legacy scripts parse successfully |
| Original provenance | Three unchanged scripts and historical CSV byte-identical; three path-only patches reverse to original hashes |
| Aggregate export | Eight tables; 344 visible numeric tokens; 134 mean/SD pairs unchanged |
| Prior source-audit ledger | 348 tokens; four Table 7 spacing tokens explicitly identified and excluded from visible data |
| Table presentation | Deterministic Markdown reconstruction matches JSON/ledger |
| Synthetic tests with available packages | Eight tests passed |
| Standard-library-only tests (`python3 -S -B`) | Six passed; two optional NumPy/Pandas tests skipped |
| Toy HDFS preprocessing | Two synthetic sessions and labels reconstructed correctly |
| Toy BGL preprocessing | 200 synthetic messages yield two 100-line windows, with correct toy alert labels |
| Toy semantic vectors | Weighted averaging and zero-vector fallback passed |
| Negative controls | Deliberately changed table value rejected; fabricated token marker detected without returning its value |
| Public-content scan | No matched risk in package text; no actual credential value is logged |
| Private identity/project marker check | No matches; checked values not written to the artifact |
| Full legacy training | **NOT EXECUTED**; required ML dependencies unavailable |
| Final five-seed protocols | **NOT EXECUTED / implementation not recovered** |

The available runtime had NumPy 2.5.2 and Pandas 3.0.5. SciPy,
scikit-learn, XGBoost, Gensim, and PyTorch were unavailable. Package-name
discovery is not a dependency compatibility test, and no dependency lock
matching the old experiments was recovered. This release does not claim
successful full-data preprocessing or model training.

Separately, the three inspected input archives passed CRC checks and contained
no absolute/traversing archive paths or symbolic links. A streaming read of
the HDFS traces confirmed 575,061 records and 16,838 Fail labels. Those local
inputs are not part of the public artifact.

Re-run the documented commands in `README.md`; `SHA256SUMS.txt` covers the
public release files. Checksums establish file consistency, not the scientific
validity of measurements or completeness of the absent experimental records.
