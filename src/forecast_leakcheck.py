"""Leakage checks for forecast.py (final run): (1) future-perturbation of inputs, (2) flagged-value test, (3) value check."""
import sys, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import forecast as F
import lightgbm as lgb
BAS = ['CISO', 'PJM', 'ERCO', 'AECI', 'DUK']
inp = F.ROOT / 'data/derived/ci_clean.parquet'
sh = str(F.ROOT / 'data/derived/ci_hourly.parquet')
ba_list, data = F.load_series(inp, '', BAS, None, sh)
model = lgb.Booster(model_file=str(F.ROOT / 'data/derived/forecasts/lgbm_model.txt'))
F.model_threads[0] = 8
rng = np.random.default_rng(0)
bad = 0; ntest = 0
def fc(m, code, rec, iss):
    return F.lgbm_fc(model, code, rec, iss) if m == 'lgbm' else F.baseline_fc(rec['C'], iss, m)
for code, ba in enumerate(ba_list):
    rec = data[ba]; rec['R'] = F.roll_stats(rec['C'])
    for t0 in rng.integers(F.IDX_TRAIN_END, F.IDX_ISSUE_END - 100, 6):
        iss = np.array([t0])
        r2 = {'C': rec['C'].copy(), 'S': rec['S'].copy()}
        r2['C'][t0 + 1:] = rng.random(r2['C'][t0 + 1:].size).astype(np.float32) * 1000
        r2['S'][t0 + 1:] = rng.random(r2['S'][t0 + 1:].shape).astype(np.float32)
        r2['R'] = F.roll_stats(r2['C'])
        for m in F.ALL_MODELS:
            ntest += 1
            if not np.allclose(fc(m, code, rec, iss), fc(m, code, r2, iss), equal_nan=True, atol=1e-4):
                bad += 1; print('LEAK-future', ba, t0, m)
print(f'future-perturbation: {ntest} tests, {bad} failed')
# (2) flagged-hour test: model input must not depend on the values stored at flag 1/2 hours
df = pd.read_parquet(inp); df['utc'] = pd.to_datetime(df['utc'], utc=True).dt.tz_convert(None)
bad2 = 0; nflag = 0
for ba in BAS:
    d = df[df.ba == ba]
    idx = ((d.utc - F.G0) / pd.Timedelta(hours=1)).astype(int).to_numpy()
    Y = np.full(F.NG, np.nan, np.float32); Y[idx] = d.ci_clean.to_numpy(np.float32)
    fl = np.full(F.NG, -1, np.int8); fl[idx] = d.flag.to_numpy(np.int8)
    C1 = F.causal_input(Y, fl)
    Yp = Y.copy(); bd = (fl == 1) | (fl == 2); Yp[bd] = rng.random(bd.sum()).astype(np.float32) * 5000
    C2 = F.causal_input(Yp, fl)
    nflag += int(bd.sum())
    if not np.array_equal(C1, C2, equal_nan=True): bad2 += 1
    # each replaced hour equals an EARLIER valid value (within 6 h) or NaN
    ii = np.where(bd)[0]
    ok = [np.isnan(C1[i]) or any(C1[i] == Y[i - k] and not bd[i - k] for k in range(1, 7)) for i in ii]
    if not all(ok): bad2 += 1; print('replacement not an earlier valid value', ba)
print(f'flagged-input test: {nflag} flagged hours in {len(BAS)} BAs, {bad2} failures')
