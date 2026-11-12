"""Checks every quoted number three ways. Prints 'All checks passed.' or stops at the first failure."""
from queueing_model import *

def close(name, a, b, tol):
    ok = abs(a - b) <= tol * max(1.0, abs(b))
    print(f"{'ok ' if ok else 'FAIL'} {name}: {a:.3f} vs {b:.3f}")
    assert ok, name

# One barista: formula vs Markov chain (exact) vs simulation (2%)
for b in BUSY_LEVELS:
    f = mm1(b)["line_min"]
    close(f"line wait {b:.0%} formula vs chain", chain_line(b), f, 1e-6)
    close(f"line wait {b:.0%} formula vs simulation", sim_line(b, reps=6 if b < .95 else 16), f, 0.04 if b >= .95 else 0.02)
    close(f"total time {b:.0%} = line + drink", mm1(b)["total_min"], f + DRINK_MIN, 1e-9)

# The headline: total time doubles from 80% to 90%, and again to 95%
close("doubling 80 to 90", mm1(.9)["total_min"] / mm1(.8)["total_min"], 2.0, 1e-9)
close("doubling 90 to 95", mm1(.95)["total_min"] / mm1(.9)["total_min"], 2.0, 1e-9)

# Steady drinks: formula vs embedded Markov chain vs simulation
close("steady line 90% formula vs chain", embedded_chain_line_steady(.9), md1_line(.9), 1e-4)
close("steady line 90% formula vs simulation", sim_line(.9, steady=True, reps=6), md1_line(.9), 0.02)
close("2.25x line ratio holds for steady drinks", md1_line(.9) / md1_line(.8), 2.25, 1e-9)

# Two baristas sharing one line, each 90% busy
close("pooled 90% formula vs chain", chain_line(.9, servers=2), mmc_line(2, .9), 1e-6)
close("pooled 90% formula vs simulation", sim_line(.9, servers=2, reps=6), mmc_line(2, .9), 0.03)

# Cafe first, mobile waits: formula vs simulation, and the average does not move
p, s = priority_lines(.9), sim_priority(.9)
close("cafe line wait", s["cafe"], p["cafe"], 0.03)
close("mobile line wait", s["mobile"], p["mobile"], 0.05)
close("reordering keeps the average", p["average"], mm1(.9)["line_min"], 1e-9)

# Houston arithmetic: rule vs minute-by-minute steps vs random arrivals
h = overload(ILLUSTRATIVE_NORMAL_BUSY)
close("64% threshold", h["threshold"], 0.64, 1e-9)
close("overload rule vs stepping", fluid_overload(ILLUSTRATIVE_NORMAL_BUSY, 10), h["wait_added_per_hour_min"] * 10, 1e-6)
close("overload rule vs random arrivals", sim_overload_hours(ILLUSTRATIVE_NORMAL_BUSY, hours=10), h["wait_added_per_hour_min"] * 10, 0.05)

print("All checks passed.")
