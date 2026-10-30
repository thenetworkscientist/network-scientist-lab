"""Draws the three charts used in the article and README."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from risk_pooling import (N_COMPANIES, LAM, V_LINK, INDEPENDENT, LINKED,
                          spares_formula, normal_saving)

CORAL, BLUE, YELLOW, INK, GREY = "#E8735A", "#3A7BD5", "#E0A82E", "#1B2230", "#8A93A3"
plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK, "text.color": INK})
FOOT = f"SIMULATED · {N_COMPANIES} companies, {LAM} expected failures each per lead time, 95% coverage"

# fig1: own vs shared
fig, ax = plt.subplots(figsize=(8, 5))
labels = ["Each keeps its own", "Shared pool", "Shared pool,\nbad days linked"]
vals = [INDEPENDENT["separate_total"], INDEPENDENT["pooled"], LINKED["pooled"]]
bars = ax.bar(labels, vals, color=[GREY, BLUE, CORAL], width=0.6)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.6, str(v), ha="center", fontsize=16, fontweight="bold")
ax.set_ylabel("Spare transformers needed")
ax.set_title("Same protection, far fewer spares", loc="left", fontweight="bold")
ax.set_ylim(0, 38)
fig.text(0.01, 0.01, FOOT, fontsize=8, color=GREY)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("fig1_own_vs_shared.png", dpi=160)

# fig2: savings as the pool grows (exact formula; simulation agrees, see check_math.py)
ns = np.arange(1, 65)
def saving(n, v):
    return 100 * (1 - spares_formula(n * LAM, v) / (n * spares_formula(LAM, v)))
fig, ax = plt.subplots(figsize=(8, 5))
ax.step(ns, [saving(n, 0) for n in ns], where="mid", color=BLUE, lw=2.5, label="Failures unrelated")
ax.step(ns, [saving(n, V_LINK) for n in ns], where="mid", color=CORAL, lw=2.5,
        label="Failures linked (correlation 0.2)")
ax.axvline(N_COMPANIES, color=GREY, ls=":")
ax.text(N_COMPANIES + 1, 5, "16 companies", color=GREY)
ax.set_xlabel("Companies sharing one pool")
ax.set_ylabel("Spares saved vs. each keeping its own (%)")
ax.set_title("The bigger the pool, the bigger the saving, unless bad days line up",
             loc="left", fontweight="bold", fontsize=12)
ax.set_ylim(0, 100); ax.legend(frameon=False, loc="upper left")
fig.text(0.01, 0.01, f"FORMULA, checked by simulation · {LAM} expected failures per company per lead time, 95% coverage", fontsize=8, color=GREY)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("fig2_pool_size.png", dpi=160)

# fig3: general rule and its ceiling
n = np.arange(1, 101)
fig, ax = plt.subplots(figsize=(8, 5))
for rho, c in [(0, BLUE), (0.2, CORAL), (0.5, YELLOW), (1, GREY)]:
    ax.plot(n, 100 * normal_saving(n, rho), color=c, lw=2.5, label=f"correlation {rho}")
    if 0 < rho < 1:
        ax.axhline(100 * (1 - np.sqrt(rho)), color=c, ls=":", lw=1)
ax.text(70, 57, "ceiling 55%", color=CORAL)
ax.text(70, 31, "ceiling 29%", color=YELLOW)
ax.set_xlabel("Locations pooled")
ax.set_ylabel("Safety stock cushion saved (%)")
ax.set_title("Linked demand puts a ceiling on pooling", loc="left", fontweight="bold")
ax.set_ylim(0, 100); ax.legend(frameon=False, loc="upper left")
fig.text(0.01, 0.01, "FORMULA · Eppen (1979), identical locations, bell-curve demand", fontsize=8, color=GREY)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig("fig3_correlation_ceiling.png", dpi=160)
print("Saved fig1_own_vs_shared.png, fig2_pool_size.png, fig3_correlation_ceiling.png")
