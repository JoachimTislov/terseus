"""DRL — Desired-state Resource Language (Kubernetes / HCL inspired).

Documents declare resources with a desired state, an observed state, and
dependencies. Drift between desired and observed is computed at read time,
never asserted as a plan: there are no steps, no apply order, and no
reconciliation logic in the document. Convergence belongs to an external
controller, exactly as the Kubernetes controller model separates desired
state from the loop that moves current state toward it.

Semantic center: desired vs observed state with computed drift over a
dependency DAG.
Escape hatch: free-form ``labels`` and ``annotations`` string maps, and
``evidence`` is a free string (no closed registry).
"""

from __future__ import annotations

from .errors import ValidationError

SCHEMA = "drl/1"
NAME = "Desired-state Resource Language (Kubernetes/HCL inspired)"

RESOURCE_KEYS = ("id", "kind", "desired", "observed", "depends_on", "labels", "annotations", "evidence")
FORBIDDEN_KEYS = ("step", "order", "next", "then", "before", "after", "trigger", "sequence", "command", "script", "run")

TRACE_TARGET = "svc-checkout"
PROJECTION_MARKERS = ("Name: incident-472", "Kind: Incident")

MUTATION_SPEC = {
    "added": [
        "resource:action-page-status kind=ActionItem drift=0 deps=1",
        "count:evidenced=3",
        "count:resources=6",
    ],
    "removed": [
        "count:evidenced=2",
        "count:resources=5",
    ],
}


def validate(doc):
    """Validate a DRL document; return a normalized dict or raise."""
    if not isinstance(doc, dict):
        raise ValidationError(["document must be a JSON object"])
    errors = []
    if doc.get("schema") != SCHEMA:
        errors.append(f"unsupported schema: {doc.get('schema')!r}, expected {SCHEMA!r}")
    name = doc.get("name")
    if not isinstance(name, str) or not name:
        errors.append("name must be a non-empty string")
    resources = doc.get("resources")
    if not isinstance(resources, list):
        errors.append("resources must be a list")
        resources = []

    by_id = {}
    for i, r in enumerate(resources):
        if not isinstance(r, dict) or not isinstance(r.get("id"), str) or not r["id"]:
            errors.append(f"resources[{i}] must be an object with a non-empty string id")
            continue
        for key in r:
            if key in FORBIDDEN_KEYS:
                errors.append(f"forbidden workflow key {key!r} in resource {r['id']!r}")
            elif key not in RESOURCE_KEYS:
                errors.append(f"resource {r['id']!r}: unknown key {key!r}")
        if r["id"] in by_id:
            errors.append(f"duplicate resource id {r['id']!r}")
            continue
        if not isinstance(r.get("kind"), str) or not r["kind"]:
            errors.append(f"resource {r['id']!r}: kind must be a non-empty string")
        desired = r.get("desired")
        if not isinstance(desired, dict) or not desired:
            errors.append(f"resource {r['id']!r}: desired must be a non-empty map")
        else:
            for k, val in desired.items():
                if not isinstance(k, str) or isinstance(val, (dict, list)):
                    errors.append(f"resource {r['id']!r}: desired.{k} must be a scalar")
        observed = r.get("observed", {})
        if not isinstance(observed, dict):
            errors.append(f"resource {r['id']!r}: observed must be a map")
        else:
            for k, val in observed.items():
                if not isinstance(k, str) or isinstance(val, (dict, list)):
                    errors.append(f"resource {r['id']!r}: observed.{k} must be a scalar")
        for map_key in ("labels", "annotations"):
            mapping = r.get(map_key, {})
            if not isinstance(mapping, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in mapping.items()
            ):
                errors.append(f"resource {r['id']!r}: {map_key} must be a string map")
        if "evidence" in r and not isinstance(r["evidence"], str):
            errors.append(f"resource {r['id']!r}: evidence must be a string")
        by_id[r["id"]] = r

    for r in by_id.values():
        deps = r.get("depends_on", [])
        if not isinstance(deps, list) or not all(isinstance(d, str) for d in deps):
            errors.append(f"resource {r['id']!r}: depends_on must be a list of ids")
            continue
        for d in deps:
            if d not in by_id:
                errors.append(f"resource {r['id']!r}: depends_on unknown resource {d!r}")
        if r["id"] in deps:
            errors.append(f"resource {r['id']!r} depends on itself")

    # depends_on must form a DAG: no resource may be reachable from itself.
    graph = {
        r["id"]: [d for d in r.get("depends_on", []) if d in by_id]
        for r in by_id.values()
    }
    for node in sorted(graph):
        reach = set()
        stack = list(graph.get(node, ()))
        while stack:
            cur = stack.pop()
            if cur in reach:
                continue
            reach.add(cur)
            stack.extend(graph.get(cur, ()))
        if node in reach:
            errors.append(f"dependency cycle through resource {node!r}")

    if errors:
        raise ValidationError(errors)
    return {"name": name, "resources": sorted(by_id.values(), key=lambda r: r["id"])}


def drift(resource):
    """Computed drift between desired and observed for one resource."""
    items = []
    for key in sorted(resource.get("desired", {})):
        want = resource["desired"][key]
        got = resource.get("observed", {}).get(key, "missing")
        if want != got:
            items.append((key, want, got))
    return items


def summary(v):
    """Deterministic, keyed summary lines for validated resources."""
    lines = []
    drift_total = 0
    for r in v["resources"]:
        d = drift(r)
        drift_total += len(d)
        lines.append(
            f"resource:{r['id']} kind={r['kind']} drift={len(d)} deps={len(r.get('depends_on', []))}"
        )
    for r in v["resources"]:
        for key, want, got in drift(r):
            lines.append(f"drift:{r['id']}.{key} desired={want} observed={got}")
    lines.append(f"count:resources={len(v['resources'])}")
    lines.append(f"count:drift={drift_total}")
    evidenced = sum(1 for r in v["resources"] if r.get("evidence"))
    lines.append(f"count:evidenced={evidenced}")
    for r in v["resources"]:
        if not r.get("evidence"):
            lines.append(f"gap:resource-no-evidence:{r['id']}")
    return lines


def project(v):
    """Render resources in a deterministic kubectl-describe-like text."""
    out = []
    for r in v["resources"]:
        out.append(f"Name: {r['id']}")
        out.append(f"Kind: {r['kind']}")
        desired = ", ".join(f"{k}={r['desired'][k]}" for k in sorted(r.get("desired", {})))
        observed = ", ".join(f"{k}={v}" for k, v in sorted(r.get("observed", {}).items()))
        out.append(f"Desired: {desired or '-'}")
        out.append(f"Observed: {observed or '-'}")
        drifted = [key for key, _, _ in drift(r)]
        out.append(f"Drift: {','.join(drifted) if drifted else 'none'}")
        deps = ", ".join(sorted(r.get("depends_on", [])))
        out.append(f"Depends on: {deps or '(none)'}")
        if r.get("evidence"):
            out.append(f"Evidence: {r['evidence']}")
        if r.get("labels"):
            labels = ", ".join(f"{k}={v}" for k, v in sorted(r["labels"].items()))
            out.append(f"Labels: {labels}")
        out.append("")
    return "\n".join(out).rstrip()


def trace(v, target):
    """Drift, upstream blockers, and downstream waiters for one resource."""
    by_id = {r["id"]: r for r in v["resources"]}
    if target not in by_id:
        raise KeyError(f"unknown resource: {target}")
    lines = [f"resource:{target} kind={by_id[target]['kind']}"]
    d = drift(by_id[target])
    if d:
        for key, want, got in d:
            lines.append(f"drift:{target}.{key} desired={want} observed={got}")
    else:
        lines.append(f"drift:{target}=none")
    # Upstream: the dependency chain that must converge first.
    seen = set()
    frontier = sorted(by_id[target].get("depends_on", []))
    while frontier:
        nxt = []
        for rid in frontier:
            if rid in seen:
                continue
            seen.add(rid)
            lines.append(f"depends_on:{rid}")
            for key, want, got in drift(by_id[rid]):
                lines.append(f"blocked-by:{rid}.{key} desired={want} observed={got}")
            nxt.extend(by_id[rid].get("depends_on", []))
        frontier = sorted(set(nxt))
    # Downstream: resources waiting on this one, with their evidence.
    for r in v["resources"]:
        if target in r.get("depends_on", []):
            lines.append(
                f"waiting:{r['id']} evidence={r.get('evidence', 'none')}"
            )
    return lines


def observed_metrics(v):
    evidenced = sum(1 for r in v["resources"] if r.get("evidence"))
    hatch = sum(
        1
        for r in v["resources"]
        for key in ("labels", "annotations")
        if r.get(key)
    )
    return {
        "entities": len(v["resources"]),
        "evidence_coverage": evidenced / len(v["resources"]) if v["resources"] else 1.0,
        "forbidden_key_count": 0,
        "extension_key_count": hatch,
        "dangling_refs": 0,
    }


def _coverage_score(fraction):
    if fraction >= 1.0:
        return 3
    if fraction >= 0.66:
        return 2
    if fraction >= 0.33:
        return 1
    return 0


def scorecard(v):
    m = observed_metrics(v)
    cov = m["evidence_coverage"]
    return [
        {
            "criterion": "grounding",
            "score": _coverage_score(cov),
            "basis": "observed",
            "metric": "evidence_coverage",
            "note": f"{m['evidence_coverage']:.2f} of resources carry evidence; "
            "evidence-less resources are legal and surfaced as gaps",
        },
        {
            "criterion": "referential_integrity",
            "score": 3 if m["dangling_refs"] == 0 else 0,
            "basis": "observed",
            "metric": "dangling_refs",
            "note": "0 dangling depends_on references after validation",
        },
        {
            "criterion": "escape_hatch_usage",
            "score": 3 if m["extension_key_count"] > 0 else 0,
            "basis": "observed",
            "metric": "extension_key_count",
            "note": f"{m['extension_key_count']} resources use labels/annotations",
        },
        {
            "criterion": "workflow_leakage",
            "score": 3 if m["forbidden_key_count"] == 0 else 0,
            "basis": "observed",
            "metric": "forbidden_key_count",
            "note": "0 forbidden command/order keys; drift is computed, never planned",
        },
        {
            "criterion": "explainability",
            "score": 3,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment (Vibe, not Astra): desired/observed tables match "
            "how operators already read kubectl output; Kubernetes conventions are "
            "familiar, not proof.",
        },
        {
            "criterion": "edit_locality",
            "score": 3,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment: one resource edits its own lines; traces of "
            "neighbors move only when dependencies change, demonstrated by "
            "sub-experiment 3.",
        },
    ]
