"""Shared validation error type for all languages in this experiment.

Modeled on the SHACL validation-report idea: rejection is a list of located,
sorted error strings (focus-node style), not a single opaque message.
"""

from __future__ import annotations


class ValidationError(ValueError):
    """Raised when a document violates a language's validation contract."""

    def __init__(self, errors):
        self.errors = sorted(errors)
        super().__init__(
            "invalid document:\n" + "\n".join(f"- {e}" for e in self.errors)
        )
