"""Parse and validate ``workflow.yaml`` into an executable node graph.

Only the *control* graph lives in YAML (which step follows which, and under what
condition). Data flow is implicit: every step shares the container filesystem, so
there are no per-step images or mounts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

import yaml

DEFAULT_WAIT = 60.0
MANUAL_APPROVAL = "manual_approval"
MANUAL_APPROVAL_STEP = "ManualApproval"


class WorkflowError(Exception):
    """Raised for malformed ``workflow.yaml`` files."""


@dataclass
class Branch:
    """A conditional ``next``: try each condition in order; fall back to ``else``."""

    conditions: List[Tuple[str, str]]  # (condition_name, target_id), evaluated in order
    else_target: Optional[str]
    wait: float = DEFAULT_WAIT


NextSpec = Union[None, str, Branch]  # terminal | linear target | branch


@dataclass
class Node:
    id: str
    kind: str  # "step" | "manual_approval"
    step_name: Optional[str]
    per_subject: bool
    nxt: NextSpec
    ordinal: int
    limit: Optional[int] = None
    on_error: str = "stop"
    config: Dict = field(default_factory=dict)

    @property
    def is_terminal(self) -> bool:
        return self.nxt is None


class Graph:
    def __init__(self, nodes: Dict[str, Node], start_id: str, max_workers: int):
        self.nodes = nodes
        self.start_id = start_id
        self.max_workers = max_workers

    def node(self, node_id: str) -> Node:
        return self.nodes[node_id]

    @property
    def start(self) -> Node:
        return self.nodes[self.start_id]

    def step_names(self) -> List[str]:
        return [n.step_name for n in self.nodes.values() if n.step_name]

    def condition_names(self) -> List[str]:
        names = []
        for n in self.nodes.values():
            if isinstance(n.nxt, Branch):
                names.extend(c for c, _ in n.nxt.conditions)
        return names

    # ---- construction ----------------------------------------------------------
    @classmethod
    def from_yaml(cls, path: str) -> "Graph":
        with open(path) as f:
            spec = yaml.safe_load(f) or {}
        return cls.from_spec(spec)

    @classmethod
    def from_spec(cls, spec: dict) -> "Graph":
        raw_steps = spec.get("steps")
        if not raw_steps:
            raise WorkflowError("workflow.yaml must define a non-empty 'steps' list")

        max_workers = int(spec.get("max_workers", 4))
        nodes: Dict[str, Node] = {}
        for ordinal, raw in enumerate(raw_steps, start=1):
            node = _parse_node(raw, ordinal)
            if node.id in nodes:
                raise WorkflowError(f"duplicate step id: {node.id}")
            nodes[node.id] = node

        start_id = raw_steps[0]["id"]
        graph = cls(nodes, start_id, max_workers)
        _validate(graph)
        return graph


def _parse_node(raw: dict, ordinal: int) -> Node:
    if "id" not in raw:
        raise WorkflowError(f"step #{ordinal} is missing an 'id'")
    node_id = raw["id"]
    kind = raw.get("type", "step")
    if kind not in ("step", MANUAL_APPROVAL):
        raise WorkflowError(f"step '{node_id}' has unknown type '{kind}'")

    if kind == MANUAL_APPROVAL:
        step_name = MANUAL_APPROVAL_STEP
        per_subject = raw.get("per_subject", False)
    else:
        step_name = raw.get("step", node_id)
        per_subject = raw.get("per_subject", True)

    return Node(
        id=node_id,
        kind=kind,
        step_name=step_name,
        per_subject=per_subject,
        nxt=_parse_next(raw.get("next"), node_id),
        ordinal=ordinal,
        limit=raw.get("limit"),
        on_error=raw.get("on_error", "stop"),
        config=raw.get("config", {}) or {},
    )


def _parse_next(raw_next, node_id: str) -> NextSpec:
    if raw_next is None:
        return None
    if isinstance(raw_next, str):
        return raw_next
    if isinstance(raw_next, dict):
        conditions = []
        for entry in raw_next.get("if", []):
            conditions.append((entry["condition"], entry["target"]))
        return Branch(
            conditions=conditions,
            else_target=raw_next.get("else"),
            wait=float(raw_next.get("wait", DEFAULT_WAIT)),
        )
    raise WorkflowError(f"step '{node_id}' has an invalid 'next': {raw_next!r}")


def _targets(node: Node) -> List[str]:
    if node.nxt is None:
        return []
    if isinstance(node.nxt, str):
        return [node.nxt]
    targets = [t for _, t in node.nxt.conditions]
    if node.nxt.else_target:
        targets.append(node.nxt.else_target)
    return targets


def _validate(graph: Graph) -> None:
    ids = set(graph.nodes)

    for node in graph.nodes.values():
        for target in _targets(node):
            if target not in ids:
                raise WorkflowError(
                    f"step '{node.id}' points to unknown step '{target}'"
                )
        if node.on_error not in ("stop", "ignore"):
            raise WorkflowError(
                f"step '{node.id}' has invalid on_error '{node.on_error}' "
                "(expected 'stop' or 'ignore')"
            )

    if not any(n.is_terminal for n in graph.nodes.values()):
        raise WorkflowError(
            "at least one terminal step (next: null) is required so the workflow can complete"
        )

    if graph.start.per_subject:
        raise WorkflowError(
            f"the first step '{graph.start_id}' must be a barrier (per_subject: false) "
            "so it can establish the subject list"
        )
