"""Tests for expansion.gem_decode."""

import json

import pytest

from semantic_compiler.expansion.gem_decode import (
    GemParseError,
    decode_build,
    parse_build_spec,
)
from semantic_compiler.expansion.gem_decode.ontology import lookup_component
from semantic_compiler.expansion.gem_decode.schema import (
    SCHEMA_PATH,
    validate_gem_build,
)

POE_SPEC = (
    "Ice Nova + Cast on Critical Strike + Greater Multiple Projectiles; "
    "weapon: Cospri's Malice; auras: Hatred, Herald of Ice; "
    "flask: Dying Sun; anointment: Calibrated Dissent"
)

REFLEXION_SPEC = (
    "verifier: MiniMax M2.5; draft: Qwen draft; "
    "supports: MTP K=5, vLLM, expert compression; "
    "auras: BCC, TokenRouter, receipts; flask: auxiliary_i9; "
    "anointment: authority_gate"
)

COSPRI_SPEC = (
    "verifier: RTX PRO 6000 target model verified execution; "
    "draft: lightweight continuous draft model; "
    "supports: speculative decoder (MTP K=5), expert precognition, cache stack; "
    "weapon: RTX 3080 Ti secondary trigger GPU; "
    "auras: BCC retrieval, TokenRouter, KV reuse, scheduler; "
    "flask: auxiliary_i9 (Dying Sun); "
    "anointment: Calibrated Dissent"
)

COSPRI_PASS_PARAMS = {
    "draft_rate": 4000,
    "verifier_acceptance_capacity": 5000,
    "prefetch_lead": 0.05,
    "decompression_latency": 0.02,
    "transfer_latency": 0.01,
    "concurrent_sequences": 8,
    "kv_vram_budget": 16,
    "trigger_frequency": 120,
    "execution_recovery_rate": 150,
    "flask_fanout": 3,
    "draft_capacity": 5,
    "verifier_capacity": 4,
    "network_throughput": 6,
    "scheduler_slots": 4,
    "memory_capacity": 10,
    "merge_bandwidth": 5,
}


# --- parser, both dialects --------------------------------------------------

def test_parse_poe_native_dialect():
    build = parse_build_spec(POE_SPEC)
    assert build.dialect == "poe_native"
    assert build.active_skill == "Ice Nova"
    assert build.support_gems == ("Cast on Critical Strike", "Greater Multiple Projectiles")
    assert build.equipment == ("Cospri's Malice",)
    assert build.auras == ("Hatred", "Herald of Ice")
    assert build.flasks == ("Dying Sun",)
    assert build.anointments == ("Calibrated Dissent",)


def test_parse_reflexion_native_dialect():
    build = parse_build_spec(REFLEXION_SPEC)
    assert build.dialect == "reflexion_native"
    assert build.active_skill == "MiniMax M2.5"
    # draft: section feeds support_gems (a drafter modifies execution)
    assert build.support_gems == ("Qwen draft", "MTP K=5", "vLLM", "expert compression")
    assert build.auras == ("BCC", "TokenRouter", "receipts")
    assert build.flasks == ("auxiliary_i9",)
    assert build.anointments == ("authority_gate",)


def test_parser_rejects_unknown_keys_and_empty_specs():
    with pytest.raises(GemParseError):
        parse_build_spec("")
    with pytest.raises(GemParseError):
        parse_build_spec("sword: Excalibur")  # unknown section key
    with pytest.raises(GemParseError):
        parse_build_spec("verifier: A; verifier: B")  # two active skills


# --- layer classification ----------------------------------------------------

def test_layer_classification_correctness():
    result = decode_build(REFLEXION_SPEC)
    layers = result.json["layers"]
    assert layers["active_skill"]["layer"] == "Active skill"
    assert layers["active_skill"]["canonical"] == "LLM weights / verifier model"
    support_by_name = {c["name"]: c for c in layers["support_gems"]}
    assert support_by_name["Qwen draft"]["canonical"] == "draft model"
    assert support_by_name["vLLM"]["layer"] == "Support gem"
    aura_layers = {c["layer"] for c in layers["auras"]}
    assert aura_layers == {"Aura"}
    # position-dependent component: equipment host playing the flask role
    assert layers["flasks"][0]["canonical"] == "Dying Sun"
    assert layers["anointments"][0]["canonical"] == "authority_gate"


def test_unmapped_components_reported_not_dropped():
    result = decode_build("verifier: MiniMax M2.5; auras: Zxcvbn Field")
    assert "Zxcvbn Field" in result.json["unmapped_components"]
    aura = result.json["layers"]["auras"][0]
    assert aura["mapped"] is False
    assert aura["compute_analogue"] is None


def test_layer_context_override_only_in_flask_position():
    equipment_entry = lookup_component("auxiliary_i9")
    flask_entry = lookup_component("auxiliary_i9", layer="Flask")
    assert equipment_entry.layer == "Equipment"
    assert flask_entry.canonical == "Dying Sun"
    assert flask_entry.proxy_compute


# --- translation correctness against known mappings --------------------------

def test_mtp_maps_to_gmp_with_acceptance_rate_invariant():
    result = decode_build(REFLEXION_SPEC)
    mtp = next(c for c in result.json["layers"]["support_gems"] if c["name"] == "MTP K=5")
    assert "BUILD_017" in mtp["build_refs"]
    assert "Greater Multiple Projectiles" in mtp["compute_analogue"]
    assert "acceptance rate" in mtp["note"]

    poe = decode_build(POE_SPEC)
    gmp = next(c for c in poe.json["layers"]["support_gems"] if "Greater Multiple" in c["name"])
    assert "BUILD_017" in gmp["build_refs"]
    assert "acceptance rate = accuracy rating" in gmp["note"]


def test_cospri_weapon_maps_to_secondary_trigger_gpu():
    result = decode_build(POE_SPEC)
    weapon = result.json["layers"]["equipment"][0]
    assert "secondary GPU hosting the trigger workload" in weapon["compute_analogue"]


# --- cadence checks: PASS / WARN / FAIL / SKIP --------------------------------

def _check(result, check_id):
    return next(c for c in result.checks if c["check_id"] == check_id)


def test_cadence_pass_when_tuned():
    result = decode_build(COSPRI_SPEC, params=COSPRI_PASS_PARAMS)
    statuses = {c["check_id"]: c["status"] for c in result.checks}
    assert statuses == {
        "draft_rate_vs_verifier_capacity": "PASS",
        "prefetch_lead_vs_latency": "PASS",
        "concurrency_vs_kv_vram_budget": "PASS",
        "trigger_frequency_vs_recovery": "PASS",
        "flask_fanout_breakpoint": "PASS",
    }
    assert result.verdict == "HOLDS"


def test_cadence_fail_when_overcapped():
    params = {**COSPRI_PASS_PARAMS, "draft_rate": 9000}
    result = decode_build(COSPRI_SPEC, params=params)
    check = _check(result, "draft_rate_vs_verifier_capacity")
    assert check["status"] == "FAIL"
    assert "overcapping" in check["reason"]
    assert result.verdict == "STRAINS"


def test_cadence_warn_near_breakpoint_and_underutilized():
    near = decode_build(COSPRI_SPEC, params={**COSPRI_PASS_PARAMS, "draft_rate": 4800})
    assert _check(near, "draft_rate_vs_verifier_capacity")["status"] == "WARN"
    under = decode_build(COSPRI_SPEC, params={**COSPRI_PASS_PARAMS, "draft_rate": 1000})
    assert _check(under, "draft_rate_vs_verifier_capacity")["status"] == "WARN"


def test_prefetch_and_concurrency_fail_cases():
    late = decode_build(COSPRI_SPEC, params={**COSPRI_PASS_PARAMS, "prefetch_lead": 0.01})
    assert _check(late, "prefetch_lead_vs_latency")["status"] == "FAIL"
    over_seq = decode_build(COSPRI_SPEC, params={**COSPRI_PASS_PARAMS, "concurrent_sequences": 32})
    assert _check(over_seq, "concurrency_vs_kv_vram_budget")["status"] == "FAIL"


def test_flask_fanout_min_of_six_breakpoint():
    params = {**COSPRI_PASS_PARAMS, "flask_fanout": 9}
    result = decode_build(COSPRI_SPEC, params=params)
    check = _check(result, "flask_fanout_breakpoint")
    assert check["status"] == "FAIL"
    assert check["values"]["binding_constraint"] == "verifier_capacity"
    # no flasks in the build -> no flask check at all
    no_flask = decode_build("verifier: MiniMax M2.5; anointment: authority_gate", params=params)
    assert all(c["check_id"] != "flask_fanout_breakpoint" for c in no_flask.checks)


def test_missing_params_are_skip_never_guessed():
    result = decode_build(REFLEXION_SPEC)
    assert all(c["status"] == "SKIP" for c in result.checks)


# --- failure-family flags (>= 4 exercised) -------------------------------------

def test_flag_n_unscoped_aura():
    result = decode_build(POE_SPEC)  # Hatred / Herald of Ice are unscoped
    n_flags = [f for f in result.flags if "N" in f["families"]]
    assert len(n_flags) == 2
    assert any("Hatred" in f["trigger"] for f in n_flags)


def test_flag_f_trigger_without_cooldown():
    result = decode_build(POE_SPEC)  # CoC, no scheduler aura, no params
    f_flags = [f for f in result.flags if "F" in f["families"]]
    assert f_flags
    assert "Cast on Critical Strike" in f_flags[0]["trigger"]
    # adding the scheduler aura clears the flag
    with_scheduler = decode_build(POE_SPEC + "; auras: scheduler")
    assert not [f for f in with_scheduler.flags if "F" in f["families"]]


def test_flag_eh_proxy_without_authority_cost():
    result = decode_build("verifier: MiniMax M2.5; flask: Dying Sun")
    eh = [f for f in result.flags if f["families"] == ["E", "H"]]
    assert eh
    assert eh[0]["severity"] == "critical"
    assert "Hateforge" in eh[0]["description"]
    # an authority layer clears it
    with_gate = decode_build("verifier: MiniMax M2.5; flask: Dying Sun; anointment: authority_gate")
    assert not [f for f in with_gate.flags if f["families"] == ["E", "H"]]


def test_flag_e_self_refilling_budget():
    result = decode_build(
        "verifier: MiniMax M2.5; flask: Mana flask; anointment: authority_gate",
        params={"budget_refilled_by_gated_activity": True},
    )
    e_flags = [f for f in result.flags if f["code"] == "SELF_REFILLING_BUDGET"]
    assert e_flags
    assert e_flags[0]["families"] == ["E"]


def test_flag_rejections_must_not_pay():
    result = decode_build(
        "verifier: MiniMax M2.5; supports: MTP K=5, rejection credit minter; anointment: authority_gate"
    )
    flags = [f for f in result.flags if f["code"] == "REJECTIONS_MUST_NOT_PAY"]
    assert flags
    assert "rejection" in flags[0]["description"]
    # the legitimate form (returns reasons) does not flag
    legit = decode_build(
        "verifier: MiniMax M2.5; supports: MTP K=5, Verified Returning Projectiles; anointment: authority_gate"
    )
    assert not [f for f in legit.flags if f["code"] == "REJECTIONS_MUST_NOT_PAY"]


# --- Adapa fixture --------------------------------------------------------------

def test_adapa_fixture_fires_with_exact_text():
    result = decode_build("verifier: MiniMax M2.5")  # model weights, no anointment
    adapa = [f for f in result.flags if f["code"] == "ADAPA_RISK"]
    assert adapa
    assert adapa[0]["severity"] == "critical"
    assert "Wisdom Class ≠ Authority Class" in adapa[0]["description"]
    assert "Calibrated Dissent is the anti-Adapa notable" in adapa[0]["description"]
    assert result.verdict == "STRAINS"


def test_adapa_fixture_cleared_by_dissent_or_authority():
    for spec in (
        "verifier: MiniMax M2.5; anointment: Calibrated Dissent",
        "verifier: MiniMax M2.5; anointment: authority_gate",
        "verifier: MiniMax M2.5; auras: tool permissions",
    ):
        result = decode_build(spec)
        assert not [f for f in result.flags if f["code"] == "ADAPA_RISK"], spec


def test_adapa_does_not_fire_for_poe_game_builds():
    result = decode_build(POE_SPEC)  # Ice Nova is not instruction-fidelity weights
    assert not [f for f in result.flags if f["code"] == "ADAPA_RISK"]


# --- schema validation ------------------------------------------------------------

def test_schema_file_is_draft_2020_12():
    with open(SCHEMA_PATH) as f:
        on_disk = json.load(f)
    assert "2020-12" in on_disk["$schema"]


def test_decoded_records_validate_against_schema():
    for spec, params in (
        (POE_SPEC, None),
        (REFLEXION_SPEC, None),
        (COSPRI_SPEC, COSPRI_PASS_PARAMS),
    ):
        result = decode_build(spec, params=params)
        assert validate_gem_build(result.json) == []


def test_schema_rejects_bad_verdict_and_layer():
    result = decode_build(REFLEXION_SPEC)
    record = json.loads(json.dumps(result.json))
    record["verdict"] = "PROVEN"
    record["layers"]["auras"][0]["layer"] = "Weapon"
    errors = validate_gem_build(record)
    assert any("verdict" in e for e in errors)
    assert any("layer" in e for e in errors)


# --- end-to-end demo specs ---------------------------------------------------------

def test_both_demo_specs_decode_end_to_end():
    poe = decode_build(POE_SPEC)
    reflexion = decode_build(REFLEXION_SPEC)
    assert poe.build.dialect == "poe_native"
    assert reflexion.build.dialect == "reflexion_native"
    for result in (poe, reflexion):
        assert result.sheet.startswith("# Gem Decode — Build Sheet")
        assert result.verdict in ("HOLDS", "STRAINS", "UNRESOLVED")
        assert validate_gem_build(result.json) == []
    # the PoE demo spec carries the anti-Adapa anointment
    assert not [f for f in poe.flags if f["code"] == "ADAPA_RISK"]
    # the Reflexion demo spec carries an authority overlay
    assert not [f for f in reflexion.flags if f["code"] == "ADAPA_RISK"]


def test_fixture_overcapped_strains():
    params = {**COSPRI_PASS_PARAMS, "draft_rate": 9000, "trigger_frequency": 400, "flask_fanout": 9}
    result = decode_build(COSPRI_SPEC, params=params)
    assert result.verdict == "STRAINS"
    failed = [c["check_id"] for c in result.checks if c["status"] == "FAIL"]
    assert "draft_rate_vs_verifier_capacity" in failed
    assert "trigger_frequency_vs_recovery" in failed
    assert "flask_fanout_breakpoint" in failed
