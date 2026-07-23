"""Typed Path of Exile buildcraft -> compute architecture ontology.

The mapping preserves composition relationships while explicitly rejecting
material identity. It separates topology, physical slots, equipped hardware,
software components, compatibility layers, and resource reservation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BuildcraftMapping:
    mapping_id: str
    layer: str
    source: str
    target: str
    triggers: tuple[str, ...]
    preserved_invariants: tuple[str, ...]
    residuals: tuple[str, ...]
    confidence: float

    def to_fractal_mapping(self) -> dict[str, object]:
        return {
            "mapping_id": self.mapping_id,
            "mapping_family": "BUILDCRAFT_COMPUTE_ONTOLOGY",
            "layer": self.layer,
            "source": self.source,
            "target": self.target,
            "source_frame": "path_of_exile_buildcraft",
            "target_frame": "compute_architecture",
            "source_scale": "SYSTEM",
            "target_scale": "SYSTEM",
            "source_substrate": "game_build_system",
            "target_substrate": "computer_hardware_and_software",
            "mapping_class": "STRUCTURAL_ANALOGY",
            "identity_claim_allowed": False,
            "preserved_invariants": list(self.preserved_invariants),
            "residuals": list(self.residuals),
            "guardrails": [
                "Preserve relationship grammar; do not claim literal identity.",
                "Classify software by deployed function, not artifact format alone.",
                "Retain physical constraints: lanes, bandwidth, latency, thermals, drivers, power, and memory.",
                STATIC_VS_DYNAMIC_GUARDRAIL,
            ],
            "scores": {
                "structural_fit": self.confidence,
                "functional_fit": self.confidence,
                "relationship_fit": self.confidence,
                "scale_transform_validity": 0.95,
            },
        }


COMMON_RESIDUALS = (
    "Path of Exile rules are designed abstractions; compute constraints are physical and measurable.",
    "A useful structural analogy does not make the compared substrates interchangeable.",
)


# Ontology-wide guardrail (founder note, 2026-07-23): PoE builds are static at
# craft time while inference stacks reconfigure per request, and PoE damage
# math is fully deterministic while hardware scheduling is not. Every mapping
# in this registry preserves optimization STRUCTURE (multiplicative stacking,
# diminishing returns, breakpoints) — never literal mechanics.
STATIC_VS_DYNAMIC_GUARDRAIL = (
    "PoE builds are static at craft time and PoE damage math is fully deterministic; "
    "inference stacks reconfigure per request and hardware scheduling is not. "
    "These mappings preserve optimization structure (multiplicative stacking, "
    "diminishing returns, breakpoints), not literal mechanics."
)


BUILDCRAFT_MAPPINGS: tuple[BuildcraftMapping, ...] = (
    BuildcraftMapping(
        "BUILD_001", "TOPOLOGY", "character equipment paper doll",
        "motherboard and chassis topology",
        ("character sheet", "paper doll", "equipment paper doll", "motherboard topology", "chassis topology"),
        (
            "a finite topology exposes typed positions for compatible components",
            "available positions constrain the reachable build",
            "the full configuration matters more than an isolated component",
        ), COMMON_RESIDUALS, 0.94,
    ),
    BuildcraftMapping(
        "BUILD_002", "PHYSICAL_SLOT", "weapon slot",
        "PCIe accelerator slot",
        ("pcie slot", "pcie slots", "weapon slot", "weapon slots", "accelerator slot"),
        (
            "the slot accepts a compatible high-output item",
            "slot count and lane topology constrain simultaneous accelerator loadouts",
            "equipping one item can displace another candidate item",
        ),
        (
            "PCIe slots differ by generation, lane width, spacing, power delivery, and bifurcation.",
            "Weapon slots do not model host-device transfer costs.",
        ), 0.97,
    ),
    BuildcraftMapping(
        "BUILD_003", "PHYSICAL_SLOT", "body-armour slot",
        "CPU socket or primary host-compute position",
        ("cpu slot", "cpu socket", "cpu sockets", "armor slot", "armour slot", "body armour slot", "body armor slot"),
        (
            "the slot hosts the central general-purpose item supporting the build",
            "the installed item defines broad compatibility and capacity constraints",
            "changing the host item can force dependent-component changes",
        ),
        (
            "CPU compatibility includes chipset, firmware, memory, power, and cooling.",
            "Most systems expose fewer CPU sockets than a game exposes armour positions.",
        ), 0.89,
    ),
    BuildcraftMapping(
        "BUILD_004", "EQUIPPED_HARDWARE", "equipped weapon",
        "GPU or accelerator device",
        ("gpu is a weapon", "gpus are weapons", "gpu weapon", "accelerator weapon", "actual weapon"),
        (
            "the equipped item carries the primary high-throughput execution path",
            "native item properties determine which workloads scale well",
            "the rest of the build is commonly planned around the main item",
        ),
        (
            "GPUs are general accelerators, not literal weapons.",
            "Performance depends on software, drivers, memory locality, and workload shape.",
        ), 0.96,
    ),
    BuildcraftMapping(
        "BUILD_005", "EQUIPPED_HARDWARE", "equipped body armour",
        "CPU package",
        ("cpu is armor", "cpu is armour", "cpu is body armor", "cpu is body armour", "cpus are armor", "cpus are armour"),
        (
            "the equipped item supplies broad always-available host capacity",
            "it carries control, resilience, orchestration, preprocessing, networking, and utility work",
            "its value includes constrained accelerator capacity that it releases",
        ),
        (
            "CPUs can run primary workloads and GPUs can run support workloads.",
            "The armour metaphor does not imply CPU work is passive or defensive only.",
        ), 0.93,
    ),
    BuildcraftMapping(
        "BUILD_006", "ITEM_CAPACITY", "item sockets and links",
        "hardware-provided workload capacity and integration topology",
        ("six link", "6 link", "10 link", "ten link", "gem slots", "linked sockets", "socketed hardware"),
        (
            "the item exposes finite capacity for attached capabilities",
            "links determine which capabilities cooperate in one execution chain",
            "item-native modifiers can act like additional implicit supports",
        ),
        (
            "VRAM and compute capacity are continuous resources rather than literal sockets.",
            "Software dependencies can form graphs more complex than linked gems.",
        ), 0.90,
    ),
    BuildcraftMapping(
        "BUILD_007", "SOFTWARE_COMPONENT", "active skill gem",
        "LLM or primary application workload",
        ("active skill gem", "llm is a gem", "model is a gem", "primary application"),
        (
            "the component defines the primary behavior produced by the setup",
            "it requires compatible runtime and hardware support",
            "its performance depends on linked modifiers and available resources",
        ), COMMON_RESIDUALS, 0.94,
    ),
    BuildcraftMapping(
        "BUILD_008", "SOFTWARE_COMPONENT", "support gem",
        "drafter, MTP, quantization runtime, cache layer, or inference framework",
        ("support gem", "support gems", "mtp", "speculative drafter", "quantization runtime", "cache layer", "inference framework", "vllm", "sglang"),
        (
            "the component modifies execution of the primary workload",
            "support value depends on compatibility with the main workload",
            "support consumes capacity while increasing throughput, efficiency, reach, or resilience",
        ),
        (
            "Some frameworks are foundational runtimes rather than optional supports.",
            "One package can occupy different roles in different deployments.",
        ), 0.91,
    ),
    BuildcraftMapping(
        "BUILD_009", "COMPATIBILITY_LAYER", "gem tags and attribute requirements",
        "CUDA, PyTorch, drivers, ABI, package, and runtime compatibility",
        ("cuda", "pytorch", "pypi", "compatibility tags", "gem tags", "runtime compatibility"),
        (
            "capabilities only compose when compatibility requirements are satisfied",
            "a powerful component can remain unusable in an incompatible environment",
            "version and platform constraints shape the legal build space",
        ),
        (
            "CUDA, PyTorch, and PyPI occupy different layers and must not be flattened into one thing.",
            "Compatibility failures can be partial, silent, or performance-only.",
        ), 0.90,
    ),
    BuildcraftMapping(
        "BUILD_010", "RESOURCE_RESERVATION", "mana reservation",
        "occupied VRAM and persistent accelerator-memory budget",
        ("vram is mana reservation", "vram allocation is mana reservation", "mana reservation", "reserve vram", "reserved vram"),
        (
            "a finite shared pool is committed before or during execution",
            "reserved capacity reduces what other active capabilities can coexist",
            "efficiency improvements increase the effective build envelope",
        ),
        (
            "VRAM allocation includes fragmentation, temporary buffers, KV cache, and runtime overhead.",
            "Mana reservation does not model memory bandwidth or transfer latency.",
        ), 0.98,
    ),
    BuildcraftMapping(
        "BUILD_011", "ARTIFACT_CLASSIFICATION", "gem, item, recipe, or build guide",
        "repository, application, package, model, or deployment profile classified by function",
        ("open source repo", "open source repos", "repository", "repositories", "github repo", "python package", "pypi package", "docker profile"),
        (
            "artifact format does not determine runtime role",
            "classification follows what the artifact contributes when deployed",
            "the same artifact may be a component, recipe, framework, or complete loadout",
        ),
        (
            "Repositories can contain many independently deployed artifacts.",
            "Disk presence alone does not imply runtime resource consumption.",
        ), 0.92,
    ),
    BuildcraftMapping(
        "BUILD_012", "SYSTEM_CONFIGURATION", "complete character build",
        "deployed compute architecture",
        ("reflexion of building", "complete build", "compute build", "architecture build", "path of building"),
        (
            "emergent behavior comes from constrained composition",
            "local component choices create system-level trade-offs",
            "planning tools compress a large configuration search space",
        ), COMMON_RESIDUALS, 0.96,
    ),
    BuildcraftMapping(
        "BUILD_013", "DELIVERY_RISK", "many builds before the league starter reaches maps",
        "architecture proliferation before a baseline product ships",
        ("twenty viable builds", "20 viable builds", "league starter reaches maps", "before reaching maps", "too many builds"),
        (
            "option generation can outpace validation and delivery",
            "the baseline must reach a proving environment before alternatives dominate attention",
            "interesting branches can crowd out the critical shipping path",
        ), COMMON_RESIDUALS, 0.97,
    ),
    BuildcraftMapping(
        "BUILD_014", "PREMIUM_ITEM", "mirror-tier pseudo-ten-link bow",
        "RTX PRO 6000 Blackwell 96 GB-class accelerator",
        ("rtx pro 6000", "blackwell 96 gb", "mirror-tier 10 link bow", "10 link bow", "ten link bow"),
        (
            "premium native capacity enables unusually dense workload composition",
            "item-native capabilities act like implicit support links",
            "the surrounding architecture is planned around the scarce high-value component",
        ),
        (
            "Market price and game rarity are rhetorical comparisons, not valuation models.",
            "Accelerator capability remains bounded by software support, power, cooling, bandwidth, and workload fit.",
        ), 0.95,
    ),
    # Founder eureka 2026-07-23 (BUILD_015-BUILD_018).
    BuildcraftMapping(
        "BUILD_015", "CHASSIS_PRESENTATION", "character selection screen",
        "PC case / chassis as outward presentation of the build",
        ("character selection screen", "character select screen", "character select", "pc case", "computer case", "case is the character selection"),
        (
            "the vessel chosen at creation frames everything equipped afterward",
            "outward presentation communicates the build without changing its mechanics",
            "form factor constrains which components, cooling, and layout configurations fit",
        ),
        (
            "A character selection screen is a one-time irreversible choice; a case can be swapped without rebuilding the system.",
            "Case aesthetics carry no performance effect; character presentation can carry mechanical identity.",
        ), 0.90,
    ),
    BuildcraftMapping(
        "BUILD_016", "IDENTITY_BASE", "race / base class",
        "motherboard as the chassis of identity (socket types, inherent attributes, expansion ceilings)",
        ("motherboard is the race", "motherboard race", "race and base class", "race / base class", "base class", "socket types", "expansion ceilings"),
        (
            "the base determines socket types: CPU socket, PCIe topology, and RAM channels",
            "equipped items inherit constraints from the base rather than redefining it",
            "gear upgrades stay bounded by the base's inherent attributes and expansion ceilings",
        ),
        (
            "Race or base class is fixed at character creation; motherboards are replaceable hardware.",
            "The motherboard is also physical topology (BUILD_001); this facet maps identity and ceilings, not layout.",
        ), 0.92,
    ),
    BuildcraftMapping(
        "BUILD_017", "SOFTWARE_COMPONENT", "Greater Multiple Projectiles support gem",
        "MTP (multi-token prediction) speculative drafting",
        ("multi-token prediction", "greater multiple projectiles", "gmp", "multi-projectile support", "multiple projectiles support", "acceptance rate is accuracy", "speculative decoding acceptance"),
        (
            "the support fires additional units at reduced per-unit effectiveness: GMP fires additional projectiles at reduced per-projectile damage; MTP drafts additional tokens at reduced per-token acceptance",
            "net gain exists only while the hit rate holds: accuracy rating for projectiles, acceptance rate for drafted tokens",
            "speculative-decoding acceptance rate plays the exact role of accuracy rating; both are the same breakpoint math",
        ),
        (
            "GMP's damage penalty is a fixed multiplier; MTP acceptance is probabilistic and workload-dependent.",
            "Projectile count is exact and simultaneous; drafted-token count and tree shape vary by implementation.",
        ), 0.93,
    ),
    BuildcraftMapping(
        "BUILD_018", "PREMIUM_ITEM", "Mirror-of-Kalandra-tier item",
        "mirror-tier hardware (e.g., RTX PRO 6000 96GB-class flagship)",
        ("mirror-tier gpu", "mirror tier gpu", "mirror-tier hardware", "mirror of kalandra", "mirror-of-kalandra", "mirror-tier item", "perfect roll", "no upgrade path"),
        (
            "the item sits at the ceiling of the current league/budget with no upgrade path",
            "a perfect roll ends the optimization search for that slot",
            "the rest of the build is planned around owning the ceiling item",
        ),
        (
            "Mirror-tier rarity is an in-game economic construct; flagship hardware is expensive but purchasable.",
            "Hardware ceilings move with each product generation; a mirrored item stays perfect within its league.",
        ), 0.94,
    ),
)


def get_buildcraft_mapping(mapping_id: str) -> BuildcraftMapping | None:
    return next((mapping for mapping in BUILDCRAFT_MAPPINGS if mapping.mapping_id == mapping_id), None)
