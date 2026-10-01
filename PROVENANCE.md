# Artifact provenance

## Recovered material

The legacy sources and 16-row aggregate CSV were recovered from
`LogAD_project.zip`, whose entries are dated July 2026. Source entry names and
SHA-256 fingerprints are in `provenance.json`. Three path-only portability
patches are fully reversible and verified; all other included legacy bytes
are preserved. The original archive itself is not redistributed.

The final-paper table export was produced from the frozen final aggregate
table source used for the camera-ready review. Its input-document SHA-256 and
per-table SHA-256 fingerprints identify the exact source without distributing
the manuscript or disclosing repository history. The extraction was performed
in memory: only table values/context and numeric ledgers were written here.

The source-audit token sequence has 348 numeric tokens because the pre-existing
gate counted four `0.6em` spacing controls in Table 7. The public cell export
has 344 visible numeric tokens. Both ledgers are preserved, along with the
unchanged 134 mean/SD pairs. This distinction changes no measurement.

## Newly produced support material

All documentation, export/reconstruction/verifier utilities, execution wrapper,
and tests were created on 2026-10-01. JSON table exports and generated Markdown
are deterministic representations of existing published aggregates. The
synthetic tests contain invented toy messages and vectors only; they are not
benchmarks, historical outputs, or evidence supporting paper results.

## Inspected but excluded inputs

HDFS_v1 and BGL ZIP files passed CRC and safe-entry checks. Their compressed
fingerprints are recorded solely to identify the inspected release files.
HDFS Event_traces contained 575,061 sessions (558,223 Success / 16,838 Fail).
Raw logs, preprocessed benchmark arrays, and template catalogs are not copied.

Only project-specific local archive/revision locations and their accessible
Git file histories were searched. No claim is made that missing assets do not
exist elsewhere. See `MISSING_ASSETS.md` for unresolved final-experiment gaps.
