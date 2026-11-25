"""Row-level training_ready must not stay true when schema validation fails."""

from __future__ import annotations

from semantic_compiler import compile_semantic_packet
from semantic_compiler.core import dataset as dataset_mod
from semantic_compiler.core.types import Decision

# Exact Kernel Mobile prompt 06, already observed COMPILED + training_ready
# + schema_valid on this tip. Used only to obtain such a packet.
_COMPILED_INPUT = 'PagedAttention and RadixAttention share KV cache block tables during prefill-decode disaggregation, while an unbounded agentic loop repeats failing tool-calling turns and an untrusted MCP tool output tries to smuggle privileged shell commands. Meanwhile an Android device team is moving a kernel monitor\'s key generation out of the normal world and adding a secure-world runtime monitor, and a clinic is redesigning therapy intake so diagnosis happens before paperwork. The GPU is treated as the weapon; support gems consume VRAM; PCIe slots are weapon slots. Climate claims that "it snowed yesterday, therefore climate change is a hoax and the system needs no regulation" must be checked for category errors, missing evidence, and authority leakage before any routing decision.\n'


def test_training_ready_implies_schema_valid_on_compiled_row() -> None:
    packet = compile_semantic_packet(_COMPILED_INPUT)
    assert packet.decision in (
        Decision.COMPILED,
        Decision.COMPILED_WITH_GUARDRAILS,
        Decision.COMPILED_SUPERVISED_ONLY,
    )
    row = dataset_mod.build_dataset_row(packet)
    assert row["quality"]["training_ready"] is True
    assert row["audit"]["schema_valid"] is True


def test_invalid_schema_clears_row_and_mapping_training_ready(monkeypatch) -> None:
    packet = compile_semantic_packet(_COMPILED_INPUT)
    good = dataset_mod.build_dataset_row(packet)
    assert good["audit"]["schema_valid"] is True
    assert good["quality"]["training_ready"] is True
    assert any(
        mapping.get("training_ready")
        for mapping in good["isomorphism_analysis"]["mappings"]
    )

    def _force_invalid(_row):
        return {"valid": False, "errors": ["forced schema invalid for test"]}

    monkeypatch.setattr(dataset_mod, "validate_dataset_row", _force_invalid)
    bad = dataset_mod.build_dataset_row(packet)
    assert bad["audit"]["schema_valid"] is False
    assert bad["quality"]["training_ready"] is False
    for mapping in bad["isomorphism_analysis"]["mappings"]:
        assert mapping.get("training_ready") is False
