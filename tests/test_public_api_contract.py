"""Contract tests for the documented public API (README Quick Start).

These tests pin imports and the ``compile_semantic_packet`` signature so a
bolt-in add-on can depend on the documented surface. They do not pin a
specific ``Decision`` value: short prompts may return ``NEEDS_REVISION``.
"""

from __future__ import annotations

import inspect
import unittest

import semantic_compiler
from semantic_compiler import (
    AuthorityType,
    ClaimType,
    CompilerMode,
    DatasetTier,
    Decision,
    MappingClass,
    RelationshipType,
    ScaleType,
    SemanticPacket,
    compile_semantic_packet,
)
from semantic_compiler.core.packet import COMPILER_VERSION

EXPECTED_EXPORTS = (
    "compile_semantic_packet",
    "SemanticPacket",
    "ClaimType",
    "RelationshipType",
    "ScaleType",
    "AuthorityType",
    "CompilerMode",
    "Decision",
    "MappingClass",
    "DatasetTier",
)


class PublicApiContractTests(unittest.TestCase):
    def test_package_all_exports_are_importable(self) -> None:
        self.assertEqual(tuple(semantic_compiler.__all__), EXPECTED_EXPORTS)
        for name in EXPECTED_EXPORTS:
            with self.subTest(name=name):
                self.assertTrue(hasattr(semantic_compiler, name), name)
                self.assertIs(getattr(semantic_compiler, name), globals()[name])

    def test_version_is_compiler_version(self) -> None:
        self.assertEqual(semantic_compiler.__version__, COMPILER_VERSION)
        self.assertIsInstance(COMPILER_VERSION, str)
        self.assertTrue(COMPILER_VERSION)

    def test_compile_semantic_packet_signature(self) -> None:
        sig = inspect.signature(compile_semantic_packet)
        self.assertEqual(
            list(sig.parameters),
            ["input_text", "registry", "context", "mode"],
        )
        params = sig.parameters
        self.assertIsNone(params["registry"].default)
        self.assertIsNone(params["context"].default)
        self.assertEqual(params["mode"].default, "AUTO")
        # With from __future__ import annotations the annotation may be a string.
        ret = sig.return_annotation
        if isinstance(ret, str):
            self.assertEqual(ret, "SemanticPacket")
        else:
            self.assertIs(ret, SemanticPacket)

    def test_readme_compile_example_returns_versioned_packet(self) -> None:
        pkt = compile_semantic_packet(
            "The GPU is the weapon; support gems consume VRAM."
        )
        self.assertIsInstance(pkt, SemanticPacket)
        self.assertEqual(pkt.version, COMPILER_VERSION)
        self.assertEqual(pkt.raw_input, "The GPU is the weapon; support gems consume VRAM.")
        # README prints these attributes; do not pin the Decision itself.
        self.assertTrue(hasattr(pkt, "decision"))
        self.assertTrue(hasattr(pkt, "dataset_tier"))
        self.assertIsNotNone(pkt.decision)
        self.assertIsNotNone(pkt.dataset_tier)

    def test_readme_decompress_example_runs_offline(self) -> None:
        from semantic_compiler.expansion import decompress

        pkt = compile_semantic_packet(
            "PagedAttention and RadixAttention share KV cache block tables during prefill."
        )
        model = decompress(pkt)
        self.assertIsInstance(model, dict)
        self.assertIn("domain", model)
        self.assertTrue(model["domain"])

    def test_other_readme_quick_start_imports_resolve(self) -> None:
        from semantic_compiler.expansion.consciousness import (
            detect_category_error,
            evaluate_alignment,
        )
        from semantic_compiler.expansion.consciousness.client_server import (
            LAYER_STACK,
            evaluate_prayer_protocol,
        )
        from semantic_compiler.expansion.corpus import compile_corpus
        from semantic_compiler.translation import resolve_buildcraft_mappings

        self.assertTrue(callable(detect_category_error))
        self.assertTrue(callable(evaluate_alignment))
        self.assertTrue(callable(evaluate_prayer_protocol))
        self.assertTrue(LAYER_STACK)
        self.assertTrue(callable(resolve_buildcraft_mappings))
        self.assertTrue(callable(compile_corpus))




class ApiFacadeContractTests(unittest.TestCase):
    """Pin the compact ``semantic_compiler.api`` surface added for hosted MCP/HTTP."""

    def test_api_module_exports(self) -> None:
        from semantic_compiler import api

        self.assertEqual(
            tuple(api.__all__),
            ("SUMMARY_SCHEMA", "compile_json", "summary_v1"),
        )
        self.assertEqual(api.SUMMARY_SCHEMA, "summary_v1")
        self.assertTrue(callable(api.compile_json))
        self.assertTrue(callable(api.summary_v1))

    def test_compile_json_signature(self) -> None:
        from semantic_compiler.api import compile_json

        sig = inspect.signature(compile_json)
        self.assertEqual(
            list(sig.parameters),
            ["text", "registry", "context", "mode", "include_raw_input"],
        )
        params = sig.parameters
        self.assertIsNone(params["registry"].default)
        self.assertIsNone(params["context"].default)
        self.assertEqual(params["mode"].default, "AUTO")
        self.assertIs(params["include_raw_input"].default, False)
        self.assertEqual(params["include_raw_input"].kind, inspect.Parameter.KEYWORD_ONLY)

    def test_compile_json_returns_summary_v1_without_raw_input(self) -> None:
        from semantic_compiler.api import SUMMARY_SCHEMA, compile_json, summary_v1
        from semantic_compiler.core.packet import COMPILER_VERSION

        text = "The GPU is the weapon; support gems consume VRAM."
        summary = compile_json(text)
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary["schema"], SUMMARY_SCHEMA)
        self.assertEqual(summary["version"], COMPILER_VERSION)
        self.assertIn(summary["decision"], Decision.__members__)
        self.assertNotIn("raw_input", summary)
        self.assertNotIn("normalized_input", summary)
        self.assertNotIn("forward_text", summary)
        self.assertNotIn(text, str(summary))

        packet = compile_semantic_packet(text)
        from_packet = summary_v1(packet)
        self.assertEqual(from_packet["decision"], summary["decision"])
        self.assertEqual(from_packet["version"], summary["version"])
        self.assertEqual(from_packet["selected_target"], summary["selected_target"])

    def test_api_is_not_a_top_level_export(self) -> None:
        # Keep the README export tuple stable; hosts import semantic_compiler.api.
        self.assertNotIn("compile_json", semantic_compiler.__all__)
        self.assertNotIn("summary_v1", semantic_compiler.__all__)


if __name__ == "__main__":
    unittest.main()
