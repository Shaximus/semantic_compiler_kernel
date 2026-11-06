"""Entry-point wrapper that keeps decision-dependent outputs consistent (from Kestrel Lab).

Origin: the \`\`kestrel/lab-3cycle\`\` branch (commit 053f518, 2026-07-15), written against
V2.1.3. Its three-cycle report left runtime verification pending; the defects were
reproduced and the wrapper first executed against V3.0.0 on 2026-11-06 (see
\`\`docs/kestrel/Kestrel_Lab_3_Cycle_Report.md\`\`).

\`\`core/pipeline.py\`\` is under the V3.0.0 freeze, so the fixes live here instead of in the
pipeline, and \`\`semantic_compiler.compile_semantic_packet\`\` is this function.

What it fixes
-------------
1. **Stale decision-dependent derivatives.** The pipeline builds the routing packet and the
   literal, public and executive translations in Stages 7 and 8, before Stage 9 decides.
   They therefore carry \`\`decision: PENDING\`\` (or none) while the packet carries the real
   decision, and the dataset row embeds those translations. After the core pipeline returns,
   this wrapper rebuilds them from the final decision, then rebuilds the artifacts that
   embed them (dataset tier and row, SFT export, audit record).
2. **Sensitive input echoed into the SFT prompt.** For \`\`SENSITIVE\`\` and \`\`CRITICAL\`\`
   packets \`\`build_qwen_sft_output\`\` labels the prompt \`\`Compile (redacted):\`\` and then
   appends the raw text. The wrapper replaces user messages for those packets with a
   SHA-256 provenance marker. The default-deny \`\`qwen_sft_ready\`\` result is unchanged.

What it deliberately does not do
--------------------------------
* It does not change scoring, the decision, or any gate: only artifacts built *from* the
  final decision are rebuilt.
* Packets that exit early (no target system resolved) never built a routing packet or
  translations, so nothing is stale and nothing is invented for them.
* Callers that import \`\`compile_semantic_packet\`\` from \`\`semantic_compiler.core.pipeline\`\`
  directly still get the unwrapped behavior (scripts, \`\`expansion.corpus\`\`). Kestrel's own
  recommendation was to move this logic into \`\`core/pipeline.py\`\` once the freeze allows;
  this module then becomes a re-export.
"""
from __future__ import annotations

from semantic_compiler.core.audit import build_audit_record
from semantic_compiler.core.dataset import _classify_tier, build_dataset_row
from semantic_compiler.core.pipeline import (
    build_qwen_sft_output,
    build_routing_packet,
    compile_semantic_packet as _compile,
    generate_executive_translation,
    generate_literal_translation,
    generate_public_translation,
)
from semantic_compiler.core.types import PrivacySensitivity

_REDACTED_PRIVACY_LEVELS = frozenset({PrivacySensitivity.SENSITIVE, PrivacySensitivity.CRITICAL})


def _redact_sensitive_qwen_user_content(packet) -> None:
    """Ensure sensitive raw text never survives in the exported SFT user prompt."""
    if packet.privacy_sensitivity not in _REDACTED_PRIVACY_LEVELS:
        return
    digest = packet.compute_input_hash()
    for message in packet.qwen_sft_output.get("messages", []):
        if message.get("role") == "user":
            message["content"] = f"Compile (redacted input; sha256={digest})"


def _rebuild_decision_derivatives(packet) -> None:
    """Rebuild outputs derived from the final decision, in dependency order."""
    # Early exits (no target system) never built a routing packet or translations, so there
    # is nothing stale to refresh and nothing is invented for them.
    if packet.routing_packet:
        packet.routing_packet = build_routing_packet(packet)
        packet.route_to = list(packet.routing_packet.get("route_to", []))
        packet.literal_translation = generate_literal_translation(packet)
        packet.public_translation = generate_public_translation(packet)
        packet.executive_translation = generate_executive_translation(packet)

    # core.pipeline._finalize_packet builds the dataset row *before* the SFT export, and
    # compile_semantic_packet sets status "compiled" only after that, so the row it stores has
    # an empty SFT payload and status DRAFT. The corpus scripts work around that by calling
    # build_dataset_row(packet) again after compiling. Do the same here, and redact the SFT
    # export first so the copy embedded in the row is the redacted one.
    packet.dataset_tier = _classify_tier(packet)
    packet.qwen_sft_output = build_qwen_sft_output(packet)
    _redact_sensitive_qwen_user_content(packet)
    packet.dataset_row = build_dataset_row(packet)
    packet.audit = build_audit_record(packet)
    packet.mark_compilation_end()


def compile_semantic_packet(input_text, registry=None, context=None, mode="AUTO"):
    """Compile, then make every decision-dependent output reflect the final decision."""
    packet = _compile(input_text, registry=registry, context=context, mode=mode)
    _rebuild_decision_derivatives(packet)
    return packet
