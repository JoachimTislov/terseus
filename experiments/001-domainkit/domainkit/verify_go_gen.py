"""
Generates generated/go/verify/main.go straight from the schema: random
instance constructors per type, and a requires/ensures check per keyword
translated via targetlang.contract_expr_to_go. Nothing here is synthesized
by an LLM -- it's mechanical, the same way contracts.py's random testing is
mechanical on the Python side. This is what makes verification available
for a keyword the instant it's declared, whether its implementation came
from a hand-written provider or was just synthesized.
"""
import os

from .targetlang import contract_expr_to_go, to_field


def _random_ctor_body(tname, domain):
    tdef = domain.types[tname]
    lines = [f"func random{tname}(depth int) *types.{tname} {{"]
    field_inits = []
    extra = []
    for fname, ftype in tdef.fields.items():
        gofield = to_field(fname)
        optional = ftype.endswith("?")
        base = ftype.rstrip("?")
        if base == "str":
            field_inits.append(f"{gofield}: randString(6)")
        elif base == "bool":
            field_inits.append(f"{gofield}: rand.Float64() < 0.5")
        elif base == "int":
            field_inits.append(f"{gofield}: rand.Intn(100)")
        elif base in domain.types:
            var = f"_{fname}"
            if optional:
                extra.append(
                    f"\tvar {var} *types.{base}\n"
                    f"\tif rand.Float64() >= 0.4 && depth < 2 {{ {var} = random{base}(depth+1) }}"
                )
            else:
                extra.append(f"\t{var} := random{base}(depth+1)")
            field_inits.append(f"{gofield}: {var}")
    lines.extend(extra)
    lines.append(f"\treturn &types.{tname}{{{', '.join(field_inits)}}}")
    lines.append("}\n")
    return "\n".join(lines)


def _verify_fn(kname, kdef, domain, trials=500):
    requires_go = contract_expr_to_go(kdef.contract.requires)
    ensures_go = contract_expr_to_go(kdef.contract.ensures)

    setup = [f"subject := random{kdef.subject}(0)"]
    reassign = [f"subject = random{kdef.subject}(0)"]
    call_args = "subject"
    if kdef.object:
        setup.append(f"object := random{kdef.object}(0)")
        reassign.append(f"object = random{kdef.object}(0)")
        call_args += ", object"

    init = "\n\t".join(setup)
    retry = "\n\t\t".join(reassign)
    return f"""
func verify_{kname}(trials int) bool {{
	checked := 0
	for i := 0; i < trials; i++ {{
		{init}
		attempts := 0
		for !({requires_go}) && attempts < 50 {{
			{retry}
			attempts++
		}}
		if !({requires_go}) {{
			continue
		}}
		checked++
		generated.{kname.capitalize()}({call_args})
		if !({ensures_go}) {{
			fmt.Println("FAIL {kname}: postcondition violated")
			return false
		}}
	}}
	fmt.Printf("{kname}: %d/%d trials satisfied requires, all PASSED ensures\\n", checked, trials)
	return checked > 0
}}"""


def generate_go_verifier(domain, out_path="generated/go/verify/main.go", trials=500):
    ctors = "\n".join(_random_ctor_body(tname, domain) for tname in domain.types)
    verifiers = "\n".join(_verify_fn(kname, kdef, domain, trials) for kname, kdef in domain.keywords.items())
    calls = "\n\t".join(f"ok = ok && verify_{k}({trials})" for k in domain.keywords)

    src = f"""// AUTO-GENERATED from schema.yaml -- do not hand-edit.
package main

import (
	"fmt"
	"math/rand"

	generated "domainkit/generated/go"
	"domainkit/generated/go/types"
)

func randString(n int) string {{
	const letters = "abcdefghijklmnopqrstuvwxyz"
	b := make([]byte, n)
	for i := range b {{
		b[i] = letters[rand.Intn(len(letters))]
	}}
	return string(b)
}}

{ctors}
{verifiers}

func main() {{
	ok := true
	{calls}
	if ok {{
		fmt.Println("\\nALL CONTRACTS VERIFIED (Go target)")
	}} else {{
		panic("contract verification failed on the Go target")
	}}
}}
"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(src)
    return out_path
