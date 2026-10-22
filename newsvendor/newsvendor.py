"""
The newsvendor problem: how much to make when demand is uncertain and you only get one shot.

A bakery bakes Q donuts in the morning. Daily demand D is uncertain.
Each costs c to make, sells for p, and any leftover is worth s at closing (0 = thrown away).

    Cu = p - c      cost of one missed sale (profit you didn't make)
    Co = c - s      cost of one leftover (money spent on something nobody bought)

Best amount to bake (Arrow, Harris & Marschak, 1951):

    P(D <= Q*) = Cu / (Cu + Co)          the "critical ratio"

If demand is normal with mean mu and standard deviation sigma:  Q* = mu + z * sigma,
where z is the standard normal value whose cumulative probability equals the critical ratio.

Run:  python newsvendor.py                         base case: $1 cost, $4 price, demand ~ 100 +/- 20
      python newsvendor.py --price 10              high margin
      python newsvendor.py --salvage 0.5           sell leftovers at closing for $0.50
      python newsvendor.py --sd 10                 a better forecast (half the uncertainty)
"""
import argparse
from statistics import NormalDist
import numpy as np

STD = NormalDist()  # standard normal


def critical_ratio(price, cost, salvage=0.0):
    cu, co = price - cost, cost - salvage
    return cu / (cu + co)


def best_quantity(price, cost, salvage=0.0, mean=100.0, sd=20.0):
    """Q* for normally distributed demand."""
    return mean + STD.inv_cdf(critical_ratio(price, cost, salvage)) * sd


def loss_function(z):
    """Standard normal loss function L(z) = E[max(Z - z, 0)] = phi(z) - z * (1 - Phi(z))."""
    return STD.pdf(z) - z * (1 - STD.cdf(z))


def expected_outcomes(q, price, cost, salvage=0.0, mean=100.0, sd=20.0):
    """Exact expected results of baking q, using the normal formulas (no simulation)."""
    z = (q - mean) / sd
    missed = sd * loss_function(z)                 # E[max(D - q, 0)]
    leftover = (q - mean) + missed                 # E[max(q - D, 0)]
    cu, co = price - cost, cost - salvage
    mismatch = co * leftover + cu * missed         # what uncertainty costs you
    return dict(q=q, missed=missed, leftover=leftover, p_leftover=STD.cdf(z),
                mismatch=mismatch, profit=cu * mean - mismatch)


def simulate(q, price, cost, salvage=0.0, mean=100.0, sd=20.0, days=400_000, seed=1):
    """The same quantities, estimated by simulating many days."""
    d = np.random.default_rng(seed).normal(mean, sd, days)
    sold, left = np.minimum(d, q), np.maximum(q - d, 0)
    return dict(q=q, missed=np.maximum(d - q, 0).mean(), leftover=left.mean(), p_leftover=(left > 0).mean(),
                profit=(price * sold + salvage * left - cost * q).mean())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Newsvendor: how many to bake?")
    ap.add_argument("--price", type=float, default=4.0)
    ap.add_argument("--cost", type=float, default=1.0)
    ap.add_argument("--salvage", type=float, default=0.0)
    ap.add_argument("--mean", type=float, default=100.0)
    ap.add_argument("--sd", type=float, default=20.0)
    a = ap.parse_args()
    cr = critical_ratio(a.price, a.cost, a.salvage)
    qs = best_quantity(a.price, a.cost, a.salvage, a.mean, a.sd)
    print(f"Critical ratio: {cr:.1%}   ->   bake about {qs:.1f}  (average demand {a.mean:.0f})")
    for label, q in [("bake the average", a.mean), ("bake Q*", qs)]:
        f = expected_outcomes(q, a.price, a.cost, a.salvage, a.mean, a.sd)
        s = simulate(q, a.price, a.cost, a.salvage, a.mean, a.sd)
        print(f"  {label:<17} profit/day ${f['profit']:7.2f} (simulated ${s['profit']:7.2f})   "
              f"leftovers {f['leftover']:5.1f}   missed sales {f['missed']:5.1f}   days with leftovers {f['p_leftover']:.0%}")
