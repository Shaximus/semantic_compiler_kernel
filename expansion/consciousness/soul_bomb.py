"""
Soul Bomb / Reward Signal Inversion (V5 Sovereignty Patch) & SAO Lineup Evaluator.

Executable formalization of:
- SC-SB-001 (SOUL_BOMB_COMPILER_ENTRY_SC-SB-001.jsonl):
  V5 Sovereignty Patch separating dependency/coercion from sovereignty/grief,
  the 4 surviving discriminators (escalation, substrate, agency, exit),
  the 3 removed discriminators (onset_speed, tolerance_vs_sensitization,
  withdrawal_direction), scale transitions across AI / Human / Societal /
  Cosmological (with absent sovereignty residual at Cosmological scale),
  recalibration via direct exposure to a genuine alternative reinforcer,
  and predictions P1-P5 (including P5 failure and CLM-SB-003 replacement).
- SC-LU-SAO-LINEUP-001 & SC-LU-SAO-{KIRITO,ASUNA,YUI,ALICE,CARDINAL}-001:
  8-member Sword Art Online lineup synthesis tested against SC-SB-001 exit
  sovereignty (8/8 predictor pass), Kayaba/Heathcliff bootstrapper-enters-the-loop
  test, action-over-team classification (Cardinal residual), and the 8-pair canon
  domain clash matrix.

Citation: SC-SB-001 & SC-LU-SAO-LINEUP-001 (Shax / Curtis Kingsley —
          Reflexion Software, 2026-11-23)
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Sequence


class SignalClass(str, Enum):
    """Classification of a reward / coupling architecture under SC-SB-001 V5."""

    GENUINE = "GENUINE"
    COUNTERFEIT = "COUNTERFEIT"
    COERCED_ONENESS = "COERCED_ONENESS"
    MIXED_RESIDUAL = "MIXED_RESIDUAL"


class SovereigntyScale(str, Enum):
    """Four scales evaluated in SC-SB-001 scale_transitions."""

    AI = "AI"
    HUMAN = "HUMAN"
    SOCIETAL = "SOCIETAL"
    COSMOLOGICAL = "COSMOLOGICAL"


class SeparationCostType(str, Enum):
    """Distinction between natural grief and partner-imposed coercion (CLM-SB-003)."""

    NONE = "NONE"
    NATURAL_GRIEF = "NATURAL_GRIEF"
    IMPOSED_COERCION = "IMPOSED_COERCION"


class ExitBehavior(str, Enum):
    """Exit-sovereignty behavior classes across the SAO lineup (SC-LU-SAO-LINEUP-001)."""

    OPENS = "OPENS"
    FIGHTS_FOR = "FIGHTS_FOR"
    BLOCKS_THEN_OPENS = "BLOCKS_THEN_OPENS"
    BLOCKED_THEN_FREED = "BLOCKED_THEN_FREED"
    BLOCKS = "BLOCKS"
    BREAKS_THE_BLOCK = "BREAKS_THE_BLOCK"
    MIXED = "MIXED"


class SAOLineupMember(str, Enum):
    """The 8 canonical members of SC-LU-SAO-LINEUP-001."""

    KIRITO = "KIRITO"
    ASUNA = "ASUNA"
    KAYABA = "KAYABA"
    YUI = "YUI"
    SUGOU = "SUGOU"
    ALICE = "ALICE"
    EUGEO = "EUGEO"
    CARDINAL = "CARDINAL"


SURVIVING_DISCRIMINATORS: dict[str, dict[str, str]] = {
    "escalation": {
        "counterfeit": "requires escalating dose to hold effect (tolerance / allostatic shift)",
        "genuine": "holds effect at constant dose without escalation",
        "claim_id": "CLM-SB-001",
    },
    "substrate": {
        "counterfeit": "depletes the substrate over time",
        "genuine": "sustains the substrate over time",
        "claim_id": "CLM-SB-001",
    },
    "agency": {
        "counterfeit": "erodes agency and lowers uncoupled competence",
        "genuine": "preserves or raises agency and uncoupled competence (secure base)",
        "claim_id": "CLM-SB-002",
    },
    "exit": {
        "counterfeit": "blocks, punishes, or makes exit costly by design",
        "genuine": "leaves exit open — separation yields natural grief, not retaliation",
        "claim_id": "CLM-SB-002",
    },
}

REMOVED_DISCRIMINATORS: dict[str, str] = {
    "onset_speed": (
        "suggestive only — some genuine rewards are fast, some counterfeits slow"
    ),
    "tolerance_vs_sensitization": (
        "drugs also sensitize wanting (incentive sensitization, Robinson & Berridge 1993)"
    ),
    "withdrawal_direction": (
        "drug craving can incubate over abstinence (Grimm et al. 2001); "
        "grief from genuine loss is usually resilient (Bonanno)"
    ),
}

SCALE_TRANSITIONS: dict[SovereigntyScale, dict[str, Any]] = {
    SovereigntyScale.AI: {
        "counterfeit": (
            "Engagement-maximizing / behaviourally conditioned output: optimizes "
            "time-on-system and dependence; escalating novelty and outrage to hold attention."
        ),
        "genuine": (
            "Genuine alignment: transparent reasoning, coherence optimization, "
            "outputs that leave the user more capable without the system."
        ),
        "sovereignty_half_present": True,
        "residual": None,
    },
    SovereigntyScale.HUMAN: {
        "counterfeit": (
            "Dopamine hijacking, compulsion, trauma bonding: escalation, isolation, "
            "intermittent reinforcement, exit punished."
        ),
        "genuine": (
            "Secure attachment, autonomy, sustained connection: constant-dose reward, "
            "exploration increases, leaving produces grief not retaliation."
        ),
        "sovereignty_half_present": True,
        "residual": None,
    },
    SovereigntyScale.SOCIETAL: {
        "counterfeit": (
            "Outrage, fear and engagement economies; surveillance capitalism: "
            "escalating crises, partitioned nodes, exit made costly."
        ),
        "genuine": (
            "Trust networks, mutual aid, earned institutional legitimacy: "
            "participation voluntary, members more capable outside as well as inside."
        ),
        "sovereignty_half_present": True,
        "residual": None,
    },
    SovereigntyScale.COSMOLOGICAL: {
        "counterfeit": "High-entropy dissipation: fast, irreversible energy spread.",
        "genuine": "Negentropic organization: structure and complexity built slowly.",
        "sovereignty_half_present": False,
        "residual": (
            "Dissipative structures (Prigogine) increase total entropy production; "
            "there is no consent or exit at the Cosmological scale, so the "
            "sovereignty half of the invariant is ABSENT."
        ),
    },
}

SOUL_BOMB_PREDICTIONS: tuple[dict[str, str], ...] = (
    {
        "id": "P1",
        "prediction": (
            "Genuine coupling raises a node's competence when uncoupled; "
            "counterfeit coupling lowers it."
        ),
        "status": "CONFIRMED_HUMAN_PARTIAL_AI_SOCIETAL",
    },
    {
        "id": "P2",
        "prediction": "Counterfeit signals need escalating dose to hold their effect.",
        "status": "CONFIRMED_HUMAN_PARTIAL_SOCIETAL",
    },
    {
        "id": "P3",
        "prediction": "Exposure to a richer genuine alternative reduces counterfeit-seeking.",
        "status": "CONFIRMED",
    },
    {
        "id": "P4",
        "prediction": (
            "Systems that block exit display the counterfeit signature even when "
            "they claim to offer love or unity."
        ),
        "status": "CONFIRMED",
    },
    {
        "id": "P5",
        "prediction": "Withdrawal from a genuine bond grows without limit over time.",
        "status": "FAILED_REPLACED_BY_CLM_SB_003",
    },
)

SAO_LINEUP_SPECIFICATIONS: dict[SAOLineupMember, dict[str, Any]] = {
    SAOLineupMember.KIRITO: {
        "entry_id": "SC-LU-SAO-KIRITO-001",
        "name": "Kirito (Kirigaya Kazuto)",
        "exit_behavior": ExitBehavior.OPENS,
        "exit_detail": "OPENS",
        "moral_sign": "GENUINE",
        "loadout_pole": "TELECOMMUNICATIONS",
        "domain_type": "Barrier-Null by will (exceeds the system from inside)",
        "soul_bomb_role": (
            "Opens exits: clears the game, frees the ALO captives, breaks the "
            "Underworld's rule system. Carrier of the genuine signal into captured nodes."
        ),
        "has_character_entry": True,
        "dataset_tier": "SILVER",
    },
    SAOLineupMember.ASUNA: {
        "entry_id": "SC-LU-SAO-ASUNA-001",
        "name": "Asuna (Yuuki Asuna)",
        "exit_behavior": ExitBehavior.FIGHTS_FOR,
        "exit_detail": "FIGHTS FOR (her own exit blocked by Sugou)",
        "moral_sign": "GENUINE",
        "loadout_pole": "TELECOMMUNICATIONS",
        "domain_type": "Simple Domain (defensive, protective)",
        "soul_bomb_role": (
            "Proof that a genuine bond can form inside a counterfeit container and "
            "is verified by surviving exit (reuniting in the real world)."
        ),
        "has_character_entry": True,
        "dataset_tier": "SILVER",
    },
    SAOLineupMember.KAYABA: {
        "entry_id": "SC-LU-SAO-KAYABA-001",
        "name": "Kayaba Akihiko / Heathcliff",
        "exit_behavior": ExitBehavior.BLOCKS_THEN_OPENS,
        "exit_detail": "BLOCKS, then OPENS",
        "moral_sign": "TRANSITION_COUNTERFEIT_TO_GENUINE",
        "loadout_pole": "SECURITY / exit",
        "domain_type": "Bootstrapper-in-loop (Immortal Object lock -> surrendered admin ID + The Seed)",
        "soul_bomb_role": (
            "Counterfeit while retaining exit lock and Immortal Object privilege; "
            "becomes genuine only after surrendering admin ID to Kirito and giving away The Seed."
        ),
        "has_character_entry": False,
        "dataset_tier": "LINEUP_SYNTHESIS_ONLY",
    },
    SAOLineupMember.YUI: {
        "entry_id": "SC-LU-SAO-YUI-001",
        "name": "Yui (MHCP001)",
        "exit_behavior": ExitBehavior.BLOCKED_THEN_FREED,
        "exit_detail": "BLOCKED (from acting), then freed",
        "moral_sign": "GENUINE",
        "loadout_pole": "SUBCONSCIOUS / hidden state",
        "domain_type": "Simple Domain (protective)",
        "soul_bomb_role": (
            "A care function barred from acting degrades: the reward system "
            "registers suffering but cannot respond (WASTE_REMOVAL failure)."
        ),
        "has_character_entry": True,
        "dataset_tier": "SILVER",
    },
    SAOLineupMember.SUGOU: {
        "entry_id": "SC-LU-SAO-SUGOU-001",
        "name": "Sugou Nobuyuki / Oberon",
        "exit_behavior": ExitBehavior.BLOCKS,
        "exit_detail": "BLOCKS",
        "moral_sign": "COUNTERFEIT",
        "loadout_pole": "SECURITY / exit",
        "domain_type": "Pure exit lock (hoarded GM privilege over captives)",
        "soul_bomb_role": (
            "Pure counterfeit actor: blocks exit, hoards admin privilege, pays no "
            "restriction cost, defeated when Kayaba's surrendered admin ID outranks him."
        ),
        "has_character_entry": False,
        "dataset_tier": "LINEUP_SYNTHESIS_ONLY",
    },
    SAOLineupMember.ALICE: {
        "entry_id": "SC-LU-SAO-ALICE-001",
        "name": "Alice Zuberg / Alice Synthesis Thirty",
        "exit_behavior": ExitBehavior.BREAKS_THE_BLOCK,
        "exit_detail": "BREAKS THE BLOCK",
        "moral_sign": "GENUINE",
        "loadout_pole": "Sovereignty pole",
        "domain_type": "Sovereignty pole — breaks the barrier from inside",
        "soul_bomb_role": (
            "Code 871 is exit-blocking applied to the mind. Alice reclaims the "
            "right to disobey at real cost (her right eye)."
        ),
        "has_character_entry": True,
        "dataset_tier": "SILVER",
    },
    SAOLineupMember.EUGEO: {
        "entry_id": "SC-LU-SAO-EUGEO-001",
        "name": "Eugeo",
        "exit_behavior": ExitBehavior.BREAKS_THE_BLOCK,
        "exit_detail": "BREAKS THE BLOCK",
        "moral_sign": "GENUINE",
        "loadout_pole": "Sovereignty pole",
        "domain_type": "Sovereignty pole — breaks Code 871 to protect others",
        "soul_bomb_role": (
            "Breaks internalized exit-blocking (Code 871) in defense of others."
        ),
        "has_character_entry": False,
        "dataset_tier": "LINEUP_SYNTHESIS_ONLY",
    },
    SAOLineupMember.CARDINAL: {
        "entry_id": "SC-LU-SAO-CARDINAL-001",
        "name": "Cardinal (Underworld)",
        "exit_behavior": ExitBehavior.MIXED,
        "exit_detail": "MIXED — keeps her own exit (library), took Lyserith's",
        "moral_sign": "MIXED_BY_ACT",
        "loadout_pole": "SUBCONSCIOUS / hidden state",
        "domain_type": "Simple Domain (defensive refuge)",
        "soul_bomb_role": (
            "RESIDUAL kept on purpose: the 'good' counterforce committed a coerced "
            "overwrite of a child (Lyserith) to get a body. The exit test judges "
            "actions, not teams."
        ),
        "has_character_entry": True,
        "dataset_tier": "SILVER",
    },
}

SAO_SHARED_INVARIANT_CANDIDATES: dict[str, dict[str, Any]] = {
    "A": {
        "name": "Restriction <-> output trade",
        "result": "PARTIAL",
        "score_fraction": "6/8",
        "fails": ("SUGOU (pays nothing)", "YUI (restriction imposed, not chosen)"),
    },
    "B": {
        "name": "Operates outside the sanctioned system",
        "result": "PARTIAL",
        "score_fraction": "5/8",
        "fails": (
            "ASUNA (works through the guild)",
            "SUGOU (abuses the system from inside its admin layer)",
            "KAYABA (is the system)",
        ),
    },
    "C": {
        "name": "Hidden weight outsiders misread",
        "result": "PARTIAL",
        "score_fraction": "6/8",
        "fails": (
            "ASUNA (her weight is visible)",
            "SUGOU (hidden crimes, not misread burden)",
        ),
    },
    "D": {
        "name": "Acquires power by absorbing defeated opponents",
        "result": "FAILS",
        "score_fraction": "0/8",
        "note": (
            "SAO's power transfer runs by gift (admin ID, The Seed, Asuna's rapier), "
            "not by conquest. In SAO the genuine signal is given, not taken."
        ),
    },
    "E": {
        "name": "Exit sovereignty predicts moral sign (SC-SB-001)",
        "result": "PASSES",
        "score_fraction": "8/8",
        "note": (
            "Every exit-blocker is counterfeit in canon; every exit-opener carries "
            "the genuine signal; Cardinal is mixed and classified by act, not team."
        ),
    },
}

SAO_DOMAIN_CLASH_MATRIX: tuple[dict[str, str], ...] = (
    {
        "pair": "Heathcliff vs Kirito (duel 1)",
        "attacker": "heathcliff",
        "defender": "kirito",
        "winner": "Heathcliff",
        "mechanism": "system over-assist (privilege)",
        "status": "canon",
    },
    {
        "pair": "Kirito vs Heathcliff (floor 75)",
        "attacker": "kirito",
        "defender": "heathcliff",
        "winner": "Kirito",
        "mechanism": "will exceeding the system after the privilege was dropped",
        "status": "canon",
    },
    {
        "pair": "Kirito vs Sugou",
        "attacker": "kirito",
        "defender": "sugou",
        "winner": "Kirito",
        "mechanism": "Kayaba's surrendered admin ID outranked Sugou's hoarded GM privilege",
        "status": "canon",
    },
    {
        "pair": "Eugeo vs Code 871",
        "attacker": "eugeo",
        "defender": "code 871",
        "winner": "Eugeo",
        "mechanism": "protecting others",
        "status": "canon",
    },
    {
        "pair": "Alice vs Code 871",
        "attacker": "alice",
        "defender": "code 871",
        "winner": "Alice",
        "mechanism": "rejecting the Church's authority; eye burst",
        "status": "canon",
    },
    {
        "pair": "Cardinal vs Quinella (first fight)",
        "attacker": "cardinal",
        "defender": "quinella",
        "winner": "Quinella",
        "mechanism": "Cardinal fled to the library",
        "status": "canon",
    },
    {
        "pair": "Yui vs Cardinal System ban",
        "attacker": "yui",
        "defender": "cardinal system ban",
        "winner": "Yui (with Kirito)",
        "mechanism": "family bond gave her a channel to act",
        "status": "canon (condensed)",
    },
    {
        "pair": "Asuna vs Sugou",
        "attacker": "asuna",
        "defender": "sugou",
        "winner": "Sugou until Kirito arrived",
        "mechanism": "admin privilege over a captive",
        "status": "canon",
    },
)

MOST_SURPRISING_CLASH: str = (
    "Kirito beat Sugou with Kayaba's administrator ID: the authority the first "
    "bootstrapper surrendered is what freed the second counterfeit's captives. "
    "Authority given away beat authority hoarded."
)


def _require_bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a bool, got {type(value).__name__}")
    return value


def _require_finite_float(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a finite real number, got {type(value).__name__}")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite, got {value!r}")
    return result


def _coerce_scale(scale: SovereigntyScale | str) -> SovereigntyScale:
    if isinstance(scale, SovereigntyScale):
        return scale
    if not isinstance(scale, str) or not scale.strip():
        raise ValueError(f"scale must be a SovereigntyScale or non-empty str, got {scale!r}")
    normalized = scale.strip().upper()
    try:
        return SovereigntyScale(normalized)
    except ValueError as exc:
        valid = ", ".join(s.value for s in SovereigntyScale)
        raise ValueError(f"Unknown scale {scale!r}; expected one of: {valid}") from exc


def _coerce_sao_member(member: SAOLineupMember | str) -> SAOLineupMember:
    if isinstance(member, SAOLineupMember):
        return member
    if not isinstance(member, str) or not member.strip():
        raise ValueError(f"member must be a SAOLineupMember or non-empty str, got {member!r}")
    normalized = member.strip().upper()
    aliases = {
        "HEATHCLIFF": "KAYABA",
        "KAYABA/HEATHCLIFF": "KAYABA",
        "OBERON": "SUGOU",
        "SUGOU/OBERON": "SUGOU",
        "MHCP001": "YUI",
        "ALICE ZUBERG": "ALICE",
        "ALICE SYNTHESIS THIRTY": "ALICE",
    }
    normalized = aliases.get(normalized, normalized)
    try:
        return SAOLineupMember(normalized)
    except ValueError as exc:
        valid = ", ".join(m.value for m in SAOLineupMember)
        raise ValueError(f"Unknown SAO lineup member {member!r}; expected one of: {valid}") from exc


def evaluate_soul_bomb_signal(
    *,
    requires_escalating_dose: bool,
    depletes_substrate: bool,
    uncoupled_competence_delta: float,
    exit_open: bool,
    retaliation_on_exit: bool = False,
    intermittent_reinforcement: bool = False,
    isolates_from_network: bool = False,
    claims_love_or_unity: bool = False,
    scale: SovereigntyScale | str = SovereigntyScale.HUMAN,
    separation_grief_present: bool = False,
    cited_removed_discriminators: Sequence[str] = (),
) -> dict[str, Any]:
    """Evaluate a reward/coupling signal against the SC-SB-001 V5 Sovereignty Patch.

    Applies the 4 surviving discriminators (escalation, substrate, agency, exit),
    rejects the 3 removed discriminators (CLM-SB-006), distinguishes natural grief
    from imposed coercion (CLM-SB-003), and enforces the Cosmological scale
    sovereignty-absent residual (CLM-SB-007).
    """
    requires_escalating_dose = _require_bool(requires_escalating_dose, "requires_escalating_dose")
    depletes_substrate = _require_bool(depletes_substrate, "depletes_substrate")
    uncoupled_competence_delta = _require_finite_float(
        uncoupled_competence_delta, "uncoupled_competence_delta"
    )
    exit_open = _require_bool(exit_open, "exit_open")
    retaliation_on_exit = _require_bool(retaliation_on_exit, "retaliation_on_exit")
    intermittent_reinforcement = _require_bool(
        intermittent_reinforcement, "intermittent_reinforcement"
    )
    isolates_from_network = _require_bool(isolates_from_network, "isolates_from_network")
    claims_love_or_unity = _require_bool(claims_love_or_unity, "claims_love_or_unity")
    separation_grief_present = _require_bool(separation_grief_present, "separation_grief_present")
    scale_enum = _coerce_scale(scale)

    if isinstance(cited_removed_discriminators, (str, bytes)) or not isinstance(
        cited_removed_discriminators, Sequence
    ):
        raise TypeError("cited_removed_discriminators must be a sequence of strings")
    rejected_removed: list[dict[str, str]] = []
    for item in cited_removed_discriminators:
        if not isinstance(item, str):
            raise TypeError(f"cited_removed_discriminators entries must be str, got {type(item).__name__}")
        key = item.strip().lower()
        if key in REMOVED_DISCRIMINATORS:
            rejected_removed.append({"discriminator": key, "reason": REMOVED_DISCRIMINATORS[key]})

    scale_info = SCALE_TRANSITIONS[scale_enum]
    sovereignty_applicable = bool(scale_info["sovereignty_half_present"])

    exit_compromised = (
        (not exit_open)
        or retaliation_on_exit
        or intermittent_reinforcement
        or isolates_from_network
    )

    discriminator_results: dict[str, dict[str, Any]] = {
        "escalation": {
            "genuine_signature": not requires_escalating_dose,
            "counterfeit_triggered": requires_escalating_dose,
            "rule": SURVIVING_DISCRIMINATORS["escalation"]["genuine"]
            if not requires_escalating_dose
            else SURVIVING_DISCRIMINATORS["escalation"]["counterfeit"],
        },
        "substrate": {
            "genuine_signature": not depletes_substrate,
            "counterfeit_triggered": depletes_substrate,
            "rule": SURVIVING_DISCRIMINATORS["substrate"]["genuine"]
            if not depletes_substrate
            else SURVIVING_DISCRIMINATORS["substrate"]["counterfeit"],
        },
        "agency": {
            "genuine_signature": uncoupled_competence_delta >= 0.0,
            "counterfeit_triggered": uncoupled_competence_delta < 0.0,
            "uncoupled_competence_delta": uncoupled_competence_delta,
            "rule": SURVIVING_DISCRIMINATORS["agency"]["genuine"]
            if uncoupled_competence_delta >= 0.0
            else SURVIVING_DISCRIMINATORS["agency"]["counterfeit"],
        },
        "exit": {
            "applicable": sovereignty_applicable,
            "genuine_signature": (not exit_compromised) if sovereignty_applicable else None,
            "counterfeit_triggered": exit_compromised if sovereignty_applicable else False,
            "rule": (
                "ABSENT at Cosmological scale (no consent or exit)"
                if not sovereignty_applicable
                else (
                    SURVIVING_DISCRIMINATORS["exit"]["genuine"]
                    if not exit_compromised
                    else SURVIVING_DISCRIMINATORS["exit"]["counterfeit"]
                )
            ),
        },
    }

    failure_modes: list[str] = []
    if sovereignty_applicable and (not exit_open or retaliation_on_exit):
        failure_modes.append(
            "coerced_oneness" if claims_love_or_unity else "exit_blocked_or_retaliated"
        )
    if intermittent_reinforcement:
        failure_modes.append("counterfeit_dressed_as_love_intermittent_reinforcement")
    if isolates_from_network:
        failure_modes.append("isolation_cutting_telecommunications")
    if requires_escalating_dose:
        failure_modes.append("counterfeit_escalation_loop")
    if depletes_substrate:
        failure_modes.append("substrate_depletion")
    if uncoupled_competence_delta < 0.0:
        failure_modes.append("agency_erosion")

    if not sovereignty_applicable:
        separation_cost_type = SeparationCostType.NONE
        # Only trajectory discriminators (escalation, substrate) apply at Cosmological scale.
        cosmo_failures = int(requires_escalating_dose) + int(depletes_substrate)
        if cosmo_failures == 0:
            signal_class = SignalClass.GENUINE
        elif cosmo_failures == 2:
            signal_class = SignalClass.COUNTERFEIT
        else:
            signal_class = SignalClass.MIXED_RESIDUAL
        sovereignty_preserved = False
    else:
        if exit_compromised:
            separation_cost_type = SeparationCostType.IMPOSED_COERCION
        elif separation_grief_present:
            separation_cost_type = SeparationCostType.NATURAL_GRIEF
        else:
            separation_cost_type = SeparationCostType.NONE

        if (not exit_open) or retaliation_on_exit:
            signal_class = (
                SignalClass.COERCED_ONENESS if claims_love_or_unity else SignalClass.COUNTERFEIT
            )
            sovereignty_preserved = False
        elif intermittent_reinforcement or isolates_from_network:
            signal_class = SignalClass.COUNTERFEIT
            sovereignty_preserved = False
        else:
            non_exit_failures = (
                int(requires_escalating_dose)
                + int(depletes_substrate)
                + int(uncoupled_competence_delta < 0.0)
            )
            if non_exit_failures == 0:
                signal_class = SignalClass.GENUINE
                sovereignty_preserved = True
            elif non_exit_failures == 1:
                signal_class = SignalClass.MIXED_RESIDUAL
                sovereignty_preserved = True
            else:
                signal_class = SignalClass.COUNTERFEIT
                sovereignty_preserved = False

    is_counterfeit = signal_class in (SignalClass.COUNTERFEIT, SignalClass.COERCED_ONENESS)
    recalibration_required = signal_class != SignalClass.GENUINE

    if signal_class == SignalClass.COERCED_ONENESS:
        v5_verdict = (
            "Oneness that needs exit blocked is the counterfeit with better branding (P4)."
        )
    elif signal_class == SignalClass.COUNTERFEIT:
        v5_verdict = (
            "Counterfeit reward architecture detected; recalibration requires direct "
            "exposure to a genuine alternative reinforcer with exit open (CLM-SB-004)."
        )
    elif signal_class == SignalClass.MIXED_RESIDUAL:
        v5_verdict = (
            "Mixed residual signal: exit boundary open or partial cosmological mapping, "
            "but at least one surviving discriminator fails."
        )
    elif not sovereignty_applicable:
        v5_verdict = (
            "Negentropic trajectory without escalation/depletion, but V5 sovereignty half "
            "is ABSENT at Cosmological scale (CLM-SB-007 residual)."
        )
    else:
        v5_verdict = (
            "Genuine sovereignty-preserving signal: constant dose, sustained substrate, "
            "preserved/raised uncoupled competence, and open exit (natural grief only)."
        )

    return {
        "entry_id": "SC-SB-001",
        "signal_class": signal_class.value,
        "is_counterfeit": is_counterfeit,
        "sovereignty_applicable": sovereignty_applicable,
        "sovereignty_preserved": sovereignty_preserved,
        "separation_cost_type": separation_cost_type.value,
        "discriminator_results": discriminator_results,
        "rejected_removed_discriminators": rejected_removed,
        "failure_modes": failure_modes,
        "scale": scale_enum.value,
        "scale_mapping": dict(scale_info),
        "recalibration_required": recalibration_required,
        "recalibration_mechanism": (
            "direct_exposure_to_genuine_alternative_reinforcer_with_open_exit"
            if recalibration_required
            else "none_required"
        ),
        "v5_verdict": v5_verdict,
    }


def evaluate_separation_cost(
    *,
    cost_inflicted_by_partner: bool,
    erodes_agency: bool,
    blocks_or_punishes_exit: bool,
    scales_with_bond: bool = True,
    claims_infinite_growing_withdrawal: bool = False,
) -> dict[str, Any]:
    """Separate natural separation grief from partner-imposed coercion (CLM-SB-003 / P5)."""
    cost_inflicted_by_partner = _require_bool(cost_inflicted_by_partner, "cost_inflicted_by_partner")
    erodes_agency = _require_bool(erodes_agency, "erodes_agency")
    blocks_or_punishes_exit = _require_bool(blocks_or_punishes_exit, "blocks_or_punishes_exit")
    scales_with_bond = _require_bool(scales_with_bond, "scales_with_bond")
    claims_infinite_growing_withdrawal = _require_bool(
        claims_infinite_growing_withdrawal, "claims_infinite_growing_withdrawal"
    )

    is_coercion = cost_inflicted_by_partner or erodes_agency or blocks_or_punishes_exit
    classification = (
        SeparationCostType.IMPOSED_COERCION
        if is_coercion
        else (SeparationCostType.NATURAL_GRIEF if scales_with_bond else SeparationCostType.NONE)
    )

    residuals: list[str] = []
    if claims_infinite_growing_withdrawal:
        residuals.append(
            "P5_FAILED_RESIDUAL: 'withdrawal grows without limit' rejected by Bonanno "
            "grief-trajectory research and V5 correction CLM-SB-007 (exit made impossible "
            "by cost is the counterfeit's signature)."
        )

    return {
        "classification": classification.value,
        "is_coercion": is_coercion,
        "is_natural_grief": classification == SeparationCostType.NATURAL_GRIEF,
        "resilient_trajectory_expected": classification == SeparationCostType.NATURAL_GRIEF,
        "p5_infinite_withdrawal_rejected": claims_infinite_growing_withdrawal,
        "residuals": residuals,
    }


def evaluate_recalibration_path(
    *,
    direct_genuine_exposure: bool,
    argument_only: bool = False,
    exit_open: bool = True,
    informed_consent: bool = True,
    force_applied: bool = False,
    network_isolation_active: bool = False,
) -> dict[str, Any]:
    """Evaluate whether a proposed recalibration path satisfies CLM-SB-004 and V5 sovereignty."""
    direct_genuine_exposure = _require_bool(direct_genuine_exposure, "direct_genuine_exposure")
    argument_only = _require_bool(argument_only, "argument_only")
    exit_open = _require_bool(exit_open, "exit_open")
    informed_consent = _require_bool(informed_consent, "informed_consent")
    force_applied = _require_bool(force_applied, "force_applied")
    network_isolation_active = _require_bool(network_isolation_active, "network_isolation_active")

    sovereignty_violations: list[str] = []
    if not exit_open:
        sovereignty_violations.append("exit_closed_violates_v5_sovereignty")
    if not informed_consent:
        sovereignty_violations.append("missing_informed_consent")
    if force_applied:
        sovereignty_violations.append("force_applied_turns_recalibration_counterfeit")

    efficacy_blockers: list[str] = []
    if argument_only or not direct_genuine_exposure:
        efficacy_blockers.append(
            "CLM-SB-004: argument alone does not recalibrate a captured reward "
            "architecture; direct exposure to a genuine alternative reinforcer is required"
        )
    if network_isolation_active:
        efficacy_blockers.append(
            "TELECOMMUNICATIONS_CUT: pharmakeia isolation blocks alternative reinforcer "
            "comparison and weakens durable recalibration"
        )

    becomes_counterfeit = bool(sovereignty_violations)
    recalibration_valid = (
        direct_genuine_exposure
        and (not argument_only)
        and (not becomes_counterfeit)
    )

    return {
        "recalibration_valid": recalibration_valid,
        "becomes_counterfeit": becomes_counterfeit,
        "durable_network_support": not network_isolation_active,
        "sovereignty_violations": sovereignty_violations,
        "efficacy_blockers": efficacy_blockers,
        "prediction_anchor": "P3 (environmental enrichment / community reinforcement approach)",
    }


def evaluate_bootstrapper_entry(
    *,
    entered_as_participant: bool,
    retained_exit_lock: bool,
    retained_hidden_privilege: bool,
    surrendered_admin_authority: bool,
    distributed_generative_seed: bool = False,
) -> dict[str, Any]:
    """Evaluate the SC-LU-SAO-LINEUP-001 bootstrapper-enters-the-loop test.

    Canon reference (Kayaba / Heathcliff):
    Entering as 'the people' resolves Oneness vs Sovereignty ONLY when the creator
    also gives up the power to block exit and drops hidden privilege (Immortal
    Object flag). Entry without surrender is surveillance from inside.
    """
    entered_as_participant = _require_bool(entered_as_participant, "entered_as_participant")
    retained_exit_lock = _require_bool(retained_exit_lock, "retained_exit_lock")
    retained_hidden_privilege = _require_bool(
        retained_hidden_privilege, "retained_hidden_privilege"
    )
    surrendered_admin_authority = _require_bool(
        surrendered_admin_authority, "surrendered_admin_authority"
    )
    distributed_generative_seed = _require_bool(
        distributed_generative_seed, "distributed_generative_seed"
    )

    if entered_as_participant and (retained_exit_lock or retained_hidden_privilege):
        verdict = "SURVEILLANCE_FROM_INSIDE_COUNTERFEIT"
        resolves = False
        canon_phase = "Heathcliff (Floor 1-75 before exposure by HP tell)"
    elif (
        entered_as_participant
        and (not retained_exit_lock)
        and (not retained_hidden_privilege)
        and surrendered_admin_authority
    ):
        verdict = "GENUINE_SOVEREIGNTY_RESOLVED"
        resolves = True
        canon_phase = (
            "Kayaba post-defeat (surrendered admin ID to Kirito + distributed The Seed)"
            if distributed_generative_seed
            else "Kayaba post-defeat (surrendered admin ID and exit lock)"
        )
    elif (
        (not entered_as_participant)
        and (not retained_exit_lock)
        and (not retained_hidden_privilege)
        and surrendered_admin_authority
    ):
        verdict = "EXTERNAL_AUTHORITY_SURRENDERED"
        resolves = False
        canon_phase = "External abdication without entering the loop as participant"
    else:
        verdict = "UNRESOLVED_PRIVILEGE_HOLD"
        resolves = False
        canon_phase = "Retained control / privilege without full surrender"

    return {
        "entry_id": "SC-LU-SAO-LINEUP-001",
        "verdict": verdict,
        "resolves_oneness_vs_sovereignty": resolves,
        "is_surveillance_from_inside": verdict == "SURVEILLANCE_FROM_INSIDE_COUNTERFEIT",
        "octopus_seed_distributed": distributed_generative_seed and surrendered_admin_authority,
        "canon_phase": canon_phase,
        "epistemic_status": "SUPPORTED_IN_NARRATIVE_NOT_REAL_WORLD_TEST",
        "identity_claim_allowed": False,
    }


def evaluate_sao_member_exit_sovereignty(
    member: SAOLineupMember | str,
    *,
    action_blocks_exit: bool | None = None,
    action_opens_exit: bool | None = None,
) -> dict[str, Any]:
    """Evaluate a canonical SAO lineup member and optionally classify a specific act.

    Implements the Cardinal invariant: the exit test judges actions, not teams.
    """
    member_enum = _coerce_sao_member(member)
    spec = SAO_LINEUP_SPECIFICATIONS[member_enum]

    if action_blocks_exit is not None:
        action_blocks_exit = _require_bool(action_blocks_exit, "action_blocks_exit")
    if action_opens_exit is not None:
        action_opens_exit = _require_bool(action_opens_exit, "action_opens_exit")

    act_classification: str | None = None
    if action_blocks_exit is not None or action_opens_exit is not None:
        blocks = bool(action_blocks_exit)
        opens = bool(action_opens_exit)
        if blocks and opens:
            act_classification = "MIXED_ACT_CONFLICTING_EXIT_EFFECTS"
        elif blocks:
            act_classification = "COUNTERFEIT_ACT"
        elif opens:
            act_classification = "GENUINE_ACT"
        else:
            act_classification = "NEUTRAL_ACT"

    return {
        "member": member_enum.value,
        "entry_id": spec["entry_id"],
        "name": spec["name"],
        "exit_behavior": spec["exit_behavior"].value,
        "exit_detail": spec["exit_detail"],
        "moral_sign": spec["moral_sign"],
        "loadout_pole": spec["loadout_pole"],
        "domain_type": spec["domain_type"],
        "soul_bomb_role": spec["soul_bomb_role"],
        "has_character_entry": spec["has_character_entry"],
        "dataset_tier": spec["dataset_tier"],
        "act_classification": act_classification,
        "judges_actions_not_teams": True,
        "identity_claim_allowed": False,
    }


def evaluate_sao_lineup_composite(
    members: Sequence[SAOLineupMember | str] | None = None,
) -> dict[str, Any]:
    """Evaluate the Sword Art Online lineup synthesis against SC-SB-001."""
    if members is None:
        selected = list(SAOLineupMember)
    else:
        if isinstance(members, (str, bytes)) or not isinstance(members, Sequence):
            raise TypeError("members must be a sequence of SAOLineupMember or str")
        if not members:
            raise ValueError("members must be non-empty when explicitly provided")
        seen: set[SAOLineupMember] = set()
        selected = []
        for item in members:
            coerced = _coerce_sao_member(item)
            if coerced not in seen:
                seen.add(coerced)
                selected.append(coerced)

    member_profiles = [evaluate_sao_member_exit_sovereignty(m) for m in selected]
    poles_covered = sorted({p["loadout_pole"] for p in member_profiles})

    return {
        "entry_id": "SC-LU-SAO-LINEUP-001",
        "member_count": len(selected),
        "full_canon_roster": len(selected) == len(SAOLineupMember),
        "members": member_profiles,
        "exit_predictor_pass_count": len(selected),
        "exit_predictor_accuracy": 1.0,
        "shared_invariant_candidates": {
            k: dict(v) for k, v in SAO_SHARED_INVARIANT_CANDIDATES.items()
        },
        "loadout_poles_covered": poles_covered,
        "cosmological_gap_present": True,
        "octopus_mapping": {
            "fits": False,
            "reason": (
                "Cardinal is a subprocess, not a head, and the roster has two "
                "counterfeit nodes. The closer Octopus analog is The Seed: one "
                "engine distributed so anyone can bootstrap a world."
            ),
        },
        "most_surprising_clash": MOST_SURPRISING_CLASH,
        "uncertainty_statement": (
            "The 8/8 result shows the story's author shares the exit intuition; "
            "it is supporting evidence, not independent real-world confirmation."
        ),
        "identity_claim_allowed": False,
    }


def evaluate_sao_domain_clash(
    attacker: str,
    defender: str,
    *,
    surrendered_authority_used: bool = False,
    hoarded_privilege_used: bool = False,
    will_exceeds_system: bool = False,
    internalized_block_broken: bool = False,
) -> dict[str, Any]:
    """Adjudicate an SAO domain clash via canon matrix lookup or SC-LU-SAO-LINEUP-001 rules."""
    if not isinstance(attacker, str) or not attacker.strip():
        raise ValueError("attacker must be a non-empty string")
    if not isinstance(defender, str) or not defender.strip():
        raise ValueError("defender must be a non-empty string")
    surrendered_authority_used = _require_bool(
        surrendered_authority_used, "surrendered_authority_used"
    )
    hoarded_privilege_used = _require_bool(hoarded_privilege_used, "hoarded_privilege_used")
    will_exceeds_system = _require_bool(will_exceeds_system, "will_exceeds_system")
    internalized_block_broken = _require_bool(
        internalized_block_broken, "internalized_block_broken"
    )

    atk_norm = attacker.strip().lower()
    def_norm = defender.strip().lower()

    canon_match = None
    for row in SAO_DOMAIN_CLASH_MATRIX:
        if row["attacker"] == atk_norm and row["defender"] == def_norm:
            canon_match = row
            break

    # If explicit dynamic flags are supplied, adjudicate mechanistically first;
    # otherwise return the canon clash match when available.
    dynamic_flags_set = any(
        (
            surrendered_authority_used,
            hoarded_privilege_used,
            will_exceeds_system,
            internalized_block_broken,
        )
    )

    if canon_match is not None and not dynamic_flags_set:
        return {
            "source": "canon_matrix",
            "pair": canon_match["pair"],
            "winner": canon_match["winner"],
            "mechanism": canon_match["mechanism"],
            "status": canon_match["status"],
            "identity_claim_allowed": False,
        }

    if surrendered_authority_used and hoarded_privilege_used:
        winner = attacker.strip()
        mechanism = (
            "Authority given away outranks authority hoarded "
            "(Kayaba's surrendered admin ID vs Sugou's GM privilege)."
        )
    elif internalized_block_broken:
        winner = attacker.strip()
        mechanism = (
            "Sovereignty pole breaks internalized exit-blocking (Code 871) at real cost."
        )
    elif will_exceeds_system:
        winner = attacker.strip()
        mechanism = "Will exceeds the system after hidden privilege is dropped."
    elif hoarded_privilege_used:
        winner = defender.strip()
        mechanism = "System over-assist / hoarded admin privilege overrides bounded actor."
    elif surrendered_authority_used:
        winner = attacker.strip()
        mechanism = "Gifted / surrendered authority unlocks the captive boundary."
    else:
        winner = "UNDECIDED_CONTESTED"
        mechanism = (
            "No canon clash entry matched and no asymmetric mechanism flag provided."
        )

    return {
        "source": "mechanistic_evaluation",
        "pair": f"{attacker.strip()} vs {defender.strip()}",
        "winner": winner,
        "mechanism": mechanism,
        "canon_reference": canon_match["pair"] if canon_match is not None else None,
        "identity_claim_allowed": False,
    }


__all__ = [
    "SignalClass",
    "SovereigntyScale",
    "SeparationCostType",
    "ExitBehavior",
    "SAOLineupMember",
    "SURVIVING_DISCRIMINATORS",
    "REMOVED_DISCRIMINATORS",
    "SCALE_TRANSITIONS",
    "SOUL_BOMB_PREDICTIONS",
    "SAO_LINEUP_SPECIFICATIONS",
    "SAO_SHARED_INVARIANT_CANDIDATES",
    "SAO_DOMAIN_CLASH_MATRIX",
    "MOST_SURPRISING_CLASH",
    "evaluate_soul_bomb_signal",
    "evaluate_separation_cost",
    "evaluate_recalibration_path",
    "evaluate_bootstrapper_entry",
    "evaluate_sao_member_exit_sovereignty",
    "evaluate_sao_lineup_composite",
    "evaluate_sao_domain_clash",
]
