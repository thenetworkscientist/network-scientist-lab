"""
Little's Law, simulated: how many beds does a hospital need?

Companion code for The Network Scientist's video and article
"How Does a Hospital Know How Many Beds It Needs?"

The model, in one paragraph
---------------------------
Patients arrive as a Poisson process (rate LAM per day) and each stays a random
time with mean MEAN_LOS days. In the first model every patient gets a bed
(Kendall notation M/G/inf). Little's Law says the average number of patients in
the hospital is L = LAM * MEAN_LOS. Because arrivals are Poisson, the number in
the hospital at any moment is exactly Poisson(L), whatever the shape of the
length-of-stay distribution ("insensitivity"). We size beds so that every patient
has a bed on TARGET (95%) of days, counted at midnight, the way hospitals count.

The what-if model has a fixed number of beds c. A patient who finds every bed
full waits in the emergency department ("boarding") until one frees up, first
come first served (M/M/c, the Erlang C model).

Every headline number is checked three ways (see check_math.py):
  1. formula   (Little's Law, Poisson census, Erlang C)
  2. discrete-event simulation (this file)
  3. brute force (try every bed count on the simulated census, keep the smallest that works)
"""
import heapq
import math

import numpy as np
from scipy.stats import poisson

# ---------------------------------------------------------------- inputs
LAM = 20.0         # admissions per day
MEAN_LOS = 5.0     # average length of stay, days
TARGET = 0.95      # share of days on which every patient has a bed
DAYS = 20_000      # simulated days per replication
WARMUP = 200       # days discarded while the empty hospital fills up
REPS = 10          # independent replications (midnight counts are autocorrelated)
SEED = 2026

L_AVG = LAM * MEAN_LOS   # Little's Law: 20 x 5 = 100


# ---------------------------------------------------------------- formulas
def beds_formula(avg_patients, target=TARGET):
    """Smallest bed count c with P(Poisson(avg) <= c) >= target."""
    return int(poisson.ppf(target, avg_patients))


def erlang_b(a, c):
    """Erlang B blocking probability, stable recursion. a = offered load (avg patients)."""
    b = 1.0
    for k in range(1, c + 1):
        b = a * b / (k + a * b)
    return b


def erlang_c(a, c):
    """Probability an arriving patient has to wait (M/M/c). Needs c > a."""
    b = erlang_b(a, c)
    return c * b / (c - a * (1 - b))


def mean_wait_if_waiting_hours(a, c, mean_los=MEAN_LOS):
    """In M/M/c the wait of those who wait is exponential with mean 1/(c*mu - lam)."""
    return mean_los / (c - a) * 24


def share_waiting_longer_than(a, c, hours, mean_los=MEAN_LOS):
    """P(wait > t) = ErlangC * exp(-(c - a) * t / mean_los)."""
    return erlang_c(a, c) * math.exp(-(c - a) * (hours / 24) / mean_los)


# ---------------------------------------------------------------- length of stay
def los_sampler(kind, rng, mean=MEAN_LOS):
    if kind == "exponential":
        return lambda: rng.exponential(mean)
    if kind == "lognormal":                      # right-skewed, sd 4 days
        sd = 4.0
        s2 = math.log(1 + (sd / mean) ** 2)
        mu = math.log(mean) - s2 / 2
        return lambda: rng.lognormal(mu, math.sqrt(s2))
    if kind == "fixed":
        return lambda: mean
    raise ValueError(kind)


# ---------------------------------------------------------------- discrete-event simulation
def simulate_census(lam, los, days, warmup, rng, weekday=None):
    """
    Every patient gets a bed (M/G/inf). The state only changes at events
    (an admission or a discharge), so instead of ticking a clock we jump from
    event to event. Discharge times sit in a heap (the event list).

    weekday: optional list of 7 multipliers for a time-varying arrival rate
    (a non-homogeneous Poisson process, sampled by thinning).

    Returns: midnight census for each day after warm-up, the time-average number
    in the hospital (L), the measured arrival rate and the measured mean stay.
    """
    lam_max = lam * (max(weekday) if weekday else 1.0)
    t, n = 0.0, 0
    discharges = []
    census = []
    next_midnight = 1.0
    area, last = 0.0, 0.0
    admitted, total_stay = 0, 0.0

    def advance(to):
        nonlocal area, last
        if to > warmup:
            area += n * (to - max(last, warmup))
        last = to

    while next_midnight <= days:
        t_arrival = t + rng.exponential(1 / lam_max)
        while True:                                   # handle events before the arrival
            t_dis = discharges[0] if discharges else math.inf
            t_next = min(t_dis, next_midnight, t_arrival)
            if t_next == t_arrival or next_midnight > days:
                break
            advance(t_next)
            if t_next == t_dis:
                heapq.heappop(discharges)
                n -= 1
            else:
                if next_midnight > warmup:
                    census.append(n)
                next_midnight += 1.0
        if next_midnight > days:
            break
        advance(t_arrival)
        t = t_arrival
        if weekday and rng.random() > weekday[int(t) % 7] / max(weekday):
            continue                                  # thinned: not a real arrival
        stay = los()
        heapq.heappush(discharges, t + stay)
        n += 1
        if t >= warmup:
            admitted += 1
            total_stay += stay

    span = days - warmup
    return np.array(census), area / span, admitted / span, total_stay / max(admitted, 1)


def simulate_boarding(lam, los, beds, days, warmup, rng):
    """
    Fixed number of beds. A patient who finds them all full boards in the ER,
    first come first served, until a bed frees. Returns each patient's wait in hours.
    """
    t = 0.0
    busy = []          # heap of discharge times of occupied beds
    queue = []         # arrival times of boarding patients (FIFO)
    waits = []
    while t < days:
        t += rng.exponential(1 / lam)
        while busy and busy[0] <= t:
            free_at = heapq.heappop(busy)
            if queue:
                arrived = queue.pop(0)
                if arrived >= warmup:
                    waits.append(free_at - arrived)
                heapq.heappush(busy, free_at + los())
        if len(busy) < beds:
            if t >= warmup:
                waits.append(0.0)
            heapq.heappush(busy, t + los())
        else:
            queue.append(t)
    return np.array(waits) * 24


# ---------------------------------------------------------------- brute force
def beds_bruteforce(census_runs, target=TARGET):
    """Try every bed count; keep the smallest that covers target share of days in the pooled runs."""
    pooled = np.concatenate(census_runs)
    for c in range(int(pooled.max()) + 2):
        if np.mean(pooled <= c) >= target:
            return c


# ---------------------------------------------------------------- run everything
def run(reps=REPS, days=DAYS, verbose=True):
    rng = np.random.default_rng(SEED)
    out = {"L_avg": L_AVG, "beds_formula": beds_formula(L_AVG)}
    out["occupancy"] = L_AVG / out["beds_formula"]

    shapes = {}
    for kind in ["exponential", "lognormal", "fixed"]:
        runs, Ls, lw = [], [], []
        for _ in range(reps):
            cen, L, lam_hat, w_hat = simulate_census(LAM, los_sampler(kind, rng), days, WARMUP, rng)
            runs.append(cen); Ls.append(L); lw.append(lam_hat * w_hat)
        pooled = np.concatenate(runs)
        shapes[kind] = dict(L=np.mean(Ls), lamW=np.mean(lw), mean=pooled.mean(), var=pooled.var(),
                            beds_bruteforce=beds_bruteforce(runs),
                            cover_116=np.mean(pooled <= 116), cover_117=np.mean(pooled <= 117),
                            census=pooled)
    out["shapes"] = shapes

    out["size"] = {a: (beds_formula(a), a / beds_formula(a)) for a in (20, 100, 500)}
    out["plus_one_day"] = (LAM * (MEAN_LOS + 1), beds_formula(LAM * (MEAN_LOS + 1)))

    wk = [1.08] * 5 + [0.80] * 2
    runs = [simulate_census(LAM, los_sampler("exponential", rng), days, WARMUP, rng, weekday=wk)[0]
            for _ in range(reps)]
    out["weekday"] = dict(var=np.concatenate(runs).var(), beds=beds_bruteforce(runs))

    whatif = {}
    for c in (105, 110, 117):
        sims = [simulate_boarding(LAM, los_sampler("exponential", rng), c, days, WARMUP, rng) for _ in range(reps)]
        w = np.concatenate(sims)
        wl = simulate_boarding(LAM, los_sampler("lognormal", rng), c, days, WARMUP, rng)
        whatif[c] = dict(
            p_wait_formula=erlang_c(L_AVG, c), p_wait_sim=np.mean(w > 0),
            wait_formula=mean_wait_if_waiting_hours(L_AVG, c), wait_sim=w[w > 0].mean(),
            over4_formula=share_waiting_longer_than(L_AVG, c, 4), over4_sim=np.mean(w >= 4),
            over24_formula=share_waiting_longer_than(L_AVG, c, 24), over24_sim=np.mean(w >= 24),
            p_wait_lognormal=np.mean(wl > 0), wait_lognormal=wl[wl > 0].mean())
    out["whatif"] = whatif

    if verbose:
        print(f"Little's Law: L = {LAM:g} x {MEAN_LOS:g} = {L_AVG:g} beds in use on average")
        print(f"Beds for every patient on {TARGET:.0%} of days: {out['beds_formula']} "
              f"(average occupancy {out['occupancy']:.1%})")
        for k, s in shapes.items():
            print(f"  {k:12s} L={s['L']:.2f}  lam*W={s['lamW']:.2f}  var={s['var']:.1f}  "
                  f"brute force={s['beds_bruteforce']}  days covered at 116={s['cover_116']:.3f}")
        for a, (b, occ) in out["size"].items():
            print(f"  average {a}: {b} beds, occupancy {occ:.1%}")
        print(f"  one extra day of stay: average {out['plus_one_day'][0]:g}, beds {out['plus_one_day'][1]}")
        print(f"  weekday pattern: variance {out['weekday']['var']:.1f}, beds {out['weekday']['beds']}")
        for c, r in whatif.items():
            print(f"  {c} beds: wait {r['p_wait_formula']:.1%} (sim {r['p_wait_sim']:.1%}), "
                  f"mean wait {r['wait_formula']:.1f} h (sim {r['wait_sim']:.1f} h), "
                  f"4h+ {r['over4_formula']:.1%}, 24h+ {r['over24_formula']:.1%}, "
                  f"lognormal {r['p_wait_lognormal']:.1%} / {r['wait_lognormal']:.1f} h")
    return out


if __name__ == "__main__":
    run()
