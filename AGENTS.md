# AGENTS.md

Agent for the [Kaggriculture Kaggle competition](https://www.kaggle.com/competitions/kaggriculture):
a two-player farming simulation. Each side runs a farm for 720 turns (30 days ×
24 turns); most coins banked at the end wins. Matches are ladder-rated; top 10
places win $5,000. **Final submission deadline: Sept 30, 2026** (entry deadline
Sept 23, 11:59 PM UTC).

## Commands

```bash
uv sync                                          # install deps (Python 3.11 venv)
uv run python run_local.py                       # main.py vs "starter", full game (~1s)
uv run python run_local.py --opponent random --games 5
uv run python run_local.py --agent agents/x.py --opponent main.py --seed 42
uv run python run_local.py --replay              # dump replay JSON to replays/
uv run kaggle competitions submit kaggriculture -f main.py -m "msg"   # submit
uv run kaggle competitions submissions kaggriculture                  # status
```

Built-in opponents: `pass`, `random`, `starter` (deterministic baseline to beat).

## Layout & conventions

- `main.py` — the live submission agent. Kaggle requires this exact name with a
  top-level `agent(obs)` function.
- `agents/` — experimental variants. Develop here, benchmark vs `main.py` and
  `starter` with `run_local.py`, promote the winner by copying into `main.py`.
- `docs/game-reference.md` — condensed rules: crop/animal economics, market
  price curves, town demand, care rules, observation/action formats.
- `replays/`, `logs/` — gitignored output.

## Authoritative references (in the installed package)

The pip package ships the actual simulation — read the source to settle any
rules question; do not guess mechanics:

- `.venv/lib/python3.11/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py` — game engine
- Same dir: `AGENTS.md` (env getting-started guide), `README.md` (full rules,
  all tables), `kaggriculture.json` (config defaults).

## Known state / results

- `main.py` is the naive single-tile wheat loop (baseline from the docs).
  Benchmarks: beats `random` (3375 vs 0), loses to `starter` (3393 vs 3536).
  It ignores fertilizer, animals, hands, land purchases, and market timing —
  all open headroom.
- Full 720-step games run in <1s locally, so benchmark with multiple games and
  seeds before calling a change an improvement.

## Gotchas (verified from the rules)

- A new seed starts at `consecutive_unwatered = 1`: water the same day it is
  planted or it becomes a weed overnight. No grace period.
- Unsold inventory is worth nothing at game end — sell before turn 720.
- Only latest 2 Kaggle submissions stay active and count for final eval;
  5 submissions/day max, 100 MiB size cap, 1.6 vCPU / 6.5 GiB RAM at runtime.
- On Kaggle, submission files unpack to `/kaggle_simulations/agent/` — for
  multi-file agents, make imports work from that path, bundle with
  `tar -czf submission.tar.gz main.py ...` (main.py at archive root).
- Selling dumps crash premium prices (strawberry/melon/milk/wool hit the $1
  floor fast); wheat and eggs absorb volume. See the price table in
  `docs/game-reference.md`.
- `obs` config values (board size, shed capacity, etc.) are configurable per
  episode — read them from the observation/config rather than hardcoding.

## Prerequisites for submitting (manual, user's Kaggle account)

1. "Join Competition" clicked on the competition page (accepts rules).
2. API token saved at `~/.kaggle/access_token` (chmod 600).
Verify with: `uv run kaggle competitions list --group entered` — if this fails,
ask the user to complete the two steps above; do not attempt them on their behalf.
