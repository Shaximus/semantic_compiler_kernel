from semantic_compiler.expansion.gem_decode import decode_build


def _by_id(result, archetype_id):
    return next(item for item in result.archetypes if item["archetype_id"] == archetype_id)


def test_qwen_cospri_shape_is_identified():
    result = decode_build(
        "verifier: Qwen 3.7 27B; draft: Qwen draft; "
        "supports: MTP K=3, Cast on Critical Strike, vLLM, expert precognition; "
        "equipment: RTX PRO 6000, RTX 3080 Ti; "
        "auras: BCC, TokenRouter, scheduler"
    )
    coc = _by_id(result, "COC_TRIGGER_CASCADE")
    assert coc["status"] == "IDENTIFIED"
    assert coc["confidence"] >= 0.85
    assert "archetypes" in result.json


def test_qwen_mtp_only_reports_attempting_cospri_and_identified_projectile_scaler():
    result = decode_build(
        "verifier: Qwen 3.7 27B; supports: MTP K=3, vLLM; equipment: RTX PRO 6000"
    )
    mtp = _by_id(result, "MTP_PROJECTILE_SCALER")
    assert mtp["status"] == "IDENTIFIED"
    coc = _by_id(result, "COC_TRIGGER_CASCADE")
    assert coc["status"] == "ATTEMPTING"
    assert coc["missing_groups"]


def test_aura_stack_detected_independently_of_founder_fixture():
    result = decode_build(
        "verifier: Qwen 35B A3B; supports: vLLM; "
        "auras: BCC, Semantic Compiler, TokenRouter, shared world state, receipts"
    )
    aura = _by_id(result, "AURA_STACKER")
    assert aura["status"] == "IDENTIFIED"


def test_moe_precognition_requires_all_structural_groups_for_identified():
    result = decode_build(
        "verifier: Qwen 35B A3B; supports: expert precognition, expert compression; "
        "auras: TokenRouter, BCC"
    )
    moe = _by_id(result, "MOE_PRECOGNITION")
    assert moe["status"] == "IDENTIFIED"


def test_sheet_names_attempted_builds():
    result = decode_build("verifier: Qwen 27B; supports: MTP K=3")
    assert "Attempted build archetypes" in result.sheet
    assert "Multi-projectile speculative throughput build" in result.sheet
