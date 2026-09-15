"""
Compiles schema.yaml to every declared target. For each keyword, per
target:

  (a) if a `bindings` entry exists, wire to that hand-written function
      (cheapest, most trustworthy path -- someone already wrote and
      presumably battle-tested this), otherwise
  (b) synthesize directly for that target, constrained by the target's
      declared `style`, then verify against the contract.

This is the reactive piece: each keyword+target's synthesized code is
cached under a hash of (subject, object, contract, style). Unchanged
keywords are never re-synthesized or re-verified on subsequent runs --
only a real change to the 4/5GL source (the schema) triggers new
non-deterministic work and a fresh automated eval pass. A failed
verification never overwrites a previously-verified implementation.
"""
import hashlib
import json
import os
import subprocess

from domainkit.schema import load_domain
from domainkit.synth import MockSynthesizer, AnthropicSynthesizer
from domainkit.verify import compile_and_verify
from domainkit.targetlang import generate_go_types
from domainkit.verify_go_gen import generate_go_verifier

CACHE_PATH = "generated/.cache.json"


def _load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def _save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def _spec_hash(kdef, style):
    payload = json.dumps({
        "subject": kdef.subject, "object": kdef.object,
        "requires": kdef.contract.requires, "ensures": kdef.contract.ensures,
        "style": style,
    }, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def compile_python(domain, cache, out_path="generated/py_wiring.py"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    synthesizer = AnthropicSynthesizer() if os.environ.get("ANTHROPIC_API_KEY") else MockSynthesizer()
    style = domain.targets["python"].style if "python" in domain.targets else ""

    lines = ["# AUTO-GENERATED wiring -- do not hand-edit.\n"]
    for kname, kdef in domain.keywords.items():
        binding = kdef.bindings.get("python")
        obj_arg = ", object" if kdef.object else ""

        if binding:
            lines.append(f"from {binding['module']} import {binding['function']} as _{kname}_impl\n")
            lines.append(f"def {kname}(subject{obj_arg}):\n    _{kname}_impl(subject{', object' if kdef.object else ''})\n\n")
            print(f"[python] {kname}: wired to {binding['module']}.{binding['function']}")
            continue

        key = f"python:{kname}"
        h = _spec_hash(kdef, style)
        cached = cache.get(key)
        if cached and cached["hash"] == h:
            lines.append(cached["code"] + "\n")
            print(f"[python] {kname}: unchanged -- reusing cached verified implementation")
            continue

        code = synthesizer.synthesize(kdef, domain, target="python")
        ok, counterexample, _ = compile_and_verify(code, kdef, domain, trials=200)
        if not ok:
            print(f"[python] {kname}: SYNTHESIS REJECTED -- {counterexample}")
            if cached:
                print(f"[python] {kname}: keeping previous verified implementation")
                lines.append(cached["code"] + "\n")
            else:
                raise RuntimeError(f"No verified implementation available for '{kname}' (python)")
            continue

        print(f"[python] {kname}: schema changed -- synthesized + verified (PASS), caching")
        cache[key] = {"hash": h, "code": code}
        lines.append(code + "\n")

    with open(out_path, "w") as f:
        f.writelines(lines)
    print(f"-> wrote {out_path}\n")


def compile_go(domain, cache, wiring_path="generated/go/wiring.go"):
    generate_go_types(domain)
    style = domain.targets["go"].style if "go" in domain.targets else ""

    header = 'package generated\n\nimport (\n\t"domainkit/generated/go/types"\n\t"domainkit/providers/go"\n)\n\n'
    body = []
    for kname, kdef in domain.keywords.items():
        binding = kdef.bindings.get("go")

        if binding:
            subj = kdef.subject
            if kdef.object:
                sig = f"func {kname.capitalize()}(subject *types.{subj}, object *types.{kdef.object})"
                call = f"provider.{binding['function']}(subject, object)"
            else:
                sig = f"func {kname.capitalize()}(subject *types.{subj})"
                call = f"provider.{binding['function']}(subject)"
            body.append(f"{sig} {{\n\t{call}\n}}\n")
            print(f"[go] {kname}: wired to provider.{binding['function']}")
            continue

        key = f"go:{kname}"
        h = _spec_hash(kdef, style)
        cached = cache.get(key)
        if cached and cached["hash"] == h:
            body.append(cached["code"])
            print(f"[go] {kname}: unchanged -- reusing cached verified implementation")
            continue

        synthesizer = AnthropicSynthesizer() if os.environ.get("ANTHROPIC_API_KEY") else MockSynthesizer()
        code = synthesizer.synthesize(kdef, domain, target="go")
        body.append(code)  # written speculatively; verified below by compiling+running Go
        cache[key] = {"hash": h, "code": code, "_pending": True}
        print(f"[go] {kname}: schema changed -- synthesizing")

    os.makedirs(os.path.dirname(wiring_path), exist_ok=True)
    with open(wiring_path, "w") as f:
        f.write(header + "\n".join(body))

    generate_go_verifier(domain)

    result = subprocess.run(["go", "run", "./generated/go/verify"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Go verification failed -- rejecting newly synthesized Go code")

    for entry in cache.values():
        entry.pop("_pending", None)
    print(f"-> wrote {wiring_path}\n")


def build(schema_path="schema.yaml"):
    domain = load_domain(schema_path)
    cache = _load_cache()
    if "python" in domain.targets:
        compile_python(domain, cache)
    if "go" in domain.targets:
        compile_go(domain, cache)
    _save_cache(cache)


if __name__ == "__main__":
    build()
