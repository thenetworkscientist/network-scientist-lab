"""Draws the four article charts. Run: python make_figures.py (the cover is make_cover.py)"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from queueing_model import *

PAPER, INK, MUTED, GRID = "#F5F6F8", "#1C2333", "#7D869A", "#E3E6EC"
CORAL, BLUE, YELLOW = "#F06A5C", "#3B7DD8", "#F2B33D"
plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"], "font.size": 12, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "axes.axisbelow": True, "figure.facecolor": PAPER, "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER,
})

def frame(title, sub, foot):
    fig = plt.figure(figsize=(8, 5.4), dpi=200)
    fig.text(0.06, 0.94, title, fontsize=17, fontweight="bold", va="top")
    fig.text(0.06, 0.875, sub, fontsize=11, color=MUTED, va="top")
    fig.text(0.06, 0.022, foot, fontsize=8.5, color=MUTED)
    fig.text(0.94, 0.022, "The Network Scientist", fontsize=8.5, color=MUTED, ha="right")
    return fig

# ---------------------------------------------------------------- fig 1: the hockey stick
fig = frame("The last few percent of busy cost the most waiting",
            "Minutes from joining the line to coffee in hand. One barista, 2 minutes a drink.",
            "SIMULATED · random arrivals and drink times · line: formula · dots: simulation")
ax = fig.add_axes([0.09, 0.17, 0.86, 0.66])
b = np.linspace(0.0, 0.97, 400)
ax.plot(b * 100, DRINK_MIN / (1 - b), color=INK, lw=2.6)
for x in (0.3, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95):
    ax.scatter(x * 100, sim_line(x, reps=3, n=150_000) + DRINK_MIN, s=34, color=BLUE, zorder=3, edgecolor=PAPER, lw=1.2)
for x, c, dx in ((0.8, BLUE, -16), (0.9, YELLOW, -17), (0.95, CORAL, -19)):
    t = mm1(x)["total_min"]
    ax.scatter(x * 100, t, s=150, color=c, zorder=4, edgecolor=INK, lw=1.2)
    ax.annotate(f"{x:.0%} busy\n{t:.0f} minutes", (x * 100, t), (x * 100 + dx, t + 4),
                fontsize=11, fontweight="bold", ha="center")
ax.set_xlim(0, 100); ax.set_ylim(0, 72)
ax.set_xlabel("How busy the barista is (%)"); ax.set_ylabel("Minutes")
fig.savefig("fig1_hockey_stick.png"); plt.close(fig)

# ---------------------------------------------------------------- fig 2: the same morning, a bit busier
fig = frame("Same morning, a little busier, a much longer line",
            "People waiting during one 4-hour morning. Same customers, same drinks, arrivals 12.5% faster.",
            "SIMULATED · one barista, 2 minutes a drink on average · one typical random morning")
ax = fig.add_axes([0.09, 0.17, 0.86, 0.66])
rng = np.random.default_rng(78)   # a typical morning: its averages match the long run (3.2 and 8.1 people)
u = rng.exponential(1.0, 400); s = rng.exponential(DRINK_MIN, 400)
for busy, c, lab in ((0.8, BLUE, "80% busy (24 an hour)"), (0.9, CORAL, "90% busy (27 an hour)")):
    arr = np.cumsum(u / (busy * MU)); free, starts = 0.0, []
    for a, d in zip(arr, s):
        st = max(a, free); starts.append(st); free = st + d
    starts = np.array(starts); grid = np.linspace(0, 240, 1200)
    waiting = [(np.sum(arr <= t) - np.sum(starts <= t)) for t in grid]
    ax.fill_between(grid / 60, waiting, step="post", color=c, alpha=0.18)
    ax.step(grid / 60, waiting, where="post", color=c, lw=2, label=lab)
ax.set_xlim(0, 4); ax.set_ylim(0, None)
ax.set_xlabel("Hours into the morning"); ax.set_ylabel("People in line")
ax.legend(frameon=False, loc="upper left", fontsize=11)
fig.savefig("fig2_same_morning.png"); plt.close(fig)

# ---------------------------------------------------------------- fig 3: fixes vs reordering
fig = frame("Spare time shrinks the line. Reordering only moves it.",
            "Minutes waiting in line, starting from one barista who is 90% busy.",
            "SIMULATED · cafe first: 70% cafe, 30% mobile, equal drink times")
ax = fig.add_axes([0.36, 0.17, 0.59, 0.66])
pr = priority_lines(0.9)
rows = [("As is: 90% busy", mm1(.9)["line_min"], MUTED),
        ("A little more help: 80% busy", mm1(.8)["line_min"], BLUE),
        ("Every drink exactly 2 minutes", md1_line(.9), BLUE),
        ("Cafe first: cafe customers", pr["cafe"], YELLOW),
        ("Cafe first: mobile customers", pr["mobile"], CORAL),
        ("Cafe first: everyone, on average", pr["average"], MUTED)]
y = np.arange(len(rows))[::-1]
for yi, (lab, v, c) in zip(y, rows):
    ax.barh(yi, v, color=c, height=0.62)
    ax.text(v + 0.8, yi, f"{v:.1f}", va="center", fontsize=11, fontweight="bold")
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=11, color=INK)
ax.axhline(2.5, color=GRID, lw=1.5); ax.grid(axis="y", visible=False)
ax.set_xlim(0, 56); ax.set_xlabel("Minutes in line")
fig.savefig("fig3_fixes.png"); plt.close(fig)

# ---------------------------------------------------------------- fig 4: past 100%
fig = frame("Past 100%, the line never settles",
            "Wait facing a new arrival after a checkpoint loses 36% of its screeners.",
            "SIMULATED · ILLUSTRATIVE · busy levels are assumptions, not airport data")
ax = fig.add_axes([0.09, 0.17, 0.86, 0.66])
hrs = np.linspace(0, 12, 200)
for nb, c in ((0.60, BLUE), (0.75, YELLOW), (0.90, CORAL)):
    o = overload(nb); y = np.maximum(0, o["load"] - 1) * 60 * hrs / 60
    ax.plot(hrs, y, color=c, lw=2.6, label=f"normally {nb:.0%} busy, now {o['load']:.0%}")
    for h in (3, 6, 9, 12):
        ax.scatter(h, sim_overload_hours(nb, hours=h) / 60, color=c, s=30, edgecolor=PAPER, zorder=3)
ax.axhline(4, color=MUTED, lw=1, ls=(0, (4, 4)))
ax.text(11.9, 4.12, "four hours", color=MUTED, fontsize=10, ha="right")
ax.set_xlim(0, 12); ax.set_ylim(0, 5.6)
ax.set_xlabel("Hours of rush"); ax.set_ylabel("Hours of waiting")
ax.legend(frameon=False, loc="upper left", fontsize=11)
fig.savefig("fig4_past_100.png"); plt.close(fig)

print("figures written")
