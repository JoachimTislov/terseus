"""CLI: run the full 6x6 sub-experiment matrix and emit JSON or text."""

from __future__ import annotations

import argparse
import json
import sys

from . import anl, harness


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
    subparsers = parser.add_subparsers(dest="command")
    agent_parser = subparsers.add_parser("agent", help="perform ANL agent CRUD")
    agent_parser.add_argument("operation", choices=("create", "read", "update", "delete"))
    agent_parser.add_argument("--file", required=True, help="ANL JSON document")
    agent_parser.add_argument("--id", required=True, help="agent identifier")
    agent_parser.add_argument("--type", dest="agent_type")
    agent_parser.add_argument("--capability", action="append", dest="capabilities")
    agent_parser.add_argument("--note")
    agent_parser.add_argument("--out", required=True, help="output JSON document")
    args = parser.parse_args(argv)

    if args.command == "agent":
        with open(args.file, encoding="utf-8") as handle:
            document = json.load(handle)
        if args.operation == "create":
            if not args.agent_type:
                parser.error("agent create requires --type")
            result = anl.create_agent(
                document, args.id, args.agent_type, args.capabilities or (), args.note
            )
        elif args.operation == "read":
            network = anl.validate(document)
            result = next((a for a in network["agents"] if a["id"] == args.id), None)
            if result is None:
                raise SystemExit(f"unknown agent: {args.id!r}")
            with open(args.out, "w", encoding="utf-8") as handle:
                json.dump(result, handle, indent=2, sort_keys=True)
                handle.write("\n")
            return 0
        elif args.operation == "update":
            result = anl.update_agent(
                document, args.id, agent_type=args.agent_type,
                capabilities=args.capabilities, note=args.note
            )
        else:
            result = anl.delete_agent(document, args.id)
        with open(args.out, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
        return 0

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
