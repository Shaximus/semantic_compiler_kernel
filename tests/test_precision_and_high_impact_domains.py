"""Regression & contract tests for V3.1.1 precision fixes and high-impact domains."""
from __future__ import annotations

import unittest

from semantic_compiler.core.pipeline import compile_semantic_packet, resolve_mode
from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.core.types import CompilerMode, Decision, MappingClass, ScaleType, ScaleTransform
from semantic_compiler.expansion import _infer_domain, decompress
from semantic_compiler.expansion.corpus import compile_corpus
from semantic_compiler.expansion.counter_mapping import Disconfirmation
from semantic_compiler.expansion.evidence_tiers import EvidenceTier
from semantic_compiler.expansion.isomorphism.overlay import MEDICAL_TO_UNIVERSAL, UNIVERSAL_FUNCTIONS
from semantic_compiler.expansion.ontology.medical_ontology import MEDICAL_ONTOLOGY
from semantic_compiler.expansion.pathology import detect_pathologies
from semantic_compiler.expansion.registry import get_template
from semantic_compiler.extraction.claims import classify_claim_types
from semantic_compiler.extraction.evidence import EVIDENCE_PRIORITY
from semantic_compiler.extraction.frames import detect_source_frames
from semantic_compiler.extraction.relationships import extract_relationships
from semantic_compiler.extraction.skeleton import extract_structural_skeleton
from semantic_compiler.gates.boundaries import check_boundary_preservation
from semantic_compiler.gates.causality import separate_causality_from_analogy
from semantic_compiler.gates.contradiction_repair import classify_semantic_error
from semantic_compiler.gates.scale import enforce_scale_separation


class PrecisionFixesTests(unittest.TestCase):
    def test_resolve_mode_honors_claim_type_key(self) -> None:
        pkt = SemanticPacket(
            raw_input="At every scale, cellular immunity mirrors network firewalls.",
            claim_types=[{"claim_type": "FRACTAL_ISOMORPHISM", "confidence": 0.85}],
        )
        self.assertEqual(resolve_mode(pkt), CompilerMode.FRACTAL_ISOMORPHISM_MAPPING)

    def test_contradiction_gate_avoids_benign_technical_false_positives(self) -> None:
        benign_inputs = [
            "The scheduler will validate leases because redundancy is required.",
            "Lazy evaluation defers allocation so the pipeline remains bounded.",
            "A plasma electron occupies an excited state due to photon absorption.",
            "The system is not literally a biological organism.",
        ]
        for text in benign_inputs:
            pkt = SemanticPacket(raw_input=text)
            self.assertIsNone(
                classify_semantic_error(pkt),
                f"Unexpected semantic error for benign technical text: {text}",
            )

    def test_causality_gate_handles_empty_and_string_declared_class(self) -> None:
        empty_res = separate_causality_from_analogy({"fractal_mappings": []})
        self.assertFalse(empty_res["analogy_only"])
        self.assertEqual(empty_res["gate_status"], "PASSED")

        str_res = separate_causality_from_analogy({
            "fractal_mappings": [
                {
                    "source_scale": "cellular",
                    "target_scale": "computer",
                    "declared_class": "CAUSAL_MAPPING",
                    "preserved_invariants": ["Function: SECURITY"],
                    "residuals": ["Different substrate"],
                }
            ],
            "evidence_inventory": [],
        })
        self.assertTrue(str_res["any_gate_failure"])
        self.assertEqual(str_res["gate_status"], "FAILED")

    def test_scale_gate_resolves_fractal_aliases(self) -> None:
        res = enforce_scale_separation({
            "fractal_mappings": [
                {
                    "source": "cell",
                    "target": "cosmos",
                    "source_scale": "cell",
                    "target_scale": "cosmos",
                    "preserved_invariants": [],
                    "changed_variables": [],
                }
            ]
        })
        self.assertEqual(res["gate_status"], "FAILED")

    def test_boundary_gate_groups_duplicates_and_string_strengths(self) -> None:
        res = check_boundary_preservation(
            source_boundaries=[
                {"type": "security", "strength": "strict"},
                {"type": "security", "strength": "medium"},
            ],
            target_boundaries=[
                {"type": "security", "strength": "weak"},
            ],
        )
        self.assertFalse(res["gate_passed"])
        self.assertEqual(len(res["violations"]), 2)

    def test_extraction_word_boundaries_and_negation(self) -> None:
        frames = detect_source_frames("The frame captures a threshold.")
        self.assertNotIn("computation", frames)
        self.assertNotIn("computation?", frames)
        self.assertNotIn("organizational?", frames)

        claims = classify_claim_types("Semantics define the boundary.")
        types = {c["claim_type"] for c in claims}
        self.assertNotIn("DEFINITION", types)

        self.assertIn("measurement", EVIDENCE_PRIORITY)
        self.assertIn("recollection", EVIDENCE_PRIORITY)
        self.assertIn("generic_prior", EVIDENCE_PRIORITY)

        pkt = SemanticPacket(raw_input="The firewall does not block authorized packets.")
        skel = extract_structural_skeleton(pkt)
        pkt.structural_skeleton = skel
        rels = extract_relationships(pkt)
        self.assertEqual(rels, [])


class ExpansionAndHighImpactDomainsTests(unittest.TestCase):
    NEW_DOMAINS = (
        "agentic_tool_orchestration",
        "capability_isolation",
        "formal_verification",
        "sovereign_local_mesh",
    )

    def test_all_medical_ontology_keys_mapped(self) -> None:
        for key in MEDICAL_ONTOLOGY:
            self.assertIn(key, MEDICAL_TO_UNIVERSAL)
            self.assertIn(MEDICAL_TO_UNIVERSAL[key], UNIVERSAL_FUNCTIONS)

    def test_healthy_templates_have_zero_component_failure_overlap_or_false_pathologies(self) -> None:
        for domain in (
            "bluetooth",
            "input_semantic_adapter",
            "reward_hijacking",
            "client_server_reality",
            "consciousness_cognition",
            *self.NEW_DOMAINS,
        ):
            tmpl = get_template(domain)
            comp_maps = {c.get("medical_map") for c in tmpl.components if c.get("medical_map")}
            fm_maps = {f.get("medical_map") for f in tmpl.failure_modes if f.get("medical_map")}
            self.assertTrue(
                comp_maps.isdisjoint(fm_maps),
                f"{domain} overlaps component and failure_mode medical_maps: {comp_maps & fm_maps}",
            )
            healthy_model = {"components": tmpl.components, "relationships": tmpl.relationships}
            pathologies = detect_pathologies(healthy_model, tmpl)
            self.assertEqual(
                pathologies,
                [],
                f"{domain} healthy components triggered false pathologies: {[p.name for p in pathologies]}",
            )

    def test_high_impact_domains_route_and_decompress_cleanly(self) -> None:
        prompts = {
            "agentic_tool_orchestration": (
                "An agentic loop orchestration runtime enforces JSON tool schema validation, "
                "approval gates, and a bounded tool budget for MCP server calls."
            ),
            "capability_isolation": (
                "An object capability sandbox eliminates ambient authority and confused deputy bugs "
                "using Capsicum handles, seccomp-bpf filters, and monotonic attenuation."
            ),
            "formal_verification": (
                "Formal verification pairs TLA+ temporal model checking with a Z3 SMT solver engine "
                "to prove loop invariant and safety invariant preservation."
            ),
            "sovereign_local_mesh": (
                "A sovereign mesh connects workstations and handhelds via Tailscale userspace tunnels, "
                "wireproxy SOCKS5 proxies, split-horizon resolution, and a local inference gateway."
            ),
        }
        for domain, prompt in prompts.items():
            pkt = SemanticPacket(raw_input=prompt)
            self.assertEqual(_infer_domain(pkt), domain)
            model = decompress(pkt)
            self.assertEqual(model["domain"], domain)
            self.assertEqual(model["pathology_profile"]["detected_pathologies"], [])

    def test_compile_semantic_packet_runs_on_new_domains(self) -> None:
        pkt = compile_semantic_packet(
            "Formal verification proves loop invariants are preserved across state transitions."
        )
        self.assertNotEqual(pkt.decision, Decision.REJECT)


if __name__ == "__main__":
    unittest.main()
