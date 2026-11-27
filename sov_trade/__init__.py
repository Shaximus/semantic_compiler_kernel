"""SC-SOV-TRADE-001: Sovereign Bilateral Authentication Exchange.

Reference implementation of the v0.1 engineering specification stored at
``docs/evidence/source-2026-11-27d/``. This is not production-certified
and has not had an external audit (R-16 is not met).
"""

from .assertion import SignedAssertionEnvelope, salted_commitment, sign_sae
from .authority import DelegationScope
from .ceremony import CeremonyResult, run_root_ceremony
from .clock import DEFAULT_SKEW_SECONDS, Clock, FrozenClock
from .crypto import (
    ALG_ED25519,
    ALG_ML_DSA_65,
    SUITE_ED25519_MLDSA65,
    backend_name,
    generate_ed25519,
    generate_hybrid,
    generate_mldsa65,
    side_channel_safe,
)
from .disputes import Dispute, open_dispute, resolve_dispute
from .identity import RecognitionRecord, TrustBundle
from .ledger import verify_inclusion_proof
from .nation import Nation, merge_public_keys, verify_receipt_offline
from .protocol import Challenge, Outcome, VerificationResult
from .receipts import BilateralVerificationReceipt, verify_receipt
from .status import evaluate_status
from .translation import MappingEntry, MappingRegistry, MappingType, provenance_round_trip
from .types import (
    ActorKind,
    AssuranceStatus,
    CaptureError,
    CheckName,
    CustodyError,
    DocClass,
    ReasonCode,
    Role,
    TradeError,
)

__all__ = [
    "ActorKind",
    "AssuranceStatus",
    "BilateralVerificationReceipt",
    "CaptureError",
    "Challenge",
    "CheckName",
    "Clock",
    "CustodyError",
    "DEFAULT_SKEW_SECONDS",
    "DelegationScope",
    "Dispute",
    "DocClass",
    "FrozenClock",
    "MappingEntry",
    "MappingRegistry",
    "MappingType",
    "Nation",
    "Outcome",
    "ReasonCode",
    "RecognitionRecord",
    "Role",
    "SignedAssertionEnvelope",
    "TradeError",
    "TrustBundle",
    "VerificationResult",
    "ALG_ED25519",
    "ALG_ML_DSA_65",
    "CeremonyResult",
    "SUITE_ED25519_MLDSA65",
    "backend_name",
    "evaluate_status",
    "generate_ed25519",
    "run_root_ceremony",
    "generate_mldsa65",
    "generate_hybrid",
    "merge_public_keys",
    "open_dispute",
    "provenance_round_trip",
    "resolve_dispute",
    "salted_commitment",
    "side_channel_safe",
    "sign_sae",
    "verify_inclusion_proof",
    "verify_receipt",
    "verify_receipt_offline",
]
