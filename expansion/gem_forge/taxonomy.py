"""Facet taxonomy and deterministic primitive extraction for Gem Forge.

The existing equipment/support/aura/anointment/flask layers describe deployment
roles. They do not fully describe behavior. Gem Forge therefore uses orthogonal
facets:

- deployment slots: where a component lives;
- capability domains: which inference surfaces it modifies;
- mechanic primitives: the transferable behavior;
- relationships: ordering, triggering, dependency, and sharing semantics.
"""
from __future__ import annotations

import re
from typing import Iterable


DEPLOYMENT_SLOTS = (
    "MODEL_PAYLOAD",
    "DRAFT_HEAD",
    "VERIFIER",
    "RUNTIME",
    "SCHEDULER",
    "ROUTER",
    "MEMORY_LAYER",
    "CACHE_LAYER",
    "RETRIEVER",
    "TOOL_EXECUTOR",
    "EVALUATOR",
    "POLICY_LAYER",
    "OBSERVABILITY",
    "DISTRIBUTED_FABRIC",
    "DATA_PIPELINE",
    "USER_INTERFACE",
    "HARDWARE_ACCELERATOR",
)

CAPABILITY_DOMAINS = (
    "GENERATION",
    "SPECULATION",
    "VERIFICATION",
    "TRIGGERING",
    "ROUTING",
    "MEMORY",
    "RETRIEVAL",
    "CACHING",
    "COMPRESSION",
    "BATCHING",
    "PARALLELISM",
    "SYNCHRONIZATION",
    "RESOURCE_BUDGETING",
    "TOOL_USE",
    "SAFETY_AUTHORITY",
    "OBSERVABILITY_PROVENANCE",
    "RECOVERY_ROLLBACK",
    "ADAPTATION_LEARNING",
    "STATE_MANAGEMENT",
    "LATENCY_CONTROL",
)

MECHANIC_PRIMITIVES = (
    "EMIT_ADDITIONAL_CANDIDATES",
    "REDUCE_PER_CANDIDATE_EFFECTIVENESS",
    "INCREASE_EXECUTION_COST",
    "REDUCE_EXECUTION_COST",
    "RESERVE_CAPACITY",
    "REDUCE_RESERVATION",
    "TRIGGER_ON_QUALIFICATION",
    "TRIGGER_ON_EVENT",
    "TRIGGER_ON_STATE_CHANGE",
    "GATE_BY_CONFIDENCE",
    "APPLY_COOLDOWN",
    "RECOVER_COOLDOWN",
    "REPEAT_EXECUTION",
    "CHAIN_TO_NEW_TARGET",
    "FORK_OUTPUT",
    "RETURN_BRANCH_FEEDBACK",
    "STORE_THEN_RELEASE",
    "PRELOAD_FUTURE_STATE",
    "PERSISTENT_SHARED_MODIFIER",
    "TARGET_SPECIFIC_MODIFIER",
    "PROXY_EXECUTION",
    "DUPLICATE_EXECUTION_LOCUS",
    "CONVERT_RESOURCE",
    "RECOVER_RESOURCE",
    "CONSUME_ALTERNATE_RESOURCE",
    "SCALE_WITH_RECENT_SUCCESS",
    "SCALE_WITH_MISSING_RESOURCE",
    "SCALE_WITH_TARGET_STATE",
    "SCALE_WITH_DISTANCE_OR_HORIZON",
    "EXTEND_DURATION",
    "REDUCE_DURATION",
    "INCREASE_AREA_OR_SCOPE",
    "REDUCE_AREA_OR_SCOPE",
    "FILTER_TARGETS",
    "PRIORITIZE_TARGET",
    "SHARE_STATE",
    "MERGE_RESULTS",
    "DEDUPLICATE_RESULTS",
    "REJECT_DEPENDENT_SUFFIX",
    "RECORD_RECEIPT",
    "ROLLBACK_ON_FAILURE",
    "FAIL_CLOSED",
    "ADAPT_PARAMETER",
)

RELATIONSHIP_TYPES = (
    "SUPPORTS",
    "TRIGGERS",
    "GATES",
    "CONSUMES",
    "RESERVES",
    "AMPLIFIES",
    "PRELOADS",
    "RETURNS_TO",
    "SHARES_WITH",
    "MERGES_INTO",
    "INVALIDATES_AFTER",
    "RUNS_BEFORE",
    "RUNS_AFTER",
    "RUNS_IN_PARALLEL",
    "FALLS_BACK_TO",
)


_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("EMIT_ADDITIONAL_CANDIDATES", ("additional projectile", "additional future token", "multiple projectile", "mtp", "fan out", "fan-out", "branch")),
    ("REDUCE_PER_CANDIDATE_EFFECTIVENESS", ("less projectile damage", "less damage", "reduced effectiveness", "acceptance-weighted")),
    ("INCREASE_EXECUTION_COST", ("cost multiplier", "reservation multiplier", "additional compute", "kv multiplier", "overhead")),
    ("REDUCE_EXECUTION_COST", ("reduced mana cost", "less mana cost", "cost reduction", "cheaper inference")),
    ("RESERVE_CAPACITY", ("reserves mana", "reservation", "persistent service", "always resident")),
    ("REDUCE_RESERVATION", ("reduced reservation", "reservation efficiency", "enlighten")),
    ("TRIGGER_ON_QUALIFICATION", ("critical strike", "cast on crit", "cast on critical", "acceptance gate", "qualified proposal")),
    ("TRIGGER_ON_EVENT", ("when hit", "on hit", "on kill", "when damage", "event trigger")),
    ("TRIGGER_ON_STATE_CHANGE", ("when stunned", "ward breaks", "state transition", "state change")),
    ("GATE_BY_CONFIDENCE", ("critical chance", "accuracy", "confidence", "acceptance probability", "qualification")),
    ("APPLY_COOLDOWN", ("cooldown", "recovery time")),
    ("RECOVER_COOLDOWN", ("cooldown recovery", "recovery rate", "cdr")),
    ("REPEAT_EXECUTION", ("repeat", "repeats", "spell echo", "multistrike")),
    ("CHAIN_TO_NEW_TARGET", ("chain", "chains", "new target")),
    ("FORK_OUTPUT", ("fork", "split", "secondary projectile")),
    ("RETURN_BRANCH_FEEDBACK", ("returning projectile", "returns", "rejection reason", "branch feedback")),
    ("STORE_THEN_RELEASE", ("unleash", "seal", "store", "release", "prepared burst")),
    ("PRELOAD_FUTURE_STATE", ("prefetch", "preload", "precognition", "anticipated route")),
    ("PERSISTENT_SHARED_MODIFIER", ("aura", "persistent modifier", "party members", "shared service")),
    ("TARGET_SPECIFIC_MODIFIER", ("mark", "curse", "target-specific", "selected target")),
    ("PROXY_EXECUTION", ("totem", "mine", "trap", "proxy", "side agent")),
    ("DUPLICATE_EXECUTION_LOCUS", ("triggerbot", "duplicate execution", "two loci", "dual verifier")),
    ("CONVERT_RESOURCE", ("convert", "instead of mana", "resource conversion")),
    ("RECOVER_RESOURCE", ("leech", "gain mana", "recover", "refund", "replenish")),
    ("CONSUME_ALTERNATE_RESOURCE", ("lifetap", "spend life", "alternate resource")),
    ("SCALE_WITH_RECENT_SUCCESS", ("power charge", "inspiration charge", "recent success")),
    ("SCALE_WITH_MISSING_RESOURCE", ("missing mana", "low life", "remaining capacity")),
    ("SCALE_WITH_TARGET_STATE", ("chilled", "shocked", "poisoned", "target state", "uncertainty")),
    ("SCALE_WITH_DISTANCE_OR_HORIZON", ("distance", "farther", "future token position", "prediction horizon")),
    ("EXTEND_DURATION", ("increased duration", "more duration", "unbound ailments")),
    ("REDUCE_DURATION", ("less duration", "reduced duration")),
    ("INCREASE_AREA_OR_SCOPE", ("increased area", "area of effect", "wider scope")),
    ("REDUCE_AREA_OR_SCOPE", ("less area", "reduced area", "narrower scope")),
    ("FILTER_TARGETS", ("cannot support", "only supports", "filter", "eligible")),
    ("PRIORITIZE_TARGET", ("priority", "mark", "focus target")),
    ("SHARE_STATE", ("shared state", "party", "prefix cache", "world state")),
    ("MERGE_RESULTS", ("merge", "reconcile", "consensus")),
    ("DEDUPLICATE_RESULTS", ("deduplicate", "de-duplicate", "duplicate suppression")),
    ("REJECT_DEPENDENT_SUFFIX", ("dependent later tokens", "discard suffix", "invalidates later")),
    ("RECORD_RECEIPT", ("receipt", "provenance", "audit trail")),
    ("ROLLBACK_ON_FAILURE", ("rollback", "restore checkpoint")),
    ("FAIL_CLOSED", ("fail closed", "fails closed", "default deny", "block on uncertainty")),
    ("ADAPT_PARAMETER", ("adaptive", "dynamically select", "controller", "auto tune", "autotune")),
)

_DOMAIN_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("GENERATION", ("generate", "token", "model", "payload")),
    ("SPECULATION", ("mtp", "speculative", "draft", "candidate", "future token")),
    ("VERIFICATION", ("verify", "verifier", "acceptance", "critic", "judge")),
    ("TRIGGERING", ("trigger", "cast on", "when hit", "on critical")),
    ("ROUTING", ("route", "router", "expert", "targeting")),
    ("MEMORY", ("memory", "context", "bcc")),
    ("RETRIEVAL", ("retrieve", "retrieval", "search")),
    ("CACHING", ("cache", "kv", "prefix")),
    ("COMPRESSION", ("compress", "quantization", "decompress")),
    ("BATCHING", ("batch", "continuous batching")),
    ("PARALLELISM", ("parallel", "fan-out", "fan out", "multiple")),
    ("SYNCHRONIZATION", ("synchronize", "merge", "reconcile", "barrier")),
    ("RESOURCE_BUDGETING", ("budget", "cost", "reservation", "capacity", "vram")),
    ("TOOL_USE", ("tool", "function call", "executor")),
    ("SAFETY_AUTHORITY", ("authority", "permission", "refusal", "policy")),
    ("OBSERVABILITY_PROVENANCE", ("receipt", "telemetry", "audit", "provenance")),
    ("RECOVERY_ROLLBACK", ("recovery", "rollback", "fallback", "restore")),
    ("ADAPTATION_LEARNING", ("learn", "adaptive", "feedback", "training")),
    ("STATE_MANAGEMENT", ("state", "world state", "checkpoint")),
    ("LATENCY_CONTROL", ("latency", "cooldown", "scheduler", "throughput")),
)


def normalize_text(parts: Iterable[str]) -> str:
    text = " ".join(str(part) for part in parts if part)
    text = text.casefold().replace("’", "'")
    text = re.sub(r"[^a-z0-9+%.'/_ -]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_primitives(parts: Iterable[str]) -> tuple[str, ...]:
    text = normalize_text(parts)
    return tuple(name for name, phrases in _RULES if any(phrase in text for phrase in phrases))


def extract_domains(parts: Iterable[str]) -> tuple[str, ...]:
    text = normalize_text(parts)
    return tuple(name for name, phrases in _DOMAIN_RULES if any(phrase in text for phrase in phrases))
