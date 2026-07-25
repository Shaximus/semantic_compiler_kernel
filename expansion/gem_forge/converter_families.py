"""Named missing-converter families for PARTIAL / UNRESOLVED gem lines.

Every line the translator leaves PARTIAL (multi-converter overlap, clause only
partially transferred) or UNRESOLVED (no converter matched) is assigned to a
precisely named converter family — the family of converter that WOULD resolve
it. Families are derived from the actual unmatched patterns of the pinned
corpus; there is deliberately no generic bucket (no "other", no "misc": a line
that matches nothing surfaces as ``UNCLASSIFIED_LINE`` so the gap is loud, and
the registry builder fails rather than silently bucketing it).

Each registry entry carries: family name, example unmatched lines (at least
three where the corpus provides them), a proposed transfer-language template,
and gem coverage (distinct gems containing a line of the family).

Classification is deterministic: ordered rules, first match wins, regex over
the casefolded line.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class ConverterFamilyRule:
    family: str
    template: str
    pattern: str
    description: str


# Ordered specific -> broad. First match wins.
CONVERTER_FAMILY_RULES: tuple[ConverterFamilyRule, ...] = (
    ConverterFamilyRule(
        "CONVERTER_FAMILY:exerted_next_attack_empowerment",
        "empowers the next {n} melee executions in the stream (queued empowerment window — requires next-execution decorator over the attack pipeline)",
        r"exert|empowers_next_x_melee|number_of_warcries_exerting|empowerd_attacks",
        "Warcry-style 'Exerts the next N attacks' empowerment windows and exerted-attack modifiers.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:warcry_power_accumulation",
        "accumulates {resource} power scaled by affected targets, then spends it on area denial/taunt effects (requires per-target power ledger primitive)",
        r"warcry|warcies|per \d+ power|minimum of [\d.]+ power|_cry\b|power_from_enemies",
        "Warcry power counting, per-power summons, minimum power floors.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:rage_economy",
        "builds and spends a rage-style escalation resource over time (gain-on-hit, decay-per-second, threshold activation — requires escalation-resource ledger)",
        r"\brage|rage_|berserk",
        "Rage gain/loss rates, rage thresholds, Berserk, Ragestorm sacrifice, enemy rage regen.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:stage_accumulation_over_time",
        "accumulates execution stages or seals on a timer or trigger, up to a cap, and discharges them on release (requires staged-charge state machine)",
        r"\bstages?\b|banner_add_stage|on placing the banner|maximum fortification|\bseal",
        "Stage gain/loss over time, stage caps, banner placement effects, seal gain frequency.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:charge_gain_on_event",
        "mints a success counter when a scoped event fires (kill / detonation / hit / enemy-death-in-zone — requires event-scoped counter minting)",
        r"gain (a|an) \w+ charge|charge when|charge on (hit|kill)|gains? a? ?\w* ?charge",
        "Power/Frenzy/Endurance charge grants keyed to events.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:charge_consumption_conditional",
        "applies a conditional modifier when success counters are consumed (per charge removed / if charges consumed — requires consume-triggered modifier hook)",
        r"charge(s)? (were )?(removed|consumed)|charge types removed|per \w+ charge removed",
        "Modifiers conditional on charge removal or consumption.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:intensity_stack_mechanics",
        "builds and loses intensity stacks that gate per-stack payload scaling (requires intensity-ledger primitive)",
        r"intensity",
        "Intensity gain/loss cadence and per-intensity scaling.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:per_stack_resource_scaling",
        "scales {effect} by {magnitude} per active stack of {stack_resource} (stack-count-coupled modifier — requires a stack ledger primitive)",
        r"per (frenzy|power|endurance) charge\b|per charge\b|per \d+ doom|per doom|per corpse|per \d+ maximum|per 100|per 5 rage",
        "Damage/effect scaling per charge, doom, corpse, or equipment stack.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:impale_application_and_effect",
        "stores a fraction of accepted payload impact and replays it on subsequent executions (impale = deferred self-similar payload — requires impact-replay primitive)",
        r"impale",
        "Impale chance on hit, impale effect magnitude, additional impales.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:knockback_displacement",
        "applies a displacement vector to the accepted target (knockback distance scaling — requires target-displacement primitive)",
        r"knock",
        "Knockback chance and knockback distance modifiers.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:shared_field_ally_grant",
        "extends the persistent modifier field's payload to the executor and compatible agents in scope (you and nearby allies — requires scope-shared grant channel)",
        r"^you and ",
        "'You and nearby Allies ...' aura payload lines: shared damage, defenses, regeneration, avoidance, accuracy.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:on_hit_debuff_application",
        "applies a named degraded-state modifier to the accepted target with {probability} probability (blind/taunt/maim/crush/intimidate/unnerve/debilitate/flee — requires named-debuff registry)",
        r"chance to (blind|taunt|maim|intimidate|unnerve|crush|debilitate|hinder)|monsters to flee|converted enemies have|chance to poison|debilitate",
        "Chance-on-hit application of named non-ailment debuffs.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:typed_susceptibility_application",
        "applies a typed or stacking susceptibility field on hit (exposure / withered / webs — requires typed-susceptibility registry with per-type caps)",
        r"exposure|withered|\bweb",
        "Cold/Fire/Lightning exposure, withered stacks, spider-web caps.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:buff_effect_scaling",
        "amplifies the magnitude of a named persistent modifier field (effect-of-buff scaling — requires named-buff registry with magnitude channel)",
        r"effect of|effect\b.*granted",
        "Increased effect of named buffs (Maim, Elusive, Cruelty, Infusion, Consecrated Ground, Onslaught, Combat Rush, Overpowered, ancestor totem buff).",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:named_buff_grant_and_duration",
        "grants a named temporary modifier field for {duration} on its trigger condition (adrenaline/onslaught/infusion/phasing/fortify/tailwind/elusive/combat rush/innervation/arcane surge/mirage archer — requires named-buff lifecycle primitive)",
        r"adrenaline|onslaught|infusion|phasing|fortif|tailwind|elusive|innervation|arcane surge|combat rush|mirage archer|phantasms last|cruelty|overpowered|\blasts?\b|stealth",
        "Grants and durations of named temporary buffs.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:brand_attachment_mechanics",
        "binds a detachable execution locus to a target and activates it periodically while attached (brand = sticky proxy — requires attach/detach proxy primitive)",
        r"brand",
        "Brand attach/detach rules, activation cadence while attached, brand cost share.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:beam_attachment_mechanics",
        "attaches continuous beam channels to the closest {n} targets, ticking at a fixed interval (beam = persistent channel — requires channel-tick primitive)",
        r"\bbeams?\b",
        "Beam attachment counts, beam tick rates, beam split/fork behavior, beam geometry.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:periodic_pulse_activation",
        "activates a payload emission every {interval} while its condition holds (pulse/strike/impact/emission cadence — requires scheduled-emission primitive)",
        r"every [\d.]+ seconds?|frequency|pulses? every|every \d+ pulses|once every|fires projectiles|projectiles.*faster",
        "Fixed-interval activations, pulse frequencies, emission rates, per-target rate limits.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:volley_sequence_emission",
        "emits payloads as a counted sequence of volleys with inter-volley spacing (requires sequenced-burst primitive)",
        r"volley|sequence of arrows|sequences of arrows",
        "Volley counts, distances between volleys, additional arrow sequences.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:projectile_bifurcation_and_bounce",
        "splits/forks/bounces a candidate trajectory into {n} child trajectories with per-hop rules (requires trajectory-splitting primitive)",
        r"\bfork|split towards|bounce|chaining range|this skill has chained|remaining chain|instead of chaining|chain_distance|zig_?zags?|changes direction|pierce|frostbolt",
        "Fork, split, bounce, chain-range, direction-change, and cross-payload (Frostbolt) interactions.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:secondary_emission_and_object_creation",
        "spawns {n} secondary emissions or persistent objects per trigger, with variant probabilities (supercharged/wrong-variant — requires counted-secondary-emission primitive with variant table)",
        r"fires? \d+|additional (spikes|blades|fissures|projectiles|arrows|corpse)|creates? [\d.]+|causes? [\d.]+|secondary projectiles|extra projectiles|thorn arrows|\bflames\b|smaller explosions|\bbursts\b|additional animate weapon copy|additional blade|additional fissure|spikes\b|lingering blade|bladestorm|consecrated ground|fungal ground|leaves a|in the ground|ground at|nova|explosions?\b|explode|supercharged|\bwrong\b",
        "Counts of secondary projectiles/spikes/explosions/novas, lingering ground objects, variant-upgrade and fumble chances.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:projectile_damage_scaling",
        "scales effectiveness of the projectile-class candidate stream specifically (requires per-class effectiveness channel)",
        r"projectile damage",
        "More/less/increased projectile damage lines the generic damage family excludes.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:sequential_section_emission",
        "emits wall/section segments on a fixed appearance schedule with declared segment length (requires segmented-emission scheduler)",
        r"between appearance|wall sections|wall will be",
        "Seconds between appearance of wall sections; wall segment lengths.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:additional_targets_and_firing_points",
        "adds {n} eligible targets or spatial firing origins to each execution (requires target-fan-out and multi-origin emission channels)",
        r"target \d|additional (nearby )?enem|hit an additional enemy|strikes target|points on each side|firing points",
        "Melee strikes hitting additional enemies; projectiles fired from side points.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:concurrent_object_and_queue_cap",
        "caps concurrently active spawned objects or queued pending executions at {n} (requires object-pool and queue concurrency caps)",
        r"can have up to|maximum of \d|maximum \d|at a time|corpses allowed|allowed\b|number of \w+ allowed|queue",
        "Caps on active blades, orbs, geysers, bladestorms, barriers, corpses, wolves, queued uses.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:corpse_resource_mechanics",
        "consumes/spawns/destroys corpse-class resources as execution fuel (requires corpse-inventory resource model)",
        r"corpse",
        "Corpse consumption, spawning levels, destruction on kill, forgotten-corpse chance.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:expendable_consumable_resource",
        "grants and spends a consumable execution resource (steel shards / vaal souls / flask charges — requires ammunition/voucher/reserve ledgers with rate limits)",
        r"steel shard|\bsoul|vaal|flask",
        "Steel shard ammunition, vaal-soul vouchers, flask-charge consumption.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:conditional_proxy_summon",
        "summons a bounded proxy worker when a scoped trigger fires (on hitting rare/unique, from corpses per power — requires conditional-summon controller)",
        r"chance to summon|summon a sentinel|summons .* (when|from|on)|mirage warrior|arbalist|sentinel",
        "Sentinel / Mirage Warrior / Arbalist conditional summons.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:artifact_level_quality_upgrade",
        "raises the level, quality, experience, or improvement count of the payload artifact itself (meta-modifier on the artifact — requires artifact-version channels)",
        r"to level of supported|to quality of supported|experience|rune",
        "+N gem level/quality grants, gem experience gain, rune improvement passes.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:loot_and_drop_scaling",
        "scales quantity/rarity of artifacts produced by terminated targets (loot = post-termination artifact yield — requires yield-scaling primitive)",
        r"quantity of items|rarity of items|items dropped|coin shower",
        "Item quantity/rarity on slain enemies, Coin Shower on kill.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:trajectory_geometry_scaling",
        "scales geometric parameters of the candidate trajectory or affected scope (distance, angle, spread, rotation, range, placement offset, reservation-coupled radius — requires geometry-channel primitive)",
        r"travel distance|beam (length|width)|chaining range|fissure|angle|branching|distance between|spread|spiral|rotations|rotates|targeting_range|aoe_range|aoe_modifiers|melee_range|hit rate|projectile spread|shockwave|area occurs|farther forward|charge distance|life reserved",
        "Travel distance, angles, spirals, rotations, ranges, spread, fissure geometry, shockwave scope, placement offsets, charge-distance and reservation-coupled scaling.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:attack_time_additive_modifier",
        "adds a flat time cost to each execution of the attack pipeline (attack-time = per-execution latency surcharge — requires latency-modifier channel)",
        r"attack time",
        "Flat seconds added to attack time, attack time per projectile.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:character_size_scaling",
        "scales the executor's effective presence footprint (character size — cosmetic-adjacent reach modifier; requires presence-footprint channel)",
        r"character size",
        "Character size modifiers.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:on_event_resource_grant",
        "grants primary/budget resource to the executor or a linked partner when a scoped event resolves (kill/hit/block — requires event-scoped resource faucet)",
        r"granted when|_when_killed|recoup|linked target|link targets|recharge",
        "Life/mana granted on kill or when hit, damage-taken recoup, linked-target recovery, reserve recharge rates.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:incoming_damage_redirection",
        "redirects a fraction of incoming damage into a buffer, delay, or prevention window before it reaches the primary pool (petrified blood / aegis / taken-from-buff — requires damage-shunt primitive)",
        r"taken from|damage taken|before your life|petrified|prevented_life_loss|physical_damage_taken|unlucky|aegis|prevent_all_damage|damage_taken|buff can take",
        "Damage taken from buff first, petrified-blood delayed loss, aegis pools, prevention windows, unlucky suppression.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:on_hit_kill_secondary_effect_routing",
        "routes secondary effects from terminating or accepted payloads (overkill reflection, debuff spread, rare-modifier theft — requires post-resolution effect routing)",
        r"overkill|reflected to other|spread when|chance to spread|killing blows|grant one of their modifiers",
        "Overkill reflection, on-hit debuff spreading, rare monster modifier theft on killing blows.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:alternate_resource_payment",
        "pays execution cost from an alternate resource pool (life instead of mana, lifetap fields — requires alternate-payment routing)",
        r"using your life|spends \d+%|sacrifices|brand's cost|blood magic|lifetap",
        "Life-cost casting, lifetap fields, cost-share lines.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:leech_instance_redirect",
        "redirects recoup instances to linked targets or converts their trigger conditions (requires leech-routing primitive)",
        r"leech",
        "Leech redirected to link targets; leech on any damage when hit.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:per_enemy_class_in_area_scaling",
        "scales an effect per present target, tiered by target class (normal/magic vs rare/unique in area — requires class-tiered presence scaling)",
        r"for each .* enem|per .* enem|enemies in area|enemy in area|while in area|in this skill's area|nearby enemies",
        "Per-enemy-in-area scaling tiered by enemy class.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:resource_threshold_conditional",
        "activates a modifier while a resource threshold holds (low life / full life / full energy shield — requires threshold-gated modifier)",
        r"low life|full life|full energy shield",
        "Modifiers gated on own low-life, target full-life, or full energy shield state.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:stance_conditional_modifier",
        "activates a modifier only while a named executor stance holds or after a stance change (requires stance-state channel)",
        r"stance",
        "Sand/blood stance conditionals and stance-change triggers.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:channelling_state_scaling",
        "scales effects based on channelling state and channelled duration (requires channel-state channel)",
        r"channel",
        "While-channelling modifiers and channel-duration triggers.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:ailment_duration_scaling",
        "extends the retention window of deferred residual state effects (ailment/poison/shock/bleed/curse duration — requires deferred-effect duration channel)",
        r"duration of .*ailments|poison duration|shock duration|bleeding duration|curse duration|ignite duration|ailments on|duration of cold|duration of lightning|duration of elemental|inflicted with an ailment",
        "Duration scaling for elemental ailments, poison, bleed, shock, curses; ailment-state conditionals.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:proxy_stat_scaling",
        "scales the stats of deployed proxy workers (totem/mine/trap/minion damage, life, placement, duration, range — requires proxy-stat channels)",
        r"totem|mine damage|mine throwing|trap|minion|golem|while totem is active|detonat|zombie|skeleton|raised",
        "Totem/mine/trap/minion stat scaling and mine detonation conditionals.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:conditional_spell_trigger",
        "executes a linked payload when a scoped trigger condition fires (stun/death/crit/kill/channel — requires linked-trigger controller)",
        r"chance to trigger|trigger supported|cast_linked|cast_when_hit|cast_spell|linked skill|on death",
        "Chance-to-trigger supported spells on stun, death, crit, kill, channel.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:keystone_grant_stat",
        "grants a named keystone policy that globally rewrites resolution rules (requires policy-grant primitive)",
        r"keystone_",
        "Granted keystones (elemental equilibrium, point blank, secrets of suffering, strong bowman).",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:pvp_scaling_override",
        "overrides scaling time constants or velocity caps for adversarial (PvP) contexts (requires context-specific scaling override)",
        r"pvp|velocity_cap",
        "PvP scaling time overrides and movement velocity caps.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:skill_behavior_override_flag",
        "flips a boolean behavior override on the skill's execution semantics (requires override-flag channel; flags preserved verbatim until semantics are mapped)",
        r"override|disable_|always_hit|cannot_crit|no_physical_chaos|deal_no_|is_not_melee|no_epk|fire_at_all_targets|no_spirit|enhanced_behaviour|force_lite|attack_is_melee",
        "Boolean overrides: melee overrides, disable conditions, always-hit, cannot-crit, deal-no-elemental, cast-time overrides.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:internal_nonmechanical_flag",
        "marks an internal presentation/cosmetic variation or degenerate artifact with no mechanic transfer (receipt-preserved, excluded from mechanics)",
        r"art_variation|_boolean|queens_demand|^[.\s]+$|^wip$",
        "Art variations, description booleans, unique display-effect flags, WIP markers, punctuation artifacts.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:interruption_avoidance",
        "raises tolerance against execution interruption while the skill runs (stun/interruption avoidance — requires interruption-tolerance channel)",
        r"avoid_stun|avoid_interruption|cannot be stunned|stun",
        "Avoid stun / avoid interruption while using the skill.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:ailment_threshold_scaling",
        "executes a finisher or scales an effect on halted-state targets below a life/ailment threshold (requires state-threshold finisher primitive)",
        r"shatter|frozen|at \d+%.*life|_at_33%_life",
        "Shattering frozen enemies below a life threshold; ailment thresholds keyed to life fractions.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:aura_field_grant_payload",
        "emits a persistent shared modifier field whose payload is an enumerated grant list with its own lifecycle (aura/buff/golem grants, refresh/expire hooks — requires field-payload enumeration channel)",
        r"aura|^buff grants?|buffs on you|^golems? grant|buff duration|refreshed|expire",
        "Aura grants X, Buff grants X, Golem grants, aura effect/duration/area, buff refresh/expire.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:curse_and_target_vulnerability_payload",
        "applies a target-specific modifier field whose payload weakens the target's accounting (curse/hex/mark payloads, block/action-speed reduction, self-vulnerability stats — requires curse-payload enumeration channel)",
        r"curse|cursed|hex\b|hexes|marked|enemies have .*(block|less|reduction)|enemies deal .* less|against_self|enemy_additional",
        "Cursed-enemy penalties and grants, curse-skill scaling, per-curse damage, mark payloads, enemy block/speed reduction, self-vulnerability stats.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:blade_resource_damage",
        "forges blade-class resources whose damage derives from buffer pools (energy blades from energy shield, ethereal blades — requires buffer-derived weapon pool)",
        r"ethereal|energy blade",
        "Energy blade min/max damage from energy shield; ethereal blade added damage.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:added_base_damage_with_resource_component",
        "adds flat or resource-proportional base effectiveness to the payload (max-life/energy-shield/mana-derived components — requires resource-derived base-value channel)",
        r"this spell deals|deals \d+% of your|as base .* damage|deals base|added .* damage|adds? [\d.]+ to|as extra|equal to .*% of",
        "This Spell deals X to Y lines, percent-of-resource base damage, added flat damage lines.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:equipment_scaled_added_damage",
        "adds payload effectiveness scaled by an equipment attribute (armour/evasion rating or quality on shield — requires equipment-attribute coupling)",
        r"on shield|shield quality|armour or evasion",
        "Added damage per armour/evasion rating or shield quality.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:resource_spend_coupled_charge_mechanics",
        "mints and spends charge counters coupled to cumulative resource spend, raising cost and effectiveness together (inspiration/blood charges — requires spend-ledger-coupled counter)",
        r"inspiration|blood charge",
        "Inspiration charge gain/loss/scaling, blood charge cost/damage coupling.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:per_recent_action_window",
        "activates or scales a modifier from actions inside a trailing time window (spent recently / lost in the past N seconds / per-duration coupling — requires sliding-window action ledger)",
        r"recently|past \d+ seconds|in the past|per [\d.]+ seconds? duration",
        "Modifiers keyed to recent spending, recent losses, and per-duration scaling windows.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:chill_freeze_application",
        "applies degraded-state (chill) or halted-state (freeze) modifiers with duration scaling (requires cold-state application channel)",
        r"chill|freeze",
        "Chill/freeze application and duration lines.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:secondary_debuff_payload",
        "attaches a secondary debuff payload with its own damage, duration, and recoup accounting (requires secondary-payload channel)",
        r"secondary debuff|debuff deals|debuff damage|debuff duration|debuff starts|uncharged debuff",
        "Secondary debuff damage/duration, debuff-damage recoup, uncharged debuff application.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:mana_cost_equalization",
        "sets base execution cost to a fraction of unreserved capacity and converts spent budget into added effectiveness (requires cost-equalization channel)",
        r"mana cost equal|damage equal to .* mana|of mana spent|mana you have spent|unreserved maximum mana|unreserved mana",
        "Archmage-style base-cost equalization and mana-spent-to-damage conversion.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:self_inflicted_damage_cost",
        "pays a self-inflicted damage toll from primary and buffer pools, upfront or per second (requires self-damage toll channel)",
        r"^take \d+%|^you burn|^you take",
        "Take N% of maximum life/energy shield as chaos damage; self-burn per second.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:orb_behavior_mechanics",
        "maintains orbiting payload objects with jump, strike, and expiry rules (requires orbiting-object lifecycle primitive)",
        r"\borb",
        "Orb jump cadence, orb expiry after strikes, orb-triggered strikes.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:combo_finisher_scaling",
        "scales the final strike of a combo sequence with accumulated combo state (requires combo-sequence ledger)",
        r"combo|final_strike|slice_and_dice",
        "Per-combo-average hits and final-strike scaling.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:repeat_targeting_bias",
        "biases repeat executions toward or away from the initial target selection (requires repeat-targeting bias channel)",
        r"repeat",
        "Repeat counts and repeat target-selection bias.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:requirement_and_eligibility_gating",
        "restricts which payloads or artifacts are eligible by level, attribute, or class requirements (requires eligibility-filter channel)",
        r"requirement|can only support|requiring level|up to level|with level \d",
        "Attribute requirement reductions, support-level restrictions, usage level caps.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:granted_skill_hidden_stat",
        "grants the skill a hidden behavioral stat not exposed as tooltip text (requires hidden-stat grant channel with receipt preservation)",
        r"^[a-z0-9_+%]+:\s*-?[\d.]+$",
        "Internal stat-id lines granting hidden skill behavior stats (skill_level, *_granted_*, per-gem behavioral constants) with no tooltip rendering.",
    ),
    ConverterFamilyRule(
        "CONVERTER_FAMILY:skill_narrative_description",
        "transfers a full-sentence mechanic narrative via clause decomposition (requires narrative-clause decomposer, not a keyword converter)",
        r"[.!?]$|^.{60,}$",
        "Long narrative description sentences (terminal punctuation, or unterminated long-form prose).",
    ),
)



_COMPILED: tuple[tuple[ConverterFamilyRule, "re.Pattern[str]"], ...] = tuple(
    (rule, re.compile(rule.pattern, re.IGNORECASE)) for rule in CONVERTER_FAMILY_RULES
)

UNCLASSIFIED = "UNCLASSIFIED_LINE"


def classify_line(line: str) -> str:
    """Return the converter family that would resolve ``line`` (first match wins)."""
    for rule, pattern in _COMPILED:
        if pattern.search(line):
            return rule.family
    return UNCLASSIFIED


def family_rule(family: str) -> ConverterFamilyRule | None:
    for rule in CONVERTER_FAMILY_RULES:
        if rule.family == family:
            return rule
    return None


@dataclass(frozen=True)
class UnmatchedLine:
    gem_id: str
    gem_name: str
    line: str
    status: str  # PARTIAL | UNRESOLVED


def build_family_registry(
    unmatched: Iterable[UnmatchedLine],
    *,
    max_examples: int = 5,
    min_examples: int = 3,
) -> dict[str, Any]:
    """Build the converter-family registry from PARTIAL/UNRESOLVED lines.

    Deterministic: families sorted by name; example lines are the first
    ``max_examples`` unique lines in sorted order; gem coverage counts distinct
    gem ids. Raises ``ValueError`` if any line is UNCLASSIFIED (no generic
    buckets) or a family cannot supply ``min_examples`` distinct examples.
    """
    entries = list(unmatched)
    unclassified = [e for e in entries if classify_line(e.line) == UNCLASSIFIED]
    if unclassified:
        sample = sorted({e.line for e in unclassified})[:10]
        raise ValueError(
            f"{len(unclassified)} line(s) matched no converter family — "
            f"refusing to bucket them generically. Examples: {sample}"
        )

    grouped: dict[str, list[UnmatchedLine]] = {}
    for entry in entries:
        grouped.setdefault(classify_line(entry.line), []).append(entry)

    families: list[dict[str, Any]] = []
    for family in sorted(grouped):
        lines = grouped[family]
        rule = family_rule(family)
        examples = sorted({e.line for e in lines})
        if len(examples) < min_examples:
            raise ValueError(
                f"family {family} has only {len(examples)} distinct example line(s) "
                f"(< {min_examples}) — merge it into a more precise sibling family"
            )
        gem_ids = sorted({e.gem_id for e in lines})
        statuses = sorted({e.status for e in lines})
        families.append({
            "family": family,
            "description": rule.description if rule else "",
            "proposed_template": rule.template if rule else "",
            "line_count": len(lines),
            "gem_coverage": len(gem_ids),
            "gem_ids": gem_ids,
            "statuses_covered": statuses,
            "example_unmatched_lines": examples[:max_examples],
        })

    return {
        "schema": "reflexion.gem_forge.converter_family_registry.v1",
        "policy": (
            "Every PARTIAL/UNRESOLVED line is assigned to the precisely named "
            "converter family that would resolve it. No generic buckets: an "
            "unclassifiable line aborts the registry build instead of being "
            "filed under 'other'."
        ),
        "family_count": len(families),
        "total_lines_classified": len(entries),
        "families": families,
    }
