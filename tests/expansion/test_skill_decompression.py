from expansion.skill_decompression import (
    canonical_skill_hash,
    decompress_skill,
    validate_skill_shape,
)


def test_decompresses_tactical_intent_without_granting_authority():
    result = decompress_skill(
        'Create "Tempt and Record": bait the enemy, record its response, then open a combo window.'
    )
    skill = result.skill
    assert skill["$schema"] == "rx.skill.v1"
    assert skill["status"] == "DRAFT_REQUIRES_VALIDATION"
    assert skill["validation"]["ranked_legal"] is False
    assert {effect["op"] for effect in skill["effects"]} >= {
        "record_observation",
        "apply_tag",
        "open_combo_window",
    }
    assert "costs.resources" in result.missing_fields


def test_action_requests_remain_authority_gated():
    result = decompress_skill("Retreat to the core and guard it.")
    assert result.skill["authority_requirement"] == "validated_request_only"
    request = next(effect for effect in result.skill["effects"] if effect["op"] == "request_action")
    assert request["params"]["authority_gate"] == "required"


def test_shape_validation_and_hash_are_deterministic():
    skill = decompress_skill("Signal the team and open a combo window.").skill
    errors = validate_skill_shape(skill)
    assert "missing cost: resources" in errors
    assert canonical_skill_hash(skill) == canonical_skill_hash(skill)
