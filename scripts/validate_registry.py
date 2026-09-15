"""Validate the machine-readable research registry without third-party dependencies."""

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "research"
SHA = re.compile(r"^[0-9a-f]{40}$")
STATES = {"proposed", "testing", "concluded", "collided", "archived", "blocked"}
RELATIONS = {"converges_with", "contradicts", "shares_evidence", "supersedes"}


def load(name):
    with (ROOT / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def main():
    approaches = load("approaches.json")["approaches"]
    projects = load("projects.json")["projects"]
    iterations = load("iterations.json")["iterations"]
    intentions = load("intentions.json")["intentions"]
    evidence = load("evidence.json")["records"]
    progress = load("progress.json")
    approach_keys = {(item["id"], item["version"]) for item in approaches}
    approach_ids = {item["id"] for item in approaches}
    project_ids = {item["id"] for item in projects}
    iteration_ids = {item["id"] for item in iterations}
    evidence_ids = {item["id"] for item in evidence}
    errors = []
    intention_ids = {item["id"] for item in intentions}
    if len(intention_ids) != len(intentions):
        errors.append("intention IDs must be unique")
    for item in intentions:
        for question in item.get("answers", []):
            if not re.fullmatch(r"Q-\d+", question):
                errors.append(f"intention {item.get('id')}: invalid question ID")
    for snapshot in progress.get("snapshots", []):
        unknown = set(snapshot.get("intention_status", {})) - intention_ids
        if unknown:
            errors.append(f"progress snapshot {snapshot.get('release')}: unknown intentions")

    if len(iteration_ids) != len(iterations):
        errors.append("iteration IDs must be unique")
    if len(approach_ids) != len(approaches):
        errors.append("approach IDs must be unique")
    if len(evidence_ids) != len(evidence):
        errors.append("evidence IDs must be unique")
    for item in evidence:
        prefix = f"evidence {item.get('id', '<missing>')}"
        if item.get("iteration") not in iteration_ids:
            errors.append(f"{prefix}: unknown iteration")
        if item.get("status") not in {"observed", "unverified", "blocked"}:
            errors.append(f"{prefix}: invalid status")
        if item.get("confidence") not in {"low", "medium", "high"}:
            errors.append(f"{prefix}: invalid confidence")
    for item in iterations:
        prefix = f"iteration {item.get('id', '<missing>')}"
        if item.get("project") not in project_ids:
            errors.append(f"{prefix}: unknown project")
        if (item.get("approach"), item.get("approach_version")) not in approach_keys:
            errors.append(f"{prefix}: unknown approach version")
        if item.get("state") not in STATES:
            errors.append(f"{prefix}: invalid state")
        if not SHA.fullmatch(item.get("commit", "")):
            errors.append(f"{prefix}: commit must be a full SHA")
        for relation in item.get("relations", []):
            if relation.get("type") not in RELATIONS:
                errors.append(f"{prefix}: invalid relation type")
            if relation.get("target") not in iteration_ids:
                errors.append(f"{prefix}: relation target does not exist")
    for item in approaches:
        if item.get("status") not in {"active", "proposed", "archived"}:
            errors.append(f"approach {item.get('id')}: invalid status")
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"valid: {len(approaches)} approaches, {len(projects)} projects, {len(iterations)} iterations, {len(intentions)} intentions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
