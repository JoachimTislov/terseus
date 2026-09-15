"""
Two things live here, both deliberately NOT touched by an LLM:

1. Translating a `requires`/`ensures` string into each target's own boolean
   syntax. This is the same limited grammar `contracts.py` evaluates with
   Python's `eval` -- ported here as string rewriting so a non-Python
   target (Go) can check the identical property natively. A real version
   of this project needs a proper parser here; see README.
2. Generating a target's type declarations straight from `domain.types`.
   Types are structure, not behavior -- there's nothing non-deterministic
   to synthesize, so this stays a plain, boring code generator.
"""
import re


def to_field(name: str) -> str:
    """Go/TS-style capitalized field name."""
    return name[0].upper() + name[1:]


def contract_expr_to_go(expr: str) -> str:
    e = expr.strip()
    negate = e.startswith("not ")
    if negate:
        e = e[4:].strip()

    e = re.sub(r"\b(subject|object)\.(\w+)", lambda m: f"{m.group(1)}.{to_field(m.group(2))}", e)
    e = e.replace(" is not None", " != nil").replace(" is None", " == nil")
    e = e.replace(" and ", " && ").replace(" or ", " || ")

    return f"!({e})" if negate else e


def go_type(field_type: str) -> str:
    optional = field_type.endswith("?")
    base = field_type.rstrip("?")
    primitives = {"str": "string", "bool": "bool", "int": "int"}
    if base in primitives:
        return primitives[base]
    return f"*{base}"  # relation to another declared type -> pointer


def generate_go_types(domain, out_path="generated/go/types/types.go"):
    lines = ["package types\n"]
    for tname, tdef in domain.types.items():
        lines.append(f"type {tname} struct {{")
        for fname, ftype in tdef.fields.items():
            lines.append(f"\t{to_field(fname)} {go_type(ftype)}")
        lines.append("}\n")

    import os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    return out_path
