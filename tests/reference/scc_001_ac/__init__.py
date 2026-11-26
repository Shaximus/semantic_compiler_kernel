"""SCC-001-AC Anti-Capture Invariant: reference harness and reference enforcement.

REFERENCE ONLY. Not kernel enforcement, not packaged, not imported by core/
or expansion/. Standard library only. See docs/SCC-001-AC_ANTI_CAPTURE.md.

The repository had no Authority Plane, no AuthorityRole, no
ALLOWED_ROLE_ACTIONS and no credential verifier before this module. The rc1
section-5 contract is copied verbatim in spec_contract.py; the rest is modelled
here so the anti-capture oracle has something to run against. That does not
change implementation_correctness for the kernel.
"""

from tests.reference.scc_001_ac.flags import (
    AUTO_QUARANTINE_ENABLED,
    ML_ANOMALY_SCORING_ENABLED,
)
from tests.reference.scc_001_ac.model import (
    AUTHORITY_PLANE_ACTIONS,
    DEFENSIVE_ACTIONS,
    HISTORY_INSENSITIVE_PERMISSIONS,
    Action,
    AuthorityPlane,
    Credential,
    Request,
    Role,
)
from tests.reference.scc_001_ac.identity import PrincipalVerifier, VerifyStatus
from tests.reference.scc_001_ac.gateway import AuthorityGateway, verdict
from tests.reference.scc_001_ac.budget import FaultModel, OverrideChannel, PartitionedBudget
from tests.reference.scc_001_ac.quarantine import QuarantineController, QuarantineState

__all__ = [
    "AUTO_QUARANTINE_ENABLED", "ML_ANOMALY_SCORING_ENABLED",
    "AUTHORITY_PLANE_ACTIONS", "DEFENSIVE_ACTIONS", "HISTORY_INSENSITIVE_PERMISSIONS",
    "Action", "AuthorityPlane", "Credential", "Request", "Role",
    "PrincipalVerifier", "VerifyStatus",
    "AuthorityGateway", "verdict",
    "FaultModel", "OverrideChannel", "PartitionedBudget",
    "QuarantineController", "QuarantineState",
]
