from __future__ import annotations

import argparse

from app.scheduler.runner import run_once, run_scheduler


def main() -> None:
    parser = argparse.ArgumentParser(description="AI savings tracker")
    parser.add_argument("command", choices=["run-once", "schedule", "dashboard"], help="run mode")
    args = parser.parse_args()

    if args.command == "run-once":
        digest = run_once()
        print(digest.summary())
    elif args.command == "schedule":
        run_scheduler()
    else:
        try:
            from app.ui.dashboard import run_dashboard

            run_dashboard()
        except ModuleNotFoundError:
            from app.ui.tk_dashboard import run_tk_dashboard

            print("[INFO] streamlit 미설치: tkinter 대시보드로 실행합니다.")
            run_tk_dashboard()


if __name__ == "__main__":
    main()
