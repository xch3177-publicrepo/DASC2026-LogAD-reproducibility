"""Tier-2 sequence model: a compact LSTM classifier over template-ID sequences."""
import numpy as np
import torch, torch.nn as nn, time

torch.manual_seed(0)

class LSTMClf(nn.Module):
    def __init__(self, vocab, emb=32, hid=64):
        super().__init__()
        self.emb = nn.Embedding(vocab + 1, emb, padding_idx=0)  # 0 = pad
        self.lstm = nn.LSTM(emb, hid, batch_first=True)
        self.head = nn.Sequential(nn.Linear(hid, 32), nn.ReLU(), nn.Linear(32, 1))
    def forward(self, x, lens):
        e = self.emb(x)
        packed = nn.utils.rnn.pack_padded_sequence(e, lens.cpu(), batch_first=True,
                                                   enforce_sorted=False)
        _, (h, _) = self.lstm(packed)
        return self.head(h[-1]).squeeze(-1)

def _pad(batch, maxlen):
    lens = np.array([min(len(s), maxlen) or 1 for s in batch])
    X = np.zeros((len(batch), lens.max()), dtype=np.int64)
    for i, s in enumerate(batch):
        s = s[:maxlen] if s else [0]
        X[i, :len(s)] = [e + 1 for e in s]     # shift ids by 1 (0=pad)
    return torch.tensor(X), torch.tensor(lens)

def train_lstm(seqs_tr, y_tr, vocab, maxlen=50, epochs=3, bs=256, lr=1e-3, log=print):
    dev = torch.device('cpu')
    torch.set_num_threads(2)
    model = LSTMClf(vocab).to(dev)
    pos_w = torch.tensor([(len(y_tr) - y_tr.sum()) / max(y_tr.sum(), 1)], dtype=torch.float32)
    crit = nn.BCEWithLogitsLoss(pos_weight=pos_w)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    idx = np.arange(len(seqs_tr))
    t0 = time.time()
    for ep in range(epochs):
        np.random.shuffle(idx)
        model.train(); tot = 0
        for b in range(0, len(idx), bs):
            bi = idx[b:b+bs]
            X, lens = _pad([seqs_tr[i] for i in bi], maxlen)
            yb = torch.tensor(y_tr[bi], dtype=torch.float32)
            opt.zero_grad()
            out = model(X, lens)
            loss = crit(out, yb)
            loss.backward(); opt.step()
            tot += loss.item() * len(bi)
        log(f'    lstm epoch {ep+1}/{epochs} loss={tot/len(idx):.4f} ({time.time()-t0:.0f}s)')
    return model

@torch.no_grad()
def predict_lstm(model, seqs, maxlen=50, bs=512):
    model.eval(); out = []
    for b in range(0, len(seqs), bs):
        X, lens = _pad(seqs[b:b+bs], maxlen)
        out.append(torch.sigmoid(model(X, lens)).numpy())
    return np.concatenate(out)

def count_params(model):
    return sum(p.numel() for p in model.parameters())
