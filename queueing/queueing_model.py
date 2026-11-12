"""
Queueing and utilization: why a line doubles when the barista is just a bit busier.

One source of truth for every number in the video, the story shorts and the article.
Each result is computed three independent ways:
  1. formula      : the textbook result (M/M/1, Pollaczek-Khinchine, Erlang C, Cobham)
  2. simulation   : customers simulated one by one
  3. brute force  : the queue's Markov chain solved numerically, no formula

Units: minutes. One barista takes 2 minutes per drink on average.
The Network Scientist. MIT licensed.
"""
import math
import numpy as np

DRINK_MIN = 2.0                 # average minutes per drink
MU = 1.0 / DRINK_MIN            # drinks per minute one barista can make
BUSY_LEVELS = (0.5, 0.8, 0.9, 0.95)
MOBILE_SHARE = 0.30             # Starbucks says mobile is "more than 30%" of US transactions
CALLOUT = 0.36                  # share of TSA officers who called out at Bush Intercontinental (CBS News)
ILLUSTRATIVE_NORMAL_BUSY = 0.90 # assumption for the article's Houston arithmetic only (labelled illustrative)


# ---------------------------------------------------------------- 1. formulas
def mm1(busy):
    """One barista, random arrivals, random drink times (M/M/1)."""
    lam = busy * MU
    total = 1.0 / (MU - lam)            # minutes from joining the line to drink in hand
    line = total - DRINK_MIN            # minutes waiting in line
    return {"busy": busy, "per_hour": lam * 60, "line_min": line,
            "total_min": total, "people_in_line": lam * line}


def md1_line(busy):
    """Same, but every drink takes exactly 2 minutes (Pollaczek-Khinchine)."""
    return busy * DRINK_MIN / (2 * (1 - busy))


def erlang_c(c, a):
    """Chance an arrival has to wait, c baristas, offered load a."""
    s = sum(a ** k / math.factorial(k) for k in range(c))
    t = a ** c / math.factorial(c) * c / (c - a)
    return t / (s + t)


def mmc_line(c, per_barista_busy):
    lam = c * per_barista_busy * MU
    return erlang_c(c, lam / MU) / (c * MU - lam)


def priority_lines(busy, share_first=1 - MOBILE_SHARE):
    """Cafe orders always made first, mobile waits (non-preemptive, Cobham 1954).
    Equal drink times for both groups."""
    w0 = busy * DRINK_MIN                       # lam * E[S^2] / 2 with exponential drinks
    r1 = share_first * busy
    cafe = w0 / (1 - r1)
    mobile = w0 / ((1 - r1) * (1 - busy))
    return {"cafe": cafe, "mobile": mobile,
            "average": share_first * cafe + (1 - share_first) * mobile}


def overload(normal_busy, callout=CALLOUT):
    """Capacity cut: load after the cut, and minutes of wait added per hour of rush."""
    load = normal_busy / (1 - callout)
    return {"threshold": 1 - callout, "load": load,
            "wait_added_per_hour_min": max(0.0, load - 1) * 60,
            "hours_to_4h_wait": 4 / (load - 1) if load > 1 else float("inf")}


# ---------------------------------------------------------------- 2. simulation
def sim_line(busy, steady=False, n=200_000, reps=12, seed=7, servers=1):
    """Average minutes waiting in line, simulated customer by customer.
    servers > 1 means one shared line feeding that many baristas."""
    rng = np.random.default_rng(seed)
    lam = servers * busy * MU
    means = []
    for _ in range(reps):
        gaps = rng.exponential(1 / lam, n)
        drinks = np.full(n, DRINK_MIN) if steady else rng.exponential(DRINK_MIN, n)
        free = [0.0] * servers          # when each barista is next free
        t, waits = 0.0, np.empty(n)
        for i in range(n):
            t += gaps[i]
            k = min(range(servers), key=free.__getitem__)
            start = max(t, free[k])
            waits[i] = start - t
            free[k] = start + drinks[i]
        means.append(waits[n // 10:].mean())   # drop the warm-up tenth
    return float(np.mean(means))


def sim_priority(busy, share_first=1 - MOBILE_SHARE, n=200_000, reps=8, seed=11):
    """Cafe first, mobile waits, one barista. Returns average line waits."""
    import heapq
    rng = np.random.default_rng(seed)
    lam = busy * MU
    out = {"cafe": [], "mobile": []}
    for _ in range(reps):
        arr = np.cumsum(rng.exponential(1 / lam, n))
        kind = rng.random(n) < share_first          # True = cafe
        drinks = rng.exponential(DRINK_MIN, n)
        cafe_q, mob_q = [], []
        i, now = 0, 0.0
        w = {"cafe": [], "mobile": []}
        while i < n or cafe_q or mob_q:
            while i < n and arr[i] <= now:
                (cafe_q if kind[i] else mob_q).append(i); i += 1
            if not cafe_q and not mob_q:
                now = arr[i]; continue
            j = cafe_q.pop(0) if cafe_q else mob_q.pop(0)
            w["cafe" if kind[j] else "mobile"].append(now - arr[j])
            now += drinks[j]
        for k in out:
            v = np.array(w[k]); out[k].append(v[len(v) // 10:].mean())
    return {k: float(np.mean(v)) for k, v in out.items()}


def sim_overload_hours(normal_busy, hours=12, callout=CALLOUT, seed=3, lanes_capacity_per_hr=600):
    """Random arrivals and screenings through a rush after a capacity cut.
    Returns the wait (minutes) a newly arriving traveller faces at the end."""
    rng = np.random.default_rng(seed)
    cap = lanes_capacity_per_hr * (1 - callout)
    lam = lanes_capacity_per_hr * normal_busy
    q = 0.0
    for _ in range(hours * 60):
        q = max(0.0, q + rng.poisson(lam / 60) - rng.poisson(cap / 60))
    return q / cap * 60


# ---------------------------------------------------------------- 3. brute force
def chain_line(busy, servers=1, size=4000):
    """Solve the birth-death Markov chain numerically (no queueing formula)."""
    lam = servers * busy * MU
    p = np.zeros(size + 1); p[0] = 1.0
    for k in range(size):                 # balance across each cut: p[k] lam = p[k+1] rate
        p[k + 1] = p[k] * lam / (min(k + 1, servers) * MU)
    p /= p.sum()
    in_line = np.maximum(np.arange(size + 1) - servers, 0)
    return float((in_line * p).sum() / lam)   # Little's Law: line wait = people in line / arrival rate


def embedded_chain_line_steady(busy, size=3000):
    """Steady drinks: number left behind at each departure, solved as a Markov chain."""
    lam = busy * MU
    a = lam * DRINK_MIN
    # chance of j arrivals during one 2-minute drink (Poisson), built without overflow
    arrivals = np.array([math.exp(-a + j * math.log(a) - math.lgamma(j + 1)) for j in range(size + 1)])
    pi = np.zeros(size + 1); pi[0] = 1.0
    # pi[j+1] from the balance equations of the M/D/1 embedded chain (standard recursion)
    for j in range(size):
        s = pi[j] - pi[0] * arrivals[j] - sum(pi[i] * arrivals[j - i + 1] for i in range(1, j + 1))
        pi[j + 1] = max(s, 0.0) / arrivals[0]
        if j > 60 and pi[j + 1] < 1e-14:
            break
    pi /= pi.sum()
    in_system = (np.arange(size + 1) * pi).sum()
    return float(in_system / lam - DRINK_MIN)


def fluid_overload(normal_busy, hours, callout=CALLOUT):
    """Step minute by minute with no randomness: brute-force check of the overload rule."""
    cap, lam, q = 1 - callout, normal_busy, 0.0
    for _ in range(int(hours * 60)):
        q = max(0.0, q + (lam - cap) / 60)
    return q / cap * 60


# ---------------------------------------------------------------- the numbers
def numbers():
    """Every number quoted anywhere, from the formulas (checked by check_math.py)."""
    n = {f"mm1_{int(b*100)}": mm1(b) for b in BUSY_LEVELS}
    n["steady_line_90"] = md1_line(0.9)
    n["pooled_two_baristas_line_90"] = mmc_line(2, 0.9)
    n["pooled_two_baristas_line_80"] = mmc_line(2, 0.8)
    n["spare_minutes_per_hour_80"] = (1 - 0.8) * 60
    n["spare_minutes_per_hour_90"] = (1 - 0.9) * 60
    n["line_wait_ratio_80_to_90"] = (0.9 / 0.1) / (0.8 / 0.2)     # any drink-time pattern
    n["priority_90"] = priority_lines(0.9)
    n["houston"] = overload(ILLUSTRATIVE_NORMAL_BUSY)
    n["houston_drain_spare_share"] = 1 - ILLUSTRATIVE_NORMAL_BUSY
    return n


if __name__ == "__main__":
    for k, v in numbers().items():
        print(k, v)
