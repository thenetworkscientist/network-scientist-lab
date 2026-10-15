"""Draws the three charts used in the README and the Medium article."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from bullwhip import shopper_demand, run_chain, swing, chen_bound, orders_from

COL = ["#1F8FD1", "#2E9E4F", "#C98F00", "#E2603A"]
NAMES = ["Shoppers buy", "Store orders", "Distributor orders", "Factory orders"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#888", "axes.labelcolor": "#333",
                     "xtick.color": "#555", "ytick.color": "#555"})

# 1. the four tiers, same scale
rows = run_chain(shopper_demand())
r = swing(rows)
weeks = np.arange(52)
fig, axes = plt.subplots(4, 1, figsize=(8, 8), sharex=True, sharey=True)
for i, ax in enumerate(axes):
    ax.axvspan(22 - .5, 23 + .5, color="#B79CFF", alpha=.25, lw=0)
    ax.axvspan(24 - .5, 26 + .5, color="#B79CFF", alpha=.10, lw=0)
    ax.axhline(100, color="#999", lw=.8, ls=":")
    ax.plot(weeks, rows[i, 40:92], color=COL[i], lw=2)
    ax.set_title(f"{NAMES[i]}   ({r[i]:.1f}x as wild as shoppers)", loc="left", fontsize=11, color="#222")
    ax.set_ylim(0, 320)
axes[0].text(22.5, 285, "sale", ha="center", color="#6B4FD8", fontsize=9)
axes[-1].set_xlabel("week")
fig.supylabel("units per week")
fig.suptitle("Same shoppers, four very different order patterns", x=0.02, ha="left", fontsize=13, weight="bold")
fig.text(0.02, 0.005, "Simulated: demand ~100/wk (sd 10), 2-week sale, 4-week moving-average forecasts, 2-week lead time, seed 34",
         fontsize=8, color="#666")
fig.tight_layout(rect=(0, 0.02, 1, 0.97))
fig.savefig("fig1_four_tiers.png", dpi=160)

# 2. lead time is the lever (factory swing), with and without shared sales data
Ls = range(0, 7)
no_share = [np.mean([swing(run_chain(shopper_demand(seed=s), lead_time=L))[3] for s in range(1, 31)]) for L in Ls]
share = [np.mean([swing(run_chain(shopper_demand(seed=s), lead_time=L, share_data=True))[3] for s in range(1, 31)]) for L in Ls]
fig, ax = plt.subplots(figsize=(8, 4.6))
ax.plot(list(Ls), no_share, "-o", color=COL[3], lw=2.2, label="Each company sees only its own orders")
ax.plot(list(Ls), share, "-o", color=COL[0], lw=2.2, label="Everyone forecasts from real shopper sales")
ax.axhline(1, color="#999", lw=.8, ls=":")
ax.set_xlabel("lead time (weeks)")
ax.set_ylabel("factory swing vs shoppers (x)")
ax.set_title("Longer lead times make the factory wilder", loc="left", fontsize=12, weight="bold", pad=22)
ax.text(0, 1.02, "Sharing real sales data helps a lot, but does not erase it", transform=ax.transAxes, fontsize=10, color="#555")
ax.legend(frameon=False)
fig.text(0.01, 0.01, "Average of 30 simulated years per point, 2-week sale included, 4-week moving average", fontsize=8, color="#666")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("fig2_lead_time.png", dpi=160)

# 3. the math checks out: one company, long run, versus the Chen et al. lower bound
rng = np.random.default_rng(7)
d = rng.normal(100, 10, 20000)
Ls = np.arange(0, 7)
sim = [orders_from(d, lead_time=L, window=4)[1000:].var() / d[1000:].var() for L in Ls]
fine = np.linspace(0, 6, 100)
fig, ax = plt.subplots(figsize=(8, 4.6))
ax.plot(fine, [chen_bound(L, 4) for L in fine], color="#333", lw=1.5, label="Formula: 1 + 2L/p + 2L\u00b2/p\u00b2  (p = 4)")
ax.plot(Ls, sim, "o", color=COL[3], ms=8, label="Simulation (20,000 weeks)")
ax.set_xlabel("lead time L (weeks)")
ax.set_ylabel("variance of orders / variance of demand")
ax.set_title("One company, one formula: the simulation lands right on the math", loc="left", fontsize=11.5, weight="bold")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig("fig3_formula_check.png", dpi=160)
print("factory no-share", [round(x, 1) for x in no_share])
print("factory share   ", [round(x, 1) for x in share])
print("sim vs bound", [(int(L), round(s, 2), round(chen_bound(L, 4), 2)) for L, s in zip(Ls, sim)])
