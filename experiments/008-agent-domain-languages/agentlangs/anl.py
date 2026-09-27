"""ANL — Agent Network Language (baseline of the 009 matrix).

The semantic contract is carried over unchanged from experiment 008: a typed
network of agents, capabilities, and evidence with per-relation structural
rules, encoding no workflow. This is an independent reimplementation inside
the 009 harness so experiment 008 stays untouched; the validated document is
returned as a plain dict rather than a custom class to keep the harness
uniform across languages.

Semantic center: a typed capability graph.
Escape hatch: free-text ``note`` fields on any record, and capabilities
without evidence are legal (surfaced as coverage gaps, never rejected).
"""

from __future__ import annotations

from .errors import ValidationError

SCHEMA = "anl/1"
NAME = "Agent Network Language (baseline from experiment 008)"

RELATION_SPECS = {
    "collaborates_with": {"directed": False, "acyclic": False, "endpoints": ("agent", "agent")},
    "critiques": {"directed": True, "acyclic": False, "endpoints": ("agent", "agent")},
    "escalates_to": {"directed": True, "acyclic": True, "endpoints": ("agent", "agent")},
    "specializes": {"directed": True, "acyclic": True, "endpoints": ("capability", "capability")},
    "contradicts": {"directed": True, "acyclic": False, "endpoints": ("evidence", "evidence")},
}

# Workflow leakage: keys that would smuggle order or triggering into a
# document that is supposed to declare structure only.
FORBIDDEN_KEYS = ("step", "order", "next", "then", "before", "after", "trigger", "sequence")

# Declared fact used by the provenance/evidence-trace sub-experiment.
TRACE_TARGET = "claim-verification"

# Substrings that must appear in the projection rendering.
PROJECTION_MARKERS = ("digraph anl", "dispatcher")

# Expected summary diff of the shipped mutation (samples/anl/mutated.json
# vs samples/anl/sample.json). The harness asserts the observed diff equals
# this exactly; nothing outside this diff may move.
MUTATION_SPEC = {
    "added": [
        "agent:oncall-engineer type=human capabilities=incident-command",
        "capability:incident-command evidence=1",
        "relation:collaborates_with count=4",
        "count:agents=5",
        "count:capabilities=7",
    ],
    "removed": [
        "relation:collaborates_with count=3",
        "count:agents=4",
        "count:capabilities=6",
    ],
}


def validate(doc):
    """Validate an ANL document; return a normalized dict or raise."""
    if not isinstance(doc, dict):
        raise ValidationError(["document must be a JSON object"])
    errors = []
    if doc.get("schema") != SCHEMA:
        errors.append(f"unsupported schema: {doc.get('schema')!r}, expected {SCHEMA!r}")
    name = doc.get("network")
    if not isinstance(name, str) or not name:
        errors.append("network name must be a non-empty string")

    def check_forbidden(record, where):
        for key in record:
            if key in FORBIDDEN_KEYS:
                errors.append(f"forbidden workflow key {key!r} in {where}")

    kind_of = {}
    records = {}

    def collect(kind, plural):
        items = doc.get(plural)
        if not isinstance(items, list):
            errors.append(f"{plural} must be a list")
            return
        for i, rec in enumerate(items):
            if not isinstance(rec, dict) or not isinstance(rec.get("id"), str) or not rec["id"]:
                errors.append(f"{plural}[{i}] must be an object with a non-empty string id")
                continue
            check_forbidden(rec, f"{plural}[{i}]")
            rid = rec["id"]
            if rid in kind_of:
                errors.append(f"duplicate id {rid!r} (also declared as {kind_of[rid]})")
                continue
            kind_of[rid] = kind
            records[rid] = rec

    collect("agent", "agents")
    collect("capability", "capabilities")
    collect("evidence", "evidence")

    for agent in doc.get("agents", []) if isinstance(doc.get("agents"), list) else []:
        for cap in agent.get("capabilities", []):
            if cap not in kind_of or kind_of[cap] != "capability":
                errors.append(f"agent {agent.get('id')!r} references unknown capability {cap!r}")
        if not isinstance(agent.get("type"), str):
            errors.append(f"agent {agent.get('id')!r} must have a string type")

    for cap in doc.get("capabilities", []) if isinstance(doc.get("capabilities"), list) else []:
        for ev in cap.get("evidenced_by", []):
            if ev not in kind_of or kind_of[ev] != "evidence":
                errors.append(f"capability {cap.get('id')!r} references unknown evidence {ev!r}")

    edges = {rel: [] for rel in RELATION_SPECS}
    seen_relations = set()
    rels = doc.get("relations")
    if not isinstance(rels, list):
        errors.append("relations must be a list")
        rels = []
    for i, rel in enumerate(rels):
        if not isinstance(rel, dict):
            errors.append(f"relations[{i}] must be an object")
            continue
        check_forbidden(rel, f"relations[{i}]")
        rtype, src, dst = rel.get("type"), rel.get("from"), rel.get("to")
        spec = RELATION_SPECS.get(rtype)
        if spec is None:
            errors.append(f"relations[{i}]: unknown relation type {rtype!r}")
            continue
        for end, kind in zip((src, dst), spec["endpoints"]):
            if end not in kind_of or kind_of[end] != kind:
                errors.append(
                    f"relation {i} ({rtype}): endpoint {end!r} is not a known {kind}"
                )
        if (rtype, src, dst) in seen_relations:
            errors.append(f"duplicate relation {rtype}: {src} -> {dst}")
        seen_relations.add((rtype, src, dst))
        edges[rtype].append((src, dst))

    for rtype, spec in RELATION_SPECS.items():
        if spec["acyclic"]:
            cycle = _find_cycle(edges[rtype])
            if cycle:
                errors.append(f"cycle in acyclic relation {rtype}: {' -> '.join(cycle)}")

    if errors:
        raise ValidationError(errors)
    by_kind = {"agent": [], "capability": [], "evidence": []}
    for rid, rec in records.items():
        by_kind[kind_of[rid]].append(rec)
    return {
        "name": name,
        "agents": sorted(by_kind["agent"], key=lambda r: r["id"]),
        "capabilities": sorted(by_kind["capability"], key=lambda r: r["id"]),
        "evidence": sorted(by_kind["evidence"], key=lambda r: r["id"]),
        "relations": sorted(
            ({"type": r["type"], "from": r["from"], "to": r["to"]} for r in rels),
            key=lambda r: (r["type"], r["from"], r["to"]),
        ),
    }


def _find_cycle(edge_list):
    """Return one cycle as a node list, or None, for a directed edge list."""
    graph = {}
    for a, b in edge_list:
        graph.setdefault(a, []).append(b)
    state = {}

    def visit(node, path):
        state[node] = 1
        for nxt in graph.get(node, ()):
            if state.get(nxt) == 1:
                return path[path.index(nxt):] + [nxt]
            if state.get(nxt, 0) == 0:
                found = visit(nxt, path + [nxt])
                if found:
                    return found
        state[node] = 2
        return None

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            found = visit(node, [node])
            if found:
                return found
    return None


def _cycle_nodes(edge_list):
    """Nodes participating in any cycle of an undirected-by-meaning edge list.

    For tolerated relations a cycle is any closed walk: with small graphs it is
    enough to report nodes on a strongly connected component of size > 1 or a
    self loop, computed by repeated reachability.
    """
    graph = {}
    for a, b in edge_list:
        graph.setdefault(a, []).append(b)
    nodes = sorted(graph)
    result = set()
    # Node n is on a cycle iff n is reachable from one of its own successors.
    for node in nodes:
        reach = set()
        stack = list(graph.get(node, ()))
        while stack:
            cur = stack.pop()
            if cur in reach:
                continue
            reach.add(cur)
            stack.extend(graph.get(cur, ()))
        if node in reach:
            result.add(node)
    return result


def summary(v):
    """Deterministic, keyed summary lines for a validated network."""
    caps_of = {}
    for agent in v["agents"]:
        for cap in agent.get("capabilities", []):
            caps_of.setdefault(cap, []).append(agent["id"])
    lines = []
    for agent in v["agents"]:
        caps = ",".join(sorted(agent.get("capabilities", [])))
        lines.append(f"agent:{agent['id']} type={agent['type']} capabilities={caps}")
    for cap in v["capabilities"]:
        n = len(cap.get("evidenced_by", []))
        lines.append(f"capability:{cap['id']} evidence={n}")
    for ev in v["evidence"]:
        lines.append(f"evidence:{ev['id']} kind={ev.get('kind', 'unspecified')}")
    counts = {}
    for rel in v["relations"]:
        counts[rel["type"]] = counts.get(rel["type"], 0) + 1
    for rtype in sorted(counts):
        lines.append(f"relation:{rtype} count={counts[rtype]}")
    by_type = {}
    for rel in v["relations"]:
        by_type.setdefault(rel["type"], []).append((rel["from"], rel["to"]))
    for rtype in sorted(by_type):
        if not RELATION_SPECS[rtype]["acyclic"]:
            cyc = _cycle_nodes(by_type[rtype])
            if cyc:
                lines.append(f"cycle:{rtype} nodes={','.join(sorted(cyc))}")
    for cap in v["capabilities"]:
        if not cap.get("evidenced_by"):
            lines.append(f"gap:capability-no-evidence:{cap['id']}")
    for agent in v["agents"]:
        if not agent.get("capabilities"):
            lines.append(f"gap:agent-no-capabilities:{agent['id']}")
    referenced = {ev for cap in v["capabilities"] for ev in cap.get("evidenced_by", [])}
    referenced |= {r["from"] for r in v["relations"] if RELATION_SPECS[r["type"]]["endpoints"][0] == "evidence"}
    referenced |= {r["to"] for r in v["relations"] if RELATION_SPECS[r["type"]]["endpoints"][1] == "evidence"}
    for ev in v["evidence"]:
        if ev["id"] not in referenced:
            lines.append(f"gap:evidence-unreferenced:{ev['id']}")
    lines.append(f"count:agents={len(v['agents'])}")
    lines.append(f"count:capabilities={len(v['capabilities'])}")
    lines.append(f"count:evidence={len(v['evidence'])}")
    return lines


def project(v):
    """Render the network as a deterministic DOT graph."""
    out = ["digraph anl {"]
    for agent in v["agents"]:
        out.append(f'  "agent:{agent["id"]}" [label="{agent["id"]} ({agent["type"]})"];')
    for cap in v["capabilities"]:
        out.append(f'  "capability:{cap["id"]}";')
    for ev in v["evidence"]:
        out.append(f'  "evidence:{ev["id"]}" [shape=box];')
    for agent in v["agents"]:
        for cap in sorted(agent.get("capabilities", [])):
            out.append(f'  "agent:{agent["id"]}" -> "capability:{cap}";')
    for cap in v["capabilities"]:
        for ev in sorted(cap.get("evidenced_by", [])):
            out.append(f'  "capability:{cap["id"]}" -> "evidence:{ev}" [style=dotted];')
    for rel in v["relations"]:
        out.append(f'  "{rel["from"]}" -> "{rel["to"]}" [label="{rel["type"]}"];')
    out.append("}")
    return "\n".join(out)


def trace(v, target):
    """Evidence trace for one capability: who holds it, what backs it."""
    cap = next((c for c in v["capabilities"] if c["id"] == target), None)
    if cap is None:
        raise KeyError(f"unknown capability: {target}")
    lines = [f"capability:{target}"]
    holders = sorted(
        a["id"] for a in v["agents"] if target in a.get("capabilities", [])
    )
    for holder in holders or ["(none)"]:
        lines.append(f"held-by:{holder}")
    evs = sorted(cap.get("evidenced_by", []))
    if not evs:
        lines.append("evidence:none")
    for ev in evs:
        rec = next(e for e in v["evidence"] if e["id"] == ev)
        lines.append(f"evidence:{ev} kind={rec.get('kind', 'unspecified')}")
        for rel in v["relations"]:
            if rel["type"] == "contradicts" and rel["from"] == ev:
                lines.append(f"contradicts:{rel['to']}")
    return lines


def observed_metrics(v):
    """Numbers the scorecard recomputes from the validated document."""
    caps = v["capabilities"]
    evidenced = sum(1 for c in caps if c.get("evidenced_by"))
    refs = 0
    for agent in v["agents"]:
        refs += sum(1 for c in agent.get("capabilities", []) if c not in {x["id"] for x in caps})
    notes = sum(1 for r in v["agents"] + caps + v["evidence"] if "note" in r)
    return {
        "entities": len(v["agents"]) + len(caps) + len(v["evidence"]),
        "evidence_coverage": (evidenced / len(caps)) if caps else 1.0,
        "forbidden_key_count": 0,
        "extension_key_count": notes,
        "dangling_refs": refs,
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
    """Six-criterion practical-fit scorecard; observed entries cite metrics."""
    m = observed_metrics(v)
    cov = m["evidence_coverage"]
    return [
        {
            "criterion": "grounding",
            "score": _coverage_score(cov),
            "basis": "observed",
            "metric": "evidence_coverage",
            "note": f"{m['evidence_coverage']:.2f} of capabilities carry evidence links; "
            "unevidenced capabilities are legal and surfaced as gaps",
        },
        {
            "criterion": "referential_integrity",
            "score": 3 if m["dangling_refs"] == 0 else 0,
            "basis": "observed",
            "metric": "dangling_refs",
            "note": f"{m['dangling_refs']} dangling references after validation",
        },
        {
            "criterion": "escape_hatch_usage",
            "score": 3 if m["extension_key_count"] > 0 else 0,
            "basis": "observed",
            "metric": "extension_key_count",
            "note": f"{m['extension_key_count']} records use the free-text note hatch",
        },
        {
            "criterion": "workflow_leakage",
            "score": 3 if m["forbidden_key_count"] == 0 else 0,
            "basis": "observed",
            "metric": "forbidden_key_count",
            "note": "0 forbidden order/trigger keys; validation rejects any that appear",
        },
        {
            "criterion": "explainability",
            "score": 3,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment (Vibe, not Astra): typed graph with five named "
            "relations reads like an org chart; humans reviewed similar shapes in "
            "008. Not measured with users.",
        },
        {
            "criterion": "edit_locality",
            "score": 3,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment: summary lines are keyed per entity, so adding "
            "one agent moves only its own lines and counts; demonstrated by "
            "sub-experiment 3 but not proven for all edits.",
        },
    ]
