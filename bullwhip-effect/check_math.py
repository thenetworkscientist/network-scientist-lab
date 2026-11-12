"""Checks every number quoted in the video and article. Run: python check_math.py  (ends with "All checks passed.")

"""
import numpy as np
from bullwhip import shopper_demand, run_chain, swing, chen_bound, orders_from

ok = True
def check(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    ok &= bool(cond)

def factory_swing(lead_time, share_data=False, seeds=range(1, 31)):
    """Factory swing (std of orders / std of shopper demand), averaged over seeds, 2-week sale included."""
    return float(np.mean([swing(run_chain(shopper_demand(seed=s), lead_time=lead_time, share_data=share_data))[3]
                          for s in seeds]))

# 1. the default run (seed 34) quoted in the video: 1.6x, 2.8x, 4.7x
r = swing(run_chain(shopper_demand()))
check(f"seed 34: store {r[1]:.1f}x, distributor {r[2]:.1f}x, factory {r[3]:.1f}x", [round(x, 1) for x in r] == [1.0, 1.6, 2.8, 4.7])

# 2. factory swing averaged over 30 seeds, 2-week lead time
no_share, share = factory_swing(2), factory_swing(2, share_data=True)
check(f"30 seeds, lead time 2: {no_share:.2f} without data sharing (4.6)", round(no_share, 1) == 4.6)
check(f"30 seeds, lead time 2: {share:.2f} with shared shopper sales data (2.9)", round(share, 1) == 2.9)

# 3. lead time is the lever: 1 week -> about 2.3, 4 weeks -> about 11.0
l1, l4 = factory_swing(1), factory_swing(4)
check(f"30 seeds, lead time 1: {l1:.2f} (2.3)", round(l1, 1) == 2.3)
check(f"30 seeds, lead time 4: {l4:.2f} (11.0)", round(l4, 1) == 11.0)

# 4. one company, 20,000 weeks, lands on the Chen et al. (2000) formula (swing bars: sqrt of 1.625, 2.5, 5.0)
rng = np.random.default_rng(7)
d = rng.normal(100, 10, 20000)
for L in range(0, 7):
    sim = orders_from(d, lead_time=L, window=4)[1000:].var() / d[1000:].var()
    bound = chen_bound(L, 4)
    check(f"L={L}: simulated variance ratio {sim:.2f} vs formula {bound:.2f}", sim >= bound * 0.95 and abs(sim - bound) / bound < 0.15)
check("formula variance for L = 1, 2, 4 (p = 4): 1.625, 2.5, 5.0",
      [round(chen_bound(L, 4), 3) for L in (1, 2, 4)] == [1.625, 2.5, 5.0])
check("swing for L = 1, 2, 4: 1.275, 1.581, 2.236",
      [round(chen_bound(L, 4) ** .5, 3) for L in (1, 2, 4)] == [1.275, 1.581, 2.236])

print("\nAll checks passed." if ok else "\nSOME CHECKS FAILED.")
