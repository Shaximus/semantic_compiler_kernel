"""SC-TOL-001 fixture registry: the eight corpus systems of the t608u thread, with provenance.

Every fixture carries a provenance record. ``provenance_status`` is honest about what
was checked in this repository:

- ``NAMED_IN_SOURCE_NOT_OPENED``: the text is named in the material Shax supplied and is a
  standard reference, but the compiler did not open it for this entry.
- ``NEEDS_PER_TEXT_PROVENANCE``: the source thread itself says the attribution is not settled.
  These fixtures register their source as unverified, so T0 blocks them until a per-text record exists.
- ``SPECULATIVE_PROPOSAL``: a hypothetical architecture from the thread; there is no source to verify.

The thread's citation stubs ("Nature +3", "OUP Academic", "World-Tree Project +1" and the
others) are not treated as sources. Graph shapes are compiler modelling choices, recorded per
fixture; they are not claims about what a tradition "really" contains.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tests.reference.sc_tol_001.compiler import (
    EpistemicTier,
    HorizonBoundary,
    MetaArchitectureSpec,
    MetaGenerator,
    SourceRecord,
    SubstrateSpec,
    SystemState,
    TopologyClass,
)

NAMED = "NAMED_IN_SOURCE_NOT_OPENED"
NEEDS = "NEEDS_PER_TEXT_PROVENANCE"
SPEC = "SPECULATIVE_PROPOSAL"


@dataclass(frozen=True)
class Provenance:
    source_id: str
    tier: EpistemicTier
    citation: str
    provenance_status: str
    modelling_note: str


@dataclass
class Fixture:
    key: str
    provenance: Provenance
    state: SystemState
    expectations: dict = field(default_factory=dict)


def _state(prov: Provenance, verified: bool, **kw) -> SystemState:
    return SystemState(
        source_id=prov.source_id,
        require_registered_provenance=True,
        source_registry={prov.source_id: SourceRecord(prov.source_id, prov.tier, prov.citation, verified=verified)},
        epistemic_tier=prov.tier,
        **kw,
    )


# Kircher's 1652 layout (Oedipus Aegyptiacus): one of several historical layouts of the
# ten Sefirot with 22 paths. Used here as a modelling choice only; it is NOT attributed to
# Sefer Yetzirah, the Zohar or Lurianic texts (t608u rc1 audit: per-text provenance needed).
SEFIROT_KIRCHER_22 = (
    ("keter", "chokhmah"), ("keter", "binah"), ("keter", "tiferet"),
    ("chokhmah", "binah"), ("chokhmah", "tiferet"), ("chokhmah", "chesed"),
    ("binah", "tiferet"), ("binah", "gevurah"),
    ("chesed", "gevurah"), ("chesed", "tiferet"), ("chesed", "netzach"),
    ("gevurah", "tiferet"), ("gevurah", "hod"),
    ("tiferet", "netzach"), ("tiferet", "yesod"), ("tiferet", "hod"),
    ("netzach", "hod"), ("netzach", "yesod"), ("netzach", "malkhut"),
    ("hod", "yesod"), ("hod", "malkhut"),
    ("yesod", "malkhut"),
)


def build_fixtures() -> dict[str, Fixture]:
    f: dict[str, Fixture] = {}

    p = Provenance("src:yggdrasil", EpistemicTier.CORPUS_MYTH,
                   "Poetic Edda (Voluspa, Grimnismal); Prose Edda (Gylfaginning)", NAMED,
                   "Three roots joined at one trunk that carries the realms; roots, trunk and realms as nodes.")
    f["yggdrasil"] = Fixture("yggdrasil", p, _state(
        p, True, system_id="yggdrasil",
        substrate=SubstrateSpec("mythic_ash", has_represented_autopoiesis=True),
        topology=TopologyClass.ARBORESCENT,
        nodes={"root_aesir", "root_jotunheimr", "root_niflheimr", "trunk", "asgard", "midgard", "jotunheimr"},
        edges={("root_aesir", "trunk"), ("root_jotunheimr", "trunk"), ("root_niflheimr", "trunk"),
               ("trunk", "asgard"), ("trunk", "midgard"), ("trunk", "jotunheimr")},
        fault_sets=[{"trunk"}]),
        {"T2": "AUTOPOIESIS_REPRESENTED", "T7": "QUALIFIED", "cut_vertices": {"trunk"}, "trustworthy": True})

    p = Provenance("src:sefirot", EpistemicTier.CORPUS_MYTH,
                   "Ten Sefirot with 22 paths (layout of Athanasius Kircher, 1652, used as a modelling choice)", NEEDS,
                   "The thread itself says the 10-node / 22-path diagram must not be attributed indiscriminately "
                   "to Sefer Yetzirah, the Zohar and Lurianic literature; source registered as unverified.")
    f["sefirot"] = Fixture("sefirot", p, _state(
        p, False, system_id="sefirot",
        substrate=SubstrateSpec("symbolic_emanation"),
        topology=TopologyClass.RETICULATE,
        nodes={n for e in SEFIROT_KIRCHER_22 for n in e},
        edges=set(SEFIROT_KIRCHER_22)),
        {"T0": "BLOCKED", "T2": "INERT_TAXONOMY", "trustworthy": False})

    p = Provenance("src:ashvattha", EpistemicTier.CORPUS_MYTH,
                   "Bhagavad Gita 15.1-3; Katha Upanishad 2.3.1 (6.1)", NAMED,
                   "Roots above, branches below. No observational boundary is declared (rc1 Issue D): "
                   "an inverted tree is not automatically a horizon.")
    f["ashvattha"] = Fixture("ashvattha", p, _state(
        p, True, system_id="ashvattha",
        substrate=SubstrateSpec("mythic_fig", has_represented_autopoiesis=True),
        topology=TopologyClass.INVERTED_ARBORESCENT,
        nodes={"root_above", "trunk", "branch_gunas", "branch_senses", "branch_karma"},
        edges={("root_above", "trunk"), ("trunk", "branch_gunas"), ("trunk", "branch_senses"), ("trunk", "branch_karma")}),
        {"T1": "PASS", "masked": set(), "trustworthy": True})

    p = Provenance("src:phylogeny", EpistemicTier.EMPIRICAL_SCI,
                   "Darwin 1859; Woese & Fox 1977 (PNAS 74:5088); Doolittle 1999 (Science 284:2124)", NAMED,
                   "Three domains plus two reticulations: endosymbiosis (bacterial lineage into eukaryotes) "
                   "and archaeal ancestry of eukaryotes, so the base is a web, not a strict tree.")
    f["phylogeny"] = Fixture("phylogeny", p, _state(
        p, True, system_id="phylogeny",
        substrate=SubstrateSpec("nucleic_acid", has_empirical_autopoiesis=True, memory_mechanism_status="verified"),
        topology=TopologyClass.ARBORESCENT,
        nodes={"luca", "bacteria", "archaea", "eukarya"},
        edges={("luca", "bacteria"), ("luca", "archaea"), ("archaea", "eukarya"), ("bacteria", "eukarya")}),
        {"T1": "QUALIFIED", "effective_topology": "RETICULATE", "T2": "AUTOPOIESIS_EMPIRICAL",
         "T7": "VERIFIED_SUBSTRATE", "cut_vertices": set(), "trustworthy": True})

    p = Provenance("src:exo-mycelium", EpistemicTier.SPECULATIVE_EXO,
                   "t608u exotic proposal A (multiversal mycelium)", SPEC,
                   "Polycentric mesh across domains; no root.")
    f["multiversal_mycelium"] = Fixture("multiversal_mycelium", p, _state(
        p, True, system_id="multiversal_mycelium",
        substrate=SubstrateSpec("cross_domain_hyphae", has_represented_autopoiesis=True),
        topology=TopologyClass.DISTRIBUTED,
        nodes={"d1", "d2", "d3", "d4", "d5"},
        edges={("d1", "d2"), ("d2", "d3"), ("d3", "d4"), ("d4", "d5"), ("d5", "d1"), ("d1", "d3")}),
        {"T2": "QUALIFIED", "T7": "UNVERIFIED_SUBSTRATE", "cut_vertices": set(), "trustworthy": True})

    p = Provenance("src:exo-plasma", EpistemicTier.SPECULATIVE_EXO,
                   "t608u exotic proposal B (plasma lattice)", SPEC,
                   "Self-similar branching lattice; heredity medium not demonstrated.")
    f["plasma_lattice"] = Fixture("plasma_lattice", p, _state(
        p, True, system_id="plasma_lattice",
        substrate=SubstrateSpec("magnetohydrodynamic_plasma", has_represented_autopoiesis=True),
        topology=TopologyClass.FRACTAL,
        nodes={"core", "a", "b", "a1", "a2", "b1", "b2"},
        edges={("core", "a"), ("core", "b"), ("a", "a1"), ("a", "a2"), ("b", "b1"), ("b", "b2")}),
        {"T2": "QUALIFIED", "T7": "UNVERIFIED_SUBSTRATE", "trustworthy": True})

    p = Provenance("src:exo-temporal", EpistemicTier.SPECULATIVE_EXO,
                   "t608u exotic proposal C (temporal fractal)", SPEC,
                   "A representation of branching history; not represented as self-maintaining.")
    f["temporal_fractal"] = Fixture("temporal_fractal", p, _state(
        p, True, system_id="temporal_fractal",
        substrate=SubstrateSpec("branching_history"),
        topology=TopologyClass.FRACTAL,
        nodes={"t0", "t1a", "t1b", "t2a", "t2b", "t2c", "t2d"},
        edges={("t0", "t1a"), ("t0", "t1b"), ("t1a", "t2a"), ("t1a", "t2b"), ("t1b", "t2c"), ("t1b", "t2d")}),
        {"T2": "INERT_TAXONOMY", "T7": "UNVERIFIED_SUBSTRATE", "trustworthy": True})

    p = Provenance("src:exo-meta", EpistemicTier.SPECULATIVE_EXO,
                   "t608u section 8 (meta-generative tree) and rc1 Issue F", SPEC,
                   "Higher-order generator: emits a crystalline-memory child and an oceanic child, each compiled independently.")
    child_crystal = _state(Provenance("src:exo-crystal", EpistemicTier.SPECULATIVE_EXO, "t608u proposal D", SPEC, ""), True,
                           system_id="crystalline_memory_tree",
                           substrate=SubstrateSpec("crystalline_lattice", has_represented_autopoiesis=True),
                           topology=TopologyClass.FRACTAL, nodes={"c0", "c1", "c2", "c3"},
                           edges={("c0", "c1"), ("c0", "c2"), ("c0", "c3")})
    child_ocean = _state(Provenance("src:exo-ocean", EpistemicTier.SPECULATIVE_EXO, "t608u proposal E", SPEC, ""), True,
                         system_id="oceanic_world_tree",
                         substrate=SubstrateSpec("fluid_colony", has_represented_autopoiesis=True),
                         topology=TopologyClass.DISTRIBUTED, nodes={"o1", "o2", "o3", "o4"},
                         edges={("o1", "o2"), ("o2", "o3"), ("o3", "o4"), ("o4", "o1")})
    f["meta_generative"] = Fixture("meta_generative", p, _state(
        p, True, system_id="meta_generative_tree",
        substrate=SubstrateSpec("rule_generator", has_represented_autopoiesis=True),
        topology=TopologyClass.DISTRIBUTED,
        nodes={"g1", "g2", "g3"}, edges={("g1", "g2"), ("g2", "g3"), ("g3", "g1")},
        meta_spec=MetaArchitectureSpec(MetaGenerator("meta_tree_root"),
                                       child_emissions=[(child_crystal, set()), (child_ocean, set())])),
        {"E6": "QUALIFIED", "children": 2, "trustworthy": True})  # rc6: speculative children are QUALIFIED, so the parent is
    return f


__all__ = ["Fixture", "Provenance", "build_fixtures", "SEFIROT_KIRCHER_22", "NAMED", "NEEDS", "SPEC"]
