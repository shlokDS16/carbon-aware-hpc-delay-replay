"""Core of the carbon-aware delay scheduler (vectorised, one balancing authority at a time).

Time axis: hours since the grid origin; interval k covers [k, k+1) and carries ci[k] (EIA hour ending origin+k+1).
A job arriving at time a may start at s in {a, a+d, ..., a+S}. The planner chooses s to minimise the integral of its
signal over [s, s + R_hat], seeing only the HP = 98 hourly intervals floor(a) .. floor(a)+97 (the same width for every
signal, so that arms differ only in the signal or the runtime estimate; forecasts hold their lead-96 value for the last
two intervals). Realised emissions use the actual ci over
[s, s + R_act]. Ties go to the earliest start.
"""
import numpy as np

HP = 98         # planner width in hourly intervals: covers frac(a) + S + R_req <= 1 + 24 + 72 = 97 h
H = 96          # planning horizon in hourly intervals (forecast leads 1..96)
STEP = 0.25     # candidate start spacing in hours


def cum_hours(ci):
    """cum[k] = integral of ci over [0, k)."""
    c = np.zeros(len(ci) + 1)
    np.cumsum(ci, out=c[1:])
    return c


def integral_abs(cum, ci, x):
    """Integral of the actual ci over [0, x] for arrays of x (hours)."""
    k = np.floor(x).astype(np.int64)
    k = np.clip(k, 0, len(ci) - 1)
    return cum[k] + (x - k) * ci[k]


def window_signal_actual(ci, a, width=HP):
    """Actual ci for the planner window: rows = jobs, cols = intervals floor(a)+j, j=0..width-1."""
    base = np.floor(a).astype(np.int64)
    idx = base[:, None] + np.arange(width)[None, :]
    return ci[np.clip(idx, 0, len(ci) - 1)]


def plan_start(signal, a, r_hat, slack):
    """Choose start times.

    signal: [n, H] planner signal for intervals floor(a)+j.
    a, r_hat, slack: [n] arrays in hours.
    Returns s [n].
    """
    n = len(a)
    W = signal.shape[1]
    cumf = np.zeros((n, W + 1))
    np.cumsum(signal, axis=1, out=cumf[:, 1:])
    k_max = int(np.ceil(np.max(slack) / STEP)) if n else 0
    offs = np.arange(k_max + 1) * STEP                       # [K]
    x0 = (a - np.floor(a))[:, None] + offs[None, :]          # start, relative to floor(a)
    x1 = x0 + r_hat[:, None]
    x1 = np.minimum(x1, float(W))                            # planner sees only its window
    x0c = np.minimum(x0, float(W))

    def eval_cum(x):
        k = np.clip(np.floor(x).astype(np.int64), 0, W - 1)
        rows = np.arange(n)[:, None]
        return cumf[rows, k] + (x - k) * signal[rows, k]

    cost = eval_cum(x1) - eval_cum(x0c)
    feasible = offs[None, :] <= slack[:, None] + 1e-9
    cost = np.where(feasible, cost, np.inf)
    best = np.argmin(cost, axis=1)                           # first minimum = earliest start
    return a + offs[best]


def realised(cum, ci, s, r_act):
    """Realised emissions integral (g/kWh x h) over [s, s + r_act]."""
    return integral_abs(cum, ci, s + r_act) - integral_abs(cum, ci, s)


def _selftest():
    rng = np.random.default_rng(0)
    t = np.arange(24 * 30)
    ci = 300 + 100 * np.sin(2 * np.pi * (t % 24) / 24) + rng.normal(0, 5, len(t))
    cum = cum_hours(ci)
    # analytic check of the integral
    assert abs(realised(cum, ci, np.array([2.5]), np.array([1.0]))[0] - (0.5 * ci[2] + 0.5 * ci[3])) < 1e-9
    n = 2000
    a = rng.uniform(0, 24 * 25, n)
    r = rng.uniform(0.5, 10, n)
    S = np.full(n, 12.0)
    sig = window_signal_actual(ci, a)
    s_or = plan_start(sig, a, r, S)
    assert np.all(s_or >= a - 1e-9) and np.all(s_or <= a + S + 1e-9)
    e_now = realised(cum, ci, a, r)
    e_or = realised(cum, ci, s_or, r)
    assert np.all(e_or <= e_now + 1e-6), "oracle with exact runtime must never lose to run-now"
    # brute force check on 50 jobs
    for j in range(50):
        cands = a[j] + np.arange(0, 12.0 + 1e-9, STEP)
        e = realised(cum, ci, cands, np.full(len(cands), r[j]))
        assert abs(e.min() - e_or[j]) < 1e-6
    # a long requested runtime should not beat the exact one on average
    s_req = plan_start(sig, a, r * 3, S)
    e_req = realised(cum, ci, s_req, r)
    print("selftest ok; saving exact %.4f, saving with 3x runtime %.4f" %
          (1 - e_or.sum() / e_now.sum(), 1 - e_req.sum() / e_now.sum()))


if __name__ == "__main__":
    _selftest()
