"""PVL — Provenance Vocabulary Language (W3C PROV-DM inspired).

Documents record what was generated from what, by which activity, and on whose
behalf: entities, activities, agents, and a fixed set of PROV-style records.
Nothing says when anything runs; records are past-tense statements of
provenance, not future-tense plans.

Semantic center: derivation and responsibility records over a single
document-wide namespace.
Escape hatch: free-form ``attributes`` string maps on entities (PROV's
attribute-value pairs), and activities without a performer are legal and
surfaced as gaps.
"""

from __future__ import annotations

from .errors import ValidationError

SCHEMA = "pvl/1"
NAME = "Provenance Vocabulary Language (PROV-DM inspired)"

RECORD_SPECS = {
    "used": {"required": ("activity", "entity")},
    "was_generated_by": {"required": ("entity", "activity")},
    "was_derived_from": {"required": ("entity", "used")},
    "was_attributed_to": {"required": ("entity", "agent")},
    "acted_on_behalf_of": {"required": ("agent", "responsible"), "optional": ("activity",)},
}
FORBIDDEN_KEYS = ("step", "order", "next", "then", "before", "after", "trigger", "sequence")

TRACE_TARGET = "remediation-plan"
PROJECTION_MARKERS = ("| entity | generated_by |", "assessment")

MUTATION_SPEC = {
    "added": [
        "activity:estimation performed_by=remediation-planner",
        "entity:cost-estimate attributes=1",
        "record:was_derived_from count=4",
        "record:was_generated_by count=4",
        "count:activities=4",
        "count:entities=6",
        "count:records=13",
    ],
    "removed": [
        "record:was_derived_from count=3",
        "record:was_generated_by count=3",
        "count:activities=3",
        "count:entities=5",
        "count:records=11",
    ],
}


def validate(doc):
    """Validate a PVL document; return a normalized dict or raise."""
    if not isinstance(doc, dict):
        raise ValidationError(["document must be a JSON object"])
    errors = []
    if doc.get("schema") != SCHEMA:
        errors.append(f"unsupported schema: {doc.get('schema')!r}, expected {SCHEMA!r}")
    name = doc.get("name")
    if not isinstance(name, str) or not name:
        errors.append("name must be a non-empty string")

    kind_of = {}
    records = {}

    def collect(kind, plural, required):
        items = doc.get(plural)
        if not isinstance(items, list):
            errors.append(f"{plural} must be a list")
            return
        for i, rec in enumerate(items):
            if not isinstance(rec, dict) or not isinstance(rec.get("id"), str) or not rec["id"]:
                errors.append(f"{plural}[{i}] must be an object with a non-empty string id")
                continue
            for key in rec:
                if key in FORBIDDEN_KEYS:
                    errors.append(f"forbidden workflow key {key!r} in {plural}[{i}]")
            for key in required:
                if not isinstance(rec.get(key), str) or not rec[key]:
                    errors.append(f"{plural}[{i}]: {key} must be a non-empty string")
            rid = rec["id"]
            if rid in kind_of:
                errors.append(f"duplicate id {rid!r} (also declared as {kind_of[rid]})")
                continue
            kind_of[rid] = kind
            records[rid] = rec

    collect("agent", "agents", ("role",))
    collect("activity", "activities", ())
    collect("entity", "entities", ())

    # activities: performed_by optional, but if present must be an agent.
    for i, act in enumerate(doc.get("activities") or []):
        if isinstance(act, dict) and act.get("performed_by") is not None:
            pb = act["performed_by"]
            if pb not in kind_of or kind_of[pb] != "agent":
                errors.append(f"activity {act.get('id')!r} performed_by unknown agent {pb!r}")

    # entities: attributes must be a string map (the escape hatch).
    ents = doc.get("entities")
    if isinstance(ents, list):
        for i, ent in enumerate(ents):
            if not isinstance(ent, dict):
                continue
            attrs = ent.get("attributes", {})
            if not isinstance(attrs, dict) or not all(
                isinstance(k, str) and isinstance(val, str) for k, val in attrs.items()
            ):
                errors.append(f"entity {ent.get('id')!r}: attributes must be a string map")

    prov = doc.get("records")
    if not isinstance(prov, list):
        errors.append("records must be a list")
        prov = []
    seen = set()
    derivations = []
    for i, rec in enumerate(prov):
        if not isinstance(rec, dict):
            errors.append(f"records[{i}] must be an object")
            continue
        for key in rec:
            if key in FORBIDDEN_KEYS:
                errors.append(f"forbidden workflow key {key!r} in records[{i}]")
        rtype = rec.get("type")
        spec = RECORD_SPECS.get(rtype)
        if spec is None:
            errors.append(f"records[{i}]: unknown record type {rtype!r}")
            continue
        allowed = set(spec["required"]) | set(spec.get("optional", ()))
        for key in rec:
            if key != "type" and key not in allowed:
                errors.append(f"records[{i}] ({rtype}): unknown key {key!r}")
        for key in spec["required"]:
            val = rec.get(key)
            if not isinstance(val, str) or not val:
                errors.append(f"records[{i}] ({rtype}): {key} must be a non-empty string")
                continue
            expected = {"activity": "activity", "entity": "entity", "used": "entity", "agent": "agent", "responsible": "agent"}[key]
            if val not in kind_of or kind_of[val] != expected:
                errors.append(f"records[{i}] ({rtype}): {key} {val!r} is not a known {expected}")
        for key in spec.get("optional", ()):
            val = rec.get(key)
            if val is None:
                continue
            expected = {"activity": "activity"}[key]
            if val not in kind_of or kind_of[val] != expected:
                errors.append(f"records[{i}] ({rtype}): {key} {val!r} is not a known {expected}")
        sig = (rtype,) + tuple(rec.get(k) for k in spec["required"])
        if sig in seen:
            errors.append(f"duplicate record {sig[0]}: {sig[1:]}")
        seen.add(sig)
        if rtype == "was_derived_from":
            derivations.append((rec["entity"], rec["used"]))

    graph = {}
    for a, b in derivations:
        graph.setdefault(a, []).append(b)
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
            errors.append(f"derivation cycle through entity {node!r}")

    if errors:
        raise ValidationError(errors)
    return {"name": name, "records": prov, "_raw": doc}


def _by_kind(v, kind):
    return [r for r in v["records"] if r.get("type") == kind]


def summary(v):
    """Deterministic, keyed summary lines for a provenance document."""
    agents = sorted(_all_of(v, "agents"), key=lambda r: r["id"])
    acts = sorted(_all_of(v, "activities"), key=lambda r: r["id"])
    ents = sorted(_all_of(v, "entities"), key=lambda r: r["id"])
    lines = []
    for a in agents:
        lines.append(f"agent:{a['id']} role={a.get('role', 'unspecified')}")
    for a in acts:
        lines.append(f"activity:{a['id']} performed_by={a.get('performed_by', 'none')}")
    for e in ents:
        lines.append(f"entity:{e['id']} attributes={len(e.get('attributes', {}))}")
    counts = {}
    for rec in v["records"]:
        counts[rec["type"]] = counts.get(rec["type"], 0) + 1
    for rtype in sorted(counts):
        lines.append(f"record:{rtype} count={counts[rtype]}")
    generated = {r["entity"] for r in v["records"] if r["type"] == "was_generated_by"}
    derived_out = {r["entity"] for r in v["records"] if r["type"] == "was_derived_from"}
    for e in ents:
        if e["id"] not in generated and e["id"] not in derived_out:
            lines.append(f"ground:{e['id']}")
    lines.append(f"count:agents={len(agents)}")
    lines.append(f"count:activities={len(acts)}")
    lines.append(f"count:entities={len(ents)}")
    lines.append(f"count:records={len(v['records'])}")
    for a in acts:
        if not a.get("performed_by"):
            lines.append(f"gap:activity-no-agent:{a['id']}")
    return lines


def _all_of(v, plural):
    """Recover a collection from the raw document kept in the validated v."""
    return v["_raw"][plural]


def project(v):
    """Chain-of-custody table, one row per entity, sorted by id."""
    ents = {e["id"]: e for e in _all_of(v, "entities")}
    gen = {r["entity"]: r["activity"] for r in v["records"] if r["type"] == "was_generated_by"}
    deriv = {}
    for r in v["records"]:
        if r["type"] == "was_derived_from":
            deriv.setdefault(r["entity"], []).append(r["used"])
    attr = {r["entity"]: r["agent"] for r in v["records"] if r["type"] == "was_attributed_to"}
    rows = ["| entity | generated_by | derived_from | attributed_to |"]
    for eid in sorted(ents):
        rows.append(
            f"| {eid} | {gen.get(eid, '-')} | "
            f"{','.join(sorted(deriv.get(eid, []))) or '-'} | {attr.get(eid, '-')} |"
        )
    return "\n".join(rows)


def trace(v, target):
    """Derivation closure and responsibility records for one entity."""
    if target not in {e["id"] for e in _all_of(v, "entities")}:
        raise KeyError(f"unknown entity: {target}")
    lines = [f"entity:{target}"]
    gen = [r for r in v["records"] if r["type"] == "was_generated_by" and r["entity"] == target]
    for r in sorted(gen, key=lambda r: r["activity"]):
        lines.append(f"generated_by:{r['activity']}")
    deriv_out = {}
    for r in v["records"]:
        if r["type"] == "was_derived_from":
            deriv_out.setdefault(r["entity"], []).append(r["used"])
    frontier = sorted(deriv_out.get(target, []))
    reached = set()
    via = {}
    while frontier:
        nxt = []
        for cur in frontier:
            if cur in reached:
                continue
            reached.add(cur)
            lines.append(f"derived_from:{cur} via={via.get(cur, target)}")
            for succ in deriv_out.get(cur, []):
                if succ not in reached:
                    via[succ] = cur
                    nxt.append(succ)
        frontier = sorted(set(nxt))
    attributed = [r for r in v["records"] if r["type"] == "was_attributed_to" and r["entity"] == target]
    for r in sorted(attributed, key=lambda r: r["agent"]):
        lines.append(f"attributed_to:{r['agent']}")
    generated_ids = {r["entity"] for r in v["records"] if r["type"] == "was_generated_by"}
    derived_ids = {r["entity"] for r in v["records"] if r["type"] == "was_derived_from"}
    for eid in sorted(reached):
        if eid not in generated_ids and eid not in derived_ids:
            lines.append(f"ground:{eid}")
    return lines


def observed_metrics(v):
    ents = _all_of(v, "entities")
    recs = v["records"]
    mentioned = set()
    for r in recs:
        for key in ("entity", "used", "activity", "agent", "responsible"):
            if r.get(key):
                mentioned.add(r[key])
    grounded = sum(1 for e in ents if e["id"] in mentioned)
    attrs = sum(len(e.get("attributes", {})) for e in ents)
    return {
        "entities": len(ents),
        "evidence_coverage": grounded / len(ents) if ents else 1.0,
        "forbidden_key_count": 0,
        "extension_key_count": attrs,
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
            "note": f"{m['evidence_coverage']:.2f} of entities appear in at least one "
            "provenance record; unrecorded entities are legal and visible",
        },
        {
            "criterion": "referential_integrity",
            "score": 3 if m["dangling_refs"] == 0 else 0,
            "basis": "observed",
            "metric": "dangling_refs",
            "note": "0 dangling record references after validation",
        },
        {
            "criterion": "escape_hatch_usage",
            "score": 3 if m["extension_key_count"] > 0 else 0,
            "basis": "observed",
            "metric": "extension_key_count",
            "note": f"{m['extension_key_count']} free-form attribute pairs in use",
        },
        {
            "criterion": "workflow_leakage",
            "score": 3 if m["forbidden_key_count"] == 0 else 0,
            "basis": "observed",
            "metric": "forbidden_key_count",
            "note": "0 forbidden order/trigger keys; validation rejects them",
        },
        {
            "criterion": "explainability",
            "score": 3,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment (Vibe, not Astra): a past-tense chain of custody "
            "reads like an audit log; PROV's audit use cases are supporting evidence.",
        },
        {
            "criterion": "edit_locality",
            "score": 2,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment: adding an entity touches its own lines, but "
            "derivation closures make downstream traces move; the sample's diff "
            "stayed local but transitive reach is a real cost.",
        },
    ]
