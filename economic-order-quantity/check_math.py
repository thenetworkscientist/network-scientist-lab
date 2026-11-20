"""Three-way check: formula, simulation, brute force. Prints 'All checks passed.'"""
import numpy as np
from eoq_model import (rolls_per_year, eoq, annual_cost, cost_ratio, simulate,
                       brute_force, PACK)

ok = True
def check(name, cond):
    global ok
    print(f"{'PASS' if cond else 'FAIL'}  {name}")
    ok &= bool(cond)

# 1. Formula vs brute force over the formula cost, households of 1 to 5
for p in range(1, 6):
    D = rolls_per_year(p)
    check(f"brute-force best Q within 1 roll of Q* (household of {p})",
          abs(brute_force(D) - eoq(D)) <= 1)

# 2. Simulation vs formula, household of 2, across pack sizes
D = rolls_per_year(2)
for q in (10, 20, 30, 50, 70):
    f, s = annual_cost(q, D), simulate(q, D, years=500)
    check(f"simulated cost within 2% of formula at Q={q}", abs(s / f - 1) < 0.02)

# 3. Brute force over the SIMULATED cost lands near the formula's Q*
qs = range(20, 56)
sim_costs = {q: simulate(q, D, years=300, seed=11) for q in qs}
q_sim = min(sim_costs, key=sim_costs.get)
check(f"simulated best Q ({q_sim}) within 3 rolls of Q* ({eoq(D):.1f})",
      abs(q_sim - eoq(D)) <= 3)

# 4. Honest numbers (input-free)
check("2x ideal costs 25% more", np.isclose(cost_ratio(2, 1), 1.25))
check("0.5x ideal costs 25% more", np.isclose(cost_ratio(0.5, 1), 1.25))
check("1.5x ideal costs about 8.3% more", np.isclose(cost_ratio(1.5, 1), 1 + 1 / 12))

# 5. Story numbers
up = 425 / 380
check("rolls used up 11.8% when sheets drop 425 -> 380", round((up - 1) * 100, 1) == 11.8)
check("ideal pack up 5.8%", round((np.sqrt(up) - 1) * 100, 1) == 5.8)

D4 = rolls_per_year(4)
check("double use: best pack for two about 52", round(eoq(D4)) == 52)
check("double use: 30-pack costs about 15% more", round((cost_ratio(30, eoq(D4)) - 1) * 100) == 15)

D2 = rolls_per_year(2)
check("receipt 37: trips $9.09, shelf $9.25, total $18.34",
      (round(5 * D2 / 37, 2), round(0.5 * 37 / 2, 2), round(annual_cost(37, D2), 2)) == (9.09, 9.25, 18.34))
check("receipt 30: trips $11.21, shelf $7.50, total $18.71, +2%",
      (round(5 * D2 / 30, 2), round(0.5 * 30 / 2, 2), round(annual_cost(30, D2), 2)) == (11.21, 7.5, 18.71)
      and round((annual_cost(30, D2) / annual_cost(37, D2) - 1) * 100) == 2)

print("\nAll checks passed." if ok else "\nSOME CHECKS FAILED.")
