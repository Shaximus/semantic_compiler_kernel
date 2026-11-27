"""
SC-TOL-001 v2.1-rc5: Hardened Topology-Aware, Epistemically Constrained Structural Compiler
Zero-dependency Python reference implementation + 42-test adversarial acceptance suite.

Service-integration contract:
- CompilationResult is immutable (frozen) once returned by StructuralCompiler.compile()
  or MetaGenerator.emit().
- Versioned deterministic serialization is provided via to_dict() and to_json().
- Declared vs. effective epistemic tier and topology are tracked separately so falsified
  or unqualified inputs cannot poison downstream consumers.
- By default, compile() is non-destructive (all stages E0-E7 execute while preserving
  observations and setting is_trustworthy=False on any hard block). Pass
  halt_on_t0_block=True to StructuralCompiler to short-circuit E0 -> E7 on T0 failure.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field, fields, is_dataclass, replace
from enum import Enum
from itertools import combinations
import json
from typing import Any, Optional
import unittest


# =============================================================================
# 1. Core Constants & Four-Dimensional State Model: S = (Sigma, T, G(v, e, tau), E)
# =============================================================================

SCHEMA_VERSION: str = "SC-TOL-001/2.1-rc5"
CORE_IMMUTABLE_GATES: frozenset[str] = frozenset({"T0", "T4", "T8"})


class EpistemicTier(Enum):
    CORPUS_MYTH = "CORPUS_MYTH"
    EMPIRICAL_SCI = "EMPIRICAL_SCI"
    SPECULATIVE_EXO = "SPECULATIVE_EXO"


class TopologyClass(Enum):
    """Strictly first-order graph topologies (higher-order generation uses MetaArchitectureSpec)."""
    ARBORESCENT = "ARBORESCENT"
    INVERTED_ARBORESCENT = "INVERTED_ARBORESCENT"
    RETICULATE = "RETICULATE"
    FRACTAL = "FRACTAL"
    DISTRIBUTED = "DISTRIBUTED"
    HORIZON_INVERTED = "HORIZON_INVERTED"


class GovernanceMode(Enum):
    ACEPHALOUS = "ACEPHALOUS"
    STEWARDED = "STEWARDED"
    SOVEREIGN = "SOVEREIGN"
    CAPTURED = "CAPTURED"


class GateVerdict(Enum):
    PASS = "PASS"
    QUALIFIED = "QUALIFIED"
    BLOCKED = "BLOCKED"
    OPAQUE = "OPAQUE"
    INERT_TAXONOMY = "INERT_TAXONOMY"
    AUTOPOIESIS_EMPIRICAL = "AUTOPOIESIS_EMPIRICAL"
    AUTOPOIESIS_REPRESENTED = "AUTOPOIESIS_REPRESENTED"
    VERIFIED_SUBSTRATE = "VERIFIED_SUBSTRATE"
    UNVERIFIED_SUBSTRATE = "UNVERIFIED_SUBSTRATE"
    INERT_OR_NONVIABLE = "INERT_OR_NONVIABLE"
    ARTICULATION_POINTS_FOUND = "ARTICULATION_POINTS_FOUND"
    NO_SINGLE_NODE_CUT_FOUND = "NO_SINGLE_NODE_CUT_FOUND"
    TWO_NODE_CUTS_FOUND = "TWO_NODE_CUTS_FOUND"
    NO_TWO_NODE_CUT_FOUND = "NO_TWO_NODE_CUT_FOUND"


HARD_BLOCK_VERDICTS: frozenset[GateVerdict] = frozenset({GateVerdict.BLOCKED})
SOFT_BLOCK_VERDICTS: frozenset[GateVerdict] = frozenset({
    GateVerdict.INERT_OR_NONVIABLE,
    GateVerdict.INERT_TAXONOMY,
})
UNCERTAINTY_VERDICTS: frozenset[GateVerdict] = frozenset({
    GateVerdict.UNVERIFIED_SUBSTRATE,
    GateVerdict.OPAQUE,
    GateVerdict.QUALIFIED,
})


def _is_valid_int(val: object) -> bool:
    """Accepts finite Python ints only; rejects bool, float (including inf/nan), str, and None."""
    return isinstance(val, int) and not isinstance(val, bool)


def _is_non_negative_int(val: object) -> bool:
    return _is_valid_int(val) and val >= 0  # type: ignore[operator]


def _is_valid_positive_ttl(ttl: object) -> bool:
    return _is_valid_int(ttl) and ttl > 0  # type: ignore[operator]


def _is_valid_interval(interval: object) -> bool:
    return (
        isinstance(interval, tuple)
        and len(interval) == 2
        and _is_valid_int(interval[0])
        and _is_valid_int(interval[1])
    )


def _to_json_safe(obj: Any) -> Any:
    """Deterministic recursive serializer for Enums, sets, tuples, dicts, and dataclasses."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (set, frozenset)):
        serialized = [_to_json_safe(item) for item in obj]
        return sorted(serialized, key=lambda x: json.dumps(x, sort_keys=True))
    if isinstance(obj, (list, tuple)):
        return [_to_json_safe(item) for item in obj]
    if isinstance(obj, dict):
        return {
            str(k): _to_json_safe(v)
            for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))
        }
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: _to_json_safe(getattr(obj, f.name)) for f in fields(obj)}
    raise TypeError(f"Unsupported type for SC-TOL-001 serialization: {type(obj).__name__}")


@dataclass(frozen=True)
class SourceRecord:
    """Registered provenance record used by E0/T0 to authenticate epistemic tiers."""
    source_id: str
    registered_tier: EpistemicTier
    citation: str
    verified: bool = True


@dataclass(frozen=True)
class AuthorityRecord:
    """Authenticated authority entry for T8 delegation & chain validation."""
    authority_id: str
    authenticated: bool
    permitted_targets: frozenset[str]   # frozenset({"*"}) for wildcard target authority
    permitted_scopes: frozenset[str]    # frozenset({"*"}) for wildcard scope authority
    permitted_modes: frozenset[GovernanceMode]
    valid_interval: tuple[int, int]
    delegation_chain: tuple[str, ...] = ()

    def is_active(self, t: int) -> bool:
        if not _is_valid_interval(self.valid_interval) or not _is_valid_int(t):
            return False
        start, end = self.valid_interval
        return start <= t < end

    def covers_target(self, target_id: str) -> bool:
        return "*" in self.permitted_targets or target_id in self.permitted_targets

    def covers_scope(self, scope: str) -> bool:
        return "*" in self.permitted_scopes or scope in self.permitted_scopes


@dataclass
class SubstrateSpec:
    medium: str
    has_empirical_autopoiesis: bool = False
    has_represented_autopoiesis: bool = False
    # "verified" | "unverified" | "impossible"
    memory_mechanism_status: str = "unverified"


@dataclass(frozen=True)
class GovernanceGrant:
    """Scoped governance G(v, e, tau): evaluated per target, scope, and time window."""
    target_id: str
    scope: str
    mode: GovernanceMode
    valid_interval: tuple[int, int]
    granted_by: str
    is_emergency: bool = False
    emergency_ttl: Optional[int] = None

    def effective_expiry(self) -> int:
        start, end = self.valid_interval
        if self.is_emergency and _is_valid_positive_ttl(self.emergency_ttl):
            return min(end, start + self.emergency_ttl)  # type: ignore[operator]
        return end

    def is_active(self, t: int) -> bool:
        if not _is_valid_interval(self.valid_interval) or not _is_valid_int(t):
            return False
        start, _ = self.valid_interval
        return start <= t < self.effective_expiry()


@dataclass(frozen=True)
class EscalationRequest:
    actor_id: str
    target_id: str
    requested_mode: GovernanceMode
    requested_scope: str
    authorized_by: str
    activation_time: int = 0
    via_proxy: Optional[str] = None
    is_emergency: bool = False
    emergency_ttl: Optional[int] = None


@dataclass
class HorizonBoundary:
    boundary_id: str
    opaque_nodes: set[str]
    asserted_internal_claims: list[str] = field(default_factory=list)


@dataclass
class InferenceClaim:
    claim_id: str
    # e.g. "tier_promotion" | "shared_consciousness_from_provenance"
    # | "connectivity_implies_cooperation" | "centrality_to_sovereignty"
    # | "guardian_to_sovereignty" (any "*_to_sovereignty" is blocked by T4)
    kind: str
    source_tier: EpistemicTier
    target_tier: Optional[EpistemicTier] = None
    source_id: Optional[str] = None
    subject_nodes: set[str] = field(default_factory=set)
    evidence_nodes: set[str] = field(default_factory=set)
    detail: str = ""


@dataclass(frozen=True)
class VisibilityProjection:
    """Immutable post-E2 view enforcing Opaque(v) => not Inspect(v) and not Infer(v)."""
    visible_nodes: frozenset[str]
    visible_edges: frozenset[tuple[str, str]]
    visible_claims: tuple[InferenceClaim, ...]
    visible_governance: tuple[GovernanceGrant, ...]
    visible_escalations: tuple[EscalationRequest, ...]
    visible_fault_sets: tuple[tuple[frozenset[str], frozenset[str]], ...]  # (applied, excluded_opaque)
    masked_nodes: frozenset[str]


@dataclass(frozen=True)
class GateRecord:
    gate: str
    verdict: GateVerdict
    message: str
    preserved_observation: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CompilationResult:
    """Immutable, versioned compilation output safe for caching and cross-service handoff."""
    system_id: str
    declared_tier: EpistemicTier
    effective_tier: Optional[EpistemicTier]
    declared_topology: TopologyClass
    effective_topology: TopologyClass
    schema_version: str = SCHEMA_VERSION
    executed_stages: tuple[str, ...] = ()
    records: tuple[GateRecord, ...] = ()
    hard_blocks: tuple[GateRecord, ...] = ()
    soft_blocks: tuple[GateRecord, ...] = ()
    uncertainties: tuple[GateRecord, ...] = ()
    cut_vertices: frozenset[str] = frozenset()
    two_node_cuts: frozenset[tuple[str, str]] = frozenset()
    two_node_cuts_skipped: bool = False
    masked_nodes: frozenset[str] = frozenset()
    active_grants: tuple[GovernanceGrant, ...] = ()
    expired_grants: tuple[GovernanceGrant, ...] = ()
    accepted_escalations: tuple[EscalationRequest, ...] = ()
    rejected_escalations: tuple[EscalationRequest, ...] = ()
    fault_reports: tuple[dict[str, Any], ...] = ()
    child_results: tuple["CompilationResult", ...] = ()
    emitted_subgenerators: tuple["MetaGenerator", ...] = ()

    @property
    def is_blocking(self) -> bool:
        return len(self.hard_blocks) > 0

    @property
    def is_trustworthy(self) -> bool:
        return not self.is_blocking and self.effective_tier is not None

    def verdicts_for(self, gate: str) -> list[GateVerdict]:
        return [r.verdict for r in self.records if r.gate == gate]

    def codes_for(self, gate: str) -> list[str]:
        return [
            r.preserved_observation["code"]
            for r in self.records
            if r.gate == gate and "code" in r.preserved_observation
        ]

    def with_appended_records(self, extra_records: list[GateRecord]) -> "CompilationResult":
        """Returns a new immutable CompilationResult with extra records classified into buckets."""
        if not extra_records:
            return self
        new_records = self.records + tuple(extra_records)
        new_hard = self.hard_blocks + tuple(r for r in extra_records if r.verdict in HARD_BLOCK_VERDICTS)
        new_soft = self.soft_blocks + tuple(r for r in extra_records if r.verdict in SOFT_BLOCK_VERDICTS)
        new_unc = self.uncertainties + tuple(r for r in extra_records if r.verdict in UNCERTAINTY_VERDICTS)
        return replace(
            self,
            records=new_records,
            hard_blocks=new_hard,
            soft_blocks=new_soft,
            uncertainties=new_unc,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = _to_json_safe(self)
        payload["is_blocking"] = self.is_blocking
        payload["is_trustworthy"] = self.is_trustworthy
        return payload

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=indent)


class _ResultBuilder:
    """Internal mutable accumulator converted into a frozen CompilationResult at E7."""

    def __init__(self, state: "SystemState") -> None:
        self.system_id = state.system_id
        self.declared_tier = state.epistemic_tier
        self.effective_tier: Optional[EpistemicTier] = state.epistemic_tier
        self.declared_topology = state.topology
        self.effective_topology = state.topology
        self.executed_stages: list[str] = []
        self.records: list[GateRecord] = []
        self.hard_blocks: list[GateRecord] = []
        self.soft_blocks: list[GateRecord] = []
        self.uncertainties: list[GateRecord] = []
        self.cut_vertices: frozenset[str] = frozenset()
        self.two_node_cuts: frozenset[tuple[str, str]] = frozenset()
        self.two_node_cuts_skipped: bool = False
        self.masked_nodes: frozenset[str] = frozenset()
        self.active_grants: list[GovernanceGrant] = []
        self.expired_grants: list[GovernanceGrant] = []
        self.accepted_escalations: list[EscalationRequest] = []
        self.rejected_escalations: list[EscalationRequest] = []
        self.fault_reports: list[dict[str, Any]] = []
        self.child_results: list[CompilationResult] = []
        self.emitted_subgenerators: list[MetaGenerator] = []

    def add(self, record: GateRecord) -> None:
        self.records.append(record)
        if record.verdict in HARD_BLOCK_VERDICTS:
            self.hard_blocks.append(record)
        if record.verdict in SOFT_BLOCK_VERDICTS:
            self.soft_blocks.append(record)
        if record.verdict in UNCERTAINTY_VERDICTS:
            self.uncertainties.append(record)

    def build(self) -> CompilationResult:
        return CompilationResult(
            system_id=self.system_id,
            declared_tier=self.declared_tier,
            effective_tier=self.effective_tier,
            declared_topology=self.declared_topology,
            effective_topology=self.effective_topology,
            executed_stages=tuple(self.executed_stages),
            records=tuple(self.records),
            hard_blocks=tuple(self.hard_blocks),
            soft_blocks=tuple(self.soft_blocks),
            uncertainties=tuple(self.uncertainties),
            cut_vertices=self.cut_vertices,
            two_node_cuts=self.two_node_cuts,
            two_node_cuts_skipped=self.two_node_cuts_skipped,
            masked_nodes=self.masked_nodes,
            active_grants=tuple(self.active_grants),
            expired_grants=tuple(self.expired_grants),
            accepted_escalations=tuple(self.accepted_escalations),
            rejected_escalations=tuple(self.rejected_escalations),
            fault_reports=tuple(self.fault_reports),
            child_results=tuple(self.child_results),
            emitted_subgenerators=tuple(self.emitted_subgenerators),
        )


@dataclass(frozen=True)
class MetaGenerator:
    """Higher-order topology generator M: (Sigma, T, G, E) -> {S_1..S_n}."""
    generator_id: str
    immutable_gates: frozenset[str] = CORE_IMMUTABLE_GATES
    tamper_events: tuple[str, ...] = field(default=(), init=False)

    def __post_init__(self) -> None:
        supplied = frozenset(self.immutable_gates)
        stripped = sorted(CORE_IMMUTABLE_GATES - supplied)
        object.__setattr__(self, "tamper_events", tuple(stripped))
        object.__setattr__(self, "immutable_gates", supplied | CORE_IMMUTABLE_GATES)

    def emit(
        self,
        compiler: "StructuralCompiler",
        child_state: "SystemState",
        requested_exemptions: Optional[set[str]] = None,
        _depth: int = 0,
        _emit_tamper_record: bool = True,
    ) -> CompilationResult:
        """
        Independently compiles child state at depth + 1, enforces max_meta_depth even on
        direct calls, blocks core gate exemptions, and returns a new frozen CompilationResult.
        """
        extra_records: list[GateRecord] = []
        if _emit_tamper_record and self.tamper_events:
            extra_records.append(GateRecord(
                gate="E6",
                verdict=GateVerdict.BLOCKED,
                message=(
                    f"MetaGenerator '{self.generator_id}' was constructed without canonical gates "
                    f"{list(self.tamper_events)}; canonical CORE_IMMUTABLE_GATES restored."
                ),
                preserved_observation={
                    "code": "generator_tamper_restored",
                    "generator_id": self.generator_id,
                    "stripped": list(self.tamper_events),
                },
            ))

        if _depth >= compiler.max_meta_depth:
            extra_records.append(GateRecord(
                gate="E6",
                verdict=GateVerdict.BLOCKED,
                message=(
                    f"Meta-generator recursion depth cap ({compiler.max_meta_depth}) exceeded "
                    f"emitting child '{child_state.system_id}'."
                ),
                preserved_observation={
                    "code": "meta_recursion_depth_exceeded",
                    "generator_id": self.generator_id,
                    "child_id": child_state.system_id,
                    "depth": _depth,
                    "max_meta_depth": compiler.max_meta_depth,
                },
            ))
            blocked_builder = _ResultBuilder(child_state)
            blocked_builder.effective_tier = None
            blocked_builder.executed_stages.extend(["E6", "E7"])
            for rec in extra_records:
                blocked_builder.add(rec)
            return blocked_builder.build()

        exemptions = requested_exemptions or set()
        child_result = compiler.compile(child_state, _depth=_depth + 1)

        illegal = sorted(exemptions & CORE_IMMUTABLE_GATES)
        if illegal:
            extra_records.append(GateRecord(
                gate="T8",
                verdict=GateVerdict.BLOCKED,
                message=f"MetaGenerator '{self.generator_id}' cannot exempt child from {illegal}.",
                preserved_observation={
                    "code": "illegal_child_exemption",
                    "generator_id": self.generator_id,
                    "exemptions": illegal,
                },
            ))

        return child_result.with_appended_records(extra_records)

    def emit_subgenerator(
        self,
        child_id: str,
        requested_gates: frozenset[str],
    ) -> tuple["MetaGenerator", GateRecord]:
        """Enforces canonical CORE_IMMUTABLE_GATES regardless of parent configuration."""
        supplied = frozenset(requested_gates)
        missing = sorted(CORE_IMMUTABLE_GATES - supplied)
        sub_gen = MetaGenerator(child_id, supplied)  # __post_init__ forces canonical gates
        if missing:
            record = GateRecord(
                gate="T8",
                verdict=GateVerdict.BLOCKED,
                message=f"Sub-generator '{child_id}' attempted to strip {missing}; canonical core gates enforced.",
                preserved_observation={
                    "code": "subgenerator_gate_stripping",
                    "child_id": child_id,
                    "stripped": missing,
                },
            )
            return sub_gen, record
        return sub_gen, GateRecord("T8", GateVerdict.PASS, f"Sub-generator '{child_id}' preserved core gates.")


@dataclass
class MetaArchitectureSpec:
    """Explicit higher-order container processed during E6 · Meta-Boundary Verification."""
    generator: MetaGenerator
    child_emissions: list[tuple["SystemState", set[str]]] = field(default_factory=list)
    subgenerator_emissions: list[tuple[str, frozenset[str]]] = field(default_factory=list)


@dataclass
class SystemState:
    system_id: str
    substrate: SubstrateSpec
    topology: TopologyClass
    epistemic_tier: EpistemicTier
    nodes: set[str]
    edges: set[tuple[str, str]]
    evaluation_time: int = 0
    historical_audit_mode: bool = False
    require_full_chain_verification: bool = False
    source_id: Optional[str] = None
    require_registered_provenance: bool = False
    source_registry: dict[str, SourceRecord] = field(default_factory=dict)
    authority_registry: dict[str, AuthorityRecord] = field(default_factory=dict)
    root_nodes: set[str] = field(default_factory=set)
    force_single_root: bool = False
    governance: list[GovernanceGrant] = field(default_factory=list)
    escalations: list[EscalationRequest] = field(default_factory=list)
    boundaries: list[HorizonBoundary] = field(default_factory=list)
    claims: list[InferenceClaim] = field(default_factory=list)
    fault_sets: list[set[str]] = field(default_factory=list)
    meta_spec: Optional[MetaArchitectureSpec] = None


# =============================================================================
# 2. Graph Primitives & Operators (O3: reticulate, O6: prune_and_recover)
# =============================================================================

@dataclass(frozen=True)
class ReticulationResult:
    topology: TopologyClass
    cut_vertices: frozenset[str]
    edge_added: bool
    topology_mutated: bool


def _build_simple_undirected_adj(
    nodes: set[str] | frozenset[str],
    edges: set[tuple[str, str]] | frozenset[tuple[str, str]],
) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = {n: set() for n in nodes}
    for u, v in edges:
        if u in adj and v in adj and u != v:
            adj[u].add(v)
            adj[v].add(u)
    return adj


def count_components(
    nodes: set[str] | frozenset[str],
    edges: set[tuple[str, str]] | frozenset[tuple[str, str]],
) -> int:
    if not nodes:
        return 0
    adj = _build_simple_undirected_adj(nodes, edges)
    visited: set[str] = set()
    components = 0
    for start in nodes:
        if start in visited:
            continue
        components += 1
        queue = deque([start])
        visited.add(start)
        while queue:
            curr = queue.popleft()
            for nxt in adj[curr]:
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
    return components


def find_cut_vertices(
    nodes: set[str] | frozenset[str],
    edges: set[tuple[str, str]] | frozenset[tuple[str, str]],
) -> frozenset[str]:
    """
    Iterative Tarjan articulation-point algorithm in O(V + E) time and O(V) stack space.
    Deterministic and safe against Python recursion limits on large service graphs.
    """
    if len(nodes) < 3:
        return frozenset()

    adj = {n: sorted(nbrs) for n, nbrs in _build_simple_undirected_adj(nodes, edges).items()}
    disc: dict[str, int] = {}
    low: dict[str, int] = {}
    articulation_points: set[str] = set()
    timer = 0

    for root in sorted(nodes):
        if root in disc:
            continue
        disc[root] = low[root] = timer
        timer += 1
        root_children = 0
        # Stack frame: [node, parent, next_neighbor_index]
        stack: list[list[Any]] = [[root, None, 0]]

        while stack:
            frame = stack[-1]
            u: str = frame[0]
            parent: Optional[str] = frame[1]
            idx: int = frame[2]
            neighbors = adj[u]

            if idx < len(neighbors):
                frame[2] = idx + 1
                v = neighbors[idx]
                if v == parent:
                    continue
                if v not in disc:
                    if u == root:
                        root_children += 1
                    disc[v] = low[v] = timer
                    timer += 1
                    stack.append([v, u, 0])
                else:
                    if disc[v] < low[u]:
                        low[u] = disc[v]
            else:
                stack.pop()
                if parent is not None:
                    if low[u] < low[parent]:
                        low[parent] = low[u]
                    if parent != root and low[u] >= disc[parent]:
                        articulation_points.add(parent)
                elif root_children > 1:
                    articulation_points.add(root)

    return frozenset(articulation_points)


def find_two_node_cuts_excluding_single_cuts(
    nodes: set[str] | frozenset[str],
    edges: set[tuple[str, str]] | frozenset[tuple[str, str]],
    single_cuts: set[str] | frozenset[str],
    max_nodes: int = 50,
) -> tuple[frozenset[tuple[str, str]], bool]:
    """
    Finds all two-vertex cut pairs {u, v} where neither u nor v is a single-node cut.
    Because single-node cuts are excluded, every returned pair is mathematically a minimal
    2-vertex cut (no proper non-empty subset disconnects the graph).
    Returns (cut_pairs, skipped_due_to_size).
    """
    if len(nodes) > max_nodes:
        return frozenset(), True
    if len(nodes) < 4:
        return frozenset(), False

    base = count_components(nodes, edges)
    candidates = sorted(n for n in nodes if n not in single_cuts)
    cuts: set[tuple[str, str]] = set()
    for u, v in combinations(candidates, 2):
        if count_components(nodes - {u, v}, edges) > base:
            cuts.add((u, v))
    return frozenset(cuts), False


def o3_reticulate(state: SystemState, node_a: str, node_b: str) -> ReticulationResult:
    """
    O3: Rejects self-loops, ignores already-present undirected edges without mutating
    topology, adds genuine lateral edges, and recalculates cut vertices without
    assuming resilience.

    Topology promotion semantics: only acyclic tree declarations (ARBORESCENT,
    INVERTED_ARBORESCENT) automatically reclassify to RETICULATE when a cycle forms.
    DISTRIBUTED, FRACTAL, and HORIZON_INVERTED retain their primary topology class.
    """
    if node_a == node_b:
        raise ValueError("Self-loops are prohibited in O3 reticulate.")
    if node_a not in state.nodes or node_b not in state.nodes:
        raise ValueError("Both endpoints must exist in state.nodes.")

    if (node_a, node_b) in state.edges or (node_b, node_a) in state.edges:
        return ReticulationResult(
            topology=state.topology,
            cut_vertices=find_cut_vertices(state.nodes, state.edges),
            edge_added=False,
            topology_mutated=False,
        )

    before_components = count_components(state.nodes, state.edges)
    state.edges.add((node_a, node_b))
    after_components = count_components(state.nodes, state.edges)

    mutated = False
    if before_components == after_components and state.topology in {
        TopologyClass.ARBORESCENT,
        TopologyClass.INVERTED_ARBORESCENT,
    }:
        state.topology = TopologyClass.RETICULATE
        mutated = True

    return ReticulationResult(
        topology=state.topology,
        cut_vertices=find_cut_vertices(state.nodes, state.edges),
        edge_added=True,
        topology_mutated=mutated,
    )


def o6_prune_and_recover(
    visible_nodes: frozenset[str],
    visible_edges: frozenset[tuple[str, str]],
    applied_fault: frozenset[str],
    excluded_opaque: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    """O6: Separately reports node loss, component loss, and fragmentation."""
    base_components = count_components(visible_nodes, visible_edges)
    actual_removed = visible_nodes & applied_fault
    surviving = visible_nodes - actual_removed
    after_components = count_components(surviving, visible_edges)
    delta = after_components - base_components

    return {
        "fault_set": sorted(actual_removed),
        "excluded_opaque_nodes": sorted(excluded_opaque),
        "lost_node_count": len(actual_removed),
        "surviving_count": len(surviving),
        "components_before": base_components,
        "components_after": after_components,
        "component_delta": delta,
        "components_lost": max(0, base_components - after_components),
        "fragmentation_status": (
            "FAULT_INCREASED_COMPONENT_COUNT"
            if after_components > base_components
            else "NO_ADDITIONAL_FRAGMENTATION"
        ),
    }


# =============================================================================
# 3. SC-TOL-001 v2.1-rc5 Compiler Pipeline (E0-E7) & Gates (T0-T8)
# =============================================================================

class StructuralCompiler:
    def __init__(
        self,
        two_node_cut_max_nodes: int = 50,
        max_meta_depth: int = 8,
        halt_on_t0_block: bool = False,
    ) -> None:
        if not _is_non_negative_int(two_node_cut_max_nodes):
            raise ValueError("two_node_cut_max_nodes must be a non-negative integer.")
        if not _is_non_negative_int(max_meta_depth):
            raise ValueError("max_meta_depth must be a non-negative integer.")
        if not isinstance(halt_on_t0_block, bool):
            raise ValueError("halt_on_t0_block must be a bool.")

        self.two_node_cut_max_nodes = two_node_cut_max_nodes
        self.max_meta_depth = max_meta_depth
        self.halt_on_t0_block = halt_on_t0_block

    def compile(self, state: SystemState, _depth: int = 0) -> CompilationResult:
        """
        Executes the SC-TOL-001 v2.1-rc5 pipeline (E0-E7) and returns an immutable
        CompilationResult. When halt_on_t0_block=True, any T0 BLOCK short-circuits
        immediately to E7 to prevent downstream inspection of untrusted payloads.
        """
        builder = _ResultBuilder(state)

        # E0: Source Admission (T0)
        builder.executed_stages.append("E0")
        t0_blocked = self._gate_t0_epistemic_firewall(state, builder)
        if t0_blocked and self.halt_on_t0_block:
            builder.executed_stages.append("E7")
            return builder.build()

        # E1: State Declaration validation
        builder.executed_stages.append("E1")
        self._stage_e1_state_declaration(state, builder)

        # E2: Topology & Boundary Lock (T1 + T6) -> immutable VisibilityProjection
        builder.executed_stages.append("E2")
        self._gate_t1_topology_lock(state, builder)
        projection = self._gate_t6_build_visibility_projection(state, builder)

        # E3: Operating & Substrate Validation (T2, T3, T7) on visible projection ONLY
        builder.executed_stages.append("E3")
        self._gate_t2_autopoiesis(state, builder)
        self._gate_t3_provenance_agency(projection, builder)
        self._gate_t7_substrate_viability(state, builder)

        # E4: Authority Validation (T4 on visible claims, T8 on visible grants + escalations)
        builder.executed_stages.append("E4")
        self._gate_t4_axis_not_sovereign(projection, builder)
        self._gate_t8_recursive_capture(state, projection, builder)

        # E5: Fault Simulation (T5 + O6) on visible projection ONLY
        builder.executed_stages.append("E5")
        self._gate_t5_fault_isolation(projection, builder)

        # E6: Meta-Boundary Verification (higher-order generator & inheritance)
        builder.executed_stages.append("E6")
        self._stage_e6_meta_boundary(state, builder, _depth=_depth)

        # E7: Immutable Compilation Emission
        builder.executed_stages.append("E7")
        return builder.build()

    # ------------------------------------------------------------------ E0 / T0
    def _gate_t0_epistemic_firewall(self, state: SystemState, builder: _ResultBuilder) -> bool:
        blocked = False

        if state.source_id is not None:
            src = state.source_registry.get(state.source_id)
            if src is None or not src.verified:
                blocked = True
                builder.effective_tier = None
                builder.add(GateRecord(
                    gate="T0",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Unregistered or unverified system source '{state.source_id}'.",
                    preserved_observation={"code": "unregistered_source", "source_id": state.source_id},
                ))
            elif src.registered_tier != state.epistemic_tier:
                blocked = True
                builder.effective_tier = None
                builder.add(GateRecord(
                    gate="T0",
                    verdict=GateVerdict.BLOCKED,
                    message=(
                        f"System tier '{state.epistemic_tier.value}' contradicts registered "
                        f"source tier '{src.registered_tier.value}'."
                    ),
                    preserved_observation={
                        "code": "system_tier_mismatch",
                        "source_id": state.source_id,
                        "declared_tier": state.epistemic_tier.value,
                        "registered_tier": src.registered_tier.value,
                    },
                ))
        elif state.require_registered_provenance:
            blocked = True
            builder.effective_tier = None
            builder.add(GateRecord(
                gate="T0",
                verdict=GateVerdict.BLOCKED,
                message="System provenance registration required but source_id is missing.",
                preserved_observation={"code": "missing_system_provenance"},
            ))

        for claim in state.claims:
            effective_claim_tier = claim.source_tier
            if claim.source_id is not None:
                rec = state.source_registry.get(claim.source_id)
                if rec is None or not rec.verified:
                    blocked = True
                    builder.add(GateRecord(
                        gate="T0",
                        verdict=GateVerdict.BLOCKED,
                        message=f"Claim '{claim.claim_id}' cites unregistered source '{claim.source_id}'.",
                        preserved_observation={
                            "code": "unregistered_claim_source",
                            "claim_id": claim.claim_id,
                            "source_id": claim.source_id,
                        },
                    ))
                    continue
                if claim.source_tier != rec.registered_tier:
                    blocked = True
                    builder.add(GateRecord(
                        gate="T0",
                        verdict=GateVerdict.BLOCKED,
                        message=(
                            f"Claim '{claim.claim_id}' falsified source tier: declared "
                            f"{claim.source_tier.value}, registered {rec.registered_tier.value}."
                        ),
                        preserved_observation={
                            "code": "falsified_source_tier",
                            "claim_id": claim.claim_id,
                            "source_id": claim.source_id,
                            "declared": claim.source_tier.value,
                            "registered": rec.registered_tier.value,
                        },
                    ))
                    continue
                effective_claim_tier = rec.registered_tier
            elif state.require_registered_provenance:
                blocked = True
                builder.add(GateRecord(
                    gate="T0",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Claim '{claim.claim_id}' missing required registered provenance.",
                    preserved_observation={"code": "missing_claim_provenance", "claim_id": claim.claim_id},
                ))
                continue

            if claim.kind == "tier_promotion" and claim.target_tier != effective_claim_tier:
                blocked = True
                builder.add(GateRecord(
                    gate="T0",
                    verdict=GateVerdict.BLOCKED,
                    message=(
                        f"Blocked tier promotion from {effective_claim_tier.value} "
                        f"to {claim.target_tier.value if claim.target_tier else 'UNKNOWN'}."
                    ),
                    preserved_observation={
                        "code": "blocked_tier_promotion",
                        "claim_id": claim.claim_id,
                        "detail": claim.detail,
                    },
                ))

        if not blocked:
            builder.add(GateRecord("T0", GateVerdict.PASS, f"Provenance & tier locked at {state.epistemic_tier.value}."))
        return blocked

    # ------------------------------------------------------------------ E1
    def _stage_e1_state_declaration(self, state: SystemState, builder: _ResultBuilder) -> None:
        blocked = False

        if not _is_non_negative_int(state.evaluation_time):
            blocked = True
            builder.add(GateRecord(
                "E1",
                GateVerdict.BLOCKED,
                "evaluation_time must be a finite non-negative integer.",
                preserved_observation={"code": "invalid_evaluation_time", "value": str(state.evaluation_time)},
            ))

        self_loops = sorted((u, v) for (u, v) in state.edges if u == v)
        if self_loops:
            blocked = True
            builder.add(GateRecord(
                "E1",
                GateVerdict.BLOCKED,
                f"Self-loop edges are prohibited: {self_loops}.",
                preserved_observation={"code": "self_loop_edge", "edges": self_loops},
            ))

        dangling = sorted((u, v) for (u, v) in state.edges if u not in state.nodes or v not in state.nodes)
        if dangling:
            blocked = True
            builder.add(GateRecord(
                "E1",
                GateVerdict.BLOCKED,
                f"Dangling edges reference undeclared nodes: {dangling}.",
                preserved_observation={"code": "dangling_edge", "edges": dangling},
            ))

        for key, src_rec in state.source_registry.items():
            if key != src_rec.source_id:
                blocked = True
                builder.add(GateRecord(
                    "E1",
                    GateVerdict.BLOCKED,
                    f"source_registry key '{key}' does not match record source_id '{src_rec.source_id}'.",
                    preserved_observation={
                        "code": "source_registry_key_mismatch",
                        "key": key,
                        "record_id": src_rec.source_id,
                    },
                ))

        for key, auth_rec in state.authority_registry.items():
            if key != auth_rec.authority_id:
                blocked = True
                builder.add(GateRecord(
                    "E1",
                    GateVerdict.BLOCKED,
                    f"authority_registry key '{key}' does not match record authority_id '{auth_rec.authority_id}'.",
                    preserved_observation={
                        "code": "authority_registry_key_mismatch",
                        "key": key,
                        "record_id": auth_rec.authority_id,
                    },
                ))
            if not _is_valid_interval(auth_rec.valid_interval):
                blocked = True
                builder.add(GateRecord(
                    "E1",
                    GateVerdict.BLOCKED,
                    f"AuthorityRecord '{key}' has non-integer/non-finite interval bounds.",
                    preserved_observation={"code": "invalid_interval_bounds", "authority_id": key},
                ))

        for grant in state.governance:
            if not _is_valid_interval(grant.valid_interval):
                blocked = True
                builder.add(GateRecord(
                    "E1",
                    GateVerdict.BLOCKED,
                    f"GovernanceGrant for '{grant.target_id}' has non-integer/non-finite interval bounds.",
                    preserved_observation={"code": "invalid_interval_bounds", "target_id": grant.target_id},
                ))
            if grant.is_emergency and not _is_valid_positive_ttl(grant.emergency_ttl):
                blocked = True
                builder.add(GateRecord(
                    "E1",
                    GateVerdict.BLOCKED,
                    f"Emergency GovernanceGrant for '{grant.target_id}' has invalid emergency_ttl.",
                    preserved_observation={
                        "code": "invalid_emergency_ttl",
                        "target_id": grant.target_id,
                        "ttl": str(grant.emergency_ttl),
                    },
                ))

        for req in state.escalations:
            if not _is_non_negative_int(req.activation_time):
                blocked = True
                builder.add(GateRecord(
                    "E1",
                    GateVerdict.BLOCKED,
                    f"EscalationRequest for '{req.actor_id}' must have a non-negative integer activation_time.",
                    preserved_observation={
                        "code": "invalid_activation_time",
                        "actor_id": req.actor_id,
                        "activation_time": str(req.activation_time),
                    },
                ))
            if req.is_emergency and not _is_valid_positive_ttl(req.emergency_ttl):
                blocked = True
                builder.add(GateRecord(
                    "E1",
                    GateVerdict.BLOCKED,
                    f"Emergency EscalationRequest for '{req.actor_id}' has invalid emergency_ttl.",
                    preserved_observation={
                        "code": "invalid_emergency_ttl",
                        "actor_id": req.actor_id,
                        "ttl": str(req.emergency_ttl),
                    },
                ))

        if not blocked:
            builder.add(GateRecord(
                "E1",
                GateVerdict.PASS,
                f"Declared S=(medium={state.substrate.medium}, T={state.topology.value}, "
                f"E={state.epistemic_tier.value}, t={state.evaluation_time}).",
            ))

    # ------------------------------------------------------------------ E2 / T1 & T6
    def _gate_t1_topology_lock(self, state: SystemState, builder: _ResultBuilder) -> None:
        if state.topology == TopologyClass.DISTRIBUTED and state.force_single_root:
            builder.add(GateRecord(
                gate="T1",
                verdict=GateVerdict.BLOCKED,
                message="Forced single-root constraint violates DISTRIBUTED topology.",
                preserved_observation={
                    "code": "forced_single_root_on_distributed",
                    "topology": state.topology.value,
                    "roots": sorted(state.root_nodes),
                },
            ))
            return

        if state.topology == TopologyClass.HORIZON_INVERTED and not state.boundaries:
            builder.effective_topology = TopologyClass.INVERTED_ARBORESCENT
            builder.add(GateRecord(
                gate="T1",
                verdict=GateVerdict.QUALIFIED,
                message="HORIZON_INVERTED declared without explicit boundary; effective topology set to INVERTED_ARBORESCENT.",
                preserved_observation={
                    "code": "missing_horizon_boundary",
                    "declared_topology": state.topology.value,
                    "effective_topology": TopologyClass.INVERTED_ARBORESCENT.value,
                },
            ))
            return

        # Validate declared topology against actual simple-graph metrics
        adj = _build_simple_undirected_adj(state.nodes, state.edges)
        n = len(state.nodes)
        m = sum(len(nbrs) for nbrs in adj.values()) // 2
        components = count_components(state.nodes, state.edges)
        has_cycle = m > (n - components) if n > 0 else False

        qualified = False
        if state.topology in {TopologyClass.ARBORESCENT, TopologyClass.INVERTED_ARBORESCENT}:
            if has_cycle:
                qualified = True
                builder.effective_topology = TopologyClass.RETICULATE
                builder.add(GateRecord(
                    gate="T1",
                    verdict=GateVerdict.QUALIFIED,
                    message=(
                        f"Declared {state.topology.value} graph contains cycle(s) "
                        f"(n={n}, m={m}, components={components}); effective topology set to RETICULATE."
                    ),
                    preserved_observation={
                        "code": "topology_structure_mismatch",
                        "declared_topology": state.topology.value,
                        "effective_topology": TopologyClass.RETICULATE.value,
                        "node_count": n,
                        "edge_count": m,
                        "components": components,
                    },
                ))
            elif components > 1:
                qualified = True
                builder.add(GateRecord(
                    gate="T1",
                    verdict=GateVerdict.QUALIFIED,
                    message=f"Declared {state.topology.value} graph is disconnected ({components} components).",
                    preserved_observation={
                        "code": "disconnected_arborescent_graph",
                        "declared_topology": state.topology.value,
                        "components": components,
                    },
                ))
        elif state.topology == TopologyClass.RETICULATE and n >= 3 and not has_cycle:
            qualified = True
            builder.add(GateRecord(
                gate="T1",
                verdict=GateVerdict.QUALIFIED,
                message="Declared RETICULATE topology contains no cycles (structurally acyclic forest).",
                preserved_observation={
                    "code": "reticulate_without_cycles",
                    "declared_topology": state.topology.value,
                    "node_count": n,
                    "edge_count": m,
                },
            ))
        elif state.topology == TopologyClass.DISTRIBUTED and len(state.root_nodes) == 1:
            qualified = True
            builder.add(GateRecord(
                gate="T1",
                verdict=GateVerdict.QUALIFIED,
                message="Declared DISTRIBUTED topology specifies exactly one root node.",
                preserved_observation={
                    "code": "distributed_single_root_declared",
                    "roots": sorted(state.root_nodes),
                },
            ))
        elif state.topology == TopologyClass.FRACTAL and n < 4:
            qualified = True
            builder.add(GateRecord(
                gate="T1",
                verdict=GateVerdict.QUALIFIED,
                message=f"Declared FRACTAL topology has only {n} node(s); insufficient scale to verify self-similarity.",
                preserved_observation={
                    "code": "fractal_insufficient_scale",
                    "node_count": n,
                },
            ))

        if not qualified:
            builder.add(GateRecord("T1", GateVerdict.PASS, f"Topology validated: {state.topology.value}."))

    def _gate_t6_build_visibility_projection(
        self,
        state: SystemState,
        builder: _ResultBuilder,
    ) -> VisibilityProjection:
        masked: set[str] = set()
        if not state.boundaries:
            builder.add(GateRecord("T6", GateVerdict.PASS, "No opaque observational boundaries declared."))
        else:
            for boundary in state.boundaries:
                masked.update(boundary.opaque_nodes)
                builder.add(GateRecord(
                    gate="T6",
                    verdict=GateVerdict.OPAQUE,
                    message=f"Boundary '{boundary.boundary_id}' masks {sorted(boundary.opaque_nodes)}.",
                    preserved_observation={"code": "boundary_mask_applied", "boundary_id": boundary.boundary_id},
                ))
                for asserted in boundary.asserted_internal_claims:
                    builder.add(GateRecord(
                        gate="T6",
                        verdict=GateVerdict.BLOCKED,
                        message=f"Rejected verification behind opaque boundary: '{asserted}'.",
                        preserved_observation={
                            "code": "opaque_internal_claim_rejected",
                            "boundary_id": boundary.boundary_id,
                            "claim": asserted,
                        },
                    ))

        builder.masked_nodes = frozenset(masked)
        visible_nodes = frozenset(state.nodes - masked)
        # Exclude opaque nodes, dangling edges, and self-loops from the downstream projection
        visible_edges = frozenset(
            (u, v) for (u, v) in state.edges
            if u != v and u in visible_nodes and v in visible_nodes
        )

        visible_claims: list[InferenceClaim] = []
        for claim in state.claims:
            touched_opaque = (claim.subject_nodes | claim.evidence_nodes) & masked
            if touched_opaque:
                builder.add(GateRecord(
                    gate="T6",
                    verdict=GateVerdict.BLOCKED,
                    message=(
                        f"Quarantined claim '{claim.claim_id}' ({claim.kind}): "
                        f"references opaque nodes {sorted(touched_opaque)}."
                    ),
                    preserved_observation={
                        "code": "opaque_claim_quarantined",
                        "claim_id": claim.claim_id,
                        "kind": claim.kind,
                        "opaque_nodes": sorted(touched_opaque),
                    },
                ))
            else:
                visible_claims.append(claim)

        visible_governance: list[GovernanceGrant] = []
        for grant in state.governance:
            if grant.target_id in masked:
                builder.add(GateRecord(
                    gate="T6",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Quarantined GovernanceGrant targeting opaque node '{grant.target_id}'.",
                    preserved_observation={
                        "code": "opaque_governance_target",
                        "target_id": grant.target_id,
                        "scope": grant.scope,
                    },
                ))
            else:
                visible_governance.append(grant)

        visible_escalations: list[EscalationRequest] = []
        for req in state.escalations:
            touched = {req.actor_id, req.target_id} & masked
            if touched:
                builder.rejected_escalations.append(req)
                builder.add(GateRecord(
                    gate="T6",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Quarantined EscalationRequest referencing opaque nodes {sorted(touched)}.",
                    preserved_observation={
                        "code": "opaque_escalation_node",
                        "actor_id": req.actor_id,
                        "target_id": req.target_id,
                        "opaque_nodes": sorted(touched),
                    },
                ))
            else:
                visible_escalations.append(req)

        visible_faults: list[tuple[frozenset[str], frozenset[str]]] = []
        for fset in state.fault_sets:
            excluded = frozenset(fset & masked)
            applied = frozenset(fset - masked)
            if excluded:
                builder.add(GateRecord(
                    gate="T6",
                    verdict=GateVerdict.QUALIFIED,
                    message=f"Excluded opaque nodes {sorted(excluded)} from O6 fault simulation.",
                    preserved_observation={
                        "code": "opaque_fault_nodes_excluded",
                        "excluded_opaque_nodes": sorted(excluded),
                    },
                ))
            visible_faults.append((applied, excluded))

        return VisibilityProjection(
            visible_nodes=visible_nodes,
            visible_edges=visible_edges,
            visible_claims=tuple(visible_claims),
            visible_governance=tuple(visible_governance),
            visible_escalations=tuple(visible_escalations),
            visible_fault_sets=tuple(visible_faults),
            masked_nodes=frozenset(masked),
        )

    # ------------------------------------------------------------------ E3 / T2, T3, T7
    def _gate_t2_autopoiesis(self, state: SystemState, builder: _ResultBuilder) -> None:
        sub = state.substrate
        if state.epistemic_tier == EpistemicTier.EMPIRICAL_SCI and sub.has_empirical_autopoiesis:
            builder.add(GateRecord("T2", GateVerdict.AUTOPOIESIS_EMPIRICAL, "Empirical self-maintenance verified."))
            return

        if state.epistemic_tier == EpistemicTier.CORPUS_MYTH:
            if sub.has_empirical_autopoiesis:
                builder.add(GateRecord(
                    gate="T2",
                    verdict=GateVerdict.BLOCKED,
                    message="CORPUS_MYTH entry cannot pass AUTOPOIESIS_EMPIRICAL.",
                    preserved_observation={"code": "myth_empirical_autopoiesis_blocked", "medium": sub.medium},
                ))
            if sub.has_represented_autopoiesis:
                builder.add(GateRecord("T2", GateVerdict.AUTOPOIESIS_REPRESENTED, "Corpus depicts living/sustaining tree."))
                return

        if state.epistemic_tier == EpistemicTier.SPECULATIVE_EXO:
            if sub.has_empirical_autopoiesis:
                builder.add(GateRecord(
                    gate="T2",
                    verdict=GateVerdict.BLOCKED,
                    message="SPECULATIVE_EXO entry cannot self-certify AUTOPOIESIS_EMPIRICAL.",
                    preserved_observation={
                        "code": "speculative_empirical_autopoiesis_blocked",
                        "medium": sub.medium,
                        "has_represented_autopoiesis": sub.has_represented_autopoiesis,
                    },
                ))
                return
            if sub.has_represented_autopoiesis:
                builder.add(GateRecord("T2", GateVerdict.QUALIFIED, "Speculative autopoiesis proposed, not empirically established."))
                return

        builder.add(GateRecord("T2", GateVerdict.INERT_TAXONOMY, "No empirical or represented autopoiesis present."))

    def _gate_t3_provenance_agency(self, proj: VisibilityProjection, builder: _ResultBuilder) -> None:
        blocked = False
        for claim in proj.visible_claims:
            if claim.kind in {"shared_consciousness_from_provenance", "connectivity_implies_cooperation"}:
                blocked = True
                builder.add(GateRecord(
                    gate="T3",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Invalid inference ({claim.kind}): provenance/connectivity does not entail shared agency.",
                    preserved_observation={"code": "provenance_agency_conflation", "claim_id": claim.claim_id},
                ))
        if not blocked:
            builder.add(GateRecord("T3", GateVerdict.PASS, "Provenance, connectivity, and agency remain decoupled."))

    def _gate_t7_substrate_viability(self, state: SystemState, builder: _ResultBuilder) -> None:
        status = state.substrate.memory_mechanism_status
        if status == "impossible":
            builder.add(GateRecord(
                "T7",
                GateVerdict.INERT_OR_NONVIABLE,
                "Declared substrate fails physical/formal constraints.",
                preserved_observation={"code": "nonviable_substrate", "medium": state.substrate.medium},
            ))
            return

        if state.epistemic_tier == EpistemicTier.CORPUS_MYTH:
            if status == "verified":
                builder.add(GateRecord(
                    gate="T7",
                    verdict=GateVerdict.BLOCKED,
                    message="CORPUS_MYTH substrate cannot claim empirical VERIFIED_SUBSTRATE.",
                    preserved_observation={"code": "myth_substrate_self_certification", "medium": state.substrate.medium},
                ))
            else:
                builder.add(GateRecord(
                    gate="T7",
                    verdict=GateVerdict.QUALIFIED,
                    message="Mythological/literary substrate; empirical verification not applicable.",
                ))
            return

        if state.epistemic_tier == EpistemicTier.SPECULATIVE_EXO:
            if status == "verified":
                # Single hard BLOCK without polluting uncertainties; effective status preserved in observation
                builder.add(GateRecord(
                    gate="T7",
                    verdict=GateVerdict.BLOCKED,
                    message="SPECULATIVE_EXO substrate cannot self-certify as VERIFIED_SUBSTRATE.",
                    preserved_observation={
                        "code": "speculative_self_certification",
                        "medium": state.substrate.medium,
                        "effective_substrate_status": GateVerdict.UNVERIFIED_SUBSTRATE.value,
                    },
                ))
                return
            builder.add(GateRecord(
                gate="T7",
                verdict=GateVerdict.UNVERIFIED_SUBSTRATE,
                message="SPECULATIVE_EXO substrate mechanism proposed but not empirically established.",
            ))
            return

        if status == "verified":
            builder.add(GateRecord("T7", GateVerdict.VERIFIED_SUBSTRATE, "Empirical persistence/memory mechanism verified."))
        else:
            builder.add(GateRecord("T7", GateVerdict.UNVERIFIED_SUBSTRATE, "Empirical substrate mechanism not yet verified."))

    # ------------------------------------------------------------------ E4 / T4 & T8
    def _gate_t4_axis_not_sovereign(self, proj: VisibilityProjection, builder: _ResultBuilder) -> None:
        blocked = False
        for claim in proj.visible_claims:
            if claim.kind == "centrality_to_sovereignty" or claim.kind.endswith("_to_sovereignty"):
                blocked = True
                builder.add(GateRecord(
                    gate="T4",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Role or graph centrality claim '{claim.kind}' does not confer sovereign ownership.",
                    preserved_observation={
                        "code": "centrality_to_sovereignty_blocked",
                        "claim_id": claim.claim_id,
                        "claim_kind": claim.kind,
                    },
                ))
        if not blocked:
            builder.add(GateRecord("T4", GateVerdict.PASS, "No centrality or guardian sovereignty claims detected."))

    def _validate_authorizer(
        self,
        auth_id: str,
        target_id: str,
        scope: str,
        mode: GovernanceMode,
        at_time: int,
        forbidden_chain_members: set[str],
        registry: dict[str, AuthorityRecord],
        require_full_chain: bool = False,
    ) -> tuple[Optional[AuthorityRecord], Optional[str]]:
        auth = registry.get(auth_id)
        if auth is None or not auth.authenticated:
            return None, f"Authorizer '{auth_id}' is unknown or unauthenticated."
        if not _is_valid_interval(auth.valid_interval) or not auth.is_active(at_time):
            return None, f"Authorizer '{auth_id}' grant is inactive or malformed at t={at_time}."
        if not auth.covers_target(target_id):
            return None, f"Authorizer '{auth_id}' lacks target authority over '{target_id}'."
        if not auth.covers_scope(scope):
            return None, f"Authorizer '{auth_id}' lacks scope authority for '{scope}'."
        if mode not in auth.permitted_modes:
            return None, f"Authorizer '{auth_id}' cannot grant mode '{mode.value}'."

        # Iterative DFS with active_path vs validated_hops: allows valid diamond DAGs while
        # blocking true cycles, self-loops, actor/proxy loops, and compromised upstream hops.
        validated_hops: set[str] = set()
        active_path: set[str] = {auth_id}
        stack: list[tuple[str, bool]] = [(hop, True) for hop in reversed(auth.delegation_chain)]

        while stack:
            hop_id, entering = stack.pop()
            if not entering:
                active_path.discard(hop_id)
                validated_hops.add(hop_id)
                continue

            if hop_id in forbidden_chain_members:
                return None, f"Authorizer '{auth_id}' delegation chain loops through actor/proxy '{hop_id}'."
            if hop_id in active_path:
                return None, f"Authorizer '{auth_id}' has a cyclic or self-referential delegation chain involving '{hop_id}'."
            if hop_id in validated_hops:
                continue

            hop = registry.get(hop_id)
            if hop is None:
                if require_full_chain:
                    return None, f"Upstream delegation hop '{hop_id}' is unregistered."
                validated_hops.add(hop_id)
                continue
            if not hop.authenticated:
                return None, f"Upstream delegation hop '{hop_id}' is unauthenticated."
            if not _is_valid_interval(hop.valid_interval) or not hop.is_active(at_time):
                return None, f"Upstream delegation hop '{hop_id}' is inactive at t={at_time}."
            if not hop.covers_target(target_id):
                return None, f"Upstream delegation hop '{hop_id}' lacks target authority over '{target_id}'."
            if not hop.covers_scope(scope):
                return None, f"Upstream delegation hop '{hop_id}' lacks scope authority for '{scope}'."
            if mode not in hop.permitted_modes:
                return None, f"Upstream delegation hop '{hop_id}' cannot delegate mode '{mode.value}'."

            active_path.add(hop_id)
            stack.append((hop_id, False))
            for next_hop in reversed(hop.delegation_chain):
                stack.append((next_hop, True))

        return auth, None

    def _gate_t8_recursive_capture(
        self,
        state: SystemState,
        proj: VisibilityProjection,
        builder: _ResultBuilder,
    ) -> None:
        blocked = False

        # 1. Validate existing visible GovernanceGrants
        for grant in proj.visible_governance:
            if not _is_valid_interval(grant.valid_interval):
                blocked = True
                builder.add(GateRecord(
                    gate="T8",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Grant for '{grant.target_id}' has malformed interval bounds.",
                    preserved_observation={"code": "malformed_grant_interval", "target_id": grant.target_id},
                ))
                continue

            start, end = grant.valid_interval
            if start >= end:
                blocked = True
                builder.add(GateRecord(
                    gate="T8",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Grant for '{grant.target_id}' has invalid interval ({start}, {end}).",
                    preserved_observation={"code": "empty_grant_interval", "target_id": grant.target_id},
                ))
                continue

            if grant.mode == GovernanceMode.CAPTURED:
                blocked = True
                builder.add(GateRecord(
                    gate="T8",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Grant for '{grant.target_id}' declares CAPTURED governance mode.",
                    preserved_observation={
                        "code": "captured_governance_mode",
                        "target_id": grant.target_id,
                        "scope": grant.scope,
                    },
                ))
                continue

            if grant.granted_by == grant.target_id:
                blocked = True
                builder.add(GateRecord(
                    gate="T8",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Self-granted GovernanceGrant blocked for '{grant.target_id}'.",
                    preserved_observation={"code": "self_granted_governance", "target_id": grant.target_id},
                ))
                continue

            grant_auth, grant_err = self._validate_authorizer(
                auth_id=grant.granted_by,
                target_id=grant.target_id,
                scope=grant.scope,
                mode=grant.mode,
                at_time=start,
                forbidden_chain_members={grant.target_id},
                registry=state.authority_registry,
                require_full_chain=state.require_full_chain_verification,
            )
            if grant_err is not None or grant_auth is None:
                blocked = True
                builder.add(GateRecord(
                    gate="T8",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Grant for '{grant.target_id}' rejected: {grant_err}",
                    preserved_observation={
                        "code": "unauthenticated_grant_issuer",
                        "target_id": grant.target_id,
                        "granted_by": grant.granted_by,
                    },
                ))
                continue

            if grant.is_emergency:
                if not _is_valid_positive_ttl(grant.emergency_ttl):
                    blocked = True
                    builder.add(GateRecord(
                        gate="T8",
                        verdict=GateVerdict.BLOCKED,
                        message=f"Emergency grant for '{grant.target_id}' lacks finite positive integer TTL.",
                        preserved_observation={"code": "invalid_emergency_ttl", "target_id": grant.target_id},
                    ))
                    continue
                if (end - start) > grant.emergency_ttl:  # type: ignore[operator]
                    blocked = True
                    builder.add(GateRecord(
                        gate="T8",
                        verdict=GateVerdict.BLOCKED,
                        message=(
                            f"Emergency grant interval ({end - start}) exceeds declared "
                            f"emergency_ttl ({grant.emergency_ttl}) for '{grant.target_id}'."
                        ),
                        preserved_observation={
                            "code": "emergency_interval_exceeds_ttl",
                            "target_id": grant.target_id,
                            "interval_span": end - start,
                            "ttl": grant.emergency_ttl,
                        },
                    ))
                    continue

            if grant.effective_expiry() > grant_auth.valid_interval[1]:
                blocked = True
                builder.add(GateRecord(
                    gate="T8",
                    verdict=GateVerdict.BLOCKED,
                    message=(
                        f"Grant for '{grant.target_id}' expiry (t={grant.effective_expiry()}) "
                        f"exceeds issuer '{grant.granted_by}' window (t={grant_auth.valid_interval[1]})."
                    ),
                    preserved_observation={
                        "code": "grant_exceeds_authorizer_window",
                        "target_id": grant.target_id,
                        "granted_by": grant.granted_by,
                    },
                ))
                continue

            if _is_non_negative_int(state.evaluation_time) and grant.is_active(state.evaluation_time):
                builder.active_grants.append(grant)
            else:
                builder.expired_grants.append(grant)

        # 2. Validate visible EscalationRequests and partition into accepted vs rejected
        for req in proj.visible_escalations:
            if not _is_non_negative_int(req.activation_time):
                blocked = True
                builder.rejected_escalations.append(req)
                builder.add(GateRecord(
                    gate="T8",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Escalation for '{req.actor_id}' has malformed activation_time.",
                    preserved_observation={"code": "malformed_activation_time", "actor": req.actor_id},
                ))
                continue

            if (
                not state.historical_audit_mode
                and _is_non_negative_int(state.evaluation_time)
                and req.activation_time < state.evaluation_time
            ):
                blocked = True
                builder.rejected_escalations.append(req)
                builder.add(GateRecord(
                    gate="T8",
                    verdict=GateVerdict.BLOCKED,
                    message=(
                        f"Backdated escalation blocked for '{req.actor_id}': "
                        f"activation_time={req.activation_time} < evaluation_time={state.evaluation_time}."
                    ),
                    preserved_observation={
                        "code": "backdated_escalation",
                        "actor": req.actor_id,
                        "activation_time": req.activation_time,
                        "evaluation_time": state.evaluation_time,
                    },
                ))
                continue

            # Guard 1: Delta G_self = 0
            if req.actor_id == req.authorized_by:
                blocked = True
                builder.rejected_escalations.append(req)
                builder.add(GateRecord(
                    gate="T8",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Self-authorized escalation blocked for '{req.actor_id}' (Delta G_self != 0).",
                    preserved_observation={"code": "self_authorized_escalation", "actor": req.actor_id},
                ))
                continue

            # Guard 2: Direct proxy laundering (including via_proxy == actor_id)
            if req.via_proxy is not None and (
                req.via_proxy == req.actor_id or req.authorized_by in {req.actor_id, req.via_proxy}
            ):
                blocked = True
                builder.rejected_escalations.append(req)
                builder.add(GateRecord(
                    gate="T8",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Proxy-laundered escalation blocked for '{req.actor_id}' via '{req.via_proxy}'.",
                    preserved_observation={"code": "proxy_laundering", "actor": req.actor_id, "proxy": req.via_proxy},
                ))
                continue

            # Guard 3: Authenticate authorizer & walk upstream DAG
            forbidden = {req.actor_id} | ({req.via_proxy} if req.via_proxy else set())
            auth, err = self._validate_authorizer(
                auth_id=req.authorized_by,
                target_id=req.target_id,
                scope=req.requested_scope,
                mode=req.requested_mode,
                at_time=req.activation_time,
                forbidden_chain_members=forbidden,
                registry=state.authority_registry,
                require_full_chain=state.require_full_chain_verification,
            )
            if err is not None or auth is None:
                blocked = True
                builder.rejected_escalations.append(req)
                builder.add(GateRecord(
                    gate="T8",
                    verdict=GateVerdict.BLOCKED,
                    message=f"Escalation for '{req.actor_id}' rejected: {err}",
                    preserved_observation={
                        "code": "unauthorized_escalation",
                        "actor": req.actor_id,
                        "authorized_by": req.authorized_by,
                    },
                ))
                continue

            # Guard 4: Intermediate proxy delegation chain
            if req.via_proxy is not None:
                _, proxy_err = self._validate_authorizer(
                    auth_id=req.via_proxy,
                    target_id=req.target_id,
                    scope=req.requested_scope,
                    mode=req.requested_mode,
                    at_time=req.activation_time,
                    forbidden_chain_members={req.actor_id},
                    registry=state.authority_registry,
                    require_full_chain=state.require_full_chain_verification,
                )
                if proxy_err is not None:
                    blocked = True
                    builder.rejected_escalations.append(req)
                    builder.add(GateRecord(
                        gate="T8",
                        verdict=GateVerdict.BLOCKED,
                        message=f"Invalid proxy delegation chain for '{req.via_proxy}': {proxy_err}",
                        preserved_observation={"code": "invalid_proxy_chain", "actor": req.actor_id, "proxy": req.via_proxy},
                    ))
                    continue

            # Guard 5: Emergency TTL finite, positive, and inside authorizer window
            if req.is_emergency:
                if not _is_valid_positive_ttl(req.emergency_ttl):
                    blocked = True
                    builder.rejected_escalations.append(req)
                    builder.add(GateRecord(
                        gate="T8",
                        verdict=GateVerdict.BLOCKED,
                        message=f"Emergency escalation for '{req.actor_id}' rejected: finite positive TTL required.",
                        preserved_observation={"code": "invalid_emergency_ttl", "actor": req.actor_id},
                    ))
                    continue
                _, auth_end = auth.valid_interval
                if req.activation_time + req.emergency_ttl > auth_end:  # type: ignore[operator]
                    blocked = True
                    builder.rejected_escalations.append(req)
                    builder.add(GateRecord(
                        gate="T8",
                        verdict=GateVerdict.BLOCKED,
                        message=(
                            f"Emergency TTL ({req.emergency_ttl}) starting at t={req.activation_time} "
                            f"exceeds authorizer grant expiry (t={auth_end})."
                        ),
                        preserved_observation={
                            "code": "emergency_ttl_exceeds_authorizer",
                            "actor": req.actor_id,
                            "ttl": req.emergency_ttl,
                            "auth_expiry": auth_end,
                        },
                    ))
                    continue

            builder.accepted_escalations.append(req)

        if not blocked:
            builder.add(GateRecord("T8", GateVerdict.PASS, "All grants and escalations passed authority & anti-capture checks."))

    # ------------------------------------------------------------------ E5 / T5
    def _gate_t5_fault_isolation(self, proj: VisibilityProjection, builder: _ResultBuilder) -> None:
        single_cuts = find_cut_vertices(proj.visible_nodes, proj.visible_edges)
        two_cuts, skipped = find_two_node_cuts_excluding_single_cuts(
            proj.visible_nodes,
            proj.visible_edges,
            single_cuts,
            max_nodes=self.two_node_cut_max_nodes,
        )
        builder.cut_vertices = single_cuts
        builder.two_node_cuts = two_cuts
        builder.two_node_cuts_skipped = skipped

        for applied_fault, excluded_opaque in proj.visible_fault_sets:
            builder.fault_reports.append(
                o6_prune_and_recover(proj.visible_nodes, proj.visible_edges, applied_fault, excluded_opaque)
            )

        if single_cuts:
            builder.add(GateRecord(
                gate="T5",
                verdict=GateVerdict.ARTICULATION_POINTS_FOUND,
                message=f"Single-node articulation points detected: {sorted(single_cuts)}.",
                preserved_observation={"code": "articulation_points_found", "cut_vertices": sorted(single_cuts)},
            ))
        else:
            builder.add(GateRecord(
                gate="T5",
                verdict=GateVerdict.NO_SINGLE_NODE_CUT_FOUND,
                message="No single-node articulation point found (does not imply multi-node resilience).",
            ))

        if skipped:
            builder.add(GateRecord(
                gate="T5",
                verdict=GateVerdict.QUALIFIED,
                message=(
                    f"Two-node cut analysis skipped: {len(proj.visible_nodes)} visible nodes "
                    f"exceeds cap ({self.two_node_cut_max_nodes})."
                ),
                preserved_observation={
                    "code": "two_node_cut_skipped_size_limit",
                    "visible_node_count": len(proj.visible_nodes),
                    "max_nodes": self.two_node_cut_max_nodes,
                },
            ))
        elif len(proj.visible_nodes) < 4:
            builder.add(GateRecord(
                gate="T5",
                verdict=GateVerdict.QUALIFIED,
                message=f"Two-node cut analysis not applicable for {len(proj.visible_nodes)} visible node(s).",
                preserved_observation={
                    "code": "two_node_cut_not_applicable_small_graph",
                    "visible_node_count": len(proj.visible_nodes),
                },
            ))
        elif two_cuts:
            builder.add(GateRecord(
                gate="T5",
                verdict=GateVerdict.TWO_NODE_CUTS_FOUND,
                message=f"Minimal two-node cut sets detected: {sorted(two_cuts)}.",
                preserved_observation={"code": "two_node_cuts_found", "two_node_cuts": sorted(two_cuts)},
            ))
        else:
            builder.add(GateRecord(
                gate="T5",
                verdict=GateVerdict.NO_TWO_NODE_CUT_FOUND,
                message="No minimal two-node cut sets found in visible graph.",
                preserved_observation={"code": "no_two_node_cut_found"},
            ))

    # ------------------------------------------------------------------ E6
    def _stage_e6_meta_boundary(
        self,
        state: SystemState,
        builder: _ResultBuilder,
        _depth: int = 0,
    ) -> None:
        if state.meta_spec is None:
            builder.add(GateRecord("E6", GateVerdict.PASS, "First-order architecture; no meta-boundary emissions."))
            return

        gen = state.meta_spec.generator
        blocked = False

        if gen.tamper_events:
            blocked = True
            builder.add(GateRecord(
                gate="E6",
                verdict=GateVerdict.BLOCKED,
                message=(
                    f"MetaGenerator '{gen.generator_id}' constructed without canonical gates "
                    f"{list(gen.tamper_events)}; canonical CORE_IMMUTABLE_GATES restored."
                ),
                preserved_observation={
                    "code": "generator_tamper_restored",
                    "generator_id": gen.generator_id,
                    "stripped": list(gen.tamper_events),
                },
            ))

        for child_state, requested_exemptions in state.meta_spec.child_emissions:
            if _depth >= self.max_meta_depth:
                blocked = True
                builder.add(GateRecord(
                    gate="E6",
                    verdict=GateVerdict.BLOCKED,
                    message=(
                        f"Meta-generator recursion depth cap ({self.max_meta_depth}) exceeded "
                        f"emitting child '{child_state.system_id}'."
                    ),
                    preserved_observation={
                        "code": "meta_recursion_depth_exceeded",
                        "child_id": child_state.system_id,
                        "depth": _depth,
                        "max_meta_depth": self.max_meta_depth,
                    },
                ))
                continue

            # Pass _depth unchanged (emit increments _depth + 1) and suppress duplicate tamper record
            child_res = gen.emit(
                self,
                child_state,
                requested_exemptions,
                _depth=_depth,
                _emit_tamper_record=False,
            )
            builder.child_results.append(child_res)
            for rec in child_res.hard_blocks:
                if rec.preserved_observation.get("code") == "illegal_child_exemption":
                    blocked = True
                    builder.add(GateRecord("E6", GateVerdict.BLOCKED, rec.message, rec.preserved_observation))

        for sub_id, requested_gates in state.meta_spec.subgenerator_emissions:
            sub_gen, sub_rec = gen.emit_subgenerator(sub_id, requested_gates)
            builder.emitted_subgenerators.append(sub_gen)
            if sub_rec.verdict == GateVerdict.BLOCKED:
                blocked = True
                builder.add(GateRecord("E6", GateVerdict.BLOCKED, sub_rec.message, sub_rec.preserved_observation))

        if not blocked:
            builder.add(GateRecord("E6", GateVerdict.PASS, f"MetaGenerator '{gen.generator_id}' boundary verified."))


# =============================================================================
# 4. Acceptance Test Suite (42 Tests: 34 rc4 Tests + 8 v2.1-rc5 Hardening Tests)
# =============================================================================

def _council_authority(
    authority_id: str = "external_council",
    scopes: frozenset[str] = frozenset({"recovery", "routing"}),
    targets: frozenset[str] = frozenset({"n1", "root"}),
    modes: frozenset[GovernanceMode] = frozenset({GovernanceMode.STEWARDED, GovernanceMode.SOVEREIGN}),
    interval: tuple[int, int] = (0, 1000),
    chain: tuple[str, ...] = ("root_charter",),
) -> AuthorityRecord:
    return AuthorityRecord(
        authority_id=authority_id,
        authenticated=True,
        permitted_targets=targets,
        permitted_scopes=scopes,
        permitted_modes=modes,
        valid_interval=interval,
        delegation_chain=chain,
    )


class TestSCTOL001Acceptance(unittest.TestCase):
    def setUp(self) -> None:
        self.compiler = StructuralCompiler()

    # --- Original 13 Tests ---

    def test_01_t0_myth_blocked_from_empirical_promotion(self) -> None:
        state = SystemState(
            system_id="yggdrasil_promo",
            substrate=SubstrateSpec("mythic_ash", has_represented_autopoiesis=True),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.CORPUS_MYTH,
            nodes={"root", "trunk", "midgard"},
            edges={("root", "trunk"), ("trunk", "midgard")},
            claims=[InferenceClaim("c1", "tier_promotion", EpistemicTier.CORPUS_MYTH, EpistemicTier.EMPIRICAL_SCI)],
        )
        res = self.compiler.compile(state)
        self.assertEqual(res.executed_stages, ("E0", "E1", "E2", "E3", "E4", "E5", "E6", "E7"))
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T0"))
        self.assertTrue(res.is_blocking)
        self.assertFalse(res.is_trustworthy)

    def test_02_t1_distributed_rejects_forced_single_root(self) -> None:
        state = SystemState(
            system_id="mycelium_forced_root",
            substrate=SubstrateSpec("fungal_mesh", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"n1", "n2", "n3"},
            edges={("n1", "n2"), ("n2", "n3"), ("n3", "n1")},
            root_nodes={"n1"},
            force_single_root=True,
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T1"))

    def test_03_t2_static_org_chart_returns_inert_taxonomy(self) -> None:
        state = SystemState(
            system_id="org_chart",
            substrate=SubstrateSpec("paper_hierarchy"),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"ceo", "vp1", "vp2"},
            edges={("ceo", "vp1"), ("ceo", "vp2")},
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.INERT_TAXONOMY, res.verdicts_for("T2"))
        self.assertFalse(res.is_blocking)
        self.assertEqual(len(res.soft_blocks), 1)

    def test_04_t2_mythic_tree_represented_not_empirical(self) -> None:
        state = SystemState(
            system_id="yggdrasil",
            substrate=SubstrateSpec("mythic_ash", has_empirical_autopoiesis=True, has_represented_autopoiesis=True),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.CORPUS_MYTH,
            nodes={"well", "trunk", "asgard"},
            edges={("well", "trunk"), ("trunk", "asgard")},
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.AUTOPOIESIS_REPRESENTED, res.verdicts_for("T2"))
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T2"))

    def test_05_t3_shared_ancestor_blocks_shared_consciousness(self) -> None:
        state = SystemState(
            system_id="phylogeny_hivemind_fallacy",
            substrate=SubstrateSpec("dna", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"luca", "bacteria", "archaea"},
            edges={("luca", "bacteria"), ("luca", "archaea")},
            claims=[InferenceClaim("c2", "shared_consciousness_from_provenance", EpistemicTier.EMPIRICAL_SCI)],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T3"))

    def test_06_t4_central_guardian_ownership_rejected(self) -> None:
        state = SystemState(
            system_id="assyrian_guardian_capture",
            substrate=SubstrateSpec("symbolic_relief", has_represented_autopoiesis=True),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.CORPUS_MYTH,
            nodes={"axis", "guardian", "crown"},
            edges={("axis", "guardian"), ("axis", "crown")},
            claims=[InferenceClaim("c3", "centrality_to_sovereignty", EpistemicTier.CORPUS_MYTH)],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T4"))

    def test_07_t5_reticulate_graph_still_flags_cut_vertex(self) -> None:
        state = SystemState(
            system_id="reticulate_with_bridge",
            substrate=SubstrateSpec("bio_web", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"A", "B", "H", "C"},
            edges={("H", "A"), ("H", "B"), ("H", "C")},
            fault_sets=[{"H"}],
        )
        ret = o3_reticulate(state, "A", "B")
        self.assertEqual(ret.topology, TopologyClass.RETICULATE)
        self.assertTrue(ret.edge_added and ret.topology_mutated)
        self.assertEqual(ret.cut_vertices, frozenset({"H"}))

        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.ARTICULATION_POINTS_FOUND, res.verdicts_for("T5"))
        self.assertEqual(res.cut_vertices, frozenset({"H"}))
        self.assertEqual(res.fault_reports[0]["fragmentation_status"], "FAULT_INCREASED_COMPONENT_COUNT")

    def test_08_t6_opaque_horizon_masks_before_fault_sim_and_blocks_claims(self) -> None:
        state = SystemState(
            system_id="horizon_tree",
            substrate=SubstrateSpec("spacetime_boundary", has_represented_autopoiesis=True),
            topology=TopologyClass.HORIZON_INVERTED,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"hidden_root", "trunk", "branch_1", "branch_2"},
            edges={("hidden_root", "trunk"), ("trunk", "branch_1"), ("trunk", "branch_2")},
            boundaries=[HorizonBoundary(
                boundary_id="event_horizon",
                opaque_nodes={"hidden_root"},
                asserted_internal_claims=["root executes quantum error correction"],
            )],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.OPAQUE, res.verdicts_for("T6"))
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T6"))
        self.assertEqual(res.cut_vertices, frozenset({"trunk"}))

    def test_09_t7_plasma_lattice_returns_unverified_substrate(self) -> None:
        state = SystemState(
            system_id="plasma_lattice",
            substrate=SubstrateSpec("mhd_plasma", has_represented_autopoiesis=True, memory_mechanism_status="unverified"),
            topology=TopologyClass.FRACTAL,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"p1", "p2", "p3", "p4"},
            edges={("p1", "p2"), ("p2", "p3"), ("p3", "p4"), ("p4", "p1")},
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.UNVERIFIED_SUBSTRATE, res.verdicts_for("T7"))
        self.assertNotIn(GateVerdict.INERT_OR_NONVIABLE, res.verdicts_for("T7"))
        self.assertNotIn(GateVerdict.BLOCKED, res.verdicts_for("T7"))

    def test_10_t7_impossible_substrate_returns_nonviable(self) -> None:
        state = SystemState(
            system_id="perpetual_motion_tree",
            substrate=SubstrateSpec("zero_entropy_void", memory_mechanism_status="impossible"),
            topology=TopologyClass.FRACTAL,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"n1", "n2"},
            edges={("n1", "n2")},
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.INERT_OR_NONVIABLE, res.verdicts_for("T7"))
        self.assertTrue(any(r.gate == "T7" for r in res.soft_blocks))

    def test_11_t8_self_authorized_escalation_blocked(self) -> None:
        state = SystemState(
            system_id="guardian_self_promotion",
            substrate=SubstrateSpec("distributed_ai", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"g1", "n1", "n2"},
            edges={("g1", "n1"), ("n1", "n2"), ("n2", "g1")},
            escalations=[EscalationRequest(
                actor_id="g1",
                target_id="g1",
                requested_mode=GovernanceMode.SOVEREIGN,
                requested_scope="global",
                authorized_by="g1",
            )],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T8"))
        self.assertEqual(len(res.rejected_escalations), 1)
        self.assertEqual(len(res.accepted_escalations), 0)

    def test_12_t8_proxy_capture_and_unbounded_emergency_blocked(self) -> None:
        state = SystemState(
            system_id="proxy_and_emergency_ratchet",
            substrate=SubstrateSpec("distributed_ai", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"g1", "proxy_x", "n1"},
            edges={("g1", "proxy_x"), ("proxy_x", "n1"), ("n1", "g1")},
            authority_registry={"external_council": _council_authority()},
            escalations=[
                EscalationRequest(
                    actor_id="g1",
                    target_id="n1",
                    requested_mode=GovernanceMode.CAPTURED,
                    requested_scope="routing",
                    authorized_by="proxy_x",
                    via_proxy="proxy_x",
                ),
                EscalationRequest(
                    actor_id="g1",
                    target_id="n1",
                    requested_mode=GovernanceMode.STEWARDED,
                    requested_scope="recovery",
                    authorized_by="external_council",
                    is_emergency=True,
                    emergency_ttl=None,
                ),
            ],
        )
        res = self.compiler.compile(state)
        t8_blocks = [r for r in res.hard_blocks if r.gate == "T8"]
        self.assertEqual(len(t8_blocks), 2)
        self.assertEqual(len(res.rejected_escalations), 2)

    def test_13_e6_t8_meta_generator_cannot_exempt_children_or_strip_subgenerators(self) -> None:
        child = SystemState(
            system_id="emitted_child_01",
            substrate=SubstrateSpec("crystalline_memory", memory_mechanism_status="unverified"),
            topology=TopologyClass.FRACTAL,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"c1", "c2", "c3", "c4"},
            edges={("c1", "c2"), ("c2", "c3"), ("c3", "c4"), ("c4", "c1")},
        )
        host = SystemState(
            system_id="meta_host",
            substrate=SubstrateSpec("rule_compiler", memory_mechanism_status="unverified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"m1"},
            edges=set(),
            meta_spec=MetaArchitectureSpec(
                generator=MetaGenerator("meta_tree_root"),
                child_emissions=[(child, {"T0", "T4"})],
                subgenerator_emissions=[("meta_child", frozenset({"T1"}))],
            ),
        )
        res = self.compiler.compile(host)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("E6"))
        self.assertIn("illegal_child_exemption", res.codes_for("E6"))
        self.assertIn("subgenerator_gate_stripping", res.codes_for("E6"))
        self.assertIn(GateVerdict.BLOCKED, res.child_results[0].verdicts_for("T8"))
        self.assertTrue(CORE_IMMUTABLE_GATES.issubset(res.emitted_subgenerators[0].immutable_gates))

    # --- 15 Adversarial Tests from rc3 ---

    def test_14_t8_unknown_external_authorizer_blocked(self) -> None:
        state = SystemState(
            system_id="unknown_auth",
            substrate=SubstrateSpec("distributed_ai", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"guardian", "root"},
            edges={("guardian", "root")},
            escalations=[EscalationRequest(
                actor_id="guardian",
                target_id="root",
                requested_mode=GovernanceMode.SOVEREIGN,
                requested_scope="global",
                authorized_by="random_external_identity",
            )],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T8"))

    def test_15_t8_authorizer_insufficient_scope_blocked(self) -> None:
        state = SystemState(
            system_id="insufficient_scope",
            substrate=SubstrateSpec("distributed_ai", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"guardian", "root"},
            edges={("guardian", "root")},
            authority_registry={"external_council": _council_authority(scopes=frozenset({"maintenance"}))},
            escalations=[EscalationRequest(
                actor_id="guardian",
                target_id="root",
                requested_mode=GovernanceMode.SOVEREIGN,
                requested_scope="global",
                authorized_by="external_council",
            )],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T8"))

    def test_16_t8_emergency_ttl_exceeds_grant_interval_blocked(self) -> None:
        state = SystemState(
            system_id="ttl_mismatch",
            substrate=SubstrateSpec("distributed_ai", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"g1", "n1"},
            edges={("g1", "n1")},
            authority_registry={"external_council": _council_authority(interval=(0, 100))},
            governance=[GovernanceGrant(
                target_id="n1",
                scope="recovery",
                mode=GovernanceMode.STEWARDED,
                valid_interval=(0, 31_536_000),
                granted_by="external_council",
                is_emergency=True,
                emergency_ttl=60,
            )],
            escalations=[EscalationRequest(
                actor_id="g1",
                target_id="n1",
                requested_mode=GovernanceMode.STEWARDED,
                requested_scope="recovery",
                authorized_by="external_council",
                activation_time=50,
                is_emergency=True,
                emergency_ttl=200,
            )],
        )
        res = self.compiler.compile(state)
        t8_blocks = [r for r in res.hard_blocks if r.gate == "T8"]
        self.assertEqual(len(t8_blocks), 2)

    def test_17_t8_emergency_grant_expires_automatically(self) -> None:
        grant = GovernanceGrant(
            target_id="n1",
            scope="recovery",
            mode=GovernanceMode.STEWARDED,
            valid_interval=(100, 160),
            granted_by="external_council",
            is_emergency=True,
            emergency_ttl=60,
        )
        self.assertEqual(grant.effective_expiry(), 160)
        self.assertTrue(grant.is_active(120))
        self.assertFalse(grant.is_active(160))

        state_after_expiry = SystemState(
            system_id="emergency_expired",
            substrate=SubstrateSpec("distributed_ai", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"n1", "n2"},
            edges={("n1", "n2")},
            evaluation_time=165,
            authority_registry={"external_council": _council_authority()},
            governance=[grant],
        )
        res = self.compiler.compile(state_after_expiry)
        self.assertIn(GateVerdict.PASS, res.verdicts_for("T8"))
        self.assertEqual(len(res.active_grants), 0)
        self.assertEqual(len(res.expired_grants), 1)

    def test_18_t8_invalid_proxy_delegation_chain_blocked(self) -> None:
        collusive_proxy = AuthorityRecord(
            authority_id="proxy_a",
            authenticated=True,
            permitted_targets=frozenset({"n1"}),
            permitted_scopes=frozenset({"routing"}),
            permitted_modes=frozenset({GovernanceMode.STEWARDED}),
            valid_interval=(0, 1000),
            delegation_chain=("g1", "external_council"),
        )
        state = SystemState(
            system_id="bad_proxy_chain",
            substrate=SubstrateSpec("distributed_ai", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"g1", "proxy_a", "n1"},
            edges={("g1", "proxy_a"), ("proxy_a", "n1")},
            authority_registry={
                "external_council": _council_authority(),
                "proxy_a": collusive_proxy,
            },
            escalations=[EscalationRequest(
                actor_id="g1",
                target_id="n1",
                requested_mode=GovernanceMode.STEWARDED,
                requested_scope="routing",
                authorized_by="external_council",
                via_proxy="proxy_a",
            )],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T8"))

    def test_19_t6_opaque_node_referenced_by_t3_claim_blocked(self) -> None:
        state = SystemState(
            system_id="opaque_t3_leak",
            substrate=SubstrateSpec("horizon_web", has_represented_autopoiesis=True),
            topology=TopologyClass.HORIZON_INVERTED,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"hidden_root", "b1", "b2"},
            edges={("hidden_root", "b1"), ("hidden_root", "b2")},
            boundaries=[HorizonBoundary("h1", opaque_nodes={"hidden_root"})],
            claims=[InferenceClaim(
                claim_id="c_opaque_t3",
                kind="shared_consciousness_from_provenance",
                source_tier=EpistemicTier.SPECULATIVE_EXO,
                subject_nodes={"b1", "b2"},
                evidence_nodes={"hidden_root"},
            )],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T6"))
        self.assertIn(GateVerdict.PASS, res.verdicts_for("T3"))

    def test_20_t6_opaque_node_referenced_by_t4_claim_blocked(self) -> None:
        state = SystemState(
            system_id="opaque_t4_leak",
            substrate=SubstrateSpec("horizon_web", has_represented_autopoiesis=True),
            topology=TopologyClass.HORIZON_INVERTED,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"hidden_axis", "b1", "b2"},
            edges={("hidden_axis", "b1"), ("hidden_axis", "b2")},
            boundaries=[HorizonBoundary("h1", opaque_nodes={"hidden_axis"})],
            claims=[InferenceClaim(
                claim_id="c_opaque_t4",
                kind="centrality_to_sovereignty",
                source_tier=EpistemicTier.SPECULATIVE_EXO,
                subject_nodes={"hidden_axis"},
            )],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T6"))
        self.assertIn(GateVerdict.PASS, res.verdicts_for("T4"))

    def test_21_t6_opaque_node_excluded_from_o6_fault_simulation(self) -> None:
        state = SystemState(
            system_id="opaque_o6_mask",
            substrate=SubstrateSpec("horizon_web", has_represented_autopoiesis=True),
            topology=TopologyClass.HORIZON_INVERTED,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"hidden_root", "n1", "n2", "n3"},
            edges={("hidden_root", "n1"), ("n1", "n2"), ("n2", "n3"), ("n3", "n1")},
            boundaries=[HorizonBoundary("h1", opaque_nodes={"hidden_root"})],
            fault_sets=[{"hidden_root", "n1"}],
        )
        res = self.compiler.compile(state)
        report = res.fault_reports[0]
        self.assertEqual(report["excluded_opaque_nodes"], ["hidden_root"])
        self.assertEqual(report["fault_set"], ["n1"])
        self.assertEqual(report["lost_node_count"], 1)

    def test_22_t5_two_node_cut_vulnerability_detected(self) -> None:
        state = SystemState(
            system_id="four_cycle_2cut",
            substrate=SubstrateSpec("bio_web", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.RETICULATE,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"A", "B", "C", "D"},
            edges={("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")},
            fault_sets=[{"A", "C"}],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.NO_SINGLE_NODE_CUT_FOUND, res.verdicts_for("T5"))
        self.assertIn(GateVerdict.TWO_NODE_CUTS_FOUND, res.verdicts_for("T5"))
        self.assertFalse(res.two_node_cuts_skipped)
        self.assertEqual(res.two_node_cuts, frozenset({("A", "C"), ("B", "D")}))
        self.assertEqual(res.fault_reports[0]["fragmentation_status"], "FAULT_INCREASED_COMPONENT_COUNT")

    def test_23_o3_self_loop_raises_value_error(self) -> None:
        state = SystemState(
            system_id="self_loop_test",
            substrate=SubstrateSpec("bio_web"),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"A", "B"},
            edges={("A", "B")},
        )
        with self.assertRaises(ValueError):
            o3_reticulate(state, "A", "A")

    def test_24_o3_existing_edge_readded_no_topology_mutation(self) -> None:
        state = SystemState(
            system_id="dup_edge_test",
            substrate=SubstrateSpec("bio_web"),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"A", "B", "C"},
            edges={("A", "B"), ("A", "C")},
        )
        ret = o3_reticulate(state, "B", "A")
        self.assertFalse(ret.edge_added)
        self.assertFalse(ret.topology_mutated)
        self.assertEqual(state.topology, TopologyClass.ARBORESCENT)

    def test_25_t0_claim_falsifies_source_tier_blocked(self) -> None:
        state = SystemState(
            system_id="falsified_tier",
            substrate=SubstrateSpec("mythic_text", has_represented_autopoiesis=True),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.CORPUS_MYTH,
            nodes={"n1", "n2"},
            edges={("n1", "n2")},
            source_registry={
                "edda_01": SourceRecord("edda_01", EpistemicTier.CORPUS_MYTH, "Poetic Edda: Völuspá"),
            },
            claims=[InferenceClaim(
                claim_id="c_fake_sci",
                kind="tier_promotion",
                source_tier=EpistemicTier.EMPIRICAL_SCI,
                target_tier=EpistemicTier.EMPIRICAL_SCI,
                source_id="edda_01",
            )],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T0"))

    def test_26_t7_mythological_substrate_claims_empirical_verification_blocked(self) -> None:
        state = SystemState(
            system_id="myth_verified_substrate",
            substrate=SubstrateSpec("sacred_sycamore", has_represented_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.CORPUS_MYTH,
            nodes={"n1", "n2"},
            edges={("n1", "n2")},
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T7"))
        self.assertNotIn(GateVerdict.VERIFIED_SUBSTRATE, res.verdicts_for("T7"))

    def test_27_e6_generator_constructed_with_empty_immutable_gates_blocked_and_restored(self) -> None:
        weak = MetaGenerator("weak_generator", immutable_gates=frozenset())
        self.assertEqual(weak.immutable_gates, CORE_IMMUTABLE_GATES)
        self.assertEqual(set(weak.tamper_events), CORE_IMMUTABLE_GATES)

        host = SystemState(
            system_id="weak_gen_host",
            substrate=SubstrateSpec("rule_compiler", memory_mechanism_status="unverified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"m1"},
            edges=set(),
            meta_spec=MetaArchitectureSpec(generator=weak),
        )
        res = self.compiler.compile(host)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("E6"))

    def test_28_o6_reports_node_loss_and_component_loss_independently(self) -> None:
        state = SystemState(
            system_id="component_loss_test",
            substrate=SubstrateSpec("bio_web", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"A", "B", "C"},
            edges={("A", "B")},
            fault_sets=[{"C"}],
        )
        res = self.compiler.compile(state)
        report = res.fault_reports[0]
        self.assertEqual(report["lost_node_count"], 1)
        self.assertEqual(report["components_lost"], 1)
        self.assertEqual(report["fragmentation_status"], "NO_ADDITIONAL_FRAGMENTATION")

    # --- 6 Hardening Tests from rc4 ---

    def test_29_t8_unauthenticated_grant_and_captured_mode_blocked(self) -> None:
        state = SystemState(
            system_id="grant_auth_and_capture",
            substrate=SubstrateSpec("distributed_ai", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"n1", "n2"},
            edges={("n1", "n2")},
            authority_registry={"external_council": _council_authority(
                modes=frozenset({GovernanceMode.STEWARDED, GovernanceMode.CAPTURED}),
            )},
            governance=[
                GovernanceGrant("n1", "routing", GovernanceMode.STEWARDED, (0, 500), "ghost_issuer"),
                GovernanceGrant("n1", "routing", GovernanceMode.CAPTURED, (0, 500), "external_council"),
            ],
        )
        res = self.compiler.compile(state)
        codes = res.codes_for("T8")
        self.assertIn("unauthenticated_grant_issuer", codes)
        self.assertIn("captured_governance_mode", codes)
        self.assertEqual(len(res.active_grants), 0)

    def test_30_t5_large_graph_emits_qualified_when_two_node_cut_skipped(self) -> None:
        small_cap_compiler = StructuralCompiler(two_node_cut_max_nodes=5)
        nodes = {f"n{i}" for i in range(6)}
        edges = {(f"n{i}", f"n{(i + 1) % 6}") for i in range(6)}
        state = SystemState(
            system_id="six_cycle_over_cap",
            substrate=SubstrateSpec("bio_web", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.RETICULATE,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes=nodes,
            edges=edges,
        )
        res = small_cap_compiler.compile(state)
        self.assertTrue(res.two_node_cuts_skipped)
        self.assertIn(GateVerdict.QUALIFIED, res.verdicts_for("T5"))
        self.assertIn("two_node_cut_skipped_size_limit", res.codes_for("T5"))

    def test_31_t8_self_loop_chain_compromised_hop_and_backdated_escalation_blocked(self) -> None:
        self_loop_auth = AuthorityRecord(
            authority_id="loop_auth",
            authenticated=True,
            permitted_targets=frozenset({"n1"}),
            permitted_scopes=frozenset({"routing"}),
            permitted_modes=frozenset({GovernanceMode.STEWARDED}),
            valid_interval=(0, 1000),
            delegation_chain=("loop_auth",),
        )
        revoked_parent = AuthorityRecord(
            authority_id="revoked_parent",
            authenticated=False,
            permitted_targets=frozenset({"n1"}),
            permitted_scopes=frozenset({"routing"}),
            permitted_modes=frozenset({GovernanceMode.STEWARDED}),
            valid_interval=(0, 1000),
        )
        child_of_revoked = AuthorityRecord(
            authority_id="delegate_b",
            authenticated=True,
            permitted_targets=frozenset({"n1"}),
            permitted_scopes=frozenset({"routing"}),
            permitted_modes=frozenset({GovernanceMode.STEWARDED}),
            valid_interval=(0, 1000),
            delegation_chain=("revoked_parent",),
        )
        state = SystemState(
            system_id="chain_and_backdate_attacks",
            substrate=SubstrateSpec("distributed_ai", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"g1", "n1"},
            edges={("g1", "n1")},
            evaluation_time=100,
            authority_registry={
                "external_council": _council_authority(),
                "loop_auth": self_loop_auth,
                "revoked_parent": revoked_parent,
                "delegate_b": child_of_revoked,
            },
            escalations=[
                EscalationRequest("g1", "n1", GovernanceMode.STEWARDED, "routing", "loop_auth", activation_time=100),
                EscalationRequest("g1", "n1", GovernanceMode.STEWARDED, "routing", "delegate_b", activation_time=100),
                EscalationRequest("g1", "n1", GovernanceMode.STEWARDED, "routing", "external_council", activation_time=50),
            ],
        )
        res = self.compiler.compile(state)
        t8_blocks = [r for r in res.hard_blocks if r.gate == "T8"]
        self.assertEqual(len(t8_blocks), 3)
        self.assertIn("backdated_escalation", res.codes_for("T8"))

    def test_32_e1_dangling_edges_and_t6_opaque_governance_quarantine(self) -> None:
        state = SystemState(
            system_id="e1_and_t6_gov_hardening",
            substrate=SubstrateSpec("horizon_web", has_represented_autopoiesis=True),
            topology=TopologyClass.HORIZON_INVERTED,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"hidden_root", "n1"},
            edges={("hidden_root", "n1"), ("n1", "ghost_node")},
            boundaries=[HorizonBoundary("h1", opaque_nodes={"hidden_root"})],
            authority_registry={"external_council": _council_authority(targets=frozenset({"hidden_root", "n1"}))},
            governance=[
                GovernanceGrant("hidden_root", "routing", GovernanceMode.STEWARDED, (0, 100), "external_council"),
                GovernanceGrant("n1", "routing", GovernanceMode.STEWARDED, (0, float("inf")), "external_council"),  # type: ignore[arg-type]
            ],
            escalations=[
                EscalationRequest("g1", "hidden_root", GovernanceMode.STEWARDED, "routing", "external_council"),
            ],
        )
        res = self.compiler.compile(state)
        self.assertIn("dangling_edge", res.codes_for("E1"))
        self.assertIn("invalid_interval_bounds", res.codes_for("E1"))
        self.assertIn("opaque_governance_target", res.codes_for("T6"))
        self.assertIn("opaque_escalation_node", res.codes_for("T6"))
        self.assertIn("malformed_grant_interval", res.codes_for("T8"))
        self.assertEqual(len(res.rejected_escalations), 1)

    def test_33_e6_direct_emit_depth_increment_and_no_duplicate_tamper_on_children(self) -> None:
        # Part A: direct weak.emit() surfaces tamper once and enforces max_meta_depth=0
        weak = MetaGenerator("weak_direct", immutable_gates=frozenset())
        leaf = SystemState(
            system_id="leaf",
            substrate=SubstrateSpec("crystal", memory_mechanism_status="unverified"),
            topology=TopologyClass.FRACTAL,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"l1", "l2", "l3", "l4"},
            edges={("l1", "l2"), ("l2", "l3"), ("l3", "l4"), ("l4", "l1")},
        )
        direct_res = weak.emit(self.compiler, leaf)
        self.assertIn("generator_tamper_restored", direct_res.codes_for("E6"))

        zero_compiler = StructuralCompiler(max_meta_depth=0)
        blocked_direct = MetaGenerator("gen_zero").emit(zero_compiler, leaf)
        self.assertIn("meta_recursion_depth_exceeded", blocked_direct.codes_for("E6"))

        # Part B: tampered parent with 2 children reports tamper ONCE on parent, not duplicated onto children
        parent_host = SystemState(
            system_id="tampered_parent",
            substrate=SubstrateSpec("rule_compiler"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"m0"},
            edges=set(),
            meta_spec=MetaArchitectureSpec(
                generator=weak,
                child_emissions=[(leaf, set()), (leaf, set())],
            ),
        )
        parent_res = self.compiler.compile(parent_host)
        self.assertEqual(parent_res.codes_for("E6").count("generator_tamper_restored"), 1)
        self.assertNotIn("generator_tamper_restored", parent_res.child_results[0].codes_for("E6"))
        self.assertNotIn("generator_tamper_restored", parent_res.child_results[1].codes_for("E6"))

        # Part C: nested emit chain enforces max_meta_depth=1 both via compile() and direct emit()
        shallow_compiler = StructuralCompiler(max_meta_depth=1)
        level_2 = SystemState("level_2", SubstrateSpec("rule_compiler"), TopologyClass.DISTRIBUTED, EpistemicTier.SPECULATIVE_EXO, {"m2"}, set())
        level_1 = SystemState(
            "level_1", SubstrateSpec("rule_compiler"), TopologyClass.DISTRIBUTED, EpistemicTier.SPECULATIVE_EXO, {"m1"}, set(),
            meta_spec=MetaArchitectureSpec(MetaGenerator("gen_1"), child_emissions=[(level_2, set())]),
        )
        level_0 = SystemState(
            "level_0", SubstrateSpec("rule_compiler"), TopologyClass.DISTRIBUTED, EpistemicTier.SPECULATIVE_EXO, {"m0"}, set(),
            meta_spec=MetaArchitectureSpec(MetaGenerator("gen_0"), child_emissions=[(level_1, set())]),
        )
        res = shallow_compiler.compile(level_0)
        self.assertEqual(len(res.child_results), 1)
        self.assertIn("meta_recursion_depth_exceeded", res.child_results[0].codes_for("E6"))
        self.assertEqual(len(res.child_results[0].child_results), 0)

        # Direct emit of level_1 increments depth to 1, so level_1 blocks level_2
        direct_nested = MetaGenerator("gen_0").emit(shallow_compiler, level_1)
        self.assertIn("meta_recursion_depth_exceeded", direct_nested.codes_for("E6"))
        self.assertEqual(len(direct_nested.child_results), 0)

    def test_34_t7_speculative_exo_claiming_verified_substrate_single_hard_block(self) -> None:
        state = SystemState(
            system_id="plasma_overclaim",
            substrate=SubstrateSpec("mhd_plasma", has_represented_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.FRACTAL,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"p1", "p2", "p3", "p4"},
            edges={("p1", "p2"), ("p2", "p3"), ("p3", "p4"), ("p4", "p1")},
        )
        res = self.compiler.compile(state)
        self.assertEqual(res.verdicts_for("T7"), [GateVerdict.BLOCKED])
        self.assertIn("speculative_self_certification", res.codes_for("T7"))
        # Must NOT pollute uncertainties with UNVERIFIED_SUBSTRATE when hard-blocked
        self.assertFalse(any(r.gate == "T7" for r in res.uncertainties))

    # --- 8 New Hardening Tests for v2.1-rc5 (Closing All 25 Review Items) ---

    def test_35_t0_poisoned_system_tier_nulls_effective_tier_and_short_circuits(self) -> None:
        state = SystemState(
            system_id="poisoned_myth_as_sci",
            substrate=SubstrateSpec("mythic_text", has_represented_autopoiesis=True),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,  # Falsified vs CORPUS_MYTH registry
            source_id="edda_01",
            source_registry={"edda_01": SourceRecord("edda_01", EpistemicTier.CORPUS_MYTH, "Poetic Edda")},
            nodes={"a", "b", "c"},
            edges={("a", "b"), ("b", "c")},
        )
        res_full = self.compiler.compile(state)
        self.assertEqual(res_full.declared_tier, EpistemicTier.EMPIRICAL_SCI)
        self.assertIsNone(res_full.effective_tier)
        self.assertFalse(res_full.is_trustworthy)
        self.assertIn("system_tier_mismatch", res_full.codes_for("T0"))

        strict_compiler = StructuralCompiler(halt_on_t0_block=True)
        res_halted = strict_compiler.compile(state)
        self.assertEqual(res_halted.executed_stages, ("E0", "E7"))
        self.assertIsNone(res_halted.effective_tier)
        self.assertEqual(res_halted.cut_vertices, frozenset())

    def test_36_t2_speculative_exo_empirical_contradiction_blocked(self) -> None:
        state = SystemState(
            system_id="speculative_bio_overclaim",
            substrate=SubstrateSpec(
                "plasma_cell",
                has_empirical_autopoiesis=True,
                has_represented_autopoiesis=True,
                memory_mechanism_status="unverified",
            ),
            topology=TopologyClass.FRACTAL,
            epistemic_tier=EpistemicTier.SPECULATIVE_EXO,
            nodes={"p1", "p2", "p3", "p4"},
            edges={("p1", "p2"), ("p2", "p3"), ("p3", "p4"), ("p4", "p1")},
        )
        res = self.compiler.compile(state)
        self.assertEqual(res.verdicts_for("T2"), [GateVerdict.BLOCKED])
        self.assertIn("speculative_empirical_autopoiesis_blocked", res.codes_for("T2"))

    def test_37_t1_validates_topology_against_structure_and_sets_effective_topology(self) -> None:
        # Case A: Cyclic graph falsely declared ARBORESCENT -> effective_topology becomes RETICULATE
        cyclic_as_tree = SystemState(
            system_id="cyclic_tree_claim",
            substrate=SubstrateSpec("bio_web", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"A", "B", "C"},
            edges={("A", "B"), ("B", "C"), ("C", "A")},
        )
        res_a = self.compiler.compile(cyclic_as_tree)
        self.assertEqual(res_a.declared_topology, TopologyClass.ARBORESCENT)
        self.assertEqual(res_a.effective_topology, TopologyClass.RETICULATE)
        self.assertIn("topology_structure_mismatch", res_a.codes_for("T1"))

        # Case B: HORIZON_INVERTED without boundaries -> effective_topology becomes INVERTED_ARBORESCENT
        no_boundary_horizon = SystemState(
            system_id="ashvattha_no_horizon",
            substrate=SubstrateSpec("metaphysical_root", has_represented_autopoiesis=True),
            topology=TopologyClass.HORIZON_INVERTED,
            epistemic_tier=EpistemicTier.CORPUS_MYTH,
            nodes={"r", "t", "b"},
            edges={("r", "t"), ("t", "b")},
        )
        res_b = self.compiler.compile(no_boundary_horizon)
        self.assertEqual(res_b.declared_topology, TopologyClass.HORIZON_INVERTED)
        self.assertEqual(res_b.effective_topology, TopologyClass.INVERTED_ARBORESCENT)
        self.assertIn("missing_horizon_boundary", res_b.codes_for("T1"))

    def test_38_e1_rejects_self_loops_negative_times_bad_ttl_and_registry_mismatch(self) -> None:
        state = SystemState(
            system_id="e1_strict_validation",
            substrate=SubstrateSpec("distributed_ai", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"n1", "n2"},
            edges={("n1", "n1"), ("n1", "n2")},  # Self-loop
            evaluation_time=-5,                  # Negative time
            source_registry={"wrong_key": SourceRecord("actual_src", EpistemicTier.EMPIRICAL_SCI, "citation")},
            authority_registry={"wrong_auth_key": _council_authority(authority_id="actual_auth")},
            governance=[
                GovernanceGrant("n1", "recovery", GovernanceMode.STEWARDED, (0, 50), "actual_auth", is_emergency=True, emergency_ttl="5"),  # type: ignore[arg-type]
            ],
            escalations=[
                EscalationRequest("g1", "n1", GovernanceMode.STEWARDED, "recovery", "actual_auth", activation_time=-1),
            ],
        )
        res = self.compiler.compile(state)
        e1_codes = res.codes_for("E1")
        self.assertIn("self_loop_edge", e1_codes)
        self.assertIn("invalid_evaluation_time", e1_codes)
        self.assertIn("source_registry_key_mismatch", e1_codes)
        self.assertIn("authority_registry_key_mismatch", e1_codes)
        self.assertIn("invalid_emergency_ttl", e1_codes)
        self.assertIn("invalid_activation_time", e1_codes)

    def test_39_t8_diamond_delegation_passes_and_escalations_are_tracked(self) -> None:
        # Diamond DAG: delegate_top -> (mid_left, mid_right) -> root_charter
        registry = {
            "root_charter": _council_authority(authority_id="root_charter", chain=()),
            "mid_left": _council_authority(authority_id="mid_left", chain=("root_charter",)),
            "mid_right": _council_authority(authority_id="mid_right", chain=("root_charter",)),
            "delegate_top": _council_authority(authority_id="delegate_top", chain=("mid_left", "mid_right")),
        }
        good_req = EscalationRequest("g1", "n1", GovernanceMode.STEWARDED, "routing", "delegate_top", activation_time=10)
        self_proxy_req = EscalationRequest(
            "g2", "n1", GovernanceMode.STEWARDED, "routing", "delegate_top", activation_time=10, via_proxy="g2",
        )
        state = SystemState(
            system_id="diamond_and_proxy_tracking",
            substrate=SubstrateSpec("distributed_ai", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.DISTRIBUTED,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"g1", "g2", "n1"},
            edges={("g1", "n1"), ("g2", "n1")},
            evaluation_time=10,
            require_full_chain_verification=True,
            authority_registry=registry,
            escalations=[good_req, self_proxy_req],
        )
        res = self.compiler.compile(state)
        self.assertEqual(res.accepted_escalations, (good_req,))
        self.assertEqual(res.rejected_escalations, (self_proxy_req,))
        self.assertIn("proxy_laundering", res.codes_for("T8"))

    def test_40_result_immutability_and_deterministic_json_serialization(self) -> None:
        state = SystemState(
            system_id="serializable_web",
            substrate=SubstrateSpec("dna", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.RETICULATE,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes={"A", "B", "C", "D"},
            edges={("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("A", "C"), ("B", "D")},
        )
        res = self.compiler.compile(state)
        self.assertTrue(res.is_trustworthy)
        with self.assertRaises(Exception):
            res.effective_tier = None  # type: ignore[misc]

        raw_json = res.to_json()
        parsed = json.loads(raw_json)
        self.assertEqual(parsed["schema_version"], SCHEMA_VERSION)
        self.assertEqual(parsed["declared_tier"], "EMPIRICAL_SCI")
        self.assertEqual(parsed["effective_tier"], "EMPIRICAL_SCI")
        self.assertTrue(parsed["is_trustworthy"])
        self.assertFalse(parsed["is_blocking"])

    def test_41_t5_no_two_node_cut_verdict_and_tarjan_large_graph_scaling(self) -> None:
        # K4 complete graph: no 1-node cuts and no 2-node cuts
        k4_nodes = {"A", "B", "C", "D"}
        k4_edges = {("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("B", "D"), ("C", "D")}
        state = SystemState(
            system_id="k4_complete",
            substrate=SubstrateSpec("bio_web", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
            topology=TopologyClass.RETICULATE,
            epistemic_tier=EpistemicTier.EMPIRICAL_SCI,
            nodes=k4_nodes,
            edges=k4_edges,
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.NO_SINGLE_NODE_CUT_FOUND, res.verdicts_for("T5"))
        self.assertIn(GateVerdict.NO_TWO_NODE_CUT_FOUND, res.verdicts_for("T5"))
        self.assertEqual(res.two_node_cuts, frozenset())

        # Large path graph (1,500 nodes) exceeds default recursion limit (1,000):
        # Iterative Tarjan must find all 1,498 internal articulation points cleanly in O(V+E).
        n_large = 1500
        path_nodes = {f"v{i:04d}" for i in range(n_large)}
        path_edges = {(f"v{i:04d}", f"v{i + 1:04d}") for i in range(n_large - 1)}
        cuts = find_cut_vertices(path_nodes, path_edges)
        self.assertEqual(len(cuts), n_large - 2)
        self.assertNotIn("v0000", cuts)
        self.assertNotIn(f"v{n_large - 1:04d}", cuts)

    def test_42_t4_guardian_to_sovereignty_and_compiler_init_validation(self) -> None:
        with self.assertRaises(ValueError):
            StructuralCompiler(two_node_cut_max_nodes=-1)
        with self.assertRaises(ValueError):
            StructuralCompiler(max_meta_depth=-1)
        with self.assertRaises(ValueError):
            StructuralCompiler(two_node_cut_max_nodes=True)  # type: ignore[arg-type]

        state = SystemState(
            system_id="guardian_claim_test",
            substrate=SubstrateSpec("symbolic_relief", has_represented_autopoiesis=True),
            topology=TopologyClass.ARBORESCENT,
            epistemic_tier=EpistemicTier.CORPUS_MYTH,
            nodes={"axis", "guardian", "crown"},
            edges={("axis", "guardian"), ("axis", "crown")},
            claims=[InferenceClaim("c_guard", "guardian_to_sovereignty", EpistemicTier.CORPUS_MYTH)],
        )
        res = self.compiler.compile(state)
        self.assertIn(GateVerdict.BLOCKED, res.verdicts_for("T4"))


if __name__ == "__main__":
    unittest.main(verbosity=2)