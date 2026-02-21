from __future__ import annotations

import subprocess
import sys


def main() -> None:
    # streamlit이 없으면 app.main dashboard에서 tkinter로 자동 fallback
    cmd = [sys.executable, "-m", "app.main", "dashboard"]
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
