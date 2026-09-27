"""008 agent domain languages: six JSON-represented domain languages for
agentic incident triage, one shared harness, six sub-experiments each.

Languages (each module is self-contained and dependency-free):
- anl  Agent Network Language (consolidated from experiment 008)
- scl  Schema Contract Language (OpenAPI/JSON Schema inspired)
- pvl  Provenance Vocabulary Language (W3C PROV-DM inspired)
- pdl  Policy Decision Language (OPA/Rego inspired)
- dtl  Decision Table Language (OMG DMN inspired)
- drl  Desired-state Resource Language (Kubernetes/HCL inspired)

See the experiment README.md for the hypothesis, the 6x6 matrix, and the
falsifiers; RESEARCH.md for the gathered practical intelligence.
"""

from .errors import ValidationError
from . import harness

__all__ = ["ValidationError", "harness"]
