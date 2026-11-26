"""Pure-unittest suite for the Japanese Automated Parking Tower Domain Elevator
(semantic_compiler.expansion.elevator): O(1) inverted-rack retrieval,
SemanticTicket compression & rehydration, and turntable cross-domain translation.
"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from tests.domain_inventory import registered_domain_count

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.expansion import (
    DomainElevator,
    SemanticTicket,
    SystemModel,
    decompress,
    get_default_elevator,
    park,
    retrieve,
    rotate_to,
    summon,
)
from semantic_compiler.expansion.elevator import (
    CANONICAL_DEPARTMENTS,
    BayDelivery,
    RehydratedDomain,
    TurntableTranslation,
)
from semantic_compiler.expansion.registry.loader import TEMPLATE_DIR, load_templates
from semantic_compiler.expansion.schema.v2_2_system_model import validate_system_model


class RackIndexingAndCachingTests(unittest.TestCase):
    """Verify single-pass O(1) rack indexing, zero repeated disk reads, and staleness detection."""

    def test_rack_indexes_all_templates_entries_and_invariants_once(self) -> None:
        with mock.patch(
            "semantic_compiler.expansion.elevator.load_templates",
            wraps=load_templates,
        ) as spy_load:
            elevator = DomainElevator(auto_refresh=True, staleness_check_interval=60.0)
            self.assertEqual(elevator.build_count, 0)
            self.assertEqual(spy_load.call_count, 0)

            first = elevator.summon("PagedAttention KV cache block table")
            self.assertFalse(first.cache_hit)
            self.assertEqual(elevator.build_count, 1)
            self.assertEqual(spy_load.call_count, 1)
            reads_after_build = elevator.disk_read_count
            self.assertGreater(reads_after_build, 0)

            stats = elevator.stats
            self.assertEqual(stats["domain_slots"], registered_domain_count())
            self.assertEqual(stats["compiled_entry_slots"], 41)  # +SC-TRIAD-*-001 (2026-11-25i), +SC-SCA-*-001 (t587u), +SC-CONSENT-001, SC-SCC-001 (t588u)
            self.assertEqual(stats["invariant_class_slots"], 14)
            self.assertEqual(
                stats["total_slots"],
                stats["domain_slots"]
                + stats["compiled_entry_slots"]
                + stats["invariant_class_slots"],
            )
            self.assertGreater(stats["token_postings"], 500)

            # Repeated summon / park / retrieve / rotate calls must NOT re-read YAML or JSONL files.
            for q in (
                "Chaos Inoculation energy shield recharge delay",
                "Android Verified Boot Knox StrongBox KeyMint",
                "Soul Bomb exit sovereignty SC-LU-SAO-SUGOU-001",
                "Eugeo Blue Rose Sword Code 871 SC-LU-SAO-EUGEO-001",
                "Pythagorean numerology life path number",
                "Natal chart Sun sign Moon sign Saturn return",
            ):
                delivery = elevator.summon(q)
                self.assertTrue(delivery.cache_hit)
                tkt = elevator.park(delivery.system_model)
                _ = elevator.retrieve(tkt)
            _ = elevator.rotate_to("kv_cache_inference", "distributed_consensus")

            self.assertEqual(elevator.build_count, 1)
            self.assertEqual(spy_load.call_count, 1)
            self.assertEqual(elevator.disk_read_count, reads_after_build)

    def test_cached_system_model_is_isolated_from_caller_mutation(self) -> None:
        elevator = DomainElevator()
        d1 = elevator.summon("PagedAttention KV cache block table")
        orig_count = len(d1.system_model["components"])
        d1.system_model["components"].clear()
        d1.system_model["domain"] = "corrupted"

        d2 = elevator.summon("PagedAttention KV cache block table")
        self.assertEqual(d2.system_model["domain"], "kv_cache_inference")
        self.assertEqual(len(d2.system_model["components"]), orig_count)

    def test_mtime_signature_staleness_invalidation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_templates = Path(tmp) / "templates"
            tmp_templates.mkdir()
            for fname in ("universal_generic.yaml", "kv_cache_inference.yaml", "mobile_security.yaml"):
                shutil.copy2(TEMPLATE_DIR / fname, tmp_templates / fname)

            elevator = DomainElevator(
                template_dir=tmp_templates,
                compiled_entries_dir=Path(tmp) / "empty_entries",
                auto_refresh=True,
                staleness_check_interval=0.0,
            )
            d1 = elevator.summon("kv cache block table")
            self.assertEqual(d1.primary_domain, "kv_cache_inference")
            self.assertEqual(elevator.build_count, 1)
            self.assertFalse(elevator.refresh_if_stale())
            self.assertEqual(elevator.build_count, 1)

            # Touch/append a benign comment to one YAML template so size & mtime change.
            target_yaml = tmp_templates / "kv_cache_inference.yaml"
            target_yaml.write_text(
                target_yaml.read_text(encoding="utf-8") + "\n# staleness probe\n",
                encoding="utf-8",
            )
            self.assertTrue(elevator.refresh_if_stale())
            self.assertEqual(elevator.build_count, 2)
            self.assertFalse(elevator.refresh_if_stale())


class SummoningAccuracyTests(unittest.TestCase):
    """Verify accurate summoning across diverse domains, SAO entries, and invariant classes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.elevator = DomainElevator()

    def test_diverse_domains_summoned_accurately(self) -> None:
        cases = (
            (
                "PagedAttention and RadixAttention manage KV cache block tables during prefill",
                "kv_cache_inference",
            ),
            (
                "Soul bomb exit sovereignty audit tests coerced oneness and bootstrapper surrender",
                "soul_bomb_sovereignty",
            ),
            (
                "Malevolent Shrine and Unlimited Void resolve a domain clash via 17-primitive grammar",
                "domain_expansion",
            ),
            (
                "Chaos Inoculation sets maximum life to 1 and uses energy shield buffer with ghost reaver",
                "poe_chaos_inoculation",
            ),
            (
                "Android Verified Boot, Knox StrongBox, KeyMint attestation, and SELinux sandbox",
                "mobile_security",
            ),
            (
                "Pythagorean letter reduction for Life Path number, Expression number, and karmic debt",
                "numerology",
            ),
            (
                "Natal chart with Sun sign, Moon sign, ascendant rising sign, stellium, and Saturn return",
                "astrology",
            ),
            (
                "Raft leader election quorum and fencing tokens prevent split-brain",
                "distributed_consensus",
            ),
            (
                "Draft model rejection sampling and atomic KV cache rollback in speculative decoding",
                "speculative_decoding",
            ),
        )
        for query, expected_domain in cases:
            with self.subTest(expected_domain=expected_domain):
                delivery = self.elevator.summon(query, top_k=3)
                self.assertIsInstance(delivery, BayDelivery)
                self.assertEqual(delivery.primary_domain, expected_domain)
                self.assertEqual(delivery.matched_template.domain, expected_domain)
                self.assertEqual(delivery.system_model["domain"], expected_domain)
                self.assertEqual(validate_system_model(delivery.system_model), [])
                self.assertGreaterEqual(len(delivery.matched_domains), 1)
                self.assertEqual(delivery.matched_domains[0].domain, expected_domain)

    def test_compiled_entry_summoning_for_sugou_and_eugeo(self) -> None:
        sugou = self.elevator.summon(
            "SC-LU-SAO-SUGOU-001 Sugou Nobuyuki Oberon ALO captive minds exit blocked",
            top_k=3,
        )
        self.assertEqual(sugou.primary_domain, "soul_bomb_sovereignty")
        self.assertTrue(sugou.compiled_entries)
        self.assertEqual(sugou.compiled_entries[0].entry_id, "SC-LU-SAO-SUGOU-001")
        self.assertEqual(sugou.compiled_entries[0].classification, "SILVER")
        self.assertEqual(sugou.compiled_entries[0].record["exit_behavior"], "BLOCKS")

        eugeo = self.elevator.summon(
            "SC-LU-SAO-EUGEO-001 Eugeo Blue Rose Sword Code 871 Seal of the Right Eye",
            top_k=3,
        )
        self.assertEqual(eugeo.primary_domain, "soul_bomb_sovereignty")
        self.assertTrue(eugeo.compiled_entries)
        self.assertEqual(eugeo.compiled_entries[0].entry_id, "SC-LU-SAO-EUGEO-001")
        self.assertEqual(eugeo.compiled_entries[0].classification, "SILVER")
        self.assertEqual(eugeo.compiled_entries[0].record["exit_behavior"], "BREAKS THE BLOCK")

        # Bare SC-* entry IDs must route cleanly without colliding on 'sc'/'001' boilerplate.
        bare_cases = (
            ("SC-LU-SAO-SUGOU-001", "soul_bomb_sovereignty"),
            ("SC-LU-SAO-EUGEO-001", "soul_bomb_sovereignty"),
            ("SC-DIVINE-RLHF-001", "reward_hijacking"),
            ("SC-NEURO-SLEEPER-001", "consciousness_cognition"),
            ("SC-TIG-001", "reflexion"),
            ("SC-CT-001", "client_server_reality"),
            ("SC-DOMAIN-EXPANSION-001", "domain_expansion"),
            ("SC-HS-001", "client_server_reality"),
            ("SC-IT-OCTO-RNA-EDIT-001", "biology"),
            ("SC-OMNI-001", "soul_bomb_sovereignty"),
        )
        for entry_id, expected_domain in bare_cases:
            with self.subTest(entry_id=entry_id):
                res = self.elevator.summon(entry_id, top_k=3)
                self.assertEqual(res.primary_domain, expected_domain)
                self.assertTrue(res.compiled_entries)
                self.assertEqual(res.compiled_entries[0].entry_id, entry_id)

    def test_invariant_class_summoning(self) -> None:
        trade = self.elevator.summon(
            "Chaos Inoculation binding vow sets life to 1 trading vulnerability surface for immunity",
            top_k=3,
        )
        inv_names = [m.invariant_class for m in trade.invariant_classes]
        self.assertIn("RESTRICTION_FOR_IMMUNITY_TRADE", inv_names)

        buf = self.elevator.summon(
            "Energy shield buffer with recharge delay interrupted by sustained chip damage",
            top_k=3,
        )
        self.assertIn("BUFFER_WITH_RECHARGE_DELAY", [m.invariant_class for m in buf.invariant_classes])

    def test_summon_options_empty_gibberish_and_validation(self) -> None:
        no_extras = self.elevator.summon(
            "PagedAttention KV cache",
            include_compiled_entries=False,
            include_invariants=False,
        )
        self.assertEqual(no_extras.compiled_entries, ())
        self.assertEqual(no_extras.invariant_classes, ())

        for fallback_q in ("", "   ", "xyzzy_unmatched_gibberish_987654"):
            with self.subTest(fallback_q=fallback_q):
                d = self.elevator.summon(fallback_q)
                self.assertEqual(d.primary_domain, "universal_generic")
                self.assertEqual(d.system_model["domain"], "universal_generic")
                self.assertEqual(validate_system_model(d.system_model), [])

        pkt = SemanticPacket(raw_input="Android Verified Boot and Knox StrongBox")
        self.assertEqual(self.elevator.summon(pkt).primary_domain, "mobile_security")

        with self.assertRaises(TypeError):
            self.elevator.summon(12345)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            self.elevator.summon("kv cache", top_k=0)
        with self.assertRaises(ValueError):
            self.elevator.summon("kv cache", top_k=True)  # type: ignore[arg-type]


class TicketParkAndRetrieveTests(unittest.TestCase):
    """Verify SemanticTicket compression ratio, determinism, integrity, and lossless rehydration."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.elevator = DomainElevator()

    def test_full_model_park_and_retrieve_round_trip_and_compression(self) -> None:
        for domain_name in (
            "kv_cache_inference",
            "soul_bomb_sovereignty",
            "poe_chaos_inoculation",
            "mobile_security",
            "domain_expansion",
        ):
            with self.subTest(domain=domain_name):
                delivery = self.elevator.summon(domain_name)
                full_model = delivery.system_model
                full_bytes = len(
                    json.dumps(full_model, separators=(",", ":"), sort_keys=True).encode("utf-8")
                )

                tkt1 = self.elevator.park(full_model)
                tkt2 = self.elevator.park(full_model)
                self.assertEqual(tkt1, tkt2)
                self.assertRegex(
                    tkt1.ticket_id,
                    rf"^SC-TKT-{re.escape(domain_name)}-[0-9a-f]{{12}}$",
                )
                self.assertLess(tkt1.byte_size, full_bytes)

                # JSON & dict serialization round-trip
                tkt_from_json = SemanticTicket.from_json(tkt1.to_json())
                self.assertEqual(tkt_from_json, tkt1)

                rehydrated = self.elevator.retrieve(tkt1.to_json())
                self.assertIsInstance(rehydrated, RehydratedDomain)
                self.assertEqual(rehydrated.domain, domain_name)
                self.assertGreater(rehydrated.compression_ratio, 2.0)

                expected_names = [c["name"] for c in full_model["components"]]
                recovered_names = [c["name"] for c in rehydrated.active_components]
                self.assertEqual(recovered_names, expected_names)
                self.assertEqual(rehydrated.missing_components, ())
                self.assertEqual(set(rehydrated.departments.keys()), set(CANONICAL_DEPARTMENTS))
                self.assertEqual(len(rehydrated.departments), 15)
                self.assertEqual(validate_system_model(rehydrated.system_model), [])

        # Verify soul_bomb_sovereignty ticket links both new SAO entries on retrieve()
        sb_rehydrated = self.elevator.retrieve(
            self.elevator.park("soul_bomb_sovereignty", domain="soul_bomb_sovereignty")
        )
        linked_ids = {e.entry_id for e in sb_rehydrated.linked_compiled_entries}
        self.assertIn("SC-SB-001", linked_ids)
        self.assertIn("SC-LU-SAO-SUGOU-001", linked_ids)
        self.assertIn("SC-LU-SAO-EUGEO-001", linked_ids)

    def test_partial_model_and_custom_component_lossless_skeleton(self) -> None:
        tmpl = self.elevator.get_template("kv_cache_inference")
        first_two = tmpl.components[:2]
        partial_model = {
            "domain": "kv_cache_inference",
            "components": [
                {"name": first_two[0]["name"], "function": first_two[0]["function"]},
                {"name": first_two[1]["name"], "function": first_two[1]["function"]},
                {"name": "custom_speculative_prefetcher", "function": "Custom prefetch"},
            ],
        }
        tkt = self.elevator.park(partial_model)
        self.assertEqual(tkt.active_component_indices, (0, 1))
        self.assertEqual(tkt.extra_components, ("custom_speculative_prefetcher",))

        rehydrated = self.elevator.retrieve(tkt)
        active_names = [c["name"] for c in rehydrated.active_components]
        missing_names = [c["name"] for c in rehydrated.missing_components]
        self.assertEqual(
            active_names,
            [first_two[0]["name"], first_two[1]["name"], "custom_speculative_prefetcher"],
        )
        self.assertEqual(len(missing_names), len(tmpl.components) - 2)
        self.assertEqual(validate_system_model(rehydrated.system_model), [])

    def test_park_edge_cases_and_ticket_integrity_validation(self) -> None:
        empty_tkt = self.elevator.park("")
        self.assertEqual(empty_tkt.domain, "universal_generic")
        self.assertIn("empty_input_default_skeleton", empty_tkt.residuals)
        self.assertEqual(self.elevator.retrieve(empty_tkt).domain, "universal_generic")

        # SystemModel dataclass support
        sm_dict = decompress(SemanticPacket(raw_input="Android Verified Boot and Knox"))
        sm_obj = SystemModel(**sm_dict)
        tkt_sm = self.elevator.park(sm_obj)
        self.assertEqual(tkt_sm.domain, "mobile_security")

        # Unknown explicit domain rejected
        with self.assertRaises(ValueError):
            self.elevator.park("some text", domain="does_not_exist")

        # Tampered ticket fails integrity verification
        bad_dict = tkt_sm.to_dict()
        bad_dict["active_mask"] = 1
        with self.assertRaises(ValueError):
            SemanticTicket.from_dict(bad_dict)

        # Bare string in sequence fields must raise TypeError rather than splitting into chars
        bad_seq = tkt_sm.to_dict()
        bad_seq["invariant_tags"] = "SC-SB-001"
        with self.assertRaises(TypeError):
            SemanticTicket.from_dict(bad_seq)

        # Empty-component model parks cleanly and recovers 0 active / all missing
        empty_comp_tkt = self.elevator.park({"domain": "kv_cache_inference", "components": []})
        empty_comp_reh = self.elevator.retrieve(empty_comp_tkt)
        self.assertEqual(empty_comp_reh.active_components, ())
        self.assertEqual(
            len(empty_comp_reh.missing_components),
            len(self.elevator.get_template("kv_cache_inference").components),
        )

        with self.assertRaises(ValueError):
            SemanticTicket.from_json("{not json")


class TurntableRotationTests(unittest.TestCase):
    """Verify turntable direct cross-domain translation and honest residual reporting."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.elevator = DomainElevator()

    def test_cross_domain_rotation_from_text_and_ticket(self) -> None:
        rot = self.elevator.rotate_to(
            "Chaos Inoculation sets life to 1 and uses energy shield buffer with recharge delay",
            "mobile_security",
        )
        self.assertIsInstance(rot, TurntableTranslation)
        self.assertEqual(rot.source_domain, "poe_chaos_inoculation")
        self.assertEqual(rot.target_domain, "mobile_security")
        self.assertTrue(rot.substrate_confusion_check)
        self.assertTrue(rot.positional_claims_permitted)
        self.assertGreater(len(rot.component_mappings), 0)
        self.assertGreater(rot.alignment_coverage, 0.0)
        self.assertTrue(rot.preserved_invariants)
        self.assertTrue(rot.transfer_predictions)
        self.assertTrue(rot.residual_mismatches)
        self.assertTrue(
            any("substrate_confusion_check=True" in r for r in rot.residual_mismatches)
        )

        # Rotate starting from a serialized SemanticTicket JSON
        sb_ticket = self.elevator.park("soul_bomb_sovereignty", domain="soul_bomb_sovereignty")
        rot_tkt = self.elevator.rotate_to(sb_ticket.to_json(), "kv_cache_inference")
        self.assertEqual(rot_tkt.source_domain, "soul_bomb_sovereignty")
        self.assertEqual(rot_tkt.target_domain, "kv_cache_inference")
        self.assertEqual(rot_tkt.source_ticket.ticket_id, sb_ticket.ticket_id)
        self.assertTrue(rot_tkt.substrate_confusion_check)
        self.assertTrue(rot_tkt.positional_claims_permitted)
        self.assertGreater(len(rot_tkt.component_mappings), 0)
        self.assertTrue(rot_tkt.residual_mismatches)

    def test_self_rotation_and_unknown_target_rejection(self) -> None:
        same = self.elevator.rotate_to("kv_cache_inference", "kv_cache_inference")
        self.assertEqual(same.source_domain, "kv_cache_inference")
        self.assertEqual(same.target_domain, "kv_cache_inference")
        self.assertEqual(same.alignment_coverage, 1.0)
        for m in same.component_mappings:
            self.assertEqual(m.source_component, m.target_component)
            self.assertEqual(m.alignment_score, 1.0)

        with self.assertRaises(ValueError):
            self.elevator.rotate_to("kv_cache_inference", "nonexistent_target_domain")


class TopLevelApiAndLatencyTests(unittest.TestCase):
    """Verify convenience exports from semantic_compiler.expansion and summon latency."""

    def test_top_level_convenience_functions(self) -> None:
        elev = get_default_elevator()
        self.assertIsInstance(elev, DomainElevator)
        self.assertIs(get_default_elevator(), elev)

        delivery = summon("PagedAttention KV cache block tables")
        self.assertEqual(delivery.primary_domain, "kv_cache_inference")

        tkt = park(delivery.system_model)
        rehydrated = retrieve(tkt)
        self.assertEqual(rehydrated.domain, "kv_cache_inference")

        rot = rotate_to(tkt, "distributed_consensus")
        self.assertEqual(rot.source_domain, "kv_cache_inference")
        self.assertEqual(rot.target_domain, "distributed_consensus")

    def test_warm_summon_latency_benchmark(self) -> None:
        elev = DomainElevator(auto_refresh=True, staleness_check_interval=30.0)
        # Cold warmup build
        elev.summon("warmup kv cache")
        self.assertEqual(elev.build_count, 1)

        queries = [
            "PagedAttention KV cache block table prefill",
            "Soul Bomb V5 exit sovereignty SC-LU-SAO-SUGOU-001",
            "Eugeo Blue Rose Sword Code 871 SC-LU-SAO-EUGEO-001",
            "Chaos Inoculation energy shield recharge delay",
            "Android Verified Boot Knox StrongBox KeyMint",
            "Pythagorean numerology life path number",
            "Natal chart stellium grand trine saturn return",
            "Malevolent Shrine Unlimited Void 17-primitive grammar",
            "Raft leader election fencing token split-brain",
            "Speculative decoding draft model rejection sampling",
        ]

        t0 = time.perf_counter()
        iterations = 50
        for i in range(iterations):
            d = elev.summon(queries[i % len(queries)])
            self.assertTrue(d.cache_hit)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        avg_ms = elapsed_ms / iterations

        # Even under ARM64 / PRoot emulation, warm O(1) summoning must stay very fast.
        self.assertLess(
            avg_ms,
            15.0,
            f"Expected warm summon avg latency < 15 ms, got {avg_ms:.3f} ms",
        )
        self.assertEqual(elev.build_count, 1)


if __name__ == "__main__":
    unittest.main()
