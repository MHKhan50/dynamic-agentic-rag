import argparse
import json
from .experiment import run_experiment


def main():
    parser = argparse.ArgumentParser(description="Run the DAR-RB synthetic benchmark")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run all baseline policies")
    run.add_argument("--episodes", type=int, default=2000, help="episodes per seed")
    run.add_argument("--seeds", type=int, nargs="+", default=[17, 29, 43, 71, 101])
    run.add_argument("--out", default="results")
    args = parser.parse_args()
    if args.episodes < 1:
        parser.error("--episodes must be >= 1")
    result = run_experiment(args.episodes, args.seeds, args.out)
    print(json.dumps(result, indent=2))
    print(f"\nWrote results to: {args.out}")

if __name__ == "__main__":
    main()
