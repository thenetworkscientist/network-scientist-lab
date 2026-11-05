"""Checks every number used in the video and article, three ways where it applies:
formula, discrete-event simulation, brute force. Run: python check_math.py"""
import math
import numpy as np
from scipy.stats import poisson
import littles_law as m

fails = []
def check(name, ok):
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok: fails.append(name)

r = m.run(reps=6, days=15_000, verbose=False)

# Little's Law
check("L = 20 x 5 = 100", m.L_AVG == 100)
for k, s in r["shapes"].items():
    check(f"simulated L close to 100 ({k}: {s['L']:.2f})", abs(s["L"] - 100) < 1.0)
    check(f"Little's Law inside the simulation: L == lambda*W ({k})", abs(s["L"] - s["lamW"]) < 0.5)
    check(f"census variance close to mean, so Poisson ({k}: {s['var']:.1f})", abs(s["var"] - 100) < 6)

# Headline: 117 beds, three ways
check("formula: 117 beds", r["beds_formula"] == 117)
check("formula: P(N<=116) < 0.95 <= P(N<=117)", poisson.cdf(116, 100) < 0.95 <= poisson.cdf(117, 100))
for k, s in r["shapes"].items():
    check(f"brute force on simulated census: 117 ({k})", s["beds_bruteforce"] == 117)
check("occupancy 85.5%", round(r["occupancy"] * 100, 1) == 85.5)

# Size effect and the extra day
check("20 -> 28 beds (71%)", r["size"][20][0] == 28 and round(r["size"][20][1] * 100) == 71)
check("500 -> 537 beds (93%)", r["size"][500][0] == 537 and round(r["size"][500][1] * 100) == 93)
check("one extra day: 120 in use, 138 beds (+21)", r["plus_one_day"] == (120, 138))
check("weekday pattern leaves the answer at 117", r["weekday"]["beds"] == 117)

# What-if: boarding, formula vs simulation
w = r["whatif"]
check("105 beds: about half wait (formula 51.6%)", round(w[105]["p_wait_formula"] * 100, 1) == 51.6)
check("105 beds: simulated share waiting within 3 points", abs(w[105]["p_wait_sim"] - w[105]["p_wait_formula"]) < 0.03)
check("105 beds: those who wait, wait about a day (formula 24.0 h)", round(w[105]["wait_formula"], 1) == 24.0)
check("105 beds: simulated wait within 4 h of formula", abs(w[105]["wait_sim"] - 24.0) < 4)
check("105 beds, lognormal stays: still about half wait, about a day (18-26 h)",
      0.45 < w[105]["p_wait_lognormal"] < 0.58 and 16 < w[105]["wait_lognormal"] < 28)
check("110 beds: 24% wait, 12 h", round(w[110]["p_wait_formula"] * 100) == 24 and round(w[110]["wait_formula"]) == 12)
check("117 beds: 6% wait, 7 h", round(w[117]["p_wait_formula"] * 100) == 6 and round(w[117]["wait_formula"]) == 7)
check("110 beds: 17% wait 4h+, 3% wait 24h+",
      round(w[110]["over4_formula"] * 100) == 17 and round(w[110]["over24_formula"] * 100) == 3)

# Red Sea: ships on a loop = sailings per day x round-trip days
extra_round_trip_days, sailing_every_days = 14.4, 7
check("Red Sea: 14.4 extra days / weekly sailing = about 2 more ships per loop",
      round(extra_round_trip_days / sailing_every_days) == 2)

print()
print("All checks passed." if not fails else f"{len(fails)} check(s) FAILED.")
