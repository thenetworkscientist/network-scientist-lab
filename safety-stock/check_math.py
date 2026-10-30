"""Checks every number used in the video and article, three ways."""
import numpy as np
from risk_pooling import (N_COMPANIES, LAM, V_LINK, INDEPENDENT, LINKED, simulate,
                          spares_brute_force, spares_formula, correlation, normal_saving)

ok = True
def check(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    ok &= bool(cond)

# Headline numbers (formula)
check("independent: 2 each, 32 separate, 13 pooled, 59% saved",
      (INDEPENDENT["each"], INDEPENDENT["separate_total"], INDEPENDENT["pooled"], INDEPENDENT["saving_pct"]) == (2, 32, 13, 59))
check("linked: 32 separate, 20 pooled, 38% saved",
      (LINKED["separate_total"], LINKED["pooled"], LINKED["saving_pct"]) == (32, 20, 38))
check("linked correlation is 0.2", abs(correlation() - 0.2) < 1e-12)

# Simulation and brute force agree with the formula
for label, v, h in [("independent", 0.0, INDEPENDENT), ("linked", V_LINK, LINKED)]:
    d = simulate(v=v)
    check(f"{label}: brute force each = formula", spares_brute_force(d[:, 0]) == h["each"])
    check(f"{label}: brute force pooled = formula", spares_brute_force(d.sum(1)) == h["pooled"])
    check(f"{label}: simulated pooled coverage >= 95%", (d.sum(1) <= h["pooled"]).mean() >= 0.95)
    check(f"{label}: one fewer pooled spare misses 95%", (d.sum(1) <= h["pooled"] - 1).mean() < 0.95)
    rho_sim = np.corrcoef(d[:, 0], d[:, 1])[0, 1]
    check(f"{label}: simulated correlation {rho_sim:.3f} matches", abs(rho_sim - (0.2 if v else 0)) < 0.01)

# Safety stock split spoken in Beat 6: 8 average, 24 vs 5 above it
check("average 8; safety stock 24 separate, 5 pooled",
      (INDEPENDENT["expected_failures"], INDEPENDENT["safety_stock_separate"], INDEPENDENT["safety_stock_pooled"]) == (8, 24, 5))
# Beat 4 wording: most of the time nothing, sometimes one, once in a while two
from scipy.stats import poisson
p0, p1, p2 = poisson.pmf([0, 1, 2], LAM)
check(f"one company: 0 failures {p0:.0%} (most), 1 {p1:.0%} (sometimes), 2 {p2:.0%} (once in a while)",
      p0 > 0.5 and 0.2 < p1 < 0.4 and p2 < 0.1)

# Square root of 16
check("pool swing is 4x one company's swing", abs(np.sqrt(N_COMPANIES*LAM) / np.sqrt(LAM) - 4) < 1e-12)
# 99% coverage
check("99%: 48 separate, 15 pooled", (N_COMPANIES*spares_formula(LAM, coverage=0.99), spares_formula(N_COMPANIES*LAM, coverage=0.99)) == (48, 15))
# General rule (bell curve), checked against simulation
check("rule: 16 locations save 75% (rho 0) and 50% (rho 0.2)",
      abs(normal_saving(16, 0) - 0.75) < 1e-12 and abs(normal_saving(16, 0.2) - 0.5) < 1e-12)
check("rule: ceiling at rho 0.2 is 55%", round(100 * (1 - np.sqrt(0.2))) == 55)
rng = np.random.default_rng(1)
x = np.sqrt(0.2) * rng.standard_normal(400_000)[:, None] + np.sqrt(0.8) * rng.standard_normal((400_000, 16))
cush_sep = 16 * np.quantile(x[:, 0], 0.95); cush_pool = np.quantile(x.sum(1), 0.95)
check(f"rule: simulated saving {100*(1-cush_pool/cush_sep):.1f}% ~ 50%", abs(1 - cush_pool/cush_sep - 0.5) < 0.01)

print("\nAll checks passed." if ok else "\nSOME CHECKS FAILED.")
