from __future__ import annotations

import argparse

from app.scheduler.runner import run_once, run_scheduler


def main() -> None:
    parser = argparse.ArgumentParser(description="AI savings tracker")
    parser.add_argument("command", choices=["run-once", "schedule"], help="run mode")
    args = parser.parse_args()

    if args.command == "run-once":
        digest = run_once()
        print(digest.summary())
    else:
        run_scheduler()


if __name__ == "__main__":
    main()
