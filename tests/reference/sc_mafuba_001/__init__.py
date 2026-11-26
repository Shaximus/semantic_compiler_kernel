"""SC-MAFUBA-001 reference helpers.

REFERENCE ONLY. Not kernel enforcement. Not an implementation of the
containment subsystems in semantic_compiler_kernel.
"""

from tests.reference.sc_mafuba_001.allowlist import (
    PROCEED_STATUSES,
    halt_reason,
    must_halt,
    resolve_branch,
)
from tests.reference.sc_mafuba_001.cbf import (
    BarrierDecision,
    toy_1d_robust_cbf,
)
from tests.reference.sc_mafuba_001.supervisor import (
    EmergencySupervisor,
    ResourceBudget,
    ShutdownRecord,
    Worker,
)

__all__ = [
    "PROCEED_STATUSES",
    "halt_reason",
    "must_halt",
    "resolve_branch",
    "BarrierDecision",
    "toy_1d_robust_cbf",
    "EmergencySupervisor",
    "ResourceBudget",
    "ShutdownRecord",
    "Worker",
]
