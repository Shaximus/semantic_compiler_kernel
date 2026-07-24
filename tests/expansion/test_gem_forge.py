from semantic_compiler.expansion.gem_forge import (
    PoeGem,
    SoftwareComponent,
    forge_component,
    load_gem_corpus,
    translate_corpus,
    translate_gem,
)


def _gmp():
    return PoeGem(
        gem_id="SupportGreaterMultipleProjectiles",
        name="Greater Multiple Projectiles Support",
        kind="support",
        tags=("Support", "Projectile"),
        wording=(
            "Supports projectile skills.",
            "Supported Skills deal (35-26)% less Projectile Damage",
            "Supported Skills fire 4 additional Projectiles",
        ),
        quality_wording=(
            "Supported Skills deal (0.5-10)% increased Projectile Damage",
        ),
        source="fixture",
    )


def test_gmp_translation_preserves_source_wording_and_builds_mtp():
    result = translate_gem(_gmp())
    assert result.inference_name == "Multi-Token Prediction Support"
    assert result.source_wording[2] == "Supported Skills fire 4 additional Projectiles"
    assert result.line_pairs[2].source == result.source_wording[2]
    assert "4 additional future Token Positions" in result.line_pairs[2].converted
    assert "EMIT_ADDITIONAL_CANDIDATES" in result.primitives
    assert "REDUCE_PER_CANDIDATE_EFFECTIVENESS" in result.primitives


def test_loader_accepts_normalized_and_repoe_style_shapes():
    normalized = load_gem_corpus({
        "gems": [{
            "id": "gmp",
            "name": "Greater Multiple Projectiles Support",
            "kind": "support",
            "tags": ["Support", "Projectile"],
            "wording": ["Supported Skills fire 4 additional Projectiles"],
        }]
    })
    assert normalized[0].kind == "support"

    repoe = load_gem_corpus({
        "Metadata/Items/Gems/SupportGemGreaterMultipleProjectiles": {
            "display_name": "Greater Multiple Projectiles Support",
            "is_support": True,
            "tags": {"support": True, "projectile": True},
            "stats": ["Supported Skills fire 4 additional Projectiles"],
        }
    })
    assert repoe[0].name == "Greater Multiple Projectiles Support"
    assert repoe[0].kind == "support"


def test_component_can_match_multiple_gems_and_preserve_novel_effects():
    corpus = (
        _gmp(),
        PoeGem(
            gem_id="CastOnCrit",
            name="Cast on Critical Strike Support",
            kind="support",
            tags=("Support", "Trigger"),
            wording=("Supported attacks trigger a supported spell when you deal a Critical Strike",),
            source="fixture",
        ),
        PoeGem(
            gem_id="ReturningProjectiles",
            name="Returning Projectiles Support",
            kind="support",
            tags=("Support", "Projectile"),
            wording=("Projectiles from Supported Skills Return to you",),
            source="fixture",
        ),
    )
    translations = translate_corpus(corpus)
    component = SoftwareComponent(
        name="Adaptive Speculative Runtime",
        description=(
            "MTP emits additional candidates, qualified proposals trigger a verifier, "
            "rejected branches return feedback, results merge and deduplicate, and "
            "the controller auto tunes K while recording a receipt."
        ),
        deployment_slots=("RUNTIME", "SCHEDULER", "VERIFIER"),
        relationships=("draft TRIGGERS verifier", "branches RETURN_TO controller"),
    )
    result = forge_component(component, translations)
    names = {match.gem_name for match in result.matches}
    assert "Greater Multiple Projectiles Support" in names
    assert "Cast on Critical Strike Support" in names
    assert "Returning Projectiles Support" in names
    assert result.composite_gem.composition == "COMPOSITE"
    assert "ADAPT_PARAMETER" in result.composite_gem.novel_effects
    assert "RECORD_RECEIPT" in result.composite_gem.novel_effects


def test_no_match_produces_novel_gem_instead_of_forced_analogy():
    component = SoftwareComponent(
        name="Receipt Signer",
        description="Records a cryptographic provenance receipt and fails closed on invalid authority.",
        deployment_slots=("OBSERVABILITY", "POLICY_LAYER"),
    )
    result = forge_component(component, (translate_gem(_gmp()),))
    assert result.composite_gem.composition == "NOVEL"
    assert "RECORD_RECEIPT" in result.composite_gem.novel_effects
    assert "FAIL_CLOSED" in result.composite_gem.novel_effects
