"""DASC log anomaly detection study.
RQ1 within-system accuracy across representation tiers (count / sequence / semantic)
RQ2 cross-system generalization (HDFS<->BGL) — only shared semantic space transfers
RQ3 cost: train time, inference throughput, model size
"""
import os, sys, json, time, warnings
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings('ignore')
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, roc_curve
from xgboost import XGBClassifier
import log_features as LF
import lstm_model as LM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.environ.get('LOGAD_PROC_DIR', os.path.join(ROOT, 'proc'))
OUT = os.environ.get('LOGAD_OUT_DIR', os.path.join(ROOT, 'out'))
os.makedirs(OUT, exist_ok=True)
DIM = 100
RNG = 0

def metrics(y, s, thr=0.5):
    yhat = (s >= thr).astype(int)
    tp = int(((y==1)&(yhat==1)).sum()); fn = int(((y==1)&(yhat==0)).sum())
    tn = int(((y==0)&(yhat==0)).sum()); fp = int(((y==0)&(yhat==1)).sum())
    fpr, tpr, _ = roc_curve(y, s); ok = fpr <= 0.01
    return dict(precision=tp/max(tp+fp,1), recall=tp/max(tp+fn,1),
                f1=f1_score(y,yhat,zero_division=0),
                roc_auc=roc_auc_score(y,s), pr_auc=average_precision_score(y,s),
                tpr_at_1fpr=float(tpr[ok].max()) if ok.any() else 0.0,
                fp=fp, tn=tn)

def size_mb(model):
    import pickle
    return len(pickle.dumps(model))/1e6

def run_count_model(name, Xtr, ytr, Xte, yte):
    spw = (len(ytr)-ytr.sum())/max(ytr.sum(),1)
    if name=='LR': m = make_pipeline(StandardScaler(with_mean=False), LogisticRegression(max_iter=1000, class_weight='balanced'))
    elif name=='RF': m = RandomForestClassifier(200, n_jobs=2, class_weight='balanced_subsample', random_state=RNG)
    else: m = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1, n_jobs=2,
                            scale_pos_weight=spw, tree_method='hist', eval_metric='aucpr', random_state=RNG)
    t0=time.time(); m.fit(Xtr,ytr); tt=time.time()-t0
    t0=time.time(); s=m.predict_proba(Xte)[:,1]; it=time.time()-t0
    r=metrics(yte,s); r.update(train_s=tt, infer_kps=len(Xte)/it/1000, size_mb=size_mb(m))
    return r, s

def main():
    hdfs = LF.load_system(PROC, 'hdfs')
    bgl  = LF.load_system(PROC, 'bgl')
    print('systems loaded:', {s['name']: s['counts'].shape for s in (hdfs,bgl)})

    # ---- shared semantic space ----
    t0=time.time()
    w2v = LF.train_template2vec([hdfs, bgl], dim=DIM)
    emb = {s['name']: LF.template_embeddings(s['templates'], w2v, DIM) for s in (hdfs,bgl)}
    sem = {s['name']: LF.session_semantic(s['counts'], emb[s['name']]) for s in (hdfs,bgl)}
    print(f'Template2Vec trained ({time.time()-t0:.0f}s), vocab={len(w2v.wv)}')

    rows = []
    splits = {}
    for S in (hdfs, bgl):
        nm=S['name']; y=S['labels']
        idx_tr, idx_te = train_test_split(np.arange(len(y)), test_size=0.3,
                                          stratify=y, random_state=RNG)
        splits[nm]=(idx_tr, idx_te)

    # ================= RQ1 within-system =================
    for S in (hdfs, bgl):
        nm=S['name']; y=S['labels']; tr,te=splits[nm]
        # Tier-1 count
        Cn = S['counts'].astype(np.float32)
        for mdl in ('LR','RF','XGB'):
            r,_=run_count_model(mdl, Cn[tr], y[tr], Cn[te], y[te])
            r.update(system=nm, tier='count', model=mdl, setting='within'); rows.append(r)
            print(f"[within {nm}] count/{mdl:3s} F1={r['f1']:.3f} PR-AUC={r['pr_auc']:.3f} "
                  f"TPR@1%FPR={r['tpr_at_1fpr']:.3f} train={r['train_s']:.1f}s", flush=True)
        # Tier-3 semantic
        Se = sem[nm]
        for mdl in ('LR','XGB'):
            r,_=run_count_model(mdl, Se[tr], y[tr], Se[te], y[te])
            r.update(system=nm, tier='semantic', model=mdl, setting='within'); rows.append(r)
            print(f"[within {nm}] semantic/{mdl:3s} F1={r['f1']:.3f} PR-AUC={r['pr_auc']:.3f} "
                  f"TPR@1%FPR={r['tpr_at_1fpr']:.3f}", flush=True)
        # Tier-2 sequence (LSTM)
        vocab = S['counts'].shape[1]
        t0=time.time()
        model = LM.train_lstm([S['seqs'][i] for i in tr], y[tr], vocab, epochs=3)
        tt=time.time()-t0
        t0=time.time(); s=LM.predict_lstm(model, [S['seqs'][i] for i in te]); it=time.time()-t0
        r=metrics(y[te], s); r.update(system=nm, tier='sequence', model='LSTM', setting='within',
                                      train_s=tt, infer_kps=len(te)/it/1000, size_mb=LM.count_params(model)*4/1e6)
        rows.append(r)
        print(f"[within {nm}] sequence/LSTM F1={r['f1']:.3f} PR-AUC={r['pr_auc']:.3f} "
              f"TPR@1%FPR={r['tpr_at_1fpr']:.3f} train={tt:.0f}s params={LM.count_params(model)}", flush=True)

    # ================= RQ2 cross-system (semantic only) =================
    for src,dst in (('hdfs','bgl'),('bgl','hdfs')):
        Ssrc = hdfs if src=='hdfs' else bgl
        Sdst = hdfs if dst=='hdfs' else bgl
        Xtr, ytr = sem[src], Ssrc['labels']
        Xte, yte = sem[dst], Sdst['labels']
        for mdl in ('LR','XGB'):
            r,_=run_count_model(mdl, Xtr, ytr, Xte, yte)
            r.update(system=f'{src}->{dst}', tier='semantic', model=mdl, setting='cross'); rows.append(r)
            print(f"[cross {src}->{dst}] semantic/{mdl:3s} F1={r['f1']:.3f} PR-AUC={r['pr_auc']:.3f} "
                  f"recall={r['recall']:.3f} prec={r['precision']:.3f}", flush=True)

    df=pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT,'log_results.csv'), index=False)
    print('\nsaved out/log_results.csv'); print(df[['setting','system','tier','model','f1','pr_auc','tpr_at_1fpr']].to_string())

if __name__=='__main__':
    main()
