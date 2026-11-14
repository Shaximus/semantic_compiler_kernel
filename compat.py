"""Entry-point wrapper that keeps decision-dependent outputs consistent (from Kestrel Lab).

Origin: the ``kestrel/lab-3cycle`` branch (commit 053f518, 2026-07-15), written against
V2.1.3. Its three-cycle report left runtime verification pending; the defects were
reproduced and the wrapper first executed against V3.0.0 on 2026-11-06 (see
``docs/kestrel/Kestrel_Lab_3_Cycle_Report.md``).

``core/pipeline.py`` is under the V3.0.0 freeze, so the fixes live here instead of in the
pipeline, and ``semantic_compiler.compile_semantic_packet`` is this function.

What it fixes
-------------
1. **Stale decision-dependent derivatives.** The pipeline builds the routing packet and the
   literal, public and executive translations in Stages 7 and 8, before Stage 9 decides.
   They therefore carry ``decision: PENDING`` (or none) while the packet carries the real
   decision, and the dataset row embeds those translations. After the core pipeline returns,
   this wrapper rebuilds them from the final decision, then rebuilds the artifacts that
   embed them (dataset tier and row, SFT export, audit record).
2. **Sensitive input echoed into the SFT prompt.** For ``SENSITIVE`` and ``CRITICAL``
   packets ``build_qwen_sft_output`` labels the prompt ``Compile (redacted):`` and then
   still interpolates the full raw input. The wrapper redacts that prompt.

The wrapper is pure post-processing: it never re-runs extraction, gates or scoring, and it
never changes the decision the pipeline returned.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from semantic_compiler.core.packet import SemanticPacket
from semantic_compiler.core.pipeline import compile_semantic_packet as _core_compile
from semantic_compiler.core.dataset import (
    build_dataset_row,
    classify_dataset_tier,
    build_qwen_sft_output,
)
from semantic_compiler.core.audit import build_audit_record
from semantic_compiler.translation import build_translations


def compile_semantic_packet(
    text: str,
    *,
    context: Optional[Dict[str, Any]] = None,
    mode: Optional[str] = None,
) -> SemanticPacket:
    """Public entry point. Runs the frozen core pipeline, then reconciles the
    decision-dependent artifacts so they match the final decision.
    """
    packet = _core_compile(text, context=context, mode=mode)

    # Rebuild translations from the final decision
    translations = build_translations(packet)
    packet.literal_translation = translations.get("literal")
    packet.public_translation = translations.get("public")
    packet.executive_translation = translations.get("executive")

    # Rebuild dataset artifacts
    packet.dataset_tier = classify_dataset_tier(packet)
    packet.dataset_row = build_dataset_row(packet)
    packet.sft_output = build_qwen_sft_output(packet)
    packet.audit_record = build_audit_record(packet)

    return packet
