"""Run local Kaggriculture episodes: main.py vs a chosen opponent.

Usage:
    uv run python run_local.py                     # main.py vs starter, full game
    uv run python run_local.py --opponent random   # vs built-in random agent
    uv run python run_local.py --steps 200         # shorter episode
    uv run python run_local.py --games 5           # best-of series
    uv run python run_local.py --replay            # dump replay JSON to replays/

Built-in opponents: pass, random, starter. Any .py agent path also works.
"""

import argparse
import json
import time
from pathlib import Path

from kaggle_environments import make


def run_game(agent_path: str, opponent: str, steps: int, seed: int | None, debug: bool):
    config = {"episodeSteps": steps}
    if seed is not None:
        config["seed"] = seed
    env = make("kaggriculture", configuration=config, debug=debug)
    env.run([agent_path, opponent])
    rewards = [s.reward for s in env.steps[-1]]
    statuses = [s.status for s in env.steps[-1]]
    return env, rewards, statuses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", default="main.py", help="path to our agent (default main.py)")
    parser.add_argument("--opponent", default="starter", help="pass | random | starter | path/to/agent.py")
    parser.add_argument("--steps", type=int, default=720, help="episode steps (default 720 = full season)")
    parser.add_argument("--games", type=int, default=1, help="number of games to run")
    parser.add_argument("--seed", type=int, default=None, help="episode seed for reproducibility")
    parser.add_argument("--replay", action="store_true", help="save replay JSON to replays/")
    parser.add_argument("--quiet", action="store_true", help="disable env debug logging")
    args = parser.parse_args()

    wins = losses = ties = 0
    for game in range(args.games):
        seed = args.seed if args.seed is not None else None
        start = time.time()
        env, rewards, statuses = run_game(args.agent, args.opponent, args.steps, seed, not args.quiet)
        elapsed = time.time() - start

        us, them = rewards[0], rewards[1]
        if us is None or statuses[0] == "ERROR":
            outcome = "ERROR"
            losses += 1
        elif us > them:
            outcome = "WIN"
            wins += 1
        elif us < them:
            outcome = "LOSS"
            losses += 1
        else:
            outcome = "TIE"
            ties += 1

        print(
            f"game {game + 1}/{args.games}: {outcome}  "
            f"us={us} vs {args.opponent}={them}  "
            f"statuses={statuses}  ({elapsed:.1f}s)"
        )

        if args.replay:
            replay_dir = Path(__file__).parent / "replays"
            replay_dir.mkdir(exist_ok=True)
            stamp = time.strftime("%Y%m%d-%H%M%S")
            out = replay_dir / f"replay-{stamp}-g{game + 1}.json"
            out.write_text(json.dumps(env.toJSON()))
            print(f"  replay -> {out}")

    if args.games > 1:
        print(f"\nrecord vs {args.opponent}: {wins}W-{losses}L-{ties}T")


if __name__ == "__main__":
    main()
