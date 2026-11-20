"""
Economic order quantity: how many rolls to bring home at once.

One household, one product (toilet paper). Every restock costs a fixed amount
(a trip: time and gas). Every roll in the closet costs a little each year (shelf
space). The economic order quantity (Harris, 1913) balances the two.

All cost inputs are ILLUSTRATIVE, not measured. What matters for the shape of
the answer is the ratio of trip cost to storage cost, and the honest number
(how much a "wrong" pack size costs) does not depend on the inputs at all.
"""
import numpy as np

# ---------------- inputs ----------------
SHEETS_PER_PERSON_PER_DAY = 35      # Cottonelle (manufacturer) estimate; flagged in sources.md
SHEETS_PER_ROLL = 380               # Kirkland Signature, costco.com
SHEETS_PER_ROLL_OLD = 425           # Kirkland before the change (US 2021, Canada spotted 2024)
PACK = 30                           # Kirkland Signature pack, costco.com
TRIP_COST = 5.00                    # $ per restock trip (illustrative: share of a trip's time and gas)
STORAGE_COST = 0.50                 # $ per roll per year of closet space (illustrative)


def rolls_per_year(people, sheets_per_roll=SHEETS_PER_ROLL):
    return people * SHEETS_PER_PERSON_PER_DAY * 365 / sheets_per_roll


def eoq(D, K=TRIP_COST, h=STORAGE_COST):
    """Harris's square-root formula: Q* = sqrt(2 K D / h)."""
    return np.sqrt(2 * K * D / h)


def annual_cost(Q, D, K=TRIP_COST, h=STORAGE_COST):
    """Trips per year x trip cost + average stock x storage cost."""
    return K * D / Q + h * Q / 2


def cost_ratio(Q, Qstar):
    """Cost of ordering Q relative to the best Q*: 1/2 (Q/Q* + Q*/Q). Input-free."""
    return 0.5 * (Q / Qstar + Qstar / Q)


def simulate(Q, D, years=2000, K=TRIP_COST, h=STORAGE_COST, seed=7):
    """Day-by-day closet. Daily use is random (Poisson around D/365 rolls).
    When the closet runs out, buy a pack of Q the same day.
    Returns average annual cost (trips + storage)."""
    rng = np.random.default_rng(seed)
    days = 365 * years
    use = rng.poisson(D / 365, size=days)
    stock, trips, roll_days = Q, 1, 0.0
    for u in use:
        need = u
        while need > 0:
            take = min(need, stock)
            stock -= take
            need -= take
            if stock == 0:
                stock = Q
                trips += 1
        roll_days += stock - 0.5 * u          # average level during the day (approx.)
    avg_stock = roll_days / days
    return (K * trips + h * avg_stock * days / 365) / years


def brute_force(D, K=TRIP_COST, h=STORAGE_COST, qs=range(4, 101)):
    costs = {q: annual_cost(q, D, K, h) for q in qs}
    return min(costs, key=costs.get)


if __name__ == "__main__":
    print(f"Inputs: trip ${TRIP_COST:.2f}, storage ${STORAGE_COST:.2f}/roll/yr, "
          f"{SHEETS_PER_PERSON_PER_DAY} sheets/person/day, {SHEETS_PER_ROLL} sheets/roll\n")
    print("people  rolls/yr  Q*(formula)  Q*(brute)  cost of 30 vs ideal  trips/yr at 30")
    for p in range(1, 6):
        D = rolls_per_year(p)
        Qs = eoq(D)
        print(f"{p:>6}  {D:8.1f}  {Qs:11.1f}  {brute_force(D):9d}  "
              f"{(cost_ratio(PACK, Qs) - 1) * 100:18.1f}%  {D / PACK:14.1f}")

    print("\nHonest number (input-free): cost of ordering a multiple of the ideal")
    for m in (0.5, 0.75, 1.5, 2, 3):
        print(f"  {m:>4} x ideal -> {(cost_ratio(m, 1) - 1) * 100:5.1f}% more")

    print("\nStory 1: rolls shrank 425 -> 380 sheets, pack stayed 30")
    up = SHEETS_PER_ROLL_OLD / SHEETS_PER_ROLL
    print(f"  rolls used go up {(up - 1) * 100:.1f}%, ideal pack goes up only {(np.sqrt(up) - 1) * 100:.1f}%")

    print("\nStory 2: storage gets expensive (food that goes stale)")
    for k in (4, 10, 100):
        print(f"  storage cost x{k:<3} -> ideal pack x{1 / np.sqrt(k):.2f}")

    print("\nSimulation vs formula, household of 2:")
    D = rolls_per_year(2)
    for q in (10, 20, 30, 37, 50, 70):
        f, s = annual_cost(q, D), simulate(q, D, years=500)
        print(f"  Q={q:>3}: formula ${f:6.2f}  simulated ${s:6.2f}  diff {(s / f - 1) * 100:+.1f}%")
