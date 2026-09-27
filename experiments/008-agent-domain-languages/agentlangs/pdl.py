"""PDL — Policy Decision Language (OPA/Rego inspired).

Documents declare unordered rules that assert decisions (allow / deny /
escalate) over structured incident facts. Rules are assertions on data, not
steps: evaluation collects every matching rule, and disagreement between two
matching non-default rules is an error, never a silent precedence. The
optional single default rule fires only when nothing else matches.

Semantic center: unordered decision assertions with conflict-as-error.
Escape hatch: free-text ``note`` fields, and ``cites`` entries are free
strings (policy citations are not a closed registry); uncited rules are
legal and surfaced as gaps.
"""

from __future__ import annotations

from .errors import ValidationError

SCHEMA = "pdl/1"
NAME = "Policy Decision Language (OPA/Rego inspired)"

DECISIONS = ("allow", "deny", "escalate")
OPS = ("eq", "neq", "in", "lt", "gt")
RULE_KEYS = ("id", "decision", "when", "cites", "note", "default")
FORBIDDEN_KEYS = ("step", "order", "next", "then", "before", "after", "trigger", "sequence", "priority")

# Fact bundle used by the provenance/evidence-trace sub-experiment: a
# concrete situation the policy is evaluated against.
EVAL_FACTS = {
    "action": "close",
    "actor": {"role": "analyst"},
    "incident": {"severity": "sev2"},
}

TRACE_TARGET = "decision:close"
PROJECTION_MARKERS = ("policy incident-access-policy", "deny when action = close")

MUTATION_SPEC = {
    "added": [
        "rule:escalate-customer-visible decision=escalate conds=1 default=False cites=1",
        "decision:escalate count=2",
        "count:rules=6",
    ],
    "removed": [
        "decision:escalate count=1",
        "count:rules=5",
    ],
}


class EvalConflictError(ValueError):
    """Raised when two matching non-default rules assert different decisions."""


def validate(doc):
    """Validate a PDL document; return a normalized dict or raise."""
    if not isinstance(doc, dict):
        raise ValidationError(["document must be a JSON object"])
    errors = []
    if doc.get("schema") != SCHEMA:
        errors.append(f"unsupported schema: {doc.get('schema')!r}, expected {SCHEMA!r}")
    name = doc.get("name")
    if not isinstance(name, str) or not name:
        errors.append("name must be a non-empty string")
    rules = doc.get("rules")
    if not isinstance(rules, list):
        errors.append("rules must be a list")
        rules = []

    ids = set()
    defaults = 0
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict) or not isinstance(rule.get("id"), str) or not rule["id"]:
            errors.append(f"rules[{i}] must be an object with a non-empty string id")
            continue
        for key in rule:
            if key in FORBIDDEN_KEYS:
                errors.append(f"forbidden workflow key {key!r} in rule {rule['id']!r}")
            elif key not in RULE_KEYS:
                errors.append(f"rule {rule['id']!r}: unknown key {key!r}")
        if rule["id"] in ids:
            errors.append(f"duplicate rule id {rule['id']!r}")
        ids.add(rule["id"])
        if rule.get("decision") not in DECISIONS:
            errors.append(f"rule {rule['id']!r}: decision must be one of {', '.join(DECISIONS)}")
        if rule.get("default"):
            defaults += 1
            if rule.get("when"):
                errors.append(f"rule {rule['id']!r}: a default rule must have no conditions")
        when = rule.get("when", [])
        if not isinstance(when, list):
            errors.append(f"rule {rule['id']!r}: when must be a list of conditions")
            continue
        for j, cond in enumerate(when):
            if not isinstance(cond, dict):
                errors.append(f"rule {rule['id']!r} when[{j}]: condition must be an object")
                continue
            if cond.get("op") not in OPS:
                errors.append(f"rule {rule['id']!r} when[{j}]: unknown op {cond.get('op')!r}")
            if not isinstance(cond.get("field"), str) or not cond["field"]:
                errors.append(f"rule {rule['id']!r} when[{j}]: field must be a non-empty string")
            if cond.get("op") == "in":
                if not isinstance(cond.get("values"), list) or not cond["values"]:
                    errors.append(f"rule {rule['id']!r} when[{j}]: op 'in' needs a non-empty values list")
            elif "value" not in cond:
                errors.append(f"rule {rule['id']!r} when[{j}]: op {cond.get('op')!r} needs a value")
            elif cond.get("op") in ("lt", "gt") and not isinstance(cond["value"], (int, float)):
                errors.append(f"rule {rule['id']!r} when[{j}]: op {cond.get('op')!r} needs a numeric value")
        cites = rule.get("cites", [])
        if not isinstance(cites, list) or not all(isinstance(c, str) and c for c in cites):
            errors.append(f"rule {rule['id']!r}: cites must be a list of non-empty strings")
    if defaults > 1:
        errors.append(f"{defaults} default rules; at most one is allowed")

    if errors:
        raise ValidationError(errors)
    return {"name": name, "rules": sorted(rules, key=lambda r: r["id"])}


def _lookup(facts, path):
    cur = facts
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _matches(rule, facts):
    for cond in rule.get("when", []):
        actual = _lookup(facts, cond["field"])
        op = cond["op"]
        if op == "eq":
            if actual != cond["value"]:
                return False
        elif op == "neq":
            if actual == cond["value"]:
                return False
        elif op == "in":
            if actual not in cond["values"]:
                return False
        elif op == "lt":
            if not isinstance(actual, (int, float)) or not actual < cond["value"]:
                return False
        elif op == "gt":
            if not isinstance(actual, (int, float)) or not actual > cond["value"]:
                return False
    return True


def evaluate(v, facts):
    """Evaluate a policy against a fact bundle.

    Returns (decision, matched_rule_ids, conflict) where conflict is None or
    the sorted pair of disagreeing rule ids. Mirrors Rego: matching rules
    must agree; a default rule covers the no-match case.
    """
    matched = [r for r in v["rules"] if not r.get("default") and _matches(r, facts)]
    decisions = {r["decision"] for r in matched}
    if len(decisions) > 1:
        first, second = sorted(decisions)
        a = next(r["id"] for r in matched if r["decision"] == first)
        b = next(r["id"] for r in matched if r["decision"] == second)
        return None, [r["id"] for r in matched], tuple(sorted((a, b)))
    if decisions:
        return decisions.pop(), [r["id"] for r in matched], None
    default = next((r for r in v["rules"] if r.get("default")), None)
    if default is None:
        return "undefined", [], None
    return default["decision"], [default["id"]], None


def summary(v):
    """Deterministic, keyed summary lines for a validated policy."""
    lines = []
    for rule in v["rules"]:
        lines.append(
            f"rule:{rule['id']} decision={rule['decision']} "
            f"conds={len(rule.get('when', []))} default={bool(rule.get('default'))} "
            f"cites={len(rule.get('cites', []))}"
        )
    counts = {}
    for rule in v["rules"]:
        counts[rule["decision"]] = counts.get(rule["decision"], 0) + 1
    for decision in sorted(counts):
        lines.append(f"decision:{decision} count={counts[decision]}")
    lines.append(f"count:rules={len(v['rules'])}")
    for rule in v["rules"]:
        if not rule.get("cites"):
            lines.append(f"gap:rule-no-cites:{rule['id']}")
    return lines


def project(v):
    """Render the policy as readable text, one line per rule, sorted by id."""
    out = [f"policy {v['name']}"]
    for rule in v["rules"]:
        conds = []
        for cond in rule.get("when", []):
            op = {"eq": "=", "neq": "!=", "in": "in", "lt": "<", "gt": ">"}[cond["op"]]
            if cond["op"] == "in":
                rendered = f"{cond['field']} {op} [{','.join(cond['values'])}]"
            else:
                rendered = f"{cond['field']} {op} {cond['value']}"
            conds.append(rendered)
        body = " AND ".join(conds) if conds else "always"
        prefix = "DEFAULT " if rule.get("default") else ""
        cites = f" [cites: {', '.join(rule['cites'])}]" if rule.get("cites") else ""
        out.append(f"- {prefix}{rule['decision']} when {body}{cites}")
    return "\n".join(out)


def trace(v, target):
    """Trace a decision for the declared fact bundle back to rules and cites."""
    if target != "decision:close":
        raise KeyError(f"unknown trace target: {target}")
    facts = EVAL_FACTS
    decision, matched, conflict = evaluate(v, facts)
    if conflict:
        raise EvalConflictError(
            f"matching rules {conflict[0]} and {conflict[1]} assert different decisions"
        )
    lines = [f"target:{target}"]
    lines.append("facts:action=close actor.role=analyst incident.severity=sev2")
    if matched:
        for rid in matched:
            lines.append(f"matched:{rid}")
    else:
        lines.append("matched:none")
    lines.append(f"decision:{decision}")
    for rid in matched:
        rule = next(r for r in v["rules"] if r["id"] == rid)
        for cite in sorted(rule.get("cites", [])):
            lines.append(f"cite:{cite}")
        if not rule.get("cites"):
            lines.append(f"cite:none:{rid}")
    return lines


def observed_metrics(v):
    cited = sum(1 for r in v["rules"] if r.get("cites"))
    notes = sum(1 for r in v["rules"] if r.get("note"))
    _, _, conflict = evaluate(v, EVAL_FACTS)
    return {
        "entities": len(v["rules"]),
        "evidence_coverage": cited / len(v["rules"]) if v["rules"] else 1.0,
        "forbidden_key_count": 0,
        "extension_key_count": notes,
        "dangling_refs": 1 if conflict else 0,
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
            "note": f"{m['evidence_coverage']:.2f} of rules cite a source; uncited "
            "rules are legal and surfaced as gaps",
        },
        {
            "criterion": "referential_integrity",
            "score": 3 if m["dangling_refs"] == 0 else 0,
            "basis": "observed",
            "metric": "dangling_refs",
            "note": "0 rule conflicts on the declared fact bundle "
            "(conflicts are errors, never precedence)",
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
            "note": "0 forbidden order/priority keys; rule order carries no meaning",
        },
        {
            "criterion": "explainability",
            "score": 3,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment (Vibe, not Astra): decisions-as-code with one "
            "line per rule matches how OPA users read allow/deny lists; conflicts "
            "erroring loudly aids review. Not measured with users.",
        },
        {
            "criterion": "edit_locality",
            "score": 3,
            "basis": "judgment",
            "metric": None,
            "note": "Design judgment: rules are independent assertions, so adding "
            "one rule cannot move another rule's lines; demonstrated by "
            "sub-experiment 3.",
        },
    ]
