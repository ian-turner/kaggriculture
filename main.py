"""Kaggriculture submission agent.

Baseline: the documented wheat loop — buy a wheat seed, plant it, water it,
harvest at maturity, sell, repeat. A starting point to iterate on.

Submission contract (from the competition docs):
- File must be named main.py with an `agent(obs)` function at module top level.
- On Kaggle, files are unpacked to /kaggle_simulations/agent/ — keep any
  multi-file imports relative to that path.
- Runtime limits: 1.6 vCPUs, 6.5 GiB RAM, 100 MiB submission size.
"""

WHEAT_FIRST_YIELD_DAY = 2


def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    fx, fy = me["farmer"]
    tile = me["tiles"][fy][fx]

    market = []

    # Keep one wheat seed queued up.
    if private["seeds"].get("WHEAT", 0) == 0 and me["money"] >= 10:
        market.append(["BUY_SEED", "WHEAT", 1])

    # Sell any wheat sitting in the shed.
    wheat_in_shed = private["shed"].get("WHEAT", 0)
    if wheat_in_shed > 0:
        market.append(["SELL", "WHEAT", wheat_in_shed])

    # Standing on an empty tile: plant.
    if tile is None and private["seeds"].get("WHEAT", 0) > 0:
        return {"farmer": ["PLANT", "WHEAT"], "hands": [], "market": market}

    # Standing on a plant: harvest if mature, else water.
    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
        crop_age = obs["day"] - tile["planted_day"]
        if crop_age >= WHEAT_FIRST_YIELD_DAY:
            return {"farmer": ["HARVEST"], "hands": [], "market": market}
        if not tile["watered_today"]:
            return {"farmer": ["WATER"], "hands": [], "market": market}

    return {"farmer": ["PASS"], "hands": [], "market": market}
