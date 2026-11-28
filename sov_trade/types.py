"""Shared types, reason codes and exceptions for SC-SOV-TRADE-001."""

from __future__ import annotations

from enum import Enum
from typing import Any


class DocClass(str, Enum):
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    EXPORT_DOCUMENTATION = "export_documentation"
    IMPORT_DOCUMENTATION = "import_documentation"
    CUSTOMS_DECLARATION = "customs_declaration"
    REGULATORY_DECLARATION = "regulatory_declaration"
    INSPECTION_RECORD = "inspection_record"
    COMPLIANCE_RECORD = "compliance_record"
    SHIPMENT_CONFIRMATION = "shipment_confirmation"
    DELIVERY_CONFIRMATION = "delivery_confirmation"
    CONTRACTUAL_ACKNOWLEDGMENT = "contractual_acknowledgment"


class Role(str, Enum):
    SIGN = "sign"
    APPROVE = "approve"
    DEPLOY = "deploy"


class ActorKind(str, Enum):
    NATIONAL_ROOT = "nr"
    INSTITUTIONAL_ISSUER = "ii"
    OPERATIONAL_SIGNER = "os"
    VERIFIER_AGENT = "va"
    TRANSLATION_SIGNER = "tr"
    RECEIPT_SIGNER = "rs"
    OFFICER = "officer"


class Outcome(str, Enum):
    ACCEPTED = "accepted"
    ACCEPTED_WITH_CONDITIONS = "accepted_with_conditions"
    DEFERRED = "deferred"
    REJECTED = "rejected"


class CheckName(str, Enum):
    SCHEMA = "schema"
    SIGNATURE = "signature"
    CHAIN = "chain"
    SCOPE = "scope"
    VALIDITY_WINDOW = "validity_window"
    REVOCATION = "revocation"
    REPLAY = "replay"
    BINDING = "binding"


class ReasonCode(str, Enum):
    OK = "ok"
    UNKNOWN_MAJOR_VERSION = "unknown_major_version"
    CANONICAL_FORM_MISMATCH = "canonical_form_mismatch"
    SIGNATURE_INVALID = "signature_invalid"
    HYBRID_INCOMPLETE = "hybrid_incomplete"
    CHAIN_INVALID = "chain_invalid"
    CROSS_ISSUANCE = "cross_issuance"
    UNRECOGNIZED_ANCHOR = "unrecognized_anchor"
    RECOGNITION_WITHDRAWN = "recognition_withdrawn"
    RECOGNITION_SCOPE = "recognition_scope"
    DELEGATION_SCOPE = "delegation_scope"
    SCOPE_WIDENED = "scope_widened"
    EXPIRED = "expired"
    NOT_YET_VALID = "not_yet_valid"
    CLOCK_DRIFT = "clock_drift"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    STATUS_UNKNOWN = "status_unknown"
    STATUS_STALE = "status_stale"
    CHALLENGE_MISMATCH = "challenge_mismatch"
    TXN_BINDING_MISMATCH = "txn_binding_mismatch"
    REPLAYED = "replayed"
    ROOT_SIGNED_ASSERTION = "root_signed_assertion"
    VERIFIER_SIGNED_ASSERTION = "verifier_signed_assertion"
    CAPTURE_SELF_ESCALATION = "capture_self_escalation"
    CAPTURE_PROXY_LAUNDER = "capture_proxy_launder"
    EMERGENCY_TTL_INVALID = "emergency_ttl_invalid"
    ADVISORY_USED_AS_AUTH = "advisory_used_as_auth"
    ROLE_SEPARATION = "role_separation"
    DUAL_CONTROL_REQUIRED = "dual_control_required"
    LEDGER_FORK = "ledger_fork"
    CONSISTENCY_PROOF_MISSING = "consistency_proof_missing"
    TRANSLATION_ALTERED_SOURCE = "translation_altered_source"
    CLASS_CHANGE_UNCONFIRMED = "class_change_unconfirmed"
    FAIL_CLOSED = "fail_closed"


class MappingType(str, Enum):
    EXACT = "exact"
    NARROWING = "narrowing"
    BROADENING = "broadening"
    NO_EQUIVALENT = "no_equivalent"


class AssuranceStatus(str, Enum):
    """R-16 is not met by this reference build."""

    NOT_MET = "not_met"
    NOT_CLAIMED = "not_claimed"


class TradeError(Exception):
    """Base error for the sovereign trade package."""

    def __init__(self, reason: ReasonCode, message: str = "") -> None:
        self.reason = reason
        super().__init__(message or reason.value)


class CaptureError(TradeError):
    """An anti-capture rule was violated."""


class CustodyError(TradeError):
    """Key custody or role-separation rule was violated."""


def as_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return value
    raise TypeError(f"cannot convert {type(value)!r} to dict")
