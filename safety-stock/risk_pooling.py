"""
Why sharing spare parts beats hoarding them: risk pooling, simulated.
Companion code for The Network Scientist (video + Medium article).

The model
---------
16 power companies. While a replacement transformer is being built, each one
expects LAM = 0.5 transformer failures on average (illustrative, not sourced).
Each wants to be covered COVERAGE = 95% of the time.

Question: how many spares do they need if each keeps its own,
versus one shared pool?

Two versions:
  * independent: one company's failures tell you nothing about another's
  * linked: a shared "bad stretch" factor G (average 1, variance V_LINK)
    multiplies every company's failure rate at once. With LAM = 0.5 and
    V_LINK = 0.5 the correlation between two companies is 0.2.

Every headline number is computed three ways:
  1. formula      exact Poisson / negative binomial quantiles
  2. simulation   many simulated lead times, coverage measured
  3. brute force  smallest whole number of spares that hits 95% in the simulation
"""
import numpy as np
from scipy.stats import poisson, nbinom, norm

N_COMPANIES = 16      # companies in the pool
LAM = 0.5             # expected failures per company during one replacement lead time
COVERAGE = 0.95       # share of lead times with no shortage
V_LINK = 0.5          # variance of the shared bad-stretch factor (linked version)
RUNS = 1_000_000      # simulated lead times
SEED = 2026


# ---------- 1. formula ----------
def spares_formula(mean, v=0.0, coverage=COVERAGE):
    """Smallest S with P(failures <= S) >= coverage.
    v = 0: Poisson(mean). v > 0: Poisson with a gamma-shared rate = negative binomial."""
    s = 0
    if v == 0:
        while poisson.cdf(s, mean) < coverage:
            s += 1
    else:
        r = 1.0 / v                      # gamma shape
        p = r / (r + mean)
        while nbinom.cdf(s, r, p) < coverage:
            s += 1
    return s


def correlation(lam=LAM, v=V_LINK):
    """Correlation between two companies' failure counts in the linked version."""
    return lam * v / (1 + lam * v)


# ---------- 2. simulation ----------
def simulate(n=N_COMPANIES, lam=LAM, v=0.0, runs=RUNS, seed=SEED):
    """Failure counts, shape (runs, n). Row = one lead time, column = one company."""
    rng = np.random.default_rng(seed)
    g = rng.gamma(1 / v, v, runs) if v > 0 else np.ones(runs)   # shared bad-stretch factor
    return rng.poisson(lam * g[:, None], (runs, n))


# ---------- 3. brute force ----------
def spares_brute_force(draws, coverage=COVERAGE):
    """Try S = 0, 1, 2, ... and keep the first that covers the target share of lead times."""
    s = 0
    while (draws <= s).mean() < coverage:
        s += 1
    return s


def headline(v=0.0, n=N_COMPANIES, lam=LAM):
    """All the numbers for one version. topic.py imports this (one source of truth)."""
    each = spares_formula(lam, v)
    pooled = spares_formula(n * lam, v)
    expected = n * lam                     # average failures the whole group must cover
    return {
        "each": each,
        "separate_total": n * each,
        "pooled": pooled,
        "expected_failures": expected,
        "safety_stock_separate": n * each - expected,   # spares above the average, separate yards
        "safety_stock_pooled": pooled - expected,       # spares above the average, shared yard
        "saving_pct": round(100 * (1 - pooled / (n * each))),
        "correlation": round(correlation(lam, v), 2) if v > 0 else 0.0,
    }


INDEPENDENT = headline(0.0)
LINKED = headline(V_LINK)


def normal_saving(n, rho):
    """General rule for a large, steady item (bell-curve demand): share of the
    safety-stock cushion saved by pooling n identical locations with correlation rho.
    Eppen (1979). As n grows, the saving approaches 1 - sqrt(rho)."""
    return 1 - np.sqrt(1 / n + (n - 1) * rho / n)


if __name__ == "__main__":
    print(f"{N_COMPANIES} companies, {LAM} expected failures each per lead time, "
          f"{COVERAGE:.0%} coverage\n")
    for name, v in [("Independent", 0.0), ("Linked (corr 0.2)", V_LINK)]:
        h = headline(v)
        d = simulate(v=v)
        bf_each, bf_pool = spares_brute_force(d[:, 0]), spares_brute_force(d.sum(1))
        cov_each, cov_pool = (d[:, 0] <= h["each"]).mean(), (d.sum(1) <= h["pooled"]).mean()
        print(f"{name}")
        print(f"  formula     : {h['each']} each, {h['separate_total']} separate, "
              f"{h['pooled']} pooled, saving {h['saving_pct']}%")
        print(f"  simulation  : coverage {cov_each:.2%} each, {cov_pool:.2%} pooled")
        print(f"  brute force : {bf_each} each, {N_COMPANIES*bf_each} separate, {bf_pool} pooled\n")

    print("Safety stock (spares above the average):")
    print(f"  average failures for all {N_COMPANIES}: {INDEPENDENT['expected_failures']:.0f}")
    print(f"  separate yards: {INDEPENDENT['separate_total']} - {INDEPENDENT['expected_failures']:.0f} = "
          f"{INDEPENDENT['safety_stock_separate']:.0f}; shared yard: {INDEPENDENT['pooled']} - "
          f"{INDEPENDENT['expected_failures']:.0f} = {INDEPENDENT['safety_stock_pooled']:.0f}")
    print(f"  one company, chance of 0 / 1 / 2 failures: "
          f"{poisson.pmf(0, LAM):.0%} / {poisson.pmf(1, LAM):.0%} / {poisson.pmf(2, LAM):.0%}\n")

    print("Why the square root: swings (standard deviation) of failures")
    print(f"  one company : mean {LAM}, swing {np.sqrt(LAM):.2f}")
    print(f"  pool of 16  : mean {N_COMPANIES*LAM:.0f}, swing {np.sqrt(N_COMPANIES*LAM):.2f} "
          f"(x{np.sqrt(N_COMPANIES):.0f}, not x16)")
    z = norm.ppf(COVERAGE)
    print(f"  bell-curve shortcut S = mean + z x swing, z = {z:.3f}: "
          f"{LAM + z*np.sqrt(LAM):.2f} -> {int(np.ceil(LAM + z*np.sqrt(LAM)))}, "
          f"{N_COMPANIES*LAM + z*np.sqrt(N_COMPANIES*LAM):.2f} -> "
          f"{int(np.ceil(N_COMPANIES*LAM + z*np.sqrt(N_COMPANIES*LAM)))}\n")

    print("Raising the bar to 99% coverage (independent):")
    print(f"  {spares_formula(LAM, coverage=0.99)} each = "
          f"{N_COMPANIES*spares_formula(LAM, coverage=0.99)} separate, "
          f"{spares_formula(N_COMPANIES*LAM, coverage=0.99)} pooled\n")

    print("General rule, cushion saved by pooling n locations (bell curve):")
    for rho in [0, 0.2, 0.5, 1]:
        row = ", ".join(f"n={k}: {100*normal_saving(k, rho):.0f}%" for k in [2, 4, 16, 64])
        print(f"  rho {rho}: {row}; ceiling {100*(1-np.sqrt(rho)):.0f}%")
