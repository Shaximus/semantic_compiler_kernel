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
    AdmitResult,
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
SPEC_RC2 = DOCS / "SC-MAFUBA-001_v1.1.0-rc2.md"

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
        self.assertEqual(budget.admit(7.9), "CONTINUE")
        self.assertAlmostEqual(budget.r_used, 7.9)
        self.assertGreater(budget.r_free, budget.r_reserve)
        status = budget.admit(0.1)
        self.assertEqual(status, "PREEMPTIVE_FAIL_CLOSED")
        self.assertAlmostEqual(budget.r_used, 7.9)
        branch, reason = resolve_branch(status.status, value="should-not-leak")
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
        # reserve_used is now a measured debit (0.5 fixed + 16 bytes * 0.01), not the
        # literal r_reserve the v1.1.0-rc1 helper returned, which made this unfalsifiable.
        self.assertTrue(record.completed)
        self.assertAlmostEqual(record.reserve_used, 0.66)
        self.assertLessEqual(record.reserve_used, budget.r_reserve)
        self.assertEqual(record.evidence, b"X" * 16)
        self.assertIs(supervisor.last_shutdown, record)
        self.assertEqual(supervisor.try_resume(), "QUARANTINE_LOCKED")
        # The v1.0.0 bug asserted FAIL_CLOSED here; the preemptive status must
        # still halt, and the shutdown path must have actually run.
        self.assertIsNotNone(supervisor.last_shutdown)


class ReviewRegressionTests(unittest.TestCase):
    """Defects found reviewing the rc1 reference helpers (reference-only fixes)."""

    def test_cbf_outside_safe_set_fails_closed(self) -> None:
        d = toy_1d_robust_cbf(x=1.5, u_nom=0.0, x_max=1.0, r_max=0.2, u_max=1.0)
        self.assertEqual(d.status, "FAIL_CLOSED")
        self.assertEqual(d.reason, "OUTSIDE_SAFE_SET")
        self.assertIsNone(d.u)
        # h == 0 is still inside Omega_safe (h >= 0); only the inequality decides.
        edge = toy_1d_robust_cbf(x=1.0, u_nom=0.0, x_max=1.0, r_max=0.2, u_max=1.0)
        self.assertEqual(edge.reason, "")
        self.assertEqual(edge.status, "CONTINUE")

    def test_cbf_non_finite_or_illformed_never_continues(self) -> None:
        nan, inf = float("nan"), float("inf")
        cases = [
            dict(x=nan, u_nom=0.0), dict(x=inf, u_nom=0.0), dict(x=-inf, u_nom=0.0),
            dict(x=0.0, u_nom=nan), dict(x=0.0, u_nom=0.0, r_max=nan),
            dict(x=0.0, u_nom=0.0, r_max=-0.1), dict(x=0.0, u_nom=0.0, u_max=-1.0),
            dict(x=True, u_nom=0.0),
        ]
        for kw in cases:
            with self.subTest(**kw):
                d = toy_1d_robust_cbf(**kw)
                self.assertEqual(d.status, "NUMERICAL_TOLERANCE_FAILURE")
                self.assertIsNone(d.u)
                self.assertTrue(must_halt(d.status))

    def test_allowlist_rejects_impersonation_and_malformed_types(self) -> None:
        class Impostor(str):
            def __eq__(self, other):  # noqa: D401
                return True
            __hash__ = lambda self: hash("ALLOW")  # noqa: E731

        for bad in (Impostor("X"), True, 1, ["ALLOW"], {"ALLOW"}, b"ALLOW", object()):
            with self.subTest(bad=type(bad).__name__):
                self.assertTrue(must_halt(bad))
                branch, reason = resolve_branch(bad, value="secret")
                self.assertEqual(branch, "HALT")
                self.assertNotEqual(reason, "secret")

    def test_admit_rejects_non_finite_and_cannot_be_poisoned(self) -> None:
        budget = ResourceBudget(r_budget=10.0, r_reserve=2.0)
        for amount in (float("nan"), float("inf"), -1.0, True, "1"):
            with self.subTest(amount=amount):
                self.assertEqual(budget.admit(amount), "FAIL_CLOSED")
                self.assertEqual(budget.r_used, 0.0)
        # The reserve is still enforced afterwards (v1.1.0-rc1: NaN admit made it permanently open).
        self.assertEqual(budget.admit(7.9), "CONTINUE")
        self.assertEqual(budget.admit(0.1), "PREEMPTIVE_FAIL_CLOSED")
        self.assertAlmostEqual(budget.r_used, 7.9)

    def test_d2_shutdown_can_fail_when_reserve_is_too_small(self) -> None:
        budget = ResourceBudget(r_budget=10.0, r_reserve=0.1)
        supervisor = EmergencySupervisor(budget, max_evidence_bytes=16)
        worker = Worker("w")
        record = supervisor.reserve_trigger_shutdown(worker, b"X" * 64)
        self.assertFalse(record.completed)
        self.assertEqual(record.status, "RESERVE_INSUFFICIENT")
        # Termination and admission stop are never skipped, even when the reserve is short.
        self.assertFalse(worker.running)
        self.assertFalse(budget.accepting_work)
        self.assertTrue(record.quarantined)
        self.assertFalse(record.automatic_resumption)
        self.assertEqual(record.evidence, b"")

    def test_d2_evidence_shrinks_to_what_the_reserve_affords(self) -> None:
        budget = ResourceBudget(r_budget=10.0, r_reserve=0.7)
        supervisor = EmergencySupervisor(budget, max_evidence_bytes=1000)
        record = supervisor.reserve_trigger_shutdown(Worker("w"), b"X" * 500)
        self.assertTrue(record.completed)
        self.assertLessEqual(record.reserve_used, budget.r_reserve + 1e-9)
        self.assertLess(len(record.evidence), 500)

    def test_strict_boundary_refuses_admission_at_equality(self) -> None:
        """STRICT 001D: work that would land exactly on the reserve is refused and not billed."""
        budget = ResourceBudget(r_budget=10.0, r_reserve=2.0)
        result = budget.admit(8.0)
        self.assertIsInstance(result, AdmitResult)
        self.assertEqual(result, "PREEMPTIVE_FAIL_CLOSED")
        self.assertTrue(result.needs_review)
        self.assertEqual(result.diagnostic, "BOUNDARY_EDGE_PENDING_DELIBERATION")
        self.assertEqual(budget.r_used, 0.0)
        self.assertEqual(budget.r_execution, 0.0)
        self.assertEqual(budget.r_enforcement, 0.0)
        self.assertGreater(budget.r_free, budget.r_reserve)
        # A refused admit does not itself mean the reserve was reached.
        self.assertTrue(budget.accepting_work)
        # A later debit that stays strictly below the reserve still proceeds.
        ok = budget.admit(7.9)
        self.assertEqual(ok, "CONTINUE")
        self.assertFalse(ok.needs_review)
        self.assertIsNone(ok.diagnostic)
        self.assertAlmostEqual(budget.r_used, 7.9)
        self.assertAlmostEqual(budget.r_execution, 7.9)

    def test_equality_edge_emits_pending_deliberation_diagnostic(self) -> None:
        """The equality edge stays visible until the provisional STRICT default is deliberated."""
        budget = ResourceBudget(r_budget=10.0, r_reserve=2.0)
        edge = budget.admit(8.0)
        self.assertEqual(edge.status, "PREEMPTIVE_FAIL_CLOSED")
        self.assertTrue(edge.needs_review)
        self.assertEqual(edge.diagnostic, "BOUNDARY_EDGE_PENDING_DELIBERATION")
        branch, reason = resolve_branch(edge.status, value="should-not-leak")
        self.assertEqual(branch, "HALT")
        self.assertEqual(reason, "PREEMPTIVE_FAIL_CLOSED")
        self.assertEqual(budget.r_used, 0.0)
        # Past the reserve is also refused, but is not the open equality question.
        overshoot = budget.admit(8.1)
        self.assertEqual(overshoot.status, "PREEMPTIVE_FAIL_CLOSED")
        self.assertFalse(overshoot.needs_review)
        self.assertIsNone(overshoot.diagnostic)
        self.assertEqual(budget.r_used, 0.0)

    def test_three_term_counters_bill_execution_and_enforcement_separately(self) -> None:
        budget = ResourceBudget(r_budget=10.0, r_reserve=2.0)
        self.assertEqual(budget.admit(3.0, purpose="execution"), "CONTINUE")
        self.assertEqual(budget.admit(1.0, purpose="enforcement"), "CONTINUE")
        self.assertAlmostEqual(budget.r_execution, 3.0)
        self.assertAlmostEqual(budget.r_enforcement, 1.0)
        self.assertAlmostEqual(budget.r_used, 4.0)
        # Remaining headroom under the strict cap is 4.0; a 4.0 debit lands on the reserve.
        self.assertEqual(budget.admit(4.0, purpose="enforcement"), "PREEMPTIVE_FAIL_CLOSED")
        self.assertAlmostEqual(budget.r_enforcement, 1.0)
        self.assertEqual(budget.admit(1.0, purpose="other"), "FAIL_CLOSED")
        self.assertAlmostEqual(budget.r_used, 4.0)

    def test_edge_driven_supervisor_fires_when_free_reaches_reserve(self) -> None:
        """Defence in depth: if free reaches the reserve for any reason, fire immediately."""
        budget = ResourceBudget(r_budget=10.0, r_reserve=2.0)
        supervisor = EmergencySupervisor(budget, max_evidence_bytes=16)
        worker = Worker("w")
        supervisor.arm(worker, b"E" * 32)
        budget.r_used = budget.r_budget - budget.r_reserve
        self.assertEqual(budget.r_free, budget.r_reserve)
        self.assertIsNotNone(supervisor.last_shutdown)
        self.assertFalse(budget.accepting_work)
        self.assertFalse(worker.running)
        self.assertTrue(worker.isolated)
        self.assertFalse(supervisor.last_shutdown.automatic_resumption)
        # Already shut down; a later admit is still preemptive.
        self.assertEqual(budget.admit(0.0), "PREEMPTIVE_FAIL_CLOSED")


class DraftRegistryConsistencyTests(unittest.TestCase):
    def test_jsonl_schema_ids_hashes_and_unawarded_gold(self) -> None:
        self.assertTrue(JSONL.is_file())
        self.assertTrue(SPEC_V100.is_file())
        self.assertTrue(SPEC_RC1.is_file())
        self.assertTrue(SPEC_RC2.is_file())
        rows = _load_jsonl(JSONL)
        by_id = {row["id"]: row for row in rows}
        self.assertIn("SC-MAFUBA-001", by_id)
        self.assertIn("SC-MAFUBA-001A", by_id)
        self.assertIn("SC-MAFUBA-001B", by_id)
        self.assertIn("SC-MAFUBA-001C", by_id)
        self.assertIn("SC-MAFUBA-001D", by_id)
        self.assertIn("SC-MAFUBA-001@1.0.0", by_id)
        self.assertIn("SC-MAFUBA-001@1.1.0-rc1", by_id)

        parent = by_id["SC-MAFUBA-001"]
        historical = by_id["SC-MAFUBA-001@1.0.0"]
        historical_rc1 = by_id["SC-MAFUBA-001@1.1.0-rc1"]
        self.assertEqual(parent["classification"], "PROPOSED_GOLD")
        self.assertIs(parent["gold_awarded"], False)
        self.assertIs(historical["gold_awarded"], False)
        self.assertIs(historical_rc1["gold_awarded"], False)
        self.assertEqual(parent["version"], "1.1.0-rc2")
        self.assertEqual(historical["version"], "1.0.0")
        self.assertEqual(historical_rc1["version"], "1.1.0-rc1")
        for sub_id in ("SC-MAFUBA-001A", "SC-MAFUBA-001B", "SC-MAFUBA-001C", "SC-MAFUBA-001D"):
            self.assertEqual(by_id[sub_id]["version"], "1.1.0-rc2")
        boundary = by_id["SC-MAFUBA-001D"]["admission_boundary"]
        self.assertEqual(boundary["rule"], "STRICT")
        self.assertEqual(boundary["status"], "PROVISIONAL_DEFAULT")
        self.assertIs(boundary["pending_deliberation"], True)
        self.assertTrue(boundary["reason"])
        parent_boundary = parent["admission_boundary"]
        self.assertEqual(parent_boundary["status"], "PROVISIONAL_DEFAULT")
        self.assertIs(parent_boundary["pending_deliberation"], True)

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

        rc2_hash = _sha256(SPEC_RC2)
        rc1_hash = _sha256(SPEC_RC1)
        v100_hash = _sha256(SPEC_V100)
        # Prior pins must not move; the candidate hash is the new rc2 file.
        self.assertEqual(
            v100_hash,
            "3e2ff55ce51f3b54985b0163340b327b60775a512828e48d48e95dacfe705863",
        )
        self.assertEqual(
            rc1_hash,
            "8d6f8c291ff9a125eef026ad2f9df1ec7e6577aa9cb97b68b8fdc91351845c23",
        )
        self.assertEqual(parent["provenance"]["spec_sha256"], rc2_hash)
        self.assertEqual(parent["provenance"]["v1_0_0_spec_sha256"], v100_hash)
        self.assertEqual(parent["provenance"]["v1_1_0_rc1_spec_sha256"], rc1_hash)
        self.assertEqual(parent["candidate"]["version"], "1.1.0-rc2")
        self.assertEqual(parent["candidate"]["spec_sha256"], rc2_hash)
        self.assertEqual(historical["provenance"]["spec_sha256"], v100_hash)
        self.assertEqual(historical_rc1["provenance"]["spec_sha256"], rc1_hash)
        artifact_versions = {item["version"]: item for item in parent["historical_artifacts"]}
        self.assertEqual(artifact_versions["1.0.0"]["spec_sha256"], v100_hash)
        self.assertEqual(artifact_versions["1.1.0-rc1"]["spec_sha256"], rc1_hash)
        self.assertEqual(len(rc2_hash), 64)
        self.assertEqual(len(rc1_hash), 64)
        self.assertEqual(len(v100_hash), 64)
        self.assertNotEqual(rc1_hash, v100_hash)
        self.assertNotEqual(rc2_hash, rc1_hash)
        self.assertNotEqual(rc2_hash, v100_hash)
