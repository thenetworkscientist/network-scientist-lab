"""Cross-checks the math three independent ways for every scenario in the article:
   1) closed-form formulas, 2) Monte Carlo simulation, 3) brute-force search for the best Q in the simulation.
   Run: python check_math.py   (prints a table and fails loudly if anything disagrees)"""
import numpy as np
from newsvendor import critical_ratio, best_quantity, expected_outcomes, simulate

SCENARIOS = [  # name, price, cost, salvage, sd
    ("Base case ($4 price)", 4.0, 1.0, 0.0, 20.0),
    ("Low margin ($1.50)", 1.5, 1.0, 0.0, 20.0),
    ("High margin ($10)", 10.0, 1.0, 0.0, 20.0),
    ("Leftovers sold at $0.50", 4.0, 1.0, 0.5, 20.0),
    ("Better forecast (sd 10)", 4.0, 1.0, 0.0, 10.0),
]

def brute_force_best_q(price, cost, salvage, sd, days=400_000, seed=2):
    d = np.random.default_rng(seed).normal(100, sd, days)
    qs = np.arange(60, 160.01, 0.5)
    prof = [(price * np.minimum(d, q) + salvage * np.maximum(q - d, 0) - cost * q).mean() for q in qs]
    return qs[int(np.argmax(prof))]

if __name__ == "__main__":
    print(f"{'scenario':<26}{'ratio':>7}{'Q* formula':>12}{'Q* search':>11}{'profit formula':>16}{'profit sim':>12}{'leftovers':>11}{'missed':>8}")
    for name, p, c, s, sd in SCENARIOS:
        cr = critical_ratio(p, c, s)
        q = best_quantity(p, c, s, 100, sd)
        f = expected_outcomes(q, p, c, s, 100, sd)
        m = simulate(q, p, c, s, 100, sd)
        qb = brute_force_best_q(p, c, s, sd)
        print(f"{name:<26}{cr:>7.1%}{q:>12.1f}{qb:>11.1f}{f['profit']:>16.2f}{m['profit']:>12.2f}{f['leftover']:>11.1f}{f['missed']:>8.1f}")
        assert abs(f["profit"] - m["profit"]) / f["profit"] < 0.01, "formula and simulation disagree on profit"
        assert abs(f["leftover"] - m["leftover"]) < 0.3 and abs(f["missed"] - m["missed"]) < 0.3, "leftovers or missed sales disagree"
        assert abs(f["p_leftover"] - cr) < 1e-9, "P(leftover) should equal the critical ratio at Q*"
        assert abs(qb - q) <= 2.0, "brute-force search found a different best Q"
    base_avg = expected_outcomes(100, 4, 1, 0, 100, 20)
    base_best = expected_outcomes(best_quantity(4, 1), 4, 1, 0, 100, 20)
    sd10 = expected_outcomes(best_quantity(4, 1, 0, 100, 10), 4, 1, 0, 100, 10)
    assert abs(sd10["mismatch"] - base_best["mismatch"] / 2) < 1e-9, "mismatch cost should be proportional to sd"
    print(f"\nBaking the average instead of Q*: ${base_best['profit'] - base_avg['profit']:.2f} less profit per day "
          f"(${(base_best['profit'] - base_avg['profit']) * 365:,.0f} a year).")
    print(f"Halving the uncertainty halves the mismatch cost: ${base_best['mismatch']:.2f} -> ${sd10['mismatch']:.2f} a day.")
    print("All checks passed.")
