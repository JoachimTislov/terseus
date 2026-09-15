"""
This is the verification boundary. A synthesized function is never trusted
because it "looks right" -- it's only accepted once it survives randomized
trials that check `requires -> ensures` actually holds. This is a informal
stand-in for the kind of guarantee tools like Sketch/Rosette give you with
an SMT solver; here we use random testing to keep the POC dependency-free.
"""
import random
import string
from types import SimpleNamespace

SAFE_NAMES = {"True": True, "False": False, "None": None}


def _random_value(type_name: str, domain, depth: int):
    optional = type_name.endswith("?")
    base = type_name.rstrip("?")

    if optional and random.random() < 0.4:
        return None
    if base == "str":
        return "".join(random.choices(string.ascii_lowercase, k=6))
    if base == "bool":
        return random.choice([True, False])
    if base == "int":
        return random.randint(0, 100)
    if base in domain.types and depth < 2:
        return random_instance(base, domain, depth + 1)
    return None


def random_instance(type_name: str, domain, depth: int = 0):
    tdef = domain.types[type_name]
    values = {fname: _random_value(ftype, domain, depth) for fname, ftype in tdef.fields.items()}
    return SimpleNamespace(**values)


def eval_expr(expr: str, subject, obj=None):
    ns = {**SAFE_NAMES, "subject": subject, "object": obj}
    return eval(expr, {"__builtins__": {}}, ns)


def verify_contract(fn, keyword_def, domain, trials: int = 200, max_setup_attempts: int = 50):
    """Returns (ok, counterexample_or_None)."""
    checked = 0
    for _ in range(trials):
        subject = random_instance(keyword_def.subject, domain)
        obj = random_instance(keyword_def.object, domain) if keyword_def.object else None

        setup_ok = False
        for _ in range(max_setup_attempts):
            try:
                if eval_expr(keyword_def.contract.requires, subject, obj):
                    setup_ok = True
                    break
            except Exception:
                pass
            subject = random_instance(keyword_def.subject, domain)
            obj = random_instance(keyword_def.object, domain) if keyword_def.object else None

        if not setup_ok:
            continue  # couldn't hit a state satisfying `requires`; skip this trial

        checked += 1
        try:
            fn(subject, obj) if keyword_def.object else fn(subject)
            ok = eval_expr(keyword_def.contract.ensures, subject, obj)
        except Exception as e:
            return False, {"subject": vars(subject), "object": vars(obj) if obj else None, "error": str(e)}

        if not ok:
            return False, {"subject": vars(subject), "object": vars(obj) if obj else None}

    if checked == 0:
        return False, {"error": "could not construct any input satisfying `requires` -- contract may be unsatisfiable"}
    return True, None
