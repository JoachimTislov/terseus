"""
The synthesizer's ONLY job is to fill in the body of a function whose
name, signature, and contract are already fixed by the schema. It cannot
introduce new fields, new keywords, or alter what `requires`/`ensures`
say -- those stay declarative and human-owned.
"""
import json
import os
import urllib.request


from .targetlang import to_field


class MockSynthesizer:
    """
    Deterministic stand-in for an LLM so the pipeline runs with no API key.
    It applies the same kind of shallow pattern-matching a real model would
    plausibly use for these simple contract shapes, for whichever target is
    requested. Swap in AnthropicSynthesizer below for the real thing.
    """

    def synthesize(self, keyword_def, domain, target="python", feedback=None):
        ensures = keyword_def.contract.ensures.strip()
        if target == "python":
            return self._python(keyword_def, ensures)
        if target == "go":
            return self._go(keyword_def, ensures)
        raise ValueError(f"MockSynthesizer has no backend for target '{target}'")

    def _python(self, keyword_def, ensures):
        obj_arg = ", object" if keyword_def.object else ""
        if "==" in ensures and ensures.split("==")[1].strip() == "object":
            field = ensures.split("==")[0].strip().split(".", 1)[1].strip()
            body = f"    subject.{field} = object\n"
        elif ensures.startswith("not subject."):
            field = ensures[len("not "):].split(".", 1)[1].strip()
            body = f"    subject.{field} = False\n"
        elif ensures.startswith("subject."):
            field = ensures.split(".", 1)[1].strip()
            body = f"    subject.{field} = True\n"
        else:
            body = "    pass  # mock synthesizer had no heuristic for this contract shape\n"
        return f"def {keyword_def.name}(subject{obj_arg}):\n{body}"

    def _go(self, keyword_def, ensures):
        obj_arg = f", object *types.{keyword_def.object}" if keyword_def.object else ""
        sig = f"func {keyword_def.name.capitalize()}(subject *types.{keyword_def.subject}{obj_arg})"
        if "==" in ensures and ensures.split("==")[1].strip() == "object":
            field = to_field(ensures.split("==")[0].strip().split(".", 1)[1].strip())
            body = f"\tsubject.{field} = object\n"
        elif ensures.startswith("not subject."):
            field = to_field(ensures[len("not "):].split(".", 1)[1].strip())
            body = f"\tsubject.{field} = false\n"
        elif ensures.startswith("subject."):
            field = to_field(ensures.split(".", 1)[1].strip())
            body = f"\tsubject.{field} = true\n"
        else:
            body = "\t// mock synthesizer had no heuristic for this contract shape\n"
        return f"{sig} {{\n{body}}}\n"


class AnthropicSynthesizer:
    """
    Real LLM-backed hole-filler. Requires ANTHROPIC_API_KEY in the
    environment. On a failed verification, the counterexample is fed back
    into the next prompt so the model can see exactly why it was rejected.
    """

    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")

    def synthesize(self, keyword_def, domain, target="python", feedback=None):
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")

        subject_fields = domain.types[keyword_def.subject].fields
        object_fields = domain.types[keyword_def.object].fields if keyword_def.object else None
        style = domain.targets[target].style if target in domain.targets else ""

        prompt = f"""You are filling in ONE function body inside a verified pipeline.
Target language: {target}. Style constraint (do not deviate): {style}
You may not invent fields, side effects, imports, or behavior beyond the contract.
Respond with ONLY JSON of the form {{"code": "..."}} -- no prose, no markdown fences.

Function name: {keyword_def.name}
Subject type '{keyword_def.subject}' fields: {subject_fields}
{"Object type '" + keyword_def.object + "' fields: " + str(object_fields) if keyword_def.object else "This keyword takes no object."}
Precondition, guaranteed true on entry: {keyword_def.contract.requires}
Postcondition, must be true when the function returns: {keyword_def.contract.ensures}
{"The previous attempt failed verification with this counterexample: " + json.dumps(feedback) if feedback else ""}
"""
        payload = json.dumps({
            "model": self.model,
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())

        text = "".join(b["text"] for b in data["content"] if b["type"] == "text").strip()
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
        return json.loads(text)["code"]
