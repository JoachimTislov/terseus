"""Harness: loads each language's JSON documents, validates them, produces
deterministic summaries, and runs the six sub-experiments per language.

Sub-experiments (identical meaning for every language):
  1 declaration            — load + validate + deterministic summary
  2 invalid-input          — every invalid_*.json must be rejected with the
                             expected located error
  3 mutation/locality      — sample vs mutated summary diff must equal the
                             module's declared MUTATION_SPEC exactly
  4 projection/rendering   — deterministic alternative rendering containing
                             the module's declared markers
  5 provenance/trace       — evidence trace for the declared target
  6 practical-fit          — six-criterion scorecard; observed entries must
                             recompute from observed_metrics
"""

from __future__ import annotations

import json
from pathlib import Path

from . import anl, dtl, drl, pdl, pvl, scl
from .errors import ValidationError

SUBEXPERIMENTS = (
    "declaration",
    "invalid-input validation",
    "mutation/locality",
    "projection/rendering",
    "provenance/evidence trace",
    "practical-fit scorecard",
)

LANGUAGES = {
    "anl": anl,
    "scl": scl,
    "pvl": pvl,
    "pdl": pdl,
    "dtl": dtl,
    "drl": drl,
}

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


def sample_path(lang, filename):
    """Path of a sample file for a language key."""
    if lang not in LANGUAGES:
        raise KeyError(f"unknown language: {lang!r} (known: {', '.join(sorted(LANGUAGES))})")
    return SAMPLES_DIR / lang / filename


def load_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def load_document(lang, filename="sample.json"):
    return load_json(sample_path(lang, filename))


def validate(lang, doc):
    """Validate a document in the named language."""
    if lang not in LANGUAGES:
        raise KeyError(f"unknown language: {lang!r} (known: {', '.join(sorted(LANGUAGES))})")
    return LANGUAGES[lang].validate(doc)


def _result(lang, n, ok, detail, data=None):
    return {
        "language": lang,
        "subexperiment": n,
        "name": SUBEXPERIMENTS[n - 1],
        "status": "pass" if ok else "fail",
        "detail": detail,
        "data": data,
    }


def run_declaration(lang):
    module = LANGUAGES[lang]
    doc = load_document(lang)
    v = module.validate(doc)
    lines = module.summary(v)
    again = module.summary(module.validate(load_document(lang)))
    if lines != again:
        raise AssertionError("summary is not deterministic")
    if not lines:
        raise AssertionError("summary is empty")
    if len(set(lines)) != len(lines):
        raise AssertionError("summary lines are not unique")
    ok = all(isinstance(line, str) for line in lines)
    return _result(lang, 1, ok, f"{len(lines)} deterministic summary lines", lines)


def run_invalid(lang):
    module = LANGUAGES[lang]
    cases = sorted(SAMPLES_DIR.joinpath(lang).glob("invalid_*.json"))
    if not cases:
        raise AssertionError(f"no invalid_* cases found for {lang}")
    rejected = 0
    problems = []
    for case in cases:
        wrapper = load_json(case)
        expect = wrapper.get("expect_error", "")
        try:
            module.validate(wrapper["document"])
        except ValidationError as err:
            if expect and expect not in str(err):
                problems.append(f"{case.name}: expected error containing {expect!r}, got {err}")
            rejected += 1
        except Exception as err:  # noqa: BLE001 - any rejection reason is recorded
            problems.append(f"{case.name}: unexpected error type {type(err).__name__}: {err}")
        else:
            problems.append(f"{case.name}: document was accepted but must be rejected")
    if problems:
        raise AssertionError("; ".join(problems))
    return _result(lang, 2, True, f"{rejected} invalid documents rejected with located errors", rejected)


def run_mutation(lang):
    module = LANGUAGES[lang]
    base = module.summary(module.validate(load_document(lang, "sample.json")))
    mutated = module.summary(module.validate(load_document(lang, "mutated.json")))
    spec = module.MUTATION_SPEC
    if len(set(base)) != len(base) or len(set(mutated)) != len(mutated):
        raise AssertionError("summary lines are not unique")
    added = sorted(set(mutated) - set(base))
    removed = sorted(set(base) - set(mutated))
    expected_added = sorted(spec["added"])
    expected_removed = sorted(spec["removed"])
    if added != expected_added or removed != expected_removed:
        raise AssertionError(
            "summary diff is not local to the declared mutation\n"
            f"added: {added}\nexpected added: {expected_added}\n"
            f"removed: {removed}\nexpected removed: {expected_removed}"
        )
    return _result(
        lang, 3, True,
        f"{len(added)} lines added, {len(removed)} removed, all within declared scope",
        {"added": added, "removed": removed},
    )


def run_projection(lang):
    module = LANGUAGES[lang]
    v = module.validate(load_document(lang))
    text = module.project(v)
    again = module.project(module.validate(load_document(lang)))
    if text != again:
        raise AssertionError("projection is not deterministic")
    missing = [m for m in module.PROJECTION_MARKERS if m not in text]
    if missing:
        raise AssertionError(f"projection missing markers: {missing}")
    return _result(lang, 4, True, f"deterministic projection, {len(text.splitlines())} lines", text)


def run_provenance(lang):
    module = LANGUAGES[lang]
    v = module.validate(load_document(lang))
    lines = module.trace(v, module.TRACE_TARGET)
    again = module.trace(module.validate(load_document(lang)), module.TRACE_TARGET)
    if lines != again:
        raise AssertionError("trace is not deterministic")
    if not lines:
        raise AssertionError("trace is empty")
    if module.TRACE_TARGET.split(":")[0] not in lines[0]:
        raise AssertionError(f"trace does not start at target {module.TRACE_TARGET!r}: {lines[0]}")
    return _result(lang, 5, True, f"evidence trace for {module.TRACE_TARGET}: {len(lines)} lines", lines)


def run_scorecard(lang):
    module = LANGUAGES[lang]
    v = module.validate(load_document(lang))
    cards = module.scorecard(v)
    again = module.scorecard(module.validate(load_document(lang)))
    if cards != again:
        raise AssertionError("scorecard is not deterministic")
    problems = []
    for card in cards:
        for key in ("criterion", "score", "basis", "note"):
            if key not in card:
                problems.append(f"scorecard entry missing {key!r}")
        if card.get("score") not in (0, 1, 2, 3):
            problems.append(f"criterion {card.get('criterion')!r}: score out of range")
        if card.get("basis") not in ("observed", "judgment"):
            problems.append(f"criterion {card.get('criterion')!r}: bad basis")
        if card.get("basis") == "observed":
            metrics = module.observed_metrics(v)
            metric = card.get("metric")
            if metric not in metrics:
                problems.append(f"criterion {card.get('criterion')!r}: unknown metric {metric!r}")
            elif str(metrics[metric]) not in card["note"] and f"{metrics[metric]:.2f}" not in card["note"]:
                problems.append(f"criterion {card.get('criterion')!r}: note does not recompute metric {metric!r}")
    if problems:
        raise AssertionError("; ".join(problems))
    total = sum(c["score"] for c in cards)
    return _result(lang, 6, True, f"scorecard {total}/18 across 6 criteria", cards)


_RUNNERS = {
    1: run_declaration,
    2: run_invalid,
    3: run_mutation,
    4: run_projection,
    5: run_provenance,
    6: run_scorecard,
}


def run_subexperiment(lang, n):
    """Run one sub-experiment; return a result dict.

    A failing sub-experiment raises, so callers can treat any return as a
    pass; the harness never fabricates a passing result.
    """
    if lang not in LANGUAGES:
        raise KeyError(f"unknown language: {lang!r} (known: {', '.join(sorted(LANGUAGES))})")
    if n not in _RUNNERS:
        raise KeyError(f"unknown sub-experiment: {n!r} (expected 1..6)")
    return _RUNNERS[n](lang)


def run_all():
    """Run the full 6x6 matrix: six languages x six sub-experiments."""
    results = []
    for lang in sorted(LANGUAGES):
        for n in range(1, 7):
            results.append(run_subexperiment(lang, n))
    return results
