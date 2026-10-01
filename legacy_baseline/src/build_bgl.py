"""Parse full BGL log with Drain and build fixed-window sessions.
Window = 100 consecutive logs (non-overlapping). Label=1 if any alert line in window.
"""
import os, json, time
import numpy as np
from drain import Drain

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(os.environ.get('LOGAD_RAW_ROOT', os.path.join(ROOT, 'raw')), 'BGL', 'BGL.log')
OUT = os.environ.get('LOGAD_PROC_DIR', os.path.join(ROOT, 'proc'))
os.makedirs(OUT, exist_ok=True)
WIN = 100

def main():
    d = Drain(depth=4, sim_th=0.4, max_child=100)
    ev_ids, alerts = [], []
    t0 = time.time()
    with open(RAW, errors='ignore') as f:
        for n, line in enumerate(f):
            parts = line.split(None, 9)
            label = parts[0] if parts else '-'
            msg = parts[9] if len(parts) >= 10 else line
            ev_ids.append(d.add_line(msg))
            alerts.append(0 if label == '-' else 1)
            if (n + 1) % 1_000_000 == 0:
                print(f'  {n+1} lines, {len(d.clusters)} templates, {time.time()-t0:.0f}s', flush=True)
    ev_ids = np.array(ev_ids, dtype=np.int32)
    alerts = np.array(alerts, dtype=np.int8)
    V = len(d.clusters)
    nwin = len(ev_ids) // WIN
    counts = np.zeros((nwin, V), dtype=np.int32)
    labels = np.zeros(nwin, dtype=np.int8)
    seqs = []
    for w in range(nwin):
        seg = ev_ids[w*WIN:(w+1)*WIN]
        for e in seg:
            counts[w, e] += 1
        labels[w] = 1 if alerts[w*WIN:(w+1)*WIN].any() else 0
        seqs.append(seg.tolist())
    np.save(os.path.join(OUT, 'bgl_counts.npy'), counts)
    np.save(os.path.join(OUT, 'bgl_labels.npy'), labels)
    with open(os.path.join(OUT, 'bgl_seqs.json'), 'w') as f:
        json.dump(seqs, f)
    templ_text = [d.template_str(i) for i in range(V)]
    with open(os.path.join(OUT, 'bgl_templates.json'), 'w') as f:
        json.dump({'events': list(range(V)), 'text': templ_text}, f)
    print(f'BGL windows={nwin} anomalies={int(labels.sum())} ({100*labels.mean():.2f}%) '
          f'vocab={V} total_lines={len(ev_ids)} time={time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()
