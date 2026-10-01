"""Build HDFS session dataset from loghub preprocessed files.
Session = per-block event sequence. Outputs count matrix, sequences, labels, templates.
"""
import os, ast, json
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(os.environ.get('LOGAD_RAW_ROOT', os.path.join(ROOT, 'raw')), 'HDFS_v1', 'preprocessed')
OUT = os.environ.get('LOGAD_PROC_DIR', os.path.join(ROOT, 'proc'))
os.makedirs(OUT, exist_ok=True)

def main():
    tpl = pd.read_csv(os.path.join(RAW, 'HDFS.log_templates.csv'))
    events = list(tpl.EventId)                       # E1..E29
    eid = {e: i for i, e in enumerate(events)}
    tpl_words = {r.EventId: r.EventTemplate for r in tpl.itertuples()}

    tr = pd.read_csv(os.path.join(RAW, 'Event_traces.csv'))
    print('traces', tr.shape, 'cols', list(tr.columns))
    # Label: Success -> 0, Fail/Anomaly -> 1
    lab = (tr['Label'].astype(str).str.lower() != 'success').astype(int)
    seqs = []
    counts = np.zeros((len(tr), len(events)), dtype=np.int32)
    for i, feat in enumerate(tr['Features'].values):
        ids = [t for t in str(feat).strip('[]').replace(' ', '').split(',') if t]
        s = [eid[e] for e in ids if e in eid]
        seqs.append(s)
        for e in s:
            counts[i, e] += 1
    np.save(os.path.join(OUT, 'hdfs_counts.npy'), counts)
    np.save(os.path.join(OUT, 'hdfs_labels.npy'), lab.values)
    with open(os.path.join(OUT, 'hdfs_seqs.json'), 'w') as f:
        json.dump(seqs, f)
    with open(os.path.join(OUT, 'hdfs_templates.json'), 'w') as f:
        json.dump({'events': events, 'text': [tpl_words[e] for e in events]}, f)
    print(f'HDFS sessions={len(tr)} anomalies={int(lab.sum())} ({100*lab.mean():.2f}%) '
          f'vocab={len(events)} avg_len={np.mean([len(s) for s in seqs]):.1f}')

if __name__ == '__main__':
    main()
