"""Executable reference model of the Chaos Inoculation spec (docs/POE_CHAOS_INOCULATION_INVARIANTS.md).

This is a toy state machine, not the game. Its numbers (shield size, delay, rates, damage
amounts) are illustrative integers chosen to make the cases small; they are NOT game values,
which are patch-dependent and deliberately absent from the template. What the tests check is
the *logic* of the sourced rules: given those rules, do the derived properties in the doc
follow? A property that holds here holds for the game only as far as the rules encoded below
match the game version they cite.

Rules encoded, with the sources the template cites for them:
* damage hits the buffer first; overflow reaches life (FANDOM-ES, MOBA-ES)
* PoE 1: chaos damage ignores the buffer (FANDOM-ES, POEDB-CI)
* PoE 2, January 2025 guide: chaos removes twice as much buffer; poison skips the buffer;
  bleeding skips the buffer and is inflicted only by a hit that damages life (MOBA-ES)
* recharge runs only after a delay with no damage taken; damage restarts the delay
* Chaos Inoculation: life is 1 and chaos damage (poison included) is ignored (POEDB-CI)
Not modeled: PoE 1 bleeding, thresholds, flasks, anything time-continuous.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import pytest


@dataclass(frozen=True)
class Rules:
    name: str
    chaos_ignores_buffer: bool
    chaos_buffer_factor: int
    bleed_needs_life_damage: bool
    models_bleed: bool


POE1 = Rules("PoE 1", chaos_ignores_buffer=True, chaos_buffer_factor=1,
             bleed_needs_life_damage=False, models_bleed=False)
POE2_JAN_2025 = Rules("PoE 2 (January 2025 guide)", chaos_ignores_buffer=False, chaos_buffer_factor=2,
                      bleed_needs_life_damage=True, models_bleed=True)
# Counterfactual: the one PoE 2 rule the bleed derivation depends on, switched off.
POE2_IF_BLEED_ON_ANY_HIT = Rules("counterfactual", chaos_ignores_buffer=False, chaos_buffer_factor=2,
                                 bleed_needs_life_damage=False, models_bleed=True)


@dataclass(frozen=True)
class Character:
    life: int
    immune: frozenset = field(default_factory=frozenset)
    buffer_max: int = 10
    delay: int = 2          # quiet ticks before recharge starts (toy value)
    recharge: int = 5       # buffer per quiet tick once the delay has passed (toy value)
    converted: int = 0      # converted recovery per tick, independent of quiet time (toy value)


CI = Character(life=1, immune=frozenset({"chaos"}))
ONE_LIFE_NO_IMMUNITY = Character(life=1)
LIFE_BUILD = Character(life=5)

# An event is (quiet ticks before it, kind, amount).
KINDS = ("hit", "chaos", "poison", "bleed_hit")


def simulate(events, rules: Rules, char: Character):
    """Return (alive, cause_of_death). Causes: 'overflow', 'bypass', 'bleed'."""
    buffer = float(char.buffer_max)
    life = float(char.life)
    quiet = 10**6

    def tick():
        nonlocal buffer, quiet
        quiet += 1
        buffer += char.converted
        if quiet >= char.delay:
            buffer += char.recharge
        buffer = min(buffer, char.buffer_max)

    for gap, kind, amount in events:
        for _ in range(gap):
            tick()
        cause = None
        if kind in ("chaos", "poison") and "chaos" in char.immune:
            tick()
            continue  # no damage taken, so the recharge delay is not restarted
        quiet = 0
        if kind == "poison" or (kind == "chaos" and rules.chaos_ignores_buffer):
            life -= amount
            cause = "bypass"
        elif kind == "chaos":
            factor = rules.chaos_buffer_factor
            if amount * factor <= buffer:
                buffer -= amount * factor
            else:
                life -= amount - buffer / factor
                buffer = 0.0
                cause = "overflow"
        else:  # hit or bleed_hit
            overflow = max(0.0, amount - buffer)
            buffer = max(0.0, buffer - amount)
            if overflow:
                life -= overflow
                cause = "overflow"
            if kind == "bleed_hit" and rules.models_bleed and life > 0:
                if overflow or not rules.bleed_needs_life_damage:
                    life -= amount  # bleeding skips the buffer
                    cause = "bleed"
        if life <= 0:
            return False, cause
        tick()
    return True, None


def all_sequences(max_len=3, gaps=(0, 3), amounts=(1, 4, 9)):
    alphabet = list(itertools.product(gaps, KINDS, amounts))
    for n in range(1, max_len + 1):
        yield from itertools.product(alphabet, repeat=n)


def causes(rules, char):
    return {simulate(seq, rules, char)[1] for seq in all_sequences()} - {None}


# --- Safety 1: every path to life goes through the buffer --------------------------------

def test_poe1_ci_only_dies_by_overflow():
    assert causes(POE1, CI) == {"overflow"}


def test_poe1_one_life_without_immunity_dies_to_one_chaos_point_at_full_buffer():
    # The reason the keystone pairs the two halves: without the immunity, the bypass is open.
    assert simulate([(0, "chaos", 1)], POE1, ONE_LIFE_NO_IMMUNITY) == (False, "bypass")
    assert simulate([(0, "chaos", 1)], POE1, CI) == (True, None)


def test_poe2_ci_only_dies_by_overflow_so_bleeding_is_never_the_first_cause():
    # Derived, not sourced: bleeding needs a hit that damages life, and at life 1 that hit is
    # already lethal. Poison is chaos, so the immunity covers it.
    assert causes(POE2_JAN_2025, CI) == {"overflow"}


def test_the_bleed_derivation_is_not_vacuous():
    # A character with real life can die to bleeding under the same rules ...
    assert "bleed" in causes(POE2_JAN_2025, LIFE_BUILD)
    # ... and CI can too if the "needs life damage" rule did not exist. That rule is the one to
    # re-verify against PoE 2 0.5.x before relying on the derivation.
    assert "bleed" in causes(POE2_IF_BLEED_ON_ANY_HIT, CI)


# --- Safety 2 and refill: the race between chip damage and recharge ----------------------

CHIP_THEN_SPIKE = [(0, "hit", 4), (0, "hit", 4), (0, "hit", 9)]
SAME_HITS_SPACED = [(0, "hit", 4), (3, "hit", 4), (3, "hit", 9)]


def test_spike_after_chip_kills_with_every_hit_below_the_maximum_buffer():
    assert all(amount < CI.buffer_max for _gap, _kind, amount in CHIP_THEN_SPIKE)
    assert simulate(CHIP_THEN_SPIKE, POE1, CI) == (False, "overflow")


def test_the_same_hits_with_quiet_gaps_are_survived():
    # Same damage, different spacing: refill depends on gaps between hits, not on the rate.
    assert simulate(SAME_HITS_SPACED, POE1, CI) == (True, None)


def test_faster_recharge_does_not_help_without_quiet_time():
    fast = Character(life=1, immune=frozenset({"chaos"}), recharge=1000)
    assert simulate(CHIP_THEN_SPIKE, POE1, fast) == (False, "overflow")


def test_converted_recovery_removes_the_quiet_time_requirement():
    leech = Character(life=1, immune=frozenset({"chaos"}), converted=4)
    assert simulate(CHIP_THEN_SPIKE, POE1, leech) == (True, None)


@pytest.mark.parametrize("rules", [POE1, POE2_JAN_2025], ids=lambda r: r.name)
def test_a_single_hit_within_the_current_buffer_never_kills_ci(rules):
    for amount in range(1, CI.buffer_max + 1):
        assert simulate([(0, "hit", amount)], rules, CI) == (True, None)
    assert simulate([(0, "hit", CI.buffer_max + 1)], rules, CI) == (False, "overflow")
