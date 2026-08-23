#!/usr/bin/env python3
"""Executable lock of composition.md's diagram-type picker and factory pack-solve.

The prose in references/composition.md is the source of truth. This module
extracts the type-picker phrases from that file and classifies a request the
same way: name > description > allusion > default map. "As an explainer"
locks the explainer register only; the map then picks the type.

Pack-solve reasons from an interaction-model fixture — one operator stage,
declared contacts only, one connected plant. It does not invent a look.
"""
from __future__ import annotations

import dataclasses
import pathlib
import re
import sys
from typing import Iterable, Sequence

COMPOSITION_MD = (
    pathlib.Path(__file__).resolve().parent.parent / "references" / "composition.md"
)

REGISTER_EDITORIAL = "editorial"
REGISTER_EXPLAINER = "explainer"

TYPE_FACTORY = "factory_flow"
TYPE_FAN_OUT = "fan_out"
TYPE_TIMELINE = "timeline"
TYPE_LOOP = "loop"
TYPE_STACK = "layer_stack"
TYPE_SLICE = "system_slice"
TYPE_COMIC = "mini_comic"
TYPE_EDITORIAL = "editorial"

DIAGRAM_TYPES = frozenset(
    {TYPE_FACTORY, TYPE_FAN_OUT, TYPE_TIMELINE, TYPE_LOOP, TYPE_STACK, TYPE_SLICE}
)
OVERRIDE_NAME = "name"
OVERRIDE_DESCRIPTION = "description"
OVERRIDE_ALLUSION = "allusion"
REGISTER_ONLY = object()

LABEL_TO_TYPE = {
    "factory flow": TYPE_FACTORY,
    "factory": TYPE_FACTORY,
    "fan-out": TYPE_FAN_OUT,
    "timeline": TYPE_TIMELINE,
    "loop": TYPE_LOOP,
    "layer stack": TYPE_STACK,
    "stack": TYPE_STACK,
    "system slice": TYPE_SLICE,
    "mini-comic": TYPE_COMIC,
    "editorial": TYPE_EDITORIAL,
    "just the scene": TYPE_EDITORIAL,
}

DESCRIPTION_TYPE = TYPE_FACTORY
ALLUSION_TYPE = TYPE_FACTORY

AUDIT_STAGES = ("intent", "bounded", "sensored", "audited", "verified")
AUDIT_REJECT = "slop"
AUDIT_RETURN = "re-audit"


@dataclasses.dataclass(frozen=True)
class TypePolicy:
    """Phrases extracted from composition.md, 'Pick the diagram type'."""

    named_phrases: tuple[str, ...]
    register_only_phrases: tuple[str, ...]
    description_examples: tuple[str, ...]
    allusion_examples: tuple[str, ...]
    default_map_labels: tuple[str, ...]
    locks_register_only: bool


@dataclasses.dataclass(frozen=True)
class DiagramDecision:
    register: str
    diagram_type: str
    override: str | None


@dataclasses.dataclass(frozen=True)
class InteractionModel:
    name: str
    contact_surfaces: frozenset[str]
    reach: str
    grip: str
    support: frozenset[str]
    special_operators: frozenset[str]
    undeclared: frozenset[str]
    forbidden_verbs: frozenset[str]
    style: str = "riso"


@dataclasses.dataclass(frozen=True)
class ContactLine:
    character_part: str
    object_part: str
    location: str
    motion: str

    def as_line(self) -> str:
        return (
            f"{self.character_part} -> {self.object_part} -> "
            f"{self.location} -> {self.motion}"
        )


@dataclasses.dataclass(frozen=True)
class FactorySkeleton:
    stages: tuple[str, ...]
    reject: str
    return_leg: str


@dataclasses.dataclass(frozen=True)
class PackSolve:
    operator_stage: str
    verb: str
    contact_part: str
    contact_map: tuple[ContactLine, ...]
    plant_stages: tuple[str, ...]
    bind: str
    style: str
    reject: str
    return_leg: str


@dataclasses.dataclass(frozen=True)
class _StageOp:
    stage: str
    verb: str
    contact_part: str
    object_part: str
    location: str
    motion: str
    required_surfaces: frozenset[str]
    required_grip: frozenset[str]
    required_special: frozenset[str]
    required_reach: str | None = None


AUDIT_FACTORY = FactorySkeleton(
    stages=AUDIT_STAGES, reject=AUDIT_REJECT, return_leg=AUDIT_RETURN
)

# Capability catalog — the solver matches these to a pack fixture.
# Prefer body-weight / press / pour / hook over invented dexterity.
_STAGE_OPS: tuple[_StageOp, ...] = (
    _StageOp(
        stage="bounded",
        verb="pedal",
        contact_part="feet",
        object_part="pedal",
        location="below body",
        motion="drives the bound plate",
        required_surfaces=frozenset({"feet"}),
        required_grip=frozenset({"pressure/contact"}),
        required_special=frozenset(),
    ),
    _StageOp(
        stage="bounded",
        verb="press",
        contact_part="arm_tips",
        object_part="press",
        location="beside body",
        motion="presses the bound plate",
        required_surfaces=frozenset({"arm_tips"}),
        required_grip=frozenset({"pressure/contact"}),
        required_special=frozenset(),
    ),
    _StageOp(
        stage="bounded",
        verb="jam",
        contact_part="body",
        object_part="bound plate",
        location="against the plate",
        motion="is the jam",
        required_surfaces=frozenset({"body"}),
        required_grip=frozenset({"none"}),
        required_special=frozenset(),
        required_reach="body-contact only",
    ),
    _StageOp(
        stage="bounded",
        verb="vessel",
        contact_part="body",
        object_part="bound plate",
        location="as the vessel",
        motion="holds the bound load",
        required_surfaces=frozenset({"body"}),
        required_grip=frozenset({"none"}),
        required_special=frozenset(),
        required_reach="body-contact only",
    ),
    _StageOp(
        stage="sensored",
        verb="pour",
        contact_part="vessel",
        object_part="sensor well",
        location="above the well",
        motion="pours a sprinkle",
        required_surfaces=frozenset({"vessel"}),
        required_grip=frozenset({"pressure/contact", "none"}),
        required_special=frozenset({"pour"}),
    ),
    _StageOp(
        stage="sensored",
        verb="sprinkle",
        contact_part="vessel",
        object_part="sensor well",
        location="above the well",
        motion="sprinkles the sample",
        required_surfaces=frozenset({"vessel"}),
        required_grip=frozenset({"pressure/contact", "none"}),
        required_special=frozenset({"pour"}),
    ),
    _StageOp(
        stage="audited",
        verb="handle",
        contact_part="hook_mitts",
        object_part="audit handle",
        location="on the bar",
        motion="hooks the audit gate",
        required_surfaces=frozenset({"hook_mitts"}),
        required_grip=frozenset({"hook"}),
        required_special=frozenset(),
    ),
    _StageOp(
        stage="slop",
        verb="hose",
        contact_part="hook_mitts",
        object_part="reject hose",
        location="beside the chute",
        motion="hooks the slop hose",
        required_surfaces=frozenset({"hook_mitts"}),
        required_grip=frozenset({"hook"}),
        required_special=frozenset(),
    ),
)

_STAGE_PREF = ("bounded", "sensored", "audited", "verified", "intent", "slop")
_VERB_PREF = (
    "jam",
    "vessel",
    "pedal",
    "press",
    "pour",
    "sprinkle",
    "handle",
    "hose",
)


def parse_composition_policy(text: str) -> TypePolicy:
    """Read the type-picker section. Tests fail if this section drifts."""
    match = re.search(
        r"## Pick the diagram type\n(?P<body>.*?)(?=\n## )", text, flags=re.S
    )
    if not match:
        raise ValueError("composition.md is missing '## Pick the diagram type'")
    body = match.group("body")

    def _item(start: str, end: str) -> str:
        chunk = re.search(
            re.escape(start) + r"(.*?)" + re.escape(end), body, flags=re.S
        )
        if not chunk:
            raise ValueError(f"composition.md type picker is missing {start!r}")
        return chunk.group(1)

    names_chunk = _item("1. The user **names** a type", "2. The user **describes**")
    desc_chunk = _item(
        "2. The user **describes** a type", "3. The user **alludes**"
    )
    allusion_chunk = _item(
        "3. The user **alludes** to a type", "4. The agent default"
    )
    def _quotes(chunk: str) -> tuple[str, ...]:
        return tuple(
            re.sub(r"\s+", " ", quoted).strip()
            for quoted in re.findall(r'"([^"]+)"', chunk)
        )

    named = _quotes(names_chunk)
    if "as an explainer" not in named:
        raise ValueError("names list must include 'as an explainer'")
    register_only = tuple(p for p in named if p == "as an explainer")
    named_types = tuple(p for p in named if p != "as an explainer")
    descriptions = _quotes(desc_chunk)
    allusions = _quotes(allusion_chunk)
    labels = tuple(
        LABEL_TO_TYPE[label]
        for label in re.findall(r"→\s+\*\*(.+?)\*\*", body)
        if label in LABEL_TO_TYPE
    )
    locks = "locks the register only" in body
    if not locks:
        raise ValueError(
            "composition.md must say 'as an explainer' locks the register only"
        )
    return TypePolicy(
        named_phrases=named_types,
        register_only_phrases=register_only,
        description_examples=descriptions,
        allusion_examples=allusions,
        default_map_labels=labels,
        locks_register_only=locks,
    )


def load_composition_policy(path: pathlib.Path | None = None) -> TypePolicy:
    return parse_composition_policy(
        (path or COMPOSITION_MD).read_text(encoding="utf-8")
    )


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("→", "->").strip())


def _register_for(diagram_type: str, *, explainer_named: bool = False) -> str:
    if explainer_named:
        return REGISTER_EXPLAINER
    if diagram_type in DIAGRAM_TYPES:
        return REGISTER_EXPLAINER
    return REGISTER_EDITORIAL


def _named_code(phrase: str) -> str | object:
    if phrase == "as an explainer":
        return REGISTER_ONLY
    if phrase == "stack":
        return TYPE_STACK
    return LABEL_TO_TYPE[phrase]


def _find_named(
    text: str, policy: TypePolicy
) -> tuple[str | object, str] | None:
    """Return (type-or-REGISTER_ONLY, matched phrase) for a name override."""
    stripped = text
    for allusion in policy.allusion_examples:
        stripped = stripped.replace(allusion, " ")
    for desc in policy.description_examples:
        stripped = stripped.replace(desc, " ")
    candidates: list[tuple[int, str, str | object]] = []
    for phrase in (*policy.register_only_phrases, *policy.named_phrases):
        if phrase == "factory":
            pattern = r"(?:as a factory|factory flow|\bfactory\b)"
        elif phrase == "fan-out":
            pattern = r"fan-?out"
        elif phrase == "mini-comic":
            pattern = r"mini-?comic"
        elif phrase == "just the scene":
            pattern = r"just the scene"
        elif phrase == "as an explainer":
            pattern = r"as an explainer"
        else:
            pattern = r"\b" + re.escape(phrase) + r"\b"
        match = re.search(pattern, stripped)
        if match:
            candidates.append((match.start(), phrase, _named_code(phrase)))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (-len(item[1]), item[0]))
    _start, phrase, code = candidates[0]
    return code, phrase


def _find_quoted_examples(text: str, examples: Sequence[str]) -> str | None:
    for example in examples:
        if example in text:
            return example
    return None


def _has_nameable_stations(text: str) -> bool:
    return bool(
        re.search(
            r"->|intent|bounded|sensored|audited|verified|stage",
            text,
        )
    )


def default_map(thesis: str) -> str:
    """Agent default from the locked thesis. Editorial wins if none fit."""
    text = _normalize(thesis)
    hits: list[str] = []

    if re.search(r"fail(?:ed)? then .{0,60}fix|before.{0,20}after", text):
        hits.append(TYPE_COMIC)
    if re.search(
        r"feedback cycle|cycle or feedback|the point is the (?:feedback )?cycle",
        text,
    ):
        hits.append(TYPE_LOOP)
    if re.search(r"one source into|split or sort|\bsort\b", text):
        hits.append(TYPE_FAN_OUT)
    if re.search(r"pipeline|recipe|staged process|intent.{0,40}bounded", text):
        hits.append(TYPE_FACTORY)
    if re.search(r"\b(timeline|history|chronolog)\b", text):
        hits.append(TYPE_TIMELINE)
    if re.search(r"\blayers?\b|capability stack", text):
        hits.append(TYPE_STACK)
    if re.search(r"connected parts|no single direction|system slice", text):
        hits.append(TYPE_SLICE)
    if re.search(r"you(?:'re| are) the\b|bottleneck", text):
        hits.append(TYPE_EDITORIAL)

    unique = list(dict.fromkeys(hits))
    if not unique:
        return TYPE_EDITORIAL
    if len(unique) == 1:
        return unique[0]
    if TYPE_FACTORY in unique and _has_nameable_stations(text):
        return TYPE_FACTORY
    for preferred in (
        TYPE_FACTORY,
        TYPE_FAN_OUT,
        TYPE_TIMELINE,
        TYPE_LOOP,
        TYPE_STACK,
        TYPE_SLICE,
        TYPE_COMIC,
        TYPE_EDITORIAL,
    ):
        if preferred in unique:
            return preferred
    return TYPE_EDITORIAL


def route_diagram(
    text: str,
    *,
    thesis: str | None = None,
    policy: TypePolicy | None = None,
) -> DiagramDecision:
    """Pick register + type. User override beats the thesis map."""
    policy = policy or load_composition_policy()
    hay = _normalize(text)
    locked = thesis if thesis is not None else text

    named = _find_named(hay, policy)
    if named is not None:
        code, _phrase = named
        if code is REGISTER_ONLY:
            diagram_type = default_map(locked)
            return DiagramDecision(
                register=REGISTER_EXPLAINER,
                diagram_type=diagram_type,
                override=OVERRIDE_NAME,
            )
        return DiagramDecision(
            register=_register_for(str(code)),
            diagram_type=str(code),
            override=OVERRIDE_NAME,
        )

    if _find_quoted_examples(hay, policy.description_examples):
        return DiagramDecision(
            register=_register_for(DESCRIPTION_TYPE),
            diagram_type=DESCRIPTION_TYPE,
            override=OVERRIDE_DESCRIPTION,
        )
    if _find_quoted_examples(hay, policy.allusion_examples):
        return DiagramDecision(
            register=_register_for(ALLUSION_TYPE),
            diagram_type=ALLUSION_TYPE,
            override=OVERRIDE_ALLUSION,
        )

    diagram_type = default_map(locked)
    return DiagramDecision(
        register=_register_for(diagram_type),
        diagram_type=diagram_type,
        override=None,
    )


def op_feasible(model: InteractionModel, op: _StageOp) -> bool:
    if op.verb in model.forbidden_verbs:
        return False
    if op.contact_part in model.undeclared:
        return False
    if not op.required_surfaces <= model.contact_surfaces:
        return False
    if op.required_grip and model.grip not in op.required_grip:
        return False
    if op.required_special and not op.required_special <= model.special_operators:
        return False
    if op.required_reach and model.reach != op.required_reach:
        return False
    if model.reach == "body-contact only" and op.contact_part != "body":
        return False
    return True


def feasibility_errors(
    model: InteractionModel,
    contacts: Iterable[ContactLine],
    *,
    verb: str | None = None,
) -> list[str]:
    """Anatomy-action gate on one contact map. Empty list = pass."""
    errors: list[str] = []
    allowed = model.contact_surfaces | model.support | frozenset(
        {"none", "ground", "inactive parts", "both arms"}
    )
    if verb and verb in model.forbidden_verbs:
        errors.append(f"forbidden verb {verb!r}")
    if verb in {"crank", "wheel", "grasp"} and model.grip in {"none", "pressure/contact"}:
        errors.append(f"{model.name} cannot {verb}")
    for line in contacts:
        if line.character_part in model.undeclared:
            errors.append(f"undeclared contact {line.character_part!r}")
        if line.object_part in model.undeclared:
            errors.append(f"undeclared tool {line.object_part!r}")
        if line.character_part not in allowed:
            errors.append(f"undeclared surface {line.character_part!r}")
    return errors


def pack_solve(
    model: InteractionModel, skeleton: FactorySkeleton | None = None
) -> PackSolve:
    """Pick ONE operator stage this body can work; bind the rest as world objects."""
    skeleton = skeleton or AUDIT_FACTORY
    allowed_stages = set(skeleton.stages) | {skeleton.reject}
    candidates = [
        op
        for op in _STAGE_OPS
        if op.stage in allowed_stages and op_feasible(model, op)
    ]
    if not candidates:
        raise ValueError(f"{model.name}: no feasible operator stage")

    def _key(op: _StageOp) -> tuple[int, int, int, int]:
        uses_special = bool(op.required_special & model.special_operators)
        special_rank = 0 if uses_special else (1 if model.special_operators else 0)
        stage_rank = (
            _STAGE_PREF.index(op.stage) if op.stage in _STAGE_PREF else 99
        )
        verb_rank = _VERB_PREF.index(op.verb) if op.verb in _VERB_PREF else 99
        reject_penalty = 1 if op.stage == skeleton.reject else 0
        return (special_rank, reject_penalty, stage_rank, verb_rank)

    chosen = min(candidates, key=_key)
    support_part = next(iter(model.support), "body")
    contact_map = (
        ContactLine(
            chosen.contact_part,
            chosen.object_part,
            chosen.location,
            chosen.motion,
        ),
        ContactLine(support_part, "ground", "below body", "supports weight"),
        ContactLine("inactive parts", "none", "at rest", "touch nothing"),
    )
    errors = feasibility_errors(model, contact_map, verb=chosen.verb)
    if errors:
        raise ValueError(f"{model.name}: infeasible solve: {errors}")
    if model.style == "whiteboard":
        raise ValueError("pack-solve must not switch to a whiteboard look")
    return PackSolve(
        operator_stage=chosen.stage,
        verb=chosen.verb,
        contact_part=chosen.contact_part,
        contact_map=contact_map,
        plant_stages=skeleton.stages,
        bind="one flow line",
        style=model.style,
        reject=skeleton.reject,
        return_leg=skeleton.return_leg,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        sys.stderr.write("usage: diagram_route.py <request text>\n")
        return 2
    decision = route_diagram(" ".join(args))
    sys.stdout.write(
        f"{decision.register}\t{decision.diagram_type}\t{decision.override or 'default'}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
