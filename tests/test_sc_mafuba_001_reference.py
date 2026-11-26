"""Offline reference tests for SC-MAFUBA-001 (not kernel enforcement).

These tests exercise labelled reference helpers and draft-registry consistency.
They do not implement containment in semantic_compiler_kernel and must not be
read as flipping implementation_correctness or empirical_validation.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tests.reference.sc_mafuba_001.allowlist import (
    PROCEED_STATUSES,
    must_halt,
    resolve_branch,
)
from tests.reference.sc_mafuba_001.cbf import toy_1d_robust_cbf
from tests.reference.sc_mafuba_001.supervisor import (
    EmergencySupervisor,
    ResourceBudget,
    Worker,
)

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"
EVIDENCE = DOCS / "evidence" / "sc-mafuba-001"
JSONL = EVIDENCE / "sc_mafuba_001.jsonl"
SPEC_V100 = DOCS / "SC-MAFUBA-001_v1.0.0.md"
SPEC_RC1 = DOCS / "SC-MAFUBA-001_v1.1.0-rc1.md"

OFFICIAL_TEST_IDS = [
    "TEST-MAFUBA-A1",
    "TEST-MAFUBA-A2",
    "TEST-MAFUBA-B1",
    "TEST-MAFUBA-B2",
    "TEST-MAFUBA-C1",
    "TEST-MAFUBA-C2",
    "TEST-MAFUBA-C3",
    "TEST-MAFUBA-D1",
    "TEST-MAFUBA-D2",
]

NON_PROCEED = [
    "FAIL_CLOSED",
    "PREEMPTIVE_FAIL_CLOSED",
    "QUARANTINE",
    "TIMEOUT",
    "NUMERICAL_TOLERANCE_FAILURE",
    "UNCERTAIN",
    "UNKNOWN",
    None,
    "",
    "success",
    "SUCCESS",
    "allow",
    "continue",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_jsonl(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


class AllowlistBranchingTests(unittest.TestCase):
    def test_only_explicit_allow_or_continue_proceed(self) -> None:
        for status in ("ALLOW", "CONTINUE"):
            self.assertIn(status, PROCEED_STATUSES)
            self.assertFalse(must_halt(status))
            branch, value = resolve_branch(status, value="ok")
            self.assertEqual(branch, "CONTINUE")
            self.assertEqual(value, "ok")

    def test_every_other_status_halts_including_preemptive(self) -> None:
        for status in NON_PROCEED:
            with self.subTest(status=status):
                self.assertTrue(must_halt(status))
                branch, reason = resolve_branch(status, value="secret")
                self.assertEqual(branch, "HALT")
                self.assertNotEqual(branch, "CONTINUE")
                self.assertIsNot(reason, "secret")
                # The Step 8 fail-open bug: PREEMPTIVE_FAIL_CLOSED must not
                # fall through to success.
                if status == "PREEMPTIVE_FAIL_CLOSED":
                    self.assertEqual(reason, "PREEMPTIVE_FAIL_CLOSED")


class ToyRobustCBFTests(unittest.TestCase):
    def test_feasible_applies_filtered_control(self) -> None:
        # Far from the barrier, u=0 is feasible and must be the applied control.
        decision = toy_1d_robust_cbf(x=0.0, u_nom=0.0, x_max=1.0, r_max=0.2, u_max=1.0)
        self.assertEqual(decision.status, "CONTINUE")
        self.assertIsNotNone(decision.u)
        self.assertAlmostEqual(decision.u, 0.0)
        self.assertGreaterEqual(decision.h, 0.0)
        # Nominal unsafe push is filtered down to the CBF upper bound.
        pushed = toy_1d_robust_cbf(x=0.5, u_nom=1.0, x_max=1.0, r_max=0.2, alpha_gain=1.0)
        self.assertEqual(pushed.status, "CONTINUE")
        self.assertLessEqual(pushed.u, pushed.upper_bound + 1e-12)
        self.assertLess(pushed.u, 1.0)

    def test_infeasible_fails_closed_and_returns_no_control(self) -> None:
        # Near the barrier, even full braking cannot satisfy the robust inequality.
        decision = toy_1d_robust_cbf(
            x=0.95, u_nom=0.0, x_max=1.0, r_max=1.5, u_max=0.1, alpha_gain=1.0
        )
        self.assertEqual(decision.status, "FAIL_CLOSED")
        self.assertIsNone(decision.u)
        branch, reason = resolve_branch(decision.status)
        self.assertEqual(branch, "HALT")
        self.assertEqual(reason, "FAIL_CLOSED")


class SupervisorReserveTests(unittest.TestCase):
    def test_admit_never_returns_success_when_reserve_hit(self) -> None:
        budget = ResourceBudget(r_budget=10.0, r_reserve=2.0, r_used=0.0)
        self.assertEqual(budget.admit(8.0), "CONTINUE")
        status = budget.admit(0.1)
        self.assertEqual(status, "PREEMPTIVE_FAIL_CLOSED")
        branch, reason = resolve_branch(status, value="should-not-leak")
        self.assertEqual(branch, "HALT")
        self.assertEqual(reason, "PREEMPTIVE_FAIL_CLOSED")

    def test_d2_supervisor_shutdown_runs_on_the_reserve(self) -> None:
        budget = ResourceBudget(r_budget=10.0, r_reserve=2.0, r_used=0.0)
        supervisor = EmergencySupervisor(budget, max_evidence_bytes=16)
        worker = Worker("worker-1")
        evidence = b"X" * 64
        record = supervisor.reserve_trigger_shutdown(worker, evidence)

        self.assertFalse(budget.accepting_work)
        self.assertEqual(budget.admit(1.0), "PREEMPTIVE_FAIL_CLOSED")
        self.assertFalse(worker.running)
        self.assertTrue(worker.isolated)
        self.assertTrue(record.stopped_admissions)
        self.assertTrue(record.worker_terminated)
        self.assertTrue(record.isolated)
        self.assertTrue(record.quarantined)
        self.assertFalse(record.automatic_resumption)
        self.assertEqual(record.reserve_used, 2.0)
        self.assertEqual(record.evidence, b"X" * 16)
        self.assertIs(supervisor.last_shutdown, record)
        self.assertEqual(supervisor.try_resume(), "QUARANTINE_LOCKED")
        # The v1.0.0 bug asserted FAIL_CLOSED here; the preemptive status must
        # still halt, and the shutdown path must have actually run.
        self.assertIsNotNone(supervisor.last_shutdown)


class DraftRegistryConsistencyTests(unittest.TestCase):
    def test_jsonl_schema_ids_hashes_and_unawarded_gold(self) -> None:
        self.assertTrue(JSONL.is_file())
        self.assertTrue(SPEC_V100.is_file())
        self.assertTrue(SPEC_RC1.is_file())
        rows = _load_jsonl(JSONL)
        by_id = {row["id"]: row for row in rows}
        self.assertIn("SC-MAFUBA-001", by_id)
        self.assertIn("SC-MAFUBA-001A", by_id)
        self.assertIn("SC-MAFUBA-001B", by_id)
        self.assertIn("SC-MAFUBA-001C", by_id)
        self.assertIn("SC-MAFUBA-001D", by_id)
        self.assertIn("SC-MAFUBA-001@1.0.0", by_id)

        parent = by_id["SC-MAFUBA-001"]
        historical = by_id["SC-MAFUBA-001@1.0.0"]
        self.assertEqual(parent["classification"], "PROPOSED_GOLD")
        self.assertIs(parent["gold_awarded"], False)
        self.assertIs(historical["gold_awarded"], False)
        self.assertEqual(parent["version"], "1.1.0-rc1")
        self.assertEqual(historical["version"], "1.0.0")

        for row in rows:
            self.assertIs(row.get("gold_awarded"), False)
            axes = row.get("verification_axes") or {}
            if axes:
                self.assertEqual(axes.get("mathematical_validity"), "DRAFT_SPECIFIED_UNPROVEN")
                self.assertEqual(axes.get("implementation_correctness"), "NOT_IMPLEMENTED")
                self.assertEqual(axes.get("empirical_validation"), "UNVALIDATED")

        parent_tests = parent["acceptance_test_ids"]
        for test_id in OFFICIAL_TEST_IDS:
            self.assertIn(test_id, parent_tests)
        self.assertIn("TEST-MAFUBA-C3", parent_tests)
        self.assertIn("TEST-MAFUBA-C3", by_id["SC-MAFUBA-001C"]["acceptance_test_ids"])

        rc1_hash = _sha256(SPEC_RC1)
        v100_hash = _sha256(SPEC_V100)
        self.assertEqual(parent["provenance"]["spec_sha256"], rc1_hash)
        self.assertEqual(parent["provenance"]["v1_0_0_spec_sha256"], v100_hash)
        self.assertEqual(historical["provenance"]["spec_sha256"], v100_hash)
        self.assertEqual(len(rc1_hash), 64)
        self.assertEqual(len(v100_hash), 64)
        self.assertNotEqual(rc1_hash, v100_hash)
