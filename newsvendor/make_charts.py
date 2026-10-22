"""Draws the three charts used in the README and the Medium article."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from newsvendor import best_quantity, expected_outcomes, simulate, critical_ratio

BLUE, GREEN, OCHRE, CORAL, GREY = "#1F8FD1", "#2E9E4F", "#C98F00", "#E2603A", "#888"
plt.rcParams.update({"text.usetex": False, "axes.formatter.use_mathtext": False, "font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": GREY})

# 1. profit vs how many you bake
qs = np.arange(60, 161)
prof = [expected_outcomes(q, 4, 1)["profit"] for q in qs]
sim_q = np.arange(70, 156, 10)
sim_p = [simulate(q, 4, 1, days=200_000)["profit"] for q in sim_q]
qstar = best_quantity(4, 1)
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.plot(qs, prof, color=CORAL, lw=2.5, label="Expected profit (formula)")
ax.plot(sim_q, sim_p, "o", color="#333", ms=5, label="Simulation (200,000 days each)")
for q, lab, col in [(100, "bake the average: 100", GREY), (qstar, f"best: {qstar:.0f}", CORAL)]:
    ax.axvline(q, color=col, ls=":" if q == 100 else "-", lw=1.4)
    ax.text(q + (1 if q > 100 else -1), 281, lab, color=col, fontsize=10, ha="left" if q > 100 else "right")
ax.set_ylim(200, 290)
ax.set_xlabel("donuts baked per day")
ax.set_ylabel("expected profit per day (\\$)")
ax.set_title("The best amount to bake is above average demand", loc="left", weight="bold")
ax.legend(frameon=False, loc="lower center")
fig.text(0.01, 0.01, "Demand ~ normal(100, 20). Cost \\$1, price \\$4, leftovers worth \\$0.", fontsize=8, color="#666")
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("fig1_profit_curve.png", dpi=160)

# 2. margins decide how much extra
prices = np.linspace(1.25, 12, 120)
qq = [best_quantity(p, 1) for p in prices]
fig, ax = plt.subplots(figsize=(8, 4.6))
ax.plot(prices, qq, color=BLUE, lw=2.5)
ax.axhline(100, color=GREY, ls=":", lw=1.2); ax.text(11.9, 101.5, "average demand", ha="right", color=GREY, fontsize=9)
for p in (1.5, 4, 10):
    q = best_quantity(p, 1); ax.plot(p, q, "o", color=CORAL)
    ax.text(p + 0.15, q - 4, f"\\${p:.2f}: bake {q:.0f}", fontsize=10)
ax.set_xlabel("selling price (\\$), cost fixed at \\$1")
ax.set_ylabel("best amount to bake")
ax.set_title("The bigger the margin, the more you should overstock", loc="left", weight="bold")
fig.tight_layout(); fig.savefig("fig2_margin.png", dpi=160)

# 3. two ways to "fix" leftovers
cases = [("Base case", 4, 1, 0.0, 20), ("Sell leftovers\nat \\$0.50", 4, 1, 0.5, 20), ("Better forecast\n(half the swings)", 4, 1, 0.0, 10)]
res = [expected_outcomes(best_quantity(p, c, s, 100, sd), p, c, s, 100, sd) for _, p, c, s, sd in cases]
fig, axes = plt.subplots(1, 2, figsize=(9, 4.4))
names = [n for n, *_ in cases]
for ax, key, title, col in [(axes[0], "leftover", "Leftovers per day", OCHRE), (axes[1], "profit", "Profit per day (\\$)", GREEN)]:
    vals = [r[key] for r in res]
    ax.bar(names, vals, color=[GREY, col, col], width=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v * 1.01, f"{v:.1f}" if key == "leftover" else f"\\${v:.0f}", ha="center", fontsize=10)
    ax.set_title(title, loc="left", weight="bold", fontsize=11)
fig.suptitle("Cheaper leftovers mean more leftovers. Better forecasts mean fewer.", x=0.01, ha="left", weight="bold")
fig.tight_layout(); fig.savefig("fig3_two_fixes.png", dpi=160)
print("charts done")
