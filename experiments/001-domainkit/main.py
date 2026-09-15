import argparse
import datetime
import os

from domainkit.schema import load_domain
from domainkit.synth import MockSynthesizer, AnthropicSynthesizer
from domainkit.verify import compile_and_verify


def build(schema_path="schema.yaml", out_path="generated_impls.py", trials=200, max_attempts=3):
    domain = load_domain(schema_path)

    synthesizer = AnthropicSynthesizer() if os.environ.get("ANTHROPIC_API_KEY") else MockSynthesizer()
    print(f"Using {type(synthesizer).__name__}\n")

    verified = []
    for kname, kdef in domain.keywords.items():
        feedback = None
        for attempt in range(1, max_attempts + 1):
            code = synthesizer.synthesize(kdef, domain, feedback=feedback)
            ok, counterexample, _ = compile_and_verify(code, kdef, domain, trials=trials)
            print(f"[{kname}] attempt {attempt}: {'PASS' if ok else 'FAIL'}")
            if ok:
                verified.append((kname, kdef.contract, code))
                break
            feedback = counterexample
        else:
            raise RuntimeError(
                f"Could not synthesize a verified implementation for '{kname}' after {max_attempts} attempts. "
                f"Last counterexample: {feedback}"
            )

    with open(out_path, "w") as f:
        f.write("# AUTO-GENERATED AND CONTRACT-VERIFIED -- do not hand-edit.\n")
        f.write(f"# domain: {domain.name}, built {datetime.datetime.utcnow().isoformat()}Z\n\n")
        for kname, contract, code in verified:
            f.write(f"# keyword: {kname}\n# requires: {contract.requires}\n# ensures: {contract.ensures}\n")
            f.write(code + "\n\n")

    print(f"\nWrote verified implementations to {out_path}")
    return domain


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", default="schema.yaml")
    parser.add_argument("--trials", type=int, default=200)
    args = parser.parse_args()
    build(args.schema, trials=args.trials)
