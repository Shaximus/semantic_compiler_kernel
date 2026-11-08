"""Task 12: Integration tests for cross-domain reconstruction.

Verifies that `decompress()` reconstructs a target-domain system model from
cross-domain analogies ("X is like Y"), preserving the medical-ontology
mappings across the domain boundary.

NOTE: the task-12 brief constructs the packet as
`SemanticPacket(input_text=...)`, but the frozen V2.1.3 core packet stores
input text in `raw_input` (there is no `input_text` field). These tests use
`raw_input=` verbatim text otherwise unchanged from the brief.
"""

from semantic_compiler.expansion import decompress
from semantic_compiler.core.packet import SemanticPacket


def test_biology_to_computation_reconstruction():
    packet = SemanticPacket(raw_input="A network firewall is like a cell membrane")
    model = decompress(packet)
    assert model["domain"] == "computation"
    assert any(c["medical_map"] == "immune_boundary" for c in model["components"])


def test_biology_to_corporate_reconstruction():
    # Same direction as the firewall test above: the subject (X in "X is like Y")
    # is the target system, and the biological mapping carries across onto it.
    packet = SemanticPacket(
        raw_input="A corporate legal department is like an immune system"
    )
    model = decompress(packet)
    assert model["domain"] == "corporate"
    legal = next(c for c in model["components"] if c["name"] == "legal_compliance")
    assert legal["medical_map"] == "immune_system"
