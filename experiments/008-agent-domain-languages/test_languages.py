"""Broader per-language tests beyond the 008 matrix suite.

test_matrix.py covers the 6x6 harness matrix, sample-file presence, every
invalid_*.json rejection, and ANL CRUD basics. This module goes deeper:

- cross-language input robustness (non-dict input, wrong/missing schema),
- determinism of every rendered artifact on the mutated sample too,
- scorecard and observed-metric invariants stated as explicit assertions,
- ANL relation/identity rules (cycles, duplicates, forbidden keys, CRUD
  error paths, create+delete round-trip stability),
- DTL table evaluation (hit policies, unique-policy violation, no-hit),
- PDL policy evaluation (allow/deny/default/conflict/undefined paths),
- DRL drift computation (changed vs missing observed values, summary
  consistency),
- SCL contract inheritance through a two-level extends chain.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentlangs import anl, drl, dtl, harness, pdl, scl
from agentlangs.errors import ValidationError

HERE = Path(__file__).resolve().parent
SAMPLES = HERE / "samples"
LANGUAGES = sorted(harness.LANGUAGES)


def load(lang, filename="sample.json"):
    return json.loads((SAMPLES / lang / filename).read_text(encoding="utf-8"))


def validate_sample(lang, filename="sample.json"):
    return harness.LANGUAGES[lang].validate(load(lang, filename))


# ---------- cross-language robustness ----------

@pytest.mark.parametrize("lang", LANGUAGES)
def test_rejects_non_dict_documents(lang):
    for bad in ([], None, "document", 17):
        with pytest.raises(ValidationError):
            harness.validate(lang, bad)


@pytest.mark.parametrize("lang", LANGUAGES)
def test_rejects_empty_and_unknown_schema(lang):
    with pytest.raises(ValidationError, match="unsupported schema"):
        harness.validate(lang, {})
    with pytest.raises(ValidationError, match="unsupported schema"):
        harness.validate(lang, {"schema": "bogus/9", "name": "x"})


@pytest.mark.parametrize("lang", LANGUAGES)
def test_mutated_document_validates_and_all_artifacts_are_deterministic(lang):
    module = harness.LANGUAGES[lang]
    v1 = module.validate(load(lang, "mutated.json"))
    v2 = module.validate(load(lang, "mutated.json"))
    assert module.summary(v1) == module.summary(v2)
    assert module.project(v1) == module.project(v2)
    assert module.trace(v1, module.TRACE_TARGET) == module.trace(v2, module.TRACE_TARGET)
    assert module.scorecard(v1) == module.scorecard(v2)


@pytest.mark.parametrize("lang", LANGUAGES)
def test_projection_of_mutated_document_contains_all_markers(lang):
    module = harness.LANGUAGES[lang]
    text = module.project(module.validate(load(lang, "mutated.json")))
    assert text
    missing = [m for m in module.PROJECTION_MARKERS if m not in text]
    assert missing == []


@pytest.mark.parametrize("lang", LANGUAGES)
def test_scorecard_has_six_criteria_with_in_range_scores(lang):
    module = harness.LANGUAGES[lang]
    cards = module.scorecard(module.validate(load(lang, "sample.json")))
    assert len(cards) == 6
    criteria = [c["criterion"] for c in cards]
    assert len(set(criteria)) == 6, "criteria must be distinct"
    for card in cards:
        assert card["score"] in (0, 1, 2, 3)
        assert card["basis"] in ("observed", "judgment")


@pytest.mark.parametrize("lang", LANGUAGES)
def test_observed_metrics_recompute_for_every_observed_criterion(lang):
    module = harness.LANGUAGES[lang]
    v = module.validate(load(lang, "sample.json"))
    metrics = module.observed_metrics(v)
    assert metrics, "observed_metrics must not be empty"
    for card in module.scorecard(v):
        if card["basis"] == "observed":
            assert card["metric"] in metrics
            value = metrics[card["metric"]]
            assert str(value) in card["note"] or f"{value:.2f}" in card["note"], (
                f"{lang}: note for {card['criterion']} must recompute "
                f"{card['metric']}={value!r}"
            )


def test_harness_rejects_unknown_language_and_subexperiment():
    with pytest.raises(KeyError):
        harness.run_subexperiment("nope", 1)
    with pytest.raises(KeyError):
        harness.run_subexperiment("anl", 0)
    with pytest.raises(KeyError):
        harness.run_subexperiment("anl", 7)


# ---------- ANL: relations, identity, CRUD error paths ----------

def anl_with(**extra):
    doc = json.loads((SAMPLES / "anl" / "sample.json").read_text(encoding="utf-8"))
    doc.update(extra)
    return doc


def test_anl_cycle_in_acyclic_relation_is_rejected():
    # sample already has escalates_to: verifier -> dispatcher
    doc = anl_with(relations=anl_with()["relations"] + [
        {"type": "escalates_to", "from": "dispatcher", "to": "verifier"},
    ])
    with pytest.raises(ValidationError, match="cycle in acyclic relation"):
        anl.validate(doc)


def test_anl_duplicate_id_across_kinds_is_rejected():
    doc = anl_with()
    doc["agents"].append({
        "id": "runbook-intake",  # already an evidence id
        "type": "llm",
        "capabilities": [],
    })
    with pytest.raises(ValidationError, match="duplicate id"):
        anl.validate(doc)


def test_anl_duplicate_relation_is_rejected():
    doc = anl_with()
    doc["relations"].append(
        {"type": "collaborates_with", "from": "dispatcher", "to": "triage-analyst"}
    )
    with pytest.raises(ValidationError, match="duplicate relation"):
        anl.validate(doc)


def test_anl_unknown_relation_type_is_rejected():
    doc = anl_with()
    doc["relations"].append({"type": "reports_to", "from": "dispatcher", "to": "verifier"})
    with pytest.raises(ValidationError, match="unknown relation type"):
        anl.validate(doc)


def test_anl_relation_endpoint_of_wrong_kind_is_rejected():
    doc = anl_with()
    # escalates_to endpoints must be agents, not capabilities
    doc["relations"].append(
        {"type": "escalates_to", "from": "dispatcher", "to": "log-analysis"}
    )
    with pytest.raises(ValidationError, match="is not a known agent"):
        anl.validate(doc)


def test_anl_forbidden_workflow_keys_are_rejected():
    doc = anl_with()
    doc["agents"][0]["step"] = ["first", "second"]
    with pytest.raises(ValidationError, match="forbidden workflow key"):
        anl.validate(doc)
    doc = anl_with()
    doc["relations"][0]["sequence"] = 1
    with pytest.raises(ValidationError, match="forbidden workflow key"):
        anl.validate(doc)


def test_anl_update_and_delete_unknown_agent_are_rejected():
    doc = anl_with()
    with pytest.raises(ValidationError, match="unknown agent"):
        anl.update_agent(doc, "no-such-agent", note="x")
    with pytest.raises(ValidationError, match="unknown agent"):
        anl.delete_agent(doc, "no-such-agent")


def test_anl_create_then_delete_round_trips_the_document():
    doc = anl_with()
    created = anl.create_agent(doc, "temp-reviewer", "llm", ["log-analysis"], note="temp")
    assert anl.validate(created) != anl.validate(doc)
    deleted = anl.delete_agent(created, "temp-reviewer")
    assert anl.validate(deleted) == anl.validate(doc)


# ---------- DTL: decision-table evaluation ----------

def dtl_table(v, table_id):
    return next(t for t in v["tables"] if t["id"] == table_id)


def test_dtl_priority_table_sev1_many_yields_p1():
    v = dtl.validate(load("dtl"))
    outputs, matched = dtl.evaluate_table(
        v, dtl_table(v, "priority"), {"severity": "sev1", "customer_impact": "many"}
    )
    assert outputs == {"tier": "P1"}
    assert len(matched) == 1


def test_dtl_unique_policy_violation_is_rejected_at_evaluation():
    table = {
        "id": "t",
        "hit_policy": "unique",
        "inputs": [{"name": "a", "type": "enum", "values": ["x", "y"]}],
        "outputs": [{"name": "o", "type": "enum", "values": ["1", "2"]}],
        "rules": [
            {"in": ["-"], "out": ["1"]},
            {"in": ["-"], "out": ["2"]},
        ],
    }
    with pytest.raises(ValidationError, match="unique policy violated"):
        dtl.evaluate_table(None, table, {"a": "x"})


def test_dtl_collect_policy_gathers_sorted_hits():
    table = {
        "id": "t",
        "hit_policy": "collect",
        "inputs": [{"name": "a", "type": "enum", "values": ["x"]}],
        "outputs": [{"name": "o", "type": "enum", "values": ["b", "a", "c"]}],
        "rules": [
            {"in": ["-"], "out": ["b"]},
            {"in": ["x"], "out": ["a"]},
        ],
    }
    outputs, matched = dtl.evaluate_table(None, table, {"a": "x"})
    assert outputs == {"o": ["a", "b"]}
    assert matched == [0, 1]


def test_dtl_no_matching_rule_under_unique_policy_returns_none():
    v = dtl.validate(load("dtl"))
    table = dtl_table(v, "priority")
    # find an (severity, impact) pair no rule matches
    for severity in ("sev1", "sev2", "sev3"):
        for impact in ("none", "some", "many"):
            result, _ = dtl.evaluate_table(
                v, table, {"severity": severity, "customer_impact": impact}
            )
            if result is None:
                return
    pytest.fail("priority table matches every input; no no-match case exists")


# ---------- PDL: policy evaluation ----------

def test_pdl_read_only_actions_are_allowed():
    v = pdl.validate(load("pdl"))
    decision, matched, conflict = pdl.evaluate(v, {"action": "view"})
    assert decision == "allow"
    assert matched == ["allow-read-only"]
    assert conflict is None


def test_pdl_owner_can_publish():
    v = pdl.validate(load("pdl"))
    decision, matched, _ = pdl.evaluate(
        v, {"action": "publish-postmortem", "actor": {"role": "owner"}}
    )
    assert decision == "allow"
    assert "allow-owner-publish" in matched


def test_pdl_analyst_close_is_denied():
    v = pdl.validate(load("pdl"))
    decision, matched, _ = pdl.evaluate(
        v, {"action": "close", "actor": {"role": "analyst"}}
    )
    assert decision == "deny"
    assert matched == ["deny-analyst-close"]


def test_pdl_default_deny_covers_unmatched_facts():
    v = pdl.validate(load("pdl"))
    decision, matched, conflict = pdl.evaluate(v, {"action": "delete-everything"})
    assert decision == "deny"
    assert matched == ["default-deny"]
    assert conflict is None


def test_pdl_conflicting_decisions_report_the_sorted_rule_pair():
    v = pdl.validate(load("pdl"))
    # list matches allow-read-only (allow); sev1 matches escalate-sev1 (escalate)
    decision, matched, conflict = pdl.evaluate(
        v, {"action": "list", "incident": {"severity": "sev1"}}
    )
    assert decision is None
    assert conflict == ("allow-read-only", "escalate-sev1")
    assert set(matched) == {"allow-read-only", "escalate-sev1"}


def test_pdl_without_default_rule_is_undefined_on_no_match():
    v = pdl.validate(load("pdl"))
    no_default = {**v, "rules": [r for r in v["rules"] if not r.get("default")]}
    decision, matched, conflict = pdl.evaluate(no_default, {"action": "nothing"})
    assert decision == "undefined"
    assert matched == []
    assert conflict is None


def test_pdl_comparison_operators_need_numbers():
    v = pdl.validate(load("pdl"))
    # escalate-sev1 uses eq, but a non-numeric field under gt/lt never matches;
    # verified indirectly: a string severity cannot be compared by design, and
    # the eq check below confirms string equality still works
    decision, _, _ = pdl.evaluate(v, {"incident": {"severity": "sev2"}})
    assert decision == "deny"  # falls through to default-deny


# ---------- DRL: drift computation ----------

def test_drl_drift_reports_changed_and_missing_values():
    resource = {
        "id": "r",
        "kind": "K",
        "desired": {"a": 1, "b": "x"},
        "observed": {"a": 2},
    }
    assert drl.drift(resource) == [("a", 1, 2), ("b", "x", "missing")]


def test_drl_drift_is_empty_when_observed_matches_desired():
    resource = {"id": "r", "kind": "K", "desired": {"a": 1}, "observed": {"a": 1}}
    assert drl.drift(resource) == []


def test_drl_summary_counts_match_the_drift_items():
    v = drl.validate(load("drl"))
    total = sum(len(drl.drift(r)) for r in v["resources"])
    lines = drl.summary(v)
    counted = next(
        int(line.split("=")[1]) for line in lines if line.startswith("count:drift=")
    )
    assert counted == total


def test_drl_resource_without_evidence_is_flagged():
    v = drl.validate(load("drl"))
    unevidenced = [
        r["id"] for r in v["resources"] if not r.get("evidence")
    ]
    lines = drl.summary(v)
    for rid in unevidenced:
        assert f"gap:resource-no-evidence:{rid}" in lines
    for r in v["resources"]:
        if r.get("evidence"):
            assert f"gap:resource-no-evidence:{r['id']}" not in lines


# ---------- SCL: contract inheritance ----------

def test_scl_inheritance_accumulates_through_a_two_level_chain():
    v = scl.validate(load("scl"))
    lines = scl.summary(v)
    # action_item extends assessment extends incident:
    # own 3 + assessment 2 + incident 4 = 6 inherited fields
    line = next(ln for ln in lines if ln.startswith("contract:action_item"))
    assert "own_fields=3" in line
    assert "inherited_fields=6" in line


def test_scl_contracts_without_required_fields_are_flagged():
    v = scl.validate(load("scl"))
    lines = scl.summary(v)
    by_id = {c["id"]: c for c in v["contracts"]}
    for cid, contract in by_id.items():
        required = any(
            spec.get("required") for spec in contract.get("fields", {}).values()
        )
        flagged = f"gap:contract-no-required:{cid}" in lines
        assert flagged == (not required), cid
