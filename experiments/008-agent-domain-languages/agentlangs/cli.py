"""CLI: run the full 6x6 sub-experiment matrix and emit JSON or text."""

from __future__ import annotations

import argparse
import json
import sys

from . import harness


def build_report():
    results = harness.run_all()
    failed = [r for r in results if r["status"] != "pass"]
    return {
        "experiment": "008-agent-domain-languages",
        "matrix": {"languages": 6, "subexperiments_per_language": 6, "total": len(results)},
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "results": results,
    }


def render_text(report):
    out = []
    out.append(f"experiment {report['experiment']}: {report['passed']}/{report['matrix']['total']} sub-experiments pass")
    out.append("")
    for r in report["results"]:
        out.append(f"[{r['status']}] {r['language']:3s} {r['subexperiment']} {r['name']}: {r['detail']}")
    out.append("")
    out.append("scorecards (criterion: score/3, basis):")
    for r in report["results"]:
        if r["subexperiment"] == 6:
            lang = r["language"]
            out.append(f"  {lang}:")
            for card in r["data"]:
                out.append(f"    {card['criterion']}: {card['score']}/3 ({card['basis']})")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="agentlangs", description=__doc__)
    parser.add_argument(
        "--format", choices=("json", "text"), default="text",
        help="output format (default: text)",
    )
    parser.add_argument(
        "--out", default=None,
        help="write output to this file instead of stdout",
    )
    parser.add_argument(
        "--language", default=None, choices=sorted(harness.LANGUAGES),
        help="restrict the matrix to one language",
    )
    args = parser.parse_args(argv)

    if args.language:
        results = [
            harness.run_subexperiment(args.language, n) for n in range(1, 7)
        ]
        failed = [r for r in results if r["status"] != "pass"]
        report = {
            "experiment": "008-agent-domain-languages",
            "matrix": {"languages": 1, "subexperiments_per_language": 6, "total": len(results)},
            "passed": len(results) - len(failed),
            "failed": len(failed),
            "results": results,
        }
    else:
        report = build_report()

    if args.format == "json":
        text = json.dumps(report, indent=2, sort_keys=True)
    else:
        text = render_text(report)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)
    return 1 if report["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
