# Dataset inputs (not redistributed)

Obtain the HDFS_v1 and BGL releases through the official Loghub repository:

- https://github.com/logpai/loghub
- HDFS dataset information: https://github.com/logpai/loghub/tree/master/HDFS
- BGL dataset information: https://github.com/logpai/loghub/tree/master/BGL
- BGL source collection: https://www.usenix.org/cfdr-data#hpc4

Follow upstream download instructions, terms, and requested citations. This
package does not download data automatically or grant redistribution rights.
The locally inspected archives contained dataset descriptions/citation
requests, but no general redistribution license was inferred from them.

Expected layout below the CLI's `--raw-root` directory:

```text
local_data/
  HDFS_v1/preprocessed/HDFS.log_templates.csv
  HDFS_v1/preprocessed/Event_traces.csv
  BGL/BGL.log
```

The HDFS legacy builder uses the released preprocessed templates and event
traces; it does not read HDFS.log. BGL is parsed in file order into
non-overlapping 100-line windows, with an alert in any line marking a window
as anomalous. Do not substitute a small sample archive and label it the full
release.

The inspected compressed archive fingerprints are recorded in
`provenance.json`. They identify the local inputs inspected for this support
artifact, not a guarantee that every upstream repackaging has the same ZIP
bytes. Raw logs and derived catalogs must stay outside the public repository.
