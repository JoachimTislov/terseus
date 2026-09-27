"""SCL — Schema Contract Language (OpenAPI / JSON Schema inspired).

Documents declare typed record contracts for the incident-triage domain:
fields with types, required-ness, cross-contract references, and single-
inheritance composition via ``extends``. Nothing in a document says when or
in what order records are produced.

Semantic center: typed contracts with composition and references.
Escape hatch: ``x-`` prefixed keys on contracts and field specs — any JSON
object, validated for shape only and never interpreted (the OpenAPI
Specification Extensions pattern).
"""

from __future__ import annotations

from .errors import ValidationError

SCHEMA = "scl/1"
NAME = "Schema Contract Language (OpenAPI/JSON Schema inspired)"

FIELD_TYPES = ("string", "number", "boolean", "enum", "ref")
CONTRACT_KEYS = ("id", "extends", "fields")
FIELD_SPEC_KEYS = ("type", "required", "values", "target")
FORBIDDEN_KEYS = ("step", "order", "next", "then", "before", "after", "trigger", "sequence")

TRACE_TARGET = "action_item"
PROJECTION_MARKERS = ("# incident-472-contracts", "enum(sev1|sev2|sev3)")

# Expected summary diff for the shipped mutation (adds the postmortem contract).
MUTATION_SPEC = {
    "added": [
        "contract:postmortem extends=incident own_fields=2 inherited_fields=4 xkeys=1",
        "count:contracts=5",
        "count:fields=14",
        "count:extensions=4",
    ],
    "removed": [
        "count:contracts=4",
        "count:fields=12",
        "count:extensions=3",
    ],
}


def validate(doc):
    """Validate an SCL document; return a normalized dict or raise."""
    if not isinstance(doc, dict):
        raise ValidationError(["document must be a JSON object"])
    errors = []
    if doc.get("schema") != SCHEMA:
        errors.append(f"unsupported schema: {doc.get('schema')!r}, expected {SCHEMA!r}")
    name = doc.get("name")
    if not isinstance(name, str) or not name:
        errors.append("name must be a non-empty string")
    contracts = doc.get("contracts")
    if not isinstance(contracts, list):
        errors.append("contracts must be a list")
        contracts = []

    by_id = {}
    for i, c in enumerate(contracts):
        if not isinstance(c, dict) or not isinstance(c.get("id"), str) or not c["id"]:
            errors.append(f"contracts[{i}] must be an object with a non-empty string id")
            continue
        if c["id"] in by_id:
            errors.append(f"duplicate contract id {c['id']!r}")
            continue
        for key in c:
            if key in FORBIDDEN_KEYS:
                errors.append(f"forbidden workflow key {key!r} in contract {c['id']!r}")
        for key in c:
            if not key.startswith("x-") and key not in CONTRACT_KEYS:
                errors.append(f"contract {c['id']!r}: unknown key {key!r}")
            if key.startswith("x-") and not isinstance(c[key], dict):
                errors.append(f"contract {c['id']!r}: extension {key!r} must be an object")
        by_id[c["id"]] = c

    for c in by_id.values():
        parent = c.get("extends")
        if parent is not None and parent not in by_id:
            errors.append(f"contract {c['id']!r} extends unknown contract {parent!r}")

    # extends must form a DAG.
    for start in sorted(by_id):
        seen = set()
        cur = start
        while by_id.get(cur, {}).get("extends"):
            if cur in seen:
                errors.append(f"extends cycle at {cur!r}")
                break
            seen.add(cur)
            cur = by_id[cur]["extends"]

    for c in by_id.values():
        fields = c.get("fields", {})
        if not isinstance(fields, dict):
            errors.append(f"contract {c['id']!r}: fields must be an object")
            continue
        for fname, spec in fields.items():
            if not isinstance(spec, dict):
                errors.append(f"contract {c['id']!r}.{fname}: field spec must be an object")
                continue
            ftype = spec.get("type")
            if ftype not in FIELD_TYPES:
                errors.append(
                    f"contract {c['id']!r}.{fname}: unknown field type {ftype!r} "
                    f"(expected one of {', '.join(FIELD_TYPES)})"
                )
            if ftype == "enum":
                values = spec.get("values")
                if not isinstance(values, list) or not values:
                    errors.append(f"contract {c['id']!r}.{fname}: enum needs a non-empty values list")
            if ftype == "ref":
                target = spec.get("target")
                if target not in by_id:
                    errors.append(f"contract {c['id']!r}.{fname}: ref target {target!r} is not a contract")
            if "required" in spec and not isinstance(spec["required"], bool):
                errors.append(f"contract {c['id']!r}.{fname}: required must be a boolean")
            for key in spec:
                if key in FORBIDDEN_KEYS:
                    errors.append(f"forbidden workflow key {key!r} in {c['id']!r}.{fname}")
                if key.startswith("x-") and not isinstance(spec[key], dict):
                    errors.append(f"contract {c['id']!r}.{fname}: extension {key!r} must be an object")
                if not key.startswith("x-") and key not in FIELD_SPEC_KEYS:
                    errors.append(f"contract {c['id']!r}.{fname}: unknown field spec key {key!r}")

    if errors:
        raise ValidationError(errors)
    return {"name": name, "contracts": sorted(by_id.values(), key=lambda c: c["id"])}


def _inherited_fields(contracts_by_id, cid):
    chain = []
    cur = contracts_by_id[cid].get("extends")
    while cur:
        chain.append(cur)
        cur = contracts_by_id[cur].get("extends")
    fields = {}
    for parent in reversed(chain):
        fields.update(contracts_by_id[parent].get("fields", {}))
    return fields


def summary(v):
    """Deterministic, keyed summary lines for validated contracts."""
    by_id = {c["id"]: c for c in v["contracts"]}
    lines = []
    for c in v["contracts"]:
        inherited = _inherited_fields(by_id, c["id"])
        own = c.get("fields", {})
        xkeys = sum(1 for k in c if k.startswith("x-"))
        xkeys += sum(1 for spec in own.values() for k in spec if k.startswith("x-"))
        lines.append(
            f"contract:{c['id']} extends={c.get('extends') or 'none'} "
            f"own_fields={len(own)} inherited_fields={len(inherited)} xkeys={xkeys}"
        )
    own_total = sum(len(c.get("fields", {})) for c in v["contracts"])
    ext_total = sum(
        sum(1 for k in c if k.startswith("x-"))
        + sum(1 for spec in c.get("fields", {}).values() for k in spec if k.startswith("x-"))
        for c in v["contracts"]
    )
    lines.append(f"count:contracts={len(v['contracts'])}")
    lines.append(f"count:fields={own_total}")
    lines.append(f"count:extensions={ext_total}")
    for c in v["contracts"]:
        own = c.get("fields", {})
        required = any(spec.get("required") for spec in own.values())
        if not required:
            lines.append(f"gap:contract-no-required:{c['id']}")
    return lines


def project(v):
    """Render contracts as an OpenAPI-components-style text block."""
    by_id = {c["id"]: c for c in v["contracts"]}
    out = [f"# {v['name']}"]
    for c in v["contracts"]:
        inherited = _inherited_fields(by_id, c["id"])
        out.append(f"{c['id']}:  # extends {c.get('extends') or 'none'}")
        for fname in sorted(set(c.get("fields", {})) | set(inherited)):
            spec = c["fields"][fname] if fname in c.get("fields", {}) else inherited[fname]
            origin = c["id"] if fname in c.get("fields", {}) else "inherited"
            ftype = spec["type"]
            if ftype == "enum":
                rendered = f"enum({'|'.join(spec['values'])})"
            elif ftype == "ref":
                rendered = f"-> {spec['target']}"
            else:
                rendered = ftype
            req = " required" if spec.get("required") else ""
            out.append(f"  {fname}: {rendered}{req}  # {origin}")
        out.append("")
    return "\n".join(out).rstrip()


def trace(v, target):
    """Field provenance: where every field of a contract comes from."""
    by_id = {c["id"]: c for c in v["contracts"]}
    if target not in by_id:
        raise KeyError(f"unknown contract: {target}")
    merged = dict(_inherited_fields(by_id, target))
    merged.update(by_id[target].get("fields", {}))
    lines = [f"contract:{target}"]
    for fname in sorted(merged):
        spec = merged[fname]
        origin = by_id[target].get("fields", {}).get(fname)
        origin_id = target if origin is not None else "inherited"
        if origin is None:
            chain = []
            cur = by_id[target].get("extends")
            while cur:
                if fname in by_id[cur].get("fields", {}):
                    chain.append(cur)
                    break
                cur = by_id[cur].get("extends")
            origin_id = chain[0] if chain else "unknown"
        req = "required" if spec.get("required") else "optional"
        lines.append(f"field:{fname} type={spec['type']} {req} origin={origin_id}")
    root = by_id[target].get("extends")
    while root and by_id[root].get("extends"):
        root = by_id[root]["extends"]
    lines.append(f"root:{root if root else target}")
    return lines


def observed_metrics(v):
    by_id = {c["id"]: c for c in v["contracts"]}
    grounded = 0
    for c in v["contracts"]:
        linked = c.get("extends") is not None
        linked = linked or any(
            spec.get("type") == "ref" for spec in c.get("fields", {}).values()
        )
        linked = linked or any(
            other.get("extends") == c["id"] for other in by_id.values()
        )
        grounded += 1 if linked else 0
    xkeys = sum(
        sum(1 for k in c if k.startswith("x-"))
        + sum(1 for spec in c.get("fields", {}).values() for k in spec if k.startswith("x-"))
        for c in v["contracts"]
    )
    return {
        "entities": len(v["contracts"]),
        "evidence_coverage": grounded / len(v["contracts"]) if v["contracts"] else 1.0,
        "forbidden_key_count": 0,
        "extension_key_count": xkeys,
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
            "note": f"{m['evidence_coverage']:.2f} of contracts participate in the "
            "composition/reference graph (SCL's grounding is linkage, not evidence)",
        },
        {
            "criterion": "referential_integrity",
            "score": 3 if m["dangling_refs"] == 0 else 0,
            "basis": "observed",
            "metric": "dangling_refs",
            "note": "0 dangling extends/ref targets after validation",
        },
        {
            "criterion": "escape_hatch_usage",
            "score": 3 if m["extension_key_count"] > 0 else 0,
            "basis": "observed",
            "metric": "extension_key_count",
            "note": f"{m['extension_key_count']} x- extension keys in use",
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
            "score": 2,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment (Vibe, not Astra): schema-literate readers parse "
            "contracts quickly, but inheritance chains force lookups. JSON Schema's "
            "success with humans is supporting evidence, not proof for this DSL.",
        },
        {
            "criterion": "edit_locality",
            "score": 3,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment: one contract edits its own summary line; "
            "inherited-field counts move for descendants, which is a real "
            "(untested-beyond-the-sample) locality cost.",
        },
    ]
