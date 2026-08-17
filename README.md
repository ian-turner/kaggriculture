# Kaggriculture

Agent for the [Kaggriculture Kaggle competition](https://www.kaggle.com/competitions/kaggriculture) —
a head-to-head farming simulation. Two agents each run a farm for 720 turns
(24 turns/day × 30 days); whoever banks the most coins wins. Ladder play with
skill ratings; top 10 win $5,000 each.

**Key dates** (11:59 PM UTC): entry/team-merge deadline **Sept 23, 2026**,
final submission **Sept 30, 2026**, leaderboard finalizes ~Oct 15, 2026.

## Layout

| Path | Purpose |
|---|---|
| `main.py` | The submission agent (`agent(obs)` at top level — required name/entry point) |
| `run_local.py` | Local episode runner: our agent vs built-in or file opponents |
| `agents/` | Experimental agent variants before they're promoted to `main.py` |
| `replays/` | Replay JSONs from local runs (gitignored) |
| `docs/game-reference.md` | Condensed game mechanics from the competition page |

The full simulation source ships inside the pip package — read it to resolve any
rules question definitively:
`.venv/lib/python3.11/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`

## Setup

```bash
uv sync
```

### One-time Kaggle account setup (manual)

1. Sign in at kaggle.com, open the [competition page](https://www.kaggle.com/competitions/kaggriculture)
   and click **Join Competition** (accepts the rules — required before submitting).
2. Generate an API token at [kaggle.com/settings/api](https://www.kaggle.com/settings/api)
   ("Generate New Token"), then save it:

```bash
mkdir -p ~/.kaggle
# paste token into ~/.kaggle/access_token, then:
chmod 600 ~/.kaggle/access_token
```

Verify: `uv run kaggle competitions list --group entered`

## Local testing

```bash
uv run python run_local.py                      # full 720-step game vs built-in "starter"
uv run python run_local.py --opponent random --games 5
uv run python run_local.py --agent agents/experiment.py --opponent main.py
uv run python run_local.py --replay             # save replay JSON for the visualizer
uv run python run_local.py --html               # save interactive HTML visualizer (open in a browser)
```

Built-in opponents: `pass`, `random`, `starter` (deterministic baseline).

## Submitting

```bash
uv run kaggle competitions submit kaggriculture -f main.py -m "description"
uv run kaggle competitions submissions kaggriculture          # status; grab SUBMISSION_ID
uv run kaggle competitions episodes <SUBMISSION_ID>           # games played
uv run kaggle competitions replay <EPISODE_ID> -p replays/    # download a replay
uv run kaggle competitions logs <EPISODE_ID> 0 -p logs/       # agent stdout/stderr
uv run kaggle competitions leaderboard kaggriculture -s
```

Multi-file submission: `tar -czf submission.tar.gz main.py helper.py` (main.py at
archive root), then submit the tarball. On Kaggle the files land in
`/kaggle_simulations/agent/` — set import paths accordingly.

**Limits:** 5 submissions/day; only the latest 2 stay active (and count for final
evaluation); 100 MiB max; runtime 1.6 vCPUs / 6.5 GiB RAM / 8 GiB disk.

On upload, a validation episode runs your agent against itself — if it errors,
the submission is rejected (logs downloadable).
