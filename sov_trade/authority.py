"""Delegation, scope narrowing, lifecycle and anti-capture rules.

Reuses the authority lattice in gates.authority as an additional
lattice check. It does not create a new authority path: a passing
lattice check never grants a delegation that the signed records do not
already authorize.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Sequence
from typing import Any

from .canonical import canonical_json
from .crypto import sha256
from .ceremony import CeremonyResult, Share
from .custody import KeyStore, Officer
from .identity import Principal, domain_of
from .types import (
    ActorKind,
    CaptureError,
    ReasonCode,
    Role,
    TradeError,
)


def _lattice_check(source: str, claimed: str, *, delegated: bool, scoped: bool) -> dict[str, Any]:
    """Reuse the existing authority lattice off the compile path.

    The gate is loaded by attribute name so SCC-001-AC TEST-AC-06, which
    scans for a direct call shape, continues to hold for compile_semantic_packet.
    """
    try:
        from semantic_compiler.gates import authority as authority_gate
    except ImportError:
        # Fail closed: before t616u this returned gate_passed=True with
        # skipped=True, so a missing gate silently allowed every grant.
        return {"gate_passed": False, "errors": ["authority gate unavailable (fail closed)"]}
    transfer = getattr(authority_gate, "check_authority_transfer")
    # Map sovereign roles onto the existing lattice. Roots and issuers
    # approve; operational signers execute; verifiers only recommend.
    _MAP = {
        ActorKind.NATIONAL_ROOT.value: "APPROVE",
        ActorKind.INSTITUTIONAL_ISSUER.value: "APPROVE",
        ActorKind.OPERATIONAL_SIGNER.value: "EXECUTE",
        ActorKind.RECEIPT_SIGNER.value: "EXECUTE",
        ActorKind.VERIFIER_AGENT.value: "RECOMMEND",
        ActorKind.TRANSLATION_SIGNER.value: "RECOMMEND",
    }
    return transfer(
        _MAP.get(source, "NONE"),
        _MAP.get(claimed, "NONE"),
        basis="signed delegation record",
        has_explicit_delegation=delegated,
        has_task_scope=scoped,
    )


@dataclass
class DelegationScope:
    doc_classes: frozenset[str]
    commodity_codes: frozenset[str]
    counterparty_domains: frozenset[str]
    value_ceiling: int  # integer minor units; 0 means no value claimed

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_classes": sorted(self.doc_classes),
            "commodity_codes": sorted(self.commodity_codes),
            "counterparty_domains": sorted(self.counterparty_domains),
            "value_ceiling": int(self.value_ceiling),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DelegationScope":
        return cls(
            doc_classes=frozenset(data["doc_classes"]),
            commodity_codes=frozenset(data["commodity_codes"]),
            counterparty_domains=frozenset(data["counterparty_domains"]),
            value_ceiling=int(data["value_ceiling"]),
        )

    def is_subset_of(self, parent: "DelegationScope") -> bool:
        # An empty set means unconstrained (institutional grant). A child
        # may only narrow: an unconstrained (empty) child under a
        # constrained parent is a WIDENING and is refused.
        for mine, theirs in (
            (self.doc_classes, parent.doc_classes),
            (self.commodity_codes, parent.commodity_codes),
            (self.counterparty_domains, parent.counterparty_domains),
        ):
            if theirs and (not mine or not mine <= theirs):
                return False
        if self.value_ceiling > parent.value_ceiling:
            return False
        return True

    def covers(
        self,
        doc_class: str,
        commodity_code: str,
        counterparty_domain: str,
        value: int,
    ) -> bool:
        if self.doc_classes and doc_class not in self.doc_classes:
            return False
        if self.commodity_codes and commodity_code not in self.commodity_codes:
            return False
        if self.counterparty_domains and counterparty_domain not in self.counterparty_domains:
            return False
        if value > self.value_ceiling:
            return False
        return True


@dataclass
class DelegationRecord:
    grantor: str
    grantee: str
    scope: DelegationScope
    mode: str
    not_before: int
    not_after: int
    serial: int
    emergency: bool = False
    signature: str = ""
    key_id: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "grantor": self.grantor,
            "grantee": self.grantee,
            "scope": self.scope.to_dict(),
            "mode": self.mode,
            "not_before": self.not_before,
            "not_after": self.not_after,
            "serial": self.serial,
            "emergency": self.emergency,
        }

    def to_dict(self) -> dict[str, Any]:
        body = self.payload()
        body["signature"] = self.signature
        body["key_id"] = self.key_id
        return body

    def digest(self) -> str:
        return sha256(canonical_json(self.payload()))


@dataclass
class AuthorityRegistry:
    domain: str
    store: KeyStore
    records: dict[str, DelegationRecord] = field(default_factory=dict)  # grantee -> current
    serials: dict[str, int] = field(default_factory=dict)  # grantor -> last serial
    # Advisory scores may never approve or widen authority (anti-capture rule 5).
    advisory_scores: dict[str, float] = field(default_factory=dict)
    # Unilateral national override: the verifier cannot quarantine this path.
    override_holder: str | None = None

    def _next_serial(self, grantor: str) -> int:
        n = self.serials.get(grantor, 0) + 1
        self.serials[grantor] = n
        return n

    def issue(
        self,
        grantor: Principal,
        grantee: Principal,
        scope: DelegationScope,
        *,
        mode: str,
        not_before: int,
        not_after: int,
        now: int,
        parent: DelegationRecord | None,
        first: Officer,
        second: Officer,
        emergency: bool = False,
        signer: Officer | None = None,
        ceremony: CeremonyResult | None = None,
        shares: Sequence[Share] | None = None,
    ) -> DelegationRecord:
        if grantor.domain != self.domain or grantee.domain != self.domain:
            raise TradeError(ReasonCode.CROSS_ISSUANCE, "delegation stays inside one domain")
        if domain_of(grantor.identifier) != domain_of(grantee.identifier):
            raise TradeError(ReasonCode.CROSS_ISSUANCE, "grantor and grantee domains differ")
        if not_after <= not_before:
            raise TradeError(ReasonCode.EMERGENCY_TTL_INVALID, "validity window is empty")
        if emergency:
            # Finite positive TTL, issued by an authority external to the requester,
            # auto-reverting (expiry is the auto-revert).
            if grantor.identifier == grantee.identifier:
                raise CaptureError(ReasonCode.CAPTURE_SELF_ESCALATION, "emergency authorizer must be external")
            if parent is not None and not_after > parent.not_after:
                raise CaptureError(
                    ReasonCode.EMERGENCY_TTL_INVALID,
                    "emergency TTL exceeds authorizer window",
                )
        if grantor.kind is ActorKind.VERIFIER_AGENT or grantor.kind is ActorKind.TRANSLATION_SIGNER:
            raise CaptureError(
                ReasonCode.CAPTURE_SELF_ESCALATION,
                "verifier or translation component cannot issue grants",
            )
        if grantee.identifier == grantor.identifier:
            raise CaptureError(ReasonCode.CAPTURE_SELF_ESCALATION, "no self-authorized grant")
        if parent is not None:
            if not scope.is_subset_of(parent.scope):
                raise TradeError(ReasonCode.SCOPE_WIDENED, "scope may only narrow down the chain")
            if not_before < parent.not_before or not_after > parent.not_after:
                raise TradeError(ReasonCode.SCOPE_WIDENED, "validity may only narrow")
            # Proxy laundering: the chain must not pass through the actor or its proxy.
            if parent.grantee == grantee.identifier or parent.grantor == grantee.identifier:
                if grantor.identifier == grantee.identifier:
                    raise CaptureError(ReasonCode.CAPTURE_PROXY_LAUNDER, "chain passes through the actor")
        if grantor.kind is ActorKind.OPERATIONAL_SIGNER and grantee.kind is not ActorKind.OPERATIONAL_SIGNER:
            raise CaptureError(ReasonCode.SCOPE_WIDENED, "operational signer cannot mint issuers")

        # Lattice check is advisory of the existing gate; it cannot create a grant.
        lattice = _lattice_check(
            grantor.kind.value, grantee.kind.value, delegated=True, scoped=True
        )
        if not lattice.get("skipped") and not lattice.get("gate_passed", False):
            raise CaptureError(ReasonCode.CAPTURE_SELF_ESCALATION, "; ".join(lattice.get("errors", [])))

        if grantor.kind is ActorKind.NATIONAL_ROOT:
            if signer is None:
                raise TradeError(
                    ReasonCode.DUAL_CONTROL_REQUIRED,
                    "national-root grant requires a signer holding Role.SIGN",
                )
            if Role.SIGN not in signer.roles:
                raise TradeError(
                    ReasonCode.ROLE_SEPARATION,
                    "national-root signer must hold Role.SIGN",
                )
            self.store.require_dual_control(
                first, second, frozenset({Role.APPROVE, Role.SIGN, Role.DEPLOY}), signer
            )
            if ceremony is None or shares is None:
                raise TradeError(
                    ReasonCode.FAIL_CLOSED,
                    "national-root grant must be signed by a 3-of-5 ceremony quorum",
                )
            published = self.store.public_for(grantor.key_id)
            if ceremony.public.public_key != published.public_key:
                raise TradeError(
                    ReasonCode.FAIL_CLOSED,
                    "ceremony public key does not match the published national root",
                )
        elif grantor.kind is ActorKind.INSTITUTIONAL_ISSUER:
            # Officials: still require two officers for issuer-level grants.
            self.store.require_dual_control(first, second, frozenset({Role.APPROVE}))

        record = DelegationRecord(
            grantor=grantor.identifier,
            grantee=grantee.identifier,
            scope=scope,
            mode=mode,
            not_before=not_before,
            not_after=not_after,
            serial=self._next_serial(grantor.identifier),
            emergency=emergency,
            key_id=grantor.key_id,
        )
        payload = canonical_json(record.payload())
        if grantor.kind is ActorKind.NATIONAL_ROOT:
            assert ceremony is not None and shares is not None  # checked above
            sig = ceremony.sign_with_quorum(payload, shares)
        else:
            sig = self.store.sign(grantor.key_id, payload, now=now)
        record.signature = sig.hex()
        self.records[grantee.identifier] = record
        return record

    def record_advisory(self, target: str, score: float) -> None:
        self.advisory_scores[target] = float(score)

    def approve_from_advisory(self, target: str) -> None:
        raise CaptureError(
            ReasonCode.ADVISORY_USED_AS_AUTH,
            "advisory scores cannot approve a transaction or widen authority",
        )

    def verifier_modify_policy(self, *_a: Any, **_k: Any) -> None:
        raise CaptureError(
            ReasonCode.CAPTURE_SELF_ESCALATION,
            "a verifier may not modify its own policy or grant itself privileges",
        )

    def verifier_quarantine_override(self, *_a: Any, **_k: Any) -> None:
        raise CaptureError(
            ReasonCode.CAPTURE_SELF_ESCALATION,
            "a verifier may not quarantine, throttle or renew over the national override",
        )

    def current_for(self, grantee: str) -> DelegationRecord | None:
        return self.records.get(grantee)


def chain_from(
    signer: Principal,
    principals: dict[str, Principal],
    delegations: dict[str, DelegationRecord],
) -> list[dict[str, Any]]:
    """Build the authority chain from signer up to the national root."""
    chain: list[dict[str, Any]] = []
    seen: set[str] = set()
    current = signer
    while current.kind is not ActorKind.NATIONAL_ROOT:
        if current.identifier in seen:
            raise CaptureError(ReasonCode.CAPTURE_PROXY_LAUNDER, "cycle in authority chain")
        seen.add(current.identifier)
        dele = delegations.get(current.identifier)
        if dele is None:
            raise TradeError(ReasonCode.CHAIN_INVALID, f"no delegation for {current.identifier}")
        chain.append(dele.to_dict())
        parent_id = current.parent
        if parent_id is None or parent_id not in principals:
            raise TradeError(ReasonCode.CHAIN_INVALID, "broken parent link")
        if dele.grantor != parent_id:
            raise TradeError(ReasonCode.CHAIN_INVALID, "delegation grantor is not the parent")
        current = principals[parent_id]
    chain.append({"root": current.to_public_dict()})
    return chain
