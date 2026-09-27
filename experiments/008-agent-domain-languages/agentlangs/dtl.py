"""DTL — Decision Table Language (OMG DMN inspired).

Documents declare decision tables: typed inputs, typed outputs, and rules
that are unordered constraints. Hit policies decide how many rules may be
satisfied and how their outputs combine. Tables can feed tables through
``input_from`` references, forming a data dependency graph; evaluation order
is derived from those references, never declared.

Semantic center: unordered constraint rows with an explicit hit policy.
Escape hatch: the ``-`` wildcard cell and free-text ``note``/``cites``
annotations on rules. Deliberately unsupported: DMN's First and Rule Order
hit policies, because they give row order meaning — exactly the workflow
leakage this experiment forbids.
"""

from __future__ import annotations

from .errors import ValidationError

SCHEMA = "dtl/1"
NAME = "Decision Table Language (DMN inspired)"

HIT_POLICIES = ("unique", "priority", "collect")
TABLE_KEYS = ("id", "hit_policy", "inputs", "outputs", "rules")
FORBIDDEN_KEYS = ("step", "order", "next", "then", "before", "after", "trigger", "sequence")

# Input bundle used by the provenance/evidence-trace sub-experiment.
EVAL_INPUTS = {"severity": "sev2", "customer_impact": "many"}

TRACE_TARGET = "response.tier"
PROJECTION_MARKERS = ("## priority", "| sev2 | many | P1 |")

MUTATION_SPEC = {
    "added": [
        "rule:priority:8 in=[sev3,none] out=[P3]",
        "table:priority policy=unique inputs=2 outputs=1 rules=9 annotated=2",
        "count:rules=13",
    ],
    "removed": [
        "table:priority policy=unique inputs=2 outputs=1 rules=8 annotated=2",
        "count:rules=12",
        "gap:input-uncovered:priority(sev3,none)",
    ],
}


def validate(doc):
    """Validate a DTL document; return a normalized dict or raise."""
    if not isinstance(doc, dict):
        raise ValidationError(["document must be a JSON object"])
    errors = []
    if doc.get("schema") != SCHEMA:
        errors.append(f"unsupported schema: {doc.get('schema')!r}, expected {SCHEMA!r}")
    name = doc.get("name")
    if not isinstance(name, str) or not name:
        errors.append("name must be a non-empty string")
    tables = doc.get("tables")
    if not isinstance(tables, list):
        errors.append("tables must be a list")
        tables = []

    by_id = {}
    for i, t in enumerate(tables):
        if not isinstance(t, dict) or not isinstance(t.get("id"), str) or not t["id"]:
            errors.append(f"tables[{i}] must be an object with a non-empty string id")
            continue
        for key in t:
            if key in FORBIDDEN_KEYS:
                errors.append(f"forbidden workflow key {key!r} in table {t['id']!r}")
            elif key not in TABLE_KEYS:
                errors.append(f"table {t['id']!r}: unknown key {key!r}")
        if t["id"] in by_id:
            errors.append(f"duplicate table id {t['id']!r}")
            continue
        if t.get("hit_policy") not in HIT_POLICIES:
            errors.append(
                f"table {t['id']!r}: unsupported hit policy {t.get('hit_policy')!r} "
                f"(supported: {', '.join(HIT_POLICIES)}; First and Rule Order are "
                "excluded by design because row order would carry meaning)"
            )
        inputs = t.get("inputs")
        outputs = t.get("outputs")
        for section, entry in (("inputs", inputs), ("outputs", outputs)):
            if not isinstance(entry, list) or not entry:
                errors.append(f"table {t['id']!r}: {section} must be a non-empty list")
        if isinstance(inputs, list):
            for j, inp in enumerate(inputs):
                if not isinstance(inp, dict) or not isinstance(inp.get("name"), str):
                    errors.append(f"table {t['id']!r} inputs[{j}]: needs a string name")
                elif inp.get("type") not in ("enum", "string", "number"):
                    errors.append(f"table {t['id']!r} inputs[{j}]: unknown type {inp.get('type')!r}")
                elif inp["type"] == "enum" and not isinstance(inp.get("values"), list):
                    errors.append(f"table {t['id']!r} inputs[{j}]: enum needs a values list")
                src = inp.get("input_from")
                if src is not None:
                    if not isinstance(src, str) or "." not in src:
                        errors.append(f"table {t['id']!r} inputs[{j}]: input_from must be '<table>.<output>'")
        if isinstance(outputs, list):
            for j, out in enumerate(outputs):
                if not isinstance(out, dict) or not isinstance(out.get("name"), str):
                    errors.append(f"table {t['id']!r} outputs[{j}]: needs a string name")
                elif out.get("type") != "enum" or not isinstance(out.get("values"), list):
                    errors.append(f"table {t['id']!r} outputs[{j}]: outputs must be enums with values")
        by_id[t["id"]] = t

    # input_from references must resolve to a feeding table's output; the
    # table graph must be acyclic.
    for t in by_id.values():
        for inp in t.get("inputs", []) if isinstance(t.get("inputs"), list) else []:
            src = inp.get("input_from")
            if src is None:
                continue
            parts = src.split(".", 1)
            if len(parts) != 2 or parts[0] not in by_id:
                errors.append(f"table {t['id']!r}: input_from {src!r} names no table")
                continue
            names = [o["name"] for o in by_id[parts[0]].get("outputs", [])]
            if parts[1] not in names:
                errors.append(f"table {t['id']!r}: input_from {src!r} names no output")
    for start in sorted(by_id):
        deps = {
            t["id"]: [
                inp["input_from"].split(".", 1)[0]
                for inp in t.get("inputs", [])
                if inp.get("input_from")
            ]
            for t in by_id.values()
        }
        seen = set()
        cur = start
        while deps.get(cur):
            if cur in seen:
                errors.append(f"input_from cycle at table {cur!r}")
                break
            seen.add(cur)
            cur = deps[cur][0]

    # Rules: shape, value legality, duplication, and unique-policy overlap.
    for t in by_id.values():
        inputs = t.get("inputs", [])
        outputs = t.get("outputs", [])
        rules = t.get("rules")
        if not isinstance(rules, list):
            errors.append(f"table {t['id']!r}: rules must be a list")
            continue
        seen_vectors = []
        for j, rule in enumerate(rules):
            if not isinstance(rule, dict):
                errors.append(f"table {t['id']!r} rules[{j}]: rule must be an object")
                continue
            for key in rule:
                if key in FORBIDDEN_KEYS:
                    errors.append(f"forbidden workflow key {key!r} in {t['id']!r} rules[{j}]")
                elif key not in ("in", "out", "note", "cites"):
                    errors.append(f"table {t['id']!r} rules[{j}]: unknown key {key!r}")
            cells = rule.get("in")
            if not isinstance(cells, list) or len(cells) != len(inputs):
                errors.append(f"table {t['id']!r} rules[{j}]: needs one input cell per input")
                continue
            for k, (cell, inp) in enumerate(zip(cells, inputs)):
                if cell == "-":
                    continue
                if inp["type"] == "enum" and cell not in inp["values"]:
                    errors.append(
                        f"table {t['id']!r} rules[{j}] input {inp['name']!r}: "
                        f"{cell!r} is not an allowed value"
                    )
                if inp["type"] == "number" and not isinstance(cell, (int, float)):
                    errors.append(f"table {t['id']!r} rules[{j}] input {inp['name']!r}: needs a number")
            outs = rule.get("out")
            if not isinstance(outs, list) or len(outs) != len(outputs):
                errors.append(f"table {t['id']!r} rules[{j}]: needs one output cell per output")
                continue
            for k, (cell, out) in enumerate(zip(outs, outputs)):
                if cell not in out["values"]:
                    errors.append(
                        f"table {t['id']!r} rules[{j}] output {out['name']!r}: "
                        f"{cell!r} is not an allowed value"
                    )
            if cells in seen_vectors:
                errors.append(f"table {t['id']!r}: duplicate rule with inputs {cells!r}")
            seen_vectors.append(cells)
        if t.get("hit_policy") == "unique":
            for a in range(len(seen_vectors)):
                for b in range(a + 1, len(seen_vectors)):
                    if _overlaps(seen_vectors[a], seen_vectors[b]):
                        errors.append(
                            f"table {t['id']!r}: unique hit policy violated; rules "
                            f"{seen_vectors[a]!r} and {seen_vectors[b]!r} can both match"
                        )

    if errors:
        raise ValidationError(errors)
    return {"name": name, "tables": sorted(by_id.values(), key=lambda t: t["id"])}


def _overlaps(va, vb):
    """Two input vectors overlap when no position has two different values."""
    return all(a == "-" or b == "-" or a == b for a, b in zip(va, vb))


def _matches_rule(cells, values):
    return all(c == "-" or c == v for c, v in zip(cells, values))


def _table_order(v):
    """Topological order of tables derived from input_from references."""
    deps = {
        t["id"]: [
            inp["input_from"].split(".", 1)[0]
            for inp in t.get("inputs", [])
            if inp.get("input_from")
        ]
        for t in v["tables"]
    }
    order = []
    remaining = sorted(deps)
    while remaining:
        ready = [tid for tid in remaining if not [d for d in deps[tid] if d in remaining]]
        if not ready:
            raise ValidationError([f"input_from cycle among: {', '.join(remaining)}"])
        for tid in sorted(ready):
            order.append(tid)
            remaining.remove(tid)
    return order


def evaluate_table(v, table, input_values):
    """Evaluate one table; returns (outputs, matched rule indexes) or raises."""
    inputs = table["inputs"]
    names = [i["name"] for i in inputs]
    values = [input_values[n] for n in names]
    matched = [
        (idx, rule)
        for idx, rule in enumerate(table.get("rules", []))
        if _matches_rule(rule["in"], values)
    ]
    outputs = table["outputs"]
    if table["hit_policy"] == "unique" or table["hit_policy"] == "priority":
        if not matched:
            return None, []
        if table["hit_policy"] == "unique" and len(matched) > 1:
            raise ValidationError(
                [f"table {table['id']!r}: unique policy violated at evaluation"]
            )
        if table["hit_policy"] == "priority":
            best = min(
                matched,
                key=lambda pair: outputs[0]["values"].index(pair[1]["out"][0]),
            )
            return dict(zip((o["name"] for o in outputs), best[1]["out"])), [best[0]]
        rule = matched[0][1]
        return dict(zip((o["name"] for o in outputs), rule["out"])), [matched[0][0]]
    # collect: all matched outputs, sorted.
    collected = {}
    for _, rule in matched:
        for out, cell in zip(outputs, rule["out"]):
            collected.setdefault(out["name"], []).append(cell)
    return {k: sorted(vals) for k, vals in collected.items()}, [idx for idx, _ in matched]


def summary(v):
    """Deterministic, keyed summary lines for validated tables."""
    lines = []
    rule_total = 0
    for t in v["tables"]:
        rules = t.get("rules", [])
        rule_total += len(rules)
        annotated = sum(1 for r in rules if r.get("note") or r.get("cites"))
        lines.append(
            f"table:{t['id']} policy={t['hit_policy']} inputs={len(t['inputs'])} "
            f"outputs={len(t['outputs'])} rules={len(rules)} annotated={annotated}"
        )
        for idx, rule in enumerate(rules):
            cells = ",".join(str(c) for c in rule["in"])
            outs = ",".join(str(c) for c in rule["out"])
            lines.append(f"rule:{t['id']}:{idx} in=[{cells}] out=[{outs}]")
    lines.append(f"count:tables={len(v['tables'])}")
    lines.append(f"count:rules={rule_total}")
    # Coverage gaps for fully-enumerable (all-enum) tables.
    for t in v["tables"]:
        if not all(i["type"] == "enum" for i in t["inputs"]):
            continue
        covered = set()
        for rule in t.get("rules", []):
            covered |= _covered_cells(rule["in"], [i["values"] for i in t["inputs"]])
        for combo in _all_cells([i["values"] for i in t["inputs"]]):
            if combo not in covered:
                lines.append(f"gap:input-uncovered:{t['id']}({','.join(combo)})")
        if not any(r.get("note") or r.get("cites") for r in t.get("rules", [])):
            lines.append(f"gap:table-no-annotation:{t['id']}")
    return lines


def _all_cells(value_lists):
    combos = [()]
    for values in value_lists:
        combos = [c + (v,) for c in combos for v in values]
    return [tuple(c) for c in combos]


def _covered_cells(cells, value_lists):
    """Expand wildcard cells into the concrete input combinations they cover."""
    return set(_all_cells(
        [values if cell == "-" else [cell] for cell, values in zip(cells, value_lists)]
    ))


def project(v):
    """Render each table as a deterministic markdown table."""
    out = []
    for t in v["tables"]:
        out.append(f"## {t['id']} (hit_policy={t['hit_policy']})")
        header = [i["name"] for i in t["inputs"]] + [o["name"] for o in t["outputs"]]
        out.append("| " + " | ".join(header) + " |")
        out.append("|" + "---|" * len(header))
        for rule in t.get("rules", []):
            cells = [str(c) for c in rule["in"]] + [str(c) for c in rule["out"]]
            out.append("| " + " | ".join(cells) + " |")
        out.append("")
    return "\n".join(out).rstrip()


def trace(v, target):
    """Evaluate the declared input bundle and trace outputs to rules."""
    if target != "response.tier":
        raise KeyError(f"unknown trace target: {target}")
    lines = [f"target:{target}"]
    facts = dict(EVAL_INPUTS)
    for tid in _table_order(v):
        table = next(t for t in v["tables"] if t["id"] == tid)
        inputs = {i["name"]: facts[i["name"]] for i in table["inputs"]}
        rendered = ",".join(f"{k}={inputs[k]}" for k in sorted(inputs))
        lines.append(f"table:{tid} inputs={rendered}")
        outs, _ = evaluate_table(v, table, inputs)
        values = [inputs[i["name"]] for i in table["inputs"]]
        for idx, rule in enumerate(table["rules"]):
            if not _matches_rule(rule["in"], values):
                continue
            cells = ",".join(str(c) for c in rule["in"])
            outs_r = ",".join(str(c) for c in rule["out"])
            lines.append(f"rule:{tid}:{idx} in=[{cells}] out=[{outs_r}]")
            for cite in sorted(rule.get("cites", [])):
                lines.append(f"cite:{cite}")
        if outs is None:
            lines.append(f"output:{tid}=none")
        else:
            for key in sorted(outs):
                val = outs[key]
                if isinstance(val, list):
                    val = "[" + ",".join(val) + "]"
                lines.append(f"output:{tid}.{key}={val}")
            facts.update(outs)
    return lines


def observed_metrics(v):
    rules = [r for t in v["tables"] for r in t.get("rules", [])]
    grounded = sum(1 for r in rules if r.get("cites"))
    annotated = sum(1 for r in rules if r.get("note"))
    return {
        "entities": len(rules),
        "evidence_coverage": grounded / len(rules) if rules else 1.0,
        "forbidden_key_count": 0,
        "extension_key_count": annotated,
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
            "note": f"{m['evidence_coverage']:.2f} of rules carry cites; unannotated "
            "rules are legal and surfaced as gaps",
        },
        {
            "criterion": "referential_integrity",
            "score": 3 if m["dangling_refs"] == 0 else 0,
            "basis": "observed",
            "metric": "dangling_refs",
            "note": "0 dangling input_from references after validation",
        },
        {
            "criterion": "escape_hatch_usage",
            "score": 3 if m["extension_key_count"] > 0 else 0,
            "basis": "observed",
            "metric": "extension_key_count",
            "note": f"{m['extension_key_count']} rules use the free-text note hatch",
        },
        {
            "criterion": "workflow_leakage",
            "score": 3 if m["forbidden_key_count"] == 0 else 0,
            "basis": "observed",
            "metric": "forbidden_key_count",
            "note": "0 forbidden order keys; First and Rule Order hit policies are "
            "rejected by validation by design",
        },
        {
            "criterion": "explainability",
            "score": 3,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment (Vibe, not Astra): decision tables are the most "
            "reviewed-by-non-programmers format in DMN practice; the table projection "
            "renders without tooling. Not measured with users.",
        },
        {
            "criterion": "edit_locality",
            "score": 2,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment: adding a rule moves its own line and the table's "
            "count, but coverage-gap lines can also appear or disappear, so edits "
            "have one indirect line of movement.",
        },
    ]
