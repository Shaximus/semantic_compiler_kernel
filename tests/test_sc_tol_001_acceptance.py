"""SC-TOL-001 v2.1-rc5 acceptance suite (42 tests), Shax t608u/t609u attachment.

The test bodies below are copied verbatim from lines 1871-2828 of
docs/evidence/source-2026-11-27a/sc_tol_001_v2.1-rc5_attachment.py (material Shax
supplied). Only this import header was added. They run against the kernel copy
(tests/reference/sc_tol_001/compiler.py, rc5 plus recorded fixes);
tests/test_sc_tol_001_kernel.py runs the same bodies against the unmodified rc5.
"""

from __future__ import annotations

import json
import unittest

from tests.reference.sc_tol_001.compiler import *  # noqa: F401,F403  (verbatim bodies use bare names)

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
