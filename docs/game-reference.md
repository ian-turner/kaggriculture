# Kaggriculture game reference

Condensed from the competition Overview page (2026-08-17). The authoritative
source is the simulation code shipped in the pip package:
`kaggle_environments/envs/kaggriculture/kaggriculture.py` (plus `AGENTS.md` and
`README.md` in the same directory).

## Game shape

- 2 players, separate farms, 720 turns = 30 days × 24 turns/day.
- Win = most coins in the bank at the end. Unsold inventory counts for nothing.
- Start: $3,000, one unlocked 5×5 quadrant of a 10×10 board, farmer at the shed.
- Each turn: one action per farmer/hand + up to 10 market orders.
- Buy neighboring quadrants for $1k / $2k / $4k.

## Economy of each object

| Type | Yield | Seed cost | Base price | First yield | Max yield day | Repeat | Max yield | Yield/tile/day |
|---|---|---|---|---|---|---|---|---|
| Wheat | one-time | 10 | 25 | day 2 | day 4 | — | 6 (4 unfert.) | 0.80 |
| Carrot | one-time | 20 | 35 | day 2 | day 3 | — | 4 (3 unfert.) | 0.75 |
| Tomato | ongoing | 50 | 60 | day 8 | day 11 | daily ×4 | 4 | 0.33 |
| Strawberry | ongoing | 100 | 120 | day 10 | day 16 | every 2d ×4 | 4 | 0.24 |
| Melon | one-time | 80 | 250 | day 10 | day 10 | — | 6 | 0.55 |
| Goose→egg | ongoing | 300 | 50 | day 4 | — | daily, forever | 4 held | 1.00 |
| Cow→milk | ongoing | 400 | 160 | day 8 | — | every 2d, forever | 6 held | 0.50 |
| Sheep→wool | ongoing | 500 | 200 | day 6 | — | every 3d, forever | 6 held | 0.33 |
| Fertilizer | — | buy 100 | sell 100 base | — | — | — | — | — |

Notes:
- Animals need a structure first: BUILD_COOP (goose) or BUILD_PASTURE (cow/sheep), 1 extra action.
- Animal "max yield" is a cap on unharvested product on the tile, not lifetime.
- Melon hits its cap of 6 at age 10 watered (age 8 fertilized).
- Tomato/strawberry decay into weeds after their 4 scheduled yields fire (harvested or not).
- One-time crops decay starting one day after max_yield_day — harvest on time.

## Care rules (miss these and you lose the asset)

- Plants: water once/day. 2 consecutive unwatered days → weed. **A new seed
  starts at consecutive_unwatered = 1** — plant and water the same day or it
  weeds overnight. No grace period.
- Animals: feed wheat once/day. 2 consecutive unfed days → escapes (lost).
  Newly placed animals start at 0 (survive first day unfed).
- CARE (once/day): if fed+cared that day, banks +1 bonus, paid out on the next
  scheduled production (only if fed that day; unfed production day wipes the bank).
- FERTILIZE: doubles the per-day yield bonus for the next 3 days, only on days
  the plant is also watered.
- Every surviving animal offers 1 fertilizer/day (COLLECT_FERTILIZER); doesn't
  accumulate.

## Yield mechanics

- One-time crops (wheat/carrot/melon): from ceil(max_yield_day / 2), each watered
  day in the bonus window adds +1 to harvestable yield (+2 if fertilized).
- Ongoing crops (tomato/strawberry): base 1 per scheduled production; 2 if
  fertilized AND watered that day.

## Actions

Per farmer/hand each turn (they can share tiles):
- Movement: NORTH/SOUTH/EAST/WEST. Locked tiles are passable but actions no-op on them.
- PLANT <crop> (consumes shared seed pool; simultaneous over-planting → none plant),
  WATER, HARVEST, FERTILIZE, DIG (clear plant/weed/empty structure).
- BUILD_COOP, BUILD_PASTURE.
- PLACE <animal> (standing on matching empty structure), FEED, CARE, COLLECT_FERTILIZER.
- Shed (from the 4 center tiles, works even while the tile is locked):
  PICKUP <item> [n], DROP (dump whole inventory), PLACE <item> [n] into shed.
- PASS.

Market orders (up to 10/turn, processed in order, one unit at a time interleaved
with the opponent):
- BUY_SEED <crop> n, BUY_ANIMAL <animal> n — unlimited supply, fixed price.
- BUY_PRODUCT — only WHEAT and FERTILIZER are buyable back.
- SELL <item> n — any product incl. fertilizer.
- HIRE — farm hand for the day, cost = fib sequence 1,1,2,3,5,8,13… resets daily.
- BUY_LAND — next quadrant: $1k, $2k, $4k.

## Logistics

- Shed at board center, accessed from the 4 center tiles (4,4),(5,4),(4,5),(5,5);
  only the NW one starts unlocked. Capacity 100 non-seed items; overflow discarded.
- Farmer + hands spawn at the shed each day, auto-drop inventory into the shed at
  end of day (overflow lost). Hands disappear at end of day.
- First hire of the day spawns at (5,4) (locked until NE bought, but passable).
- Weeds spawn on empty unlocked tiles at 0.5%/tile/day; DIG to clear.

## Market pricing

Each product: price(inv) = base ± amp·f(|inv − 10000|), floored at $1, rounded
to $. Buying/scarcity (town demand) pushes prices up; selling pushes down.
Asymmetric shapes per resource:

| Resource | Base | T | Scarcity side | Glut side | P(−T) | P(+T) | P(+2T) |
|---|---|---|---|---|---|---|---|
| Wheat | 25 | 400 | sqrt 0.80 | log 0.20 | $45 | $20 | $19 |
| Carrot | 35 | 450 | hinge 1.00 | sqrt 0.70 | $70 | $10 | $1 |
| Tomato | 60 | 200 | hinge 0.40 | sqrt 0.60 | $84 | $24 | $9 |
| Strawberry | 120 | 100 | sqrt 0.70 | linear 1.60 | $204 | $1 | $1 |
| Melon | 250 | 300 | log 0.20 | sq 3.60 | $300 | $1 | $1 |
| Egg | 50 | 332 | hinge 0.40 | log 0.20 | $70 | $40 | $39 |
| Milk | 160 | 122 | sqrt 0.60 | linear 1.60 | $256 | $1 | $1 |
| Wool | 200 | 105 | log 0.20 | sq 3.20 | $240 | $1 | $1 |
| Fertilizer | 100 | 200 | linear 0.40 | linear 0.40 | $140 | $60 | $20 |

Strategic reads:
- Premium goods (strawberry, melon, milk, wool) crash to $1 on modest gluts —
  time and bundle sales; don't dump.
- Wheat/egg absorb gluts well — safe volume plays.
- Carrot/tomato/egg spike hard under scarcity (hinge) once town demand outruns T.
- Buy price is quoted post-buy, sell price pre-sell → immediate buy-then-sell
  round-trips net exactly zero.

## Town demand (drains market inventory → raises prices)

- Town center: 1 of every product (except fertilizer) per day, flat all season.
- Shops unlock every 3 days (uniform random with replacement, max 8 instances,
  permanent). Each instance consumes 1 of each demanded product every 4 turns
  (= 6/day); single-product shops consume double.

| Shop | Demands |
|---|---|
| Bakery | eggs, wheat |
| Pizza Shop | milk, tomatoes, wheat |
| Brunch Spot | eggs, wheat, strawberries |
| Yarn Store | wool ×2 |
| Ice Cream Shop | strawberries, milk, wheat |
| Pet Cafe | carrots ×2 |
| Smoothie Shop | strawberries, milk |
| Farmers Market | wheat, carrots, tomatoes, strawberries |

Watch `obs["town"]["unlocked_shops"]` and shift production toward demanded goods.

## Turn processing order

1. Action validation → 2. player actions (simultaneous) → 3. market orders →
4. town consumption → 5. observation update → 6. day refresh (care flags reset,
weed/escape checks) → 7. market price refresh → 8. income update → 9. farm update.

## Observation (per turn)

```
obs = {
  "player": 0|1, "day": int, "hour": int,
  "farms": [farm, farm],            # public: money, tiles[y][x], farmer, hands,
                                    # unlocked_quadrants, hires_today
  "market": {"inventory": {...}, "prices": {...}},
  "town": {"unlocked_shops": [...]},
  "private": {"shed": {...}, "seeds": {...}, "inventories": [farmer_inv, ...]},
}
```

Tile values: `None` (empty), `"LOCKED"`, plant dict (crop, planted_day,
watered_today, consecutive_unwatered, yield_units, max_lifespan_step,
fertilized_until_day), weed dict, or structure dict (kind COOP/PASTURE, animal,
fed_today, consecutive_unfed, cared_today, fertilizer_available,
pending_care_bonus, yield_units).

Action return format:
```python
{"farmer": ["PLANT", "WHEAT"], "hands": [["WATER"], ...], "market": [["SELL", "WHEAT", 5], ...]}
```

## Submission constraints

- main.py at archive root, `agent(obs)` entry point; files land in
  /kaggle_simulations/agent/.
- ≤100 MiB, 1.6 vCPUs, 6.5 GiB RAM, 8 GiB disk.
- 5 submissions/day, latest 2 active + used for final eval.
- Validation episode (self-play) must not error.
- Config knobs (episodeSteps=720, boardSize=10, startingMoney=3000,
  shedCapacity=100, weedSpawnChance=0.005, ...) — don't hardcode board size etc.
