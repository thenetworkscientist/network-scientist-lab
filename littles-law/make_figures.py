"""Draws the four charts used in the article and README. Run: python make_figures.py"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import poisson
import littles_law as m

INK, CORAL, BLUE, YELLOW, GREY = "#1d2433", "#e8664f", "#3b7dd8", "#f2b632", "#9aa3b2"
plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})
FOOT = "SIMULATED · 20 admissions/day · 5-day average stay · Poisson arrivals · The Network Scientist"

r = m.run(verbose=False)

# fig1: the daily headcount wobbles around 100; 117 beds covers 95% of days
cen = r["shapes"]["exponential"]["census"]
fig, ax = plt.subplots(figsize=(9, 5.2))
bins = np.arange(cen.min(), cen.max() + 2) - 0.5
ax.hist(cen, bins=bins, density=True, color=BLUE, alpha=0.55, label="Simulated midnight headcount")
k = np.arange(60, 141)
ax.plot(k, poisson.pmf(k, 100), color=INK, lw=2, label="Formula: Poisson, mean 100")
ax.axvline(100, color=GREY, ls="--", lw=2); ax.text(101.5, ax.get_ylim()[1]*0.55, "average 100\n(Little's Law)", color=INK)
ax.axvline(117, color=CORAL, lw=3); ax.text(118, ax.get_ylim()[1]*0.75, "117 beds:\nenough on\n95% of days", color=CORAL)
ax.set_xlabel("Patients in the hospital at midnight"); ax.set_ylabel("Share of days")
ax.set_title("The average is 100. The beds you need are 117.")
ax.legend(loc="upper left", frameon=False); fig.text(0.01, 0.01, FOOT, fontsize=8, color=GREY)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("fig1_census.png", dpi=160); plt.close(fig)

# fig2: three very different stay shapes, same headcount (insensitivity)
fig, ax = plt.subplots(figsize=(9, 5.2))
for kind, col in [("exponential", BLUE), ("lognormal", CORAL), ("fixed", YELLOW)]:
    c = r["shapes"][kind]["census"]; vals, cnt = np.unique(c, return_counts=True)
    ax.plot(vals, cnt / cnt.sum(), color=col, lw=2.2,
            label=f"{kind} stays: L = {r['shapes'][kind]['L']:.1f}")
ax.plot(k, poisson.pmf(k, 100), color=INK, ls=":", lw=2, label="Poisson(100) formula")
ax.set_xlim(65, 135); ax.set_xlabel("Patients in the hospital at midnight"); ax.set_ylabel("Share of days")
ax.set_title("Different stay lengths, same 100 patients: L = λ × W")
ax.legend(frameon=False); fig.text(0.01, 0.01, FOOT, fontsize=8, color=GREY)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("fig2_insensitivity.png", dpi=160); plt.close(fig)

# fig3: bigger hospitals can run fuller
a = np.arange(5, 1001, 5); occ = [x / m.beds_formula(x) for x in a]
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(a, np.array(occ) * 100, color=BLUE, lw=2.5)
ax.axhline(85, color=GREY, ls="--"); ax.text(830, 86, "the 85% rule", color=GREY)
for x, col in [(20, CORAL), (100, INK), (500, CORAL)]:
    b, o = r["size"][x]; ax.scatter([x], [o * 100], color=col, s=70, zorder=3)
    ax.annotate(f"{x} patients: {b} beds, {o:.0%}", (x, o * 100), textcoords="offset points", xytext=(10, -18), color=col)
ax.set_xscale("log"); ax.set_xlabel("Average patients in the hospital (log scale)")
ax.set_ylabel("Safe average occupancy (%)"); ax.set_title("Same 95% target, different safe occupancy")
fig.text(0.01, 0.01, FOOT, fontsize=8, color=GREY)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("fig3_size_effect.png", dpi=160); plt.close(fig)

# fig4: cut the beds, patients board in the ER
cs = np.arange(102, 126)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(cs, [m.erlang_c(100, c) * 100 for c in cs], color=BLUE, lw=2.5, label="Share of patients who wait (Erlang C)")
ax.plot(cs, [m.mean_wait_if_waiting_hours(100, c) for c in cs], color=CORAL, lw=2.5, label="Average wait of those who wait, hours")
for c, w in r["whatif"].items():
    ax.scatter([c], [w["p_wait_sim"] * 100], color=BLUE, edgecolor=INK, s=60, zorder=3)
    ax.scatter([c], [w["wait_sim"]], color=CORAL, edgecolor=INK, s=60, zorder=3)
ax.axvline(117, color=GREY, ls="--"); ax.text(117.3, 30, "117 beds", color=GREY)
ax.axvline(105, color=GREY, ls="--"); ax.text(105.3, 30, "105 beds", color=GREY)
ax.set_xlabel("Beds"); ax.set_ylabel("Percent  /  hours"); ax.set_ylim(0, 60)
ax.set_title("Cut a few beds and the ER fills up (dots: simulation)")
ax.legend(frameon=False, loc="upper right"); fig.text(0.01, 0.01, FOOT, fontsize=8, color=GREY)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig("fig4_boarding.png", dpi=160); plt.close(fig)
print("Saved fig1_census.png, fig2_insensitivity.png, fig3_size_effect.png, fig4_boarding.png")
