"""Parameterized tests for the 008 agent-domain-language matrix.

The suite executes harness.run_all() — the same code path the CLI uses —
and asserts the full 6x6 matrix passes (36/36), runs every sub-experiment
individually, checks the required sample files, and rejects every
invalid_*.json document with its declared located error.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentlangs import anl, harness
from agentlangs.errors import ValidationError

HERE = Path(__file__).resolve().parent
SAMPLES = HERE / "samples"

LANGUAGES = sorted(harness.LANGUAGES)
SUBEXPERIMENTS = list(range(1, 7))


def test_matrix_shape_is_six_languages_by_six_subexperiments():
    assert LANGUAGES == ["anl", "drl", "dtl", "pdl", "pvl", "scl"]
    assert len(harness.SUBEXPERIMENTS) == 6
    assert SUBEXPERIMENTS == [1, 2, 3, 4, 5, 6]


def test_run_all_passes_exactly_36():
    results = harness.run_all()
    assert len(results) == 36
    failed = [r for r in results if r["status"] != "pass"]
    assert failed == []
    per_language = {}
    for result in results:
        per_language.setdefault(result["language"], []).append(result["subexperiment"])
    assert per_language == {lang: SUBEXPERIMENTS for lang in LANGUAGES}


@pytest.mark.parametrize("lang", LANGUAGES)
@pytest.mark.parametrize("n", SUBEXPERIMENTS)
def test_subexperiment_passes(lang, n):
    result = harness.run_subexperiment(lang, n)
    assert result["status"] == "pass"
    assert result["language"] == lang
    assert result["subexperiment"] == n
    assert result["name"] == harness.SUBEXPERIMENTS[n - 1]


@pytest.mark.parametrize("lang", LANGUAGES)
def test_language_directory_has_required_sample_files(lang):
    directory = SAMPLES / lang
    assert (directory / "sample.json").is_file(), f"{lang}: sample.json missing"
    assert (directory / "mutated.json").is_file(), f"{lang}: mutated.json missing"
    assert list(directory.glob("invalid_*.json")), f"{lang}: no invalid_*.json cases"


def invalid_cases():
    cases = []
    for lang in LANGUAGES:
        for path in sorted((SAMPLES / lang).glob("invalid_*.json")):
            cases.append(pytest.param(lang, path, id=f"{lang}-{path.stem}"))
    assert cases, "no invalid_* cases found anywhere"
    return cases


@pytest.mark.parametrize("lang,path", invalid_cases())
def test_invalid_document_is_rejected_with_expected_error(lang, path):
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(wrapper.get("document"), dict), f"{path.name}: no document"
    assert wrapper.get("expect_error"), f"{path.name}: no expect_error"
    with pytest.raises(ValidationError) as excinfo:
        harness.validate(lang, wrapper["document"])
    assert wrapper["expect_error"] in str(excinfo.value), (
        f"{path.name}: expected error containing {wrapper['expect_error']!r}"
    )


def test_valid_samples_are_accepted():
    for lang in LANGUAGES:
        doc = json.loads((SAMPLES / lang / "sample.json").read_text(encoding="utf-8"))
        v = harness.validate(lang, doc)
        assert v is not None


def test_agent_crud_create_read_update_delete():
    base = json.loads((SAMPLES / "anl" / "sample.json").read_text(encoding="utf-8"))
    created = anl.create_agent(
        base, "reviewer", "human", ["claim-verification"], "rotating reviewer"
    )
    assert any(agent["id"] == "reviewer" for agent in anl.validate(created)["agents"])
    reviewer = next(agent for agent in anl.validate(created)["agents"] if agent["id"] == "reviewer")
    assert reviewer["type"] == "human"
    updated = anl.update_agent(created, "reviewer", agent_type="llm", note="automated reviewer")
    reviewer = next(agent for agent in anl.validate(updated)["agents"] if agent["id"] == "reviewer")
    assert reviewer["type"] == "llm"
    assert reviewer["note"] == "automated reviewer"
    deleted = anl.delete_agent(updated, "reviewer")
    assert all(agent["id"] != "reviewer" for agent in anl.validate(deleted)["agents"])


def test_agent_delete_rejects_relation_references():
    base = json.loads((SAMPLES / "anl" / "sample.json").read_text(encoding="utf-8"))
    with pytest.raises(ValidationError, match="referenced by"):
        anl.delete_agent(base, "dispatcher")


def test_agent_create_rejects_unknown_capability():
    base = json.loads((SAMPLES / "anl" / "sample.json").read_text(encoding="utf-8"))
    with pytest.raises(ValidationError, match="unknown capability"):
        anl.create_agent(base, "reviewer", "human", ["missing"])
