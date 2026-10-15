"""
The bullwhip effect, simulated.

Four companies in a chain: shoppers -> store -> distributor -> factory.
Each company forecasts demand with a moving average of the orders it receives,
keeps an order-up-to level of (lead time x forecast), and orders whatever brings
it back to that level. Nobody does anything irrational. The swings still grow.

Run:   python bullwhip.py                      # reproduces the numbers in the video
       python bullwhip.py --lead-time 4        # try a longer lead time
       python bullwhip.py --share-data         # every company forecasts from real shopper sales
       python bullwhip.py --no-sale            # plain random demand, no promotion

Model follows Chen, Drezner, Ryan & Simchi-Levi (2000), Management Science 46(3).
"""
import argparse
import numpy as np


def shopper_demand(weeks=140, mean=100, sd=10, sale=True, seed=34):
    """Weekly shopper demand. Optional 2-week sale (+35%) followed by 3 quieter weeks (-15%)."""
    rng = np.random.default_rng(seed)
    d = rng.normal(mean, sd, weeks)
    if sale:
        d[62:64] *= 1.35      # sale weeks: people stock up
        d[64:67] *= 0.85      # after the sale: pantries are full
    return d


def orders_from(incoming, lead_time=2, window=4, forecast_from=None):
    """One company's weekly orders.

    incoming       orders this company receives from its customer
    forecast_from  what it forecasts from. Default: the orders it sees (no data sharing).
                   Pass the shopper demand to simulate shared point-of-sale data.
    """
    signal = incoming if forecast_from is None else forecast_from
    q = np.zeros(len(incoming))
    level_prev = None
    for t in range(len(incoming)):
        if t < window:
            q[t] = incoming[t]
            continue
        level = lead_time * signal[t - window + 1:t + 1].mean()           # order-up-to level
        if level_prev is None:
            level_prev = lead_time * signal[t - window:t].mean()
        q[t] = max(0.0, level - level_prev + incoming[t])                  # refill + cover the change
        level_prev = level
    return q


def run_chain(demand, tiers=3, lead_time=2, window=4, share_data=False):
    """Returns an array: row 0 = shoppers, then store, distributor, factory orders."""
    rows, incoming = [demand], demand
    for _ in range(tiers):
        incoming = orders_from(incoming, lead_time, window, forecast_from=demand if share_data else None)
        rows.append(incoming)
    return np.array(rows)


def swing(rows, start=40, end=92):
    """How much wilder each tier is than shoppers: std(orders) / std(shopper demand), over the shown weeks."""
    s = rows[:, start:end]
    return s.std(axis=1) / s[0].std()


def chen_bound(lead_time, window):
    """Lower bound on Var(orders)/Var(demand) for one company (Chen et al. 2000)."""
    L, p = lead_time, window
    return 1 + 2 * L / p + 2 * L ** 2 / p ** 2


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Simulate the bullwhip effect.")
    ap.add_argument("--lead-time", type=int, default=2)
    ap.add_argument("--window", type=int, default=4, help="weeks in the moving-average forecast")
    ap.add_argument("--share-data", action="store_true")
    ap.add_argument("--no-sale", action="store_true")
    ap.add_argument("--seed", type=int, default=34)
    a = ap.parse_args()

    demand = shopper_demand(sale=not a.no_sale, seed=a.seed)
    rows = run_chain(demand, lead_time=a.lead_time, window=a.window, share_data=a.share_data)
    r = swing(rows)
    names = ["Shoppers", "Store", "Distributor", "Factory"]
    print(f"lead time {a.lead_time} wk, {a.window}-wk moving average, "
          f"{'shared sales data' if a.share_data else 'each sees only its own orders'}, "
          f"{'no sale' if a.no_sale else '2-week sale'}")
    for n, x in zip(names, r):
        print(f"  {n:<12} {x:4.1f}x as wild as shoppers")
    print(f"  Chen et al. lower bound for one company (variance): {chen_bound(a.lead_time, a.window):.2f}x")
