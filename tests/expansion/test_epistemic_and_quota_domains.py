"""Tests for epistemic_ledger_verification and quota_bypass_mechanics domain templates."""
from semantic_compiler.expansion.registry import get_template, list_domains


def test_epistemic_ledger_verification_template():
    assert "epistemic_ledger_verification" in list_domains()
    tmpl = get_template("epistemic_ledger_verification")
    assert tmpl.domain == "epistemic_ledger_verification"
    assert tmpl.version == 1.0

    comp_names = {c["name"] for c in tmpl.components}
    assert "external_bank_ledger" in comp_names
    assert "stored_value_ledger" in comp_names
    assert "dpan_token_preference" in comp_names

    inv_text = " ".join(tmpl.invariants)
    assert "A DPAN token in a preference file does not prove settlement" in inv_text
    assert "Only the external bank ledger proves settlement" in inv_text

    fm_names = {fm["name"] for fm in tmpl.failure_modes}
    assert "false_settlement_attribution" in fm_names
    assert "stored_balance_blindspot" in fm_names


def test_quota_bypass_mechanics_template():
    assert "quota_bypass_mechanics" in list_domains()
    tmpl = get_template("quota_bypass_mechanics")
    assert tmpl.domain == "quota_bypass_mechanics"
    assert tmpl.version == 1.0

    comp_names = {c["name"] for c in tmpl.components}
    assert "online_charging_system" in comp_names
    assert "imsi_identity_binding" in comp_names
    assert "pcef_traffic_enforcer" in comp_names

    inv_text = " ".join(tmpl.invariants)
    assert "A new IMSI provisioning event forces a quota state desync in the carrier core" in inv_text

    fm_names = {fm["name"] for fm in tmpl.failure_modes}
    assert "oc_quota_desync" in fm_names
    assert "imsi_account_unbinding" in fm_names
