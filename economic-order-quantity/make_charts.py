"""Draft charts for review (final styling happens in the topic pack)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from eoq_model import rolls_per_year, eoq, annual_cost, simulate, PACK

BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1f1f1e", "#6b6a64", "#e4e3dd"
plt.rcParams.update({"font.size": 12, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False})
FOOT = "SIMULATED · illustrative trip cost \\$5, storage \\$0.50 per roll per year"

# 1. The flat-bottomed cost curve, household of 2
D = rolls_per_year(2); Qs = eoq(D)
q = np.linspace(5, 100, 400)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(q, annual_cost(q, D), color=BLUE, lw=2)
sq = np.arange(10, 101, 10)
ax.scatter(sq, [simulate(x, D, years=300) for x in sq], s=40, color=BLUE,
           edgecolor="white", linewidth=2, zorder=3, label="simulated")
ax.axvline(Qs, color=MUTED, lw=1, ls=":")
ax.annotate(f"ideal: {Qs:.0f} rolls", (Qs, annual_cost(Qs, D)), (Qs + 3, 34), color=INK)
ax.scatter([PACK], [annual_cost(PACK, D)], s=90, color=ORANGE, edgecolor="white", linewidth=2, zorder=4)
ax.annotate("the 30-pack: 2% more", (PACK, annual_cost(PACK, D)), (12, 26), color=INK,
            arrowprops=dict(arrowstyle="-", color=MUTED))
ax.set(xlabel="Rolls bought per trip", ylabel="Trips + closet space, $ per year", ylim=(0, 40))
ax.grid(axis="y", color=GRID); ax.legend(frameon=False, loc="upper right")
ax.set_title("A two-person home: the bottom of the curve is wide and flat", loc="left", color=INK)
fig.text(0.01, 0.01, FOOT, fontsize=9, color=MUTED); fig.tight_layout(rect=(0, .03, 1, 1))
fig.savefig("fig1_cost_curve.png", dpi=160); plt.close(fig)

# 2. Ideal pack vs household size (the square root)
people = np.arange(1, 6)
ideal = [eoq(rolls_per_year(p)) for p in people]
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.bar(people, ideal, width=0.55, color=BLUE)
for p, v in zip(people, ideal):
    ax.text(p, v + 1, f"{v:.0f}", ha="center", color=INK)
ax.axhline(PACK, color=ORANGE, lw=2); ax.text(0.55, PACK + 1, "30-pack", color=INK, ha="left")
ax.set(xlabel="People in the home", ylabel="Ideal rolls per trip", ylim=(0, 68), xticks=people)
ax.grid(axis="y", color=GRID)
ax.set_title("5 times the use, only 2.2 times the pack", loc="left", color=INK)
fig.text(0.01, 0.01, FOOT, fontsize=9, color=MUTED); fig.tight_layout(rect=(0, .03, 1, 1))
fig.savefig("fig2_square_root.png", dpi=160); plt.close(fig)

# 3. Two stories, two moved inputs
fig, axs = plt.subplots(1, 2, figsize=(10, 5.2))
a = axs[0]
a.bar(["Rolls used\nper year", "Ideal pack"], [11.8, 5.8], width=0.5, color=[BLUE, ORANGE])
for i, v in enumerate([11.8, 5.8]): a.text(i, v + .3, f"+{v}%", ha="center", color=INK)
a.set(ylim=(0, 15), title="Rolls shrink 425 to 380 sheets"); a.grid(axis="y", color=GRID)
b = axs[1]
k = np.array([1, 4, 10, 100])
b.bar([f"x{x}" for x in k], 100 / np.sqrt(k), width=0.5, color=BLUE)
for i, v in enumerate(100 / np.sqrt(k)): b.text(i, v + 2, f"{v:.0f}%", ha="center", color=INK)
b.set(ylim=(0, 115), xlabel="Storage cost multiplied by", ylabel="Ideal pack, % of original",
      title="Storage gets expensive (food goes stale)"); b.grid(axis="y", color=GRID)
fig.text(0.01, 0.01, "SIMULATED · square-root rule; same inputs as the other charts",
         fontsize=9, color=MUTED); fig.tight_layout(rect=(0, .03, 1, 1))
fig.savefig("fig3_two_stories.png", dpi=160); plt.close(fig)
print("charts written")
