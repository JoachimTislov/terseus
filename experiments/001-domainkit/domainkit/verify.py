from .contracts import verify_contract


def compile_and_verify(code: str, keyword_def, domain, trials: int = 200):
    ns = {}
    exec(code, {"__builtins__": {}}, ns)
    fn = ns[keyword_def.name]
    ok, counterexample = verify_contract(fn, keyword_def, domain, trials=trials)
    return ok, counterexample, fn
