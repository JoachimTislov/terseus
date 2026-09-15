"""Print a recalculated, weighted research progress report."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "research"


def main():
    intentions = json.load(open(ROOT / "intentions.json", encoding="utf-8"))["intentions"]
    snapshots = json.load(open(ROOT / "progress.json", encoding="utf-8"))["snapshots"]
    latest = snapshots[-1]["intention_status"] if snapshots else {}
    weights = {"open": 0.0, "partial": 0.5, "addressed": 1.0}
    total = sum(item["weight"] for item in intentions)
    earned = sum(item["weight"] * weights.get(latest.get(item["id"], "open"), 0.0) for item in intentions)
    print(f"Research coverage: {earned / total * 100:.1f}% ({earned:g}/{total:g} weighted points)")
    for item in intentions:
        status = latest.get(item["id"], "open")
        print(f"[{status:9}] {item['id']} {item['title']}")


if __name__ == "__main__":
    main()
