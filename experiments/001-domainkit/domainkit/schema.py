"""
The domain schema is the ONLY hand-authored source of truth. Everything
else in this project (verified implementations, the interface) is derived
from it. Nothing downstream is allowed to introduce a field, relation, or
keyword that isn't declared here.
"""
import yaml
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TypeDef:
    name: str
    fields: Dict[str, str]  # field_name -> type_name ('User', 'str', 'bool', 'User?', ...)


@dataclass
class Contract:
    requires: str
    ensures: str


@dataclass
class KeywordDef:
    name: str
    subject: str
    object: Optional[str]
    contract: Contract
    bindings: Dict[str, Dict[str, str]]  # target_lang -> {module/package, function}


@dataclass
class ViewDef:
    name: str
    entity: str
    fields: List[str]
    actions: List[str]


@dataclass
class TargetDef:
    name: str
    style: str


@dataclass
class Domain:
    name: str
    types: Dict[str, TypeDef]
    keywords: Dict[str, KeywordDef]
    views: List[ViewDef]
    targets: Dict[str, TargetDef]


def load_domain(path: str) -> Domain:
    with open(path) as f:
        raw = yaml.safe_load(f)

    types = {
        tname: TypeDef(name=tname, fields=tdef.get("fields", {}))
        for tname, tdef in raw.get("types", {}).items()
    }

    keywords = {}
    for kname, kdef in raw.get("keywords", {}).items():
        c = kdef.get("contract", {})
        keywords[kname] = KeywordDef(
            name=kname,
            subject=kdef["subject"],
            object=kdef.get("object"),
            contract=Contract(requires=c.get("requires", "True"), ensures=c.get("ensures", "True")),
            bindings=kdef.get("bindings", {}),
        )

    views = [
        ViewDef(name=v["name"], entity=v["entity"], fields=v.get("fields", []), actions=v.get("actions", []))
        for v in raw.get("interface", {}).get("views", [])
    ]

    targets = {
        tname: TargetDef(name=tname, style=tdef.get("style", ""))
        for tname, tdef in raw.get("targets", {}).items()
    }

    return Domain(name=raw["domain"], types=types, keywords=keywords, views=views, targets=targets)
