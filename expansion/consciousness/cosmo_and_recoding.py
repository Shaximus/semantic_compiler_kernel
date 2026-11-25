"""
Executable Evaluators for Flat FLRW Hubble–Schwarzschild Correspondence (SC-HS-001 v1.1.0)
and Runtime Recoding Over Fixed Base / Octopus Temperature-Dependent RNA Editing
(SC-IT-OCTO-RNA-EDIT-001).

Formalizes:
1. ``SC-HS-001`` (v1.1.0, TIG-graded):
   - Flat Friedmann critical density ``rho_c = 3 H^2 / (8 pi G)``
   - Hubble radius ``R_H = c / H`` and enclosed mass ``M_H = c^3 / (2 G H)``
   - Exact Schwarzschild-radius correspondence ``R_S = 2 G M_H / c^2 == R_H`` (CLM-HS-001)
   - Arbitrary-radius Misner–Sharp mass ``M(R) = H^2 R^3 / (2 G)`` and ratio
     ``R_S / R = (R / R_H)^2`` (CLM-HS-002A, ANCHORED) vs global black-hole-interior
     embedding (CLM-HS-002B, OPEN_HYPOTHESIS)
   - Null-expansion classification: super-Hubble spheres in expanding flat FLRW are
     ``ANTI_TRAPPED`` (both null congruences expanding), reversing to ``FUTURE_TRAPPED``
     in a contracting phase (CLM-HS-003)
   - Apparent horizon vs cosmological event horizon distinction (equal only in pure
     de Sitter, ``R_H = sqrt(3 / Lambda)``) (CLM-HS-004)
   - Gibbons–Hawking area-law horizon entropy ``S = k_B c^3 A / (4 G hbar)`` (CLM-HS-005)
   - Strict TIG epistemic separation: ``substrate_confusion_check = True`` (SC-PATCH-DU-001) with explicit
     residual mismatches (MAP:HS-001, CLM-HS-006).

2. ``SC-IT-OCTO-RNA-EDIT-001`` (Catalog Class #24 / Claude Catalog #19:
   ``RUNTIME_RECODING_OVER_FIXED_BASE``):
   - Base code remains fixed; a fast, reversible, environment-driven runtime layer
     retunes live output without writing back to the base (substrate sovereignty)
   - P1 (CONFIRMED): heavy runtime recoding freezes the base at attachment sites
     (cephalopod conserved dsRNA hairpins; AI LoRA adapter-to-base coupling)
   - P2 (CONFIRMED): runtime recoding operates orders of magnitude faster than base change
   - P3 (CONFIRMED biology / UNTESTED AI): environment-exposed components receive the
     most runtime tuning
   - P4 (UNTESTED): runtime recoding has an adaptive ceiling beyond which base change
     is required
   - Honest cross-substrate residuals across BIOLOGY, AI, HUMAN, SOCIETAL, and PHYSICAL.

Citations:
- Pathria RK, Nature 240, 298-299 (1972)
- Gibbons GW & Hawking SW, Phys. Rev. D 15, 2738-2751 (1977)
- Birk MA et al., Cell 186(12):2544-2555 (2023), doi:10.1016/j.cell.2023.05.004
- Liscovitch-Brauer N et al., Cell 169(2):191-202 (2017)
- Shax (Curtis Kingsley) — Reflexion Software (2026-11-24)
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any

# Exact CODATA / SI physical constants
SPEED_OF_LIGHT_M_S: float = 299_792_458.0
GRAVITATIONAL_CONSTANT_SI: float = 6.67430e-11
REDUCED_PLANCK_J_S: float = 1.054571817e-34
BOLTZMANN_J_K: float = 1.380649e-23
PLANCK_LENGTH_SQ_M2: float = (GRAVITATIONAL_CONSTANT_SI * REDUCED_PLANCK_J_S) / (
    SPEED_OF_LIGHT_M_S**3
)

# Representative Planck/LambdaCDM H0 (~67.4 km/s/Mpc in s^-1)
DEFAULT_HUBBLE_RATE_S_INV: float = 2.184e-18


class NullExpansionRegime(str, Enum):
    """Null-expansion classification of a sphere of areal radius R in flat FLRW (CLM-HS-003)."""

    SUB_HUBBLE_NORMAL = "SUB_HUBBLE_NORMAL"
    HUBBLE_APPARENT_HORIZON = "HUBBLE_APPARENT_HORIZON"
    SUPER_HUBBLE_ANTI_TRAPPED = "SUPER_HUBBLE_ANTI_TRAPPED"
    SUPER_HUBBLE_FUTURE_TRAPPED = "SUPER_HUBBLE_FUTURE_TRAPPED"


class RecodingSubstrate(str, Enum):
    """Cross-domain substrates for RUNTIME_RECODING_OVER_FIXED_BASE (SC-IT-OCTO-RNA-EDIT-001)."""

    BIOLOGY = "BIOLOGY"
    AI = "AI"
    HUMAN = "HUMAN"
    SOCIETAL = "SOCIETAL"
    PHYSICAL = "PHYSICAL"


HS_RESIDUAL_MISMATCHES: tuple[str, ...] = (
    "expanding FLRW super-Hubble region is anti-trapped (both null expansions positive); "
    "a black-hole interior is future-trapped (both negative)",
    "black-hole horizon is one surface about one center; Hubble horizon is observer-centered",
    "Hubble radius is the apparent horizon, not generally the event horizon",
)

RUNTIME_RECODING_SUBSTRATE_SPECS: dict[RecodingSubstrate, dict[str, Any]] = {
    RecodingSubstrate.BIOLOGY: {
        "fixed_base": "Octopus DNA genome",
        "runtime_layer": "ADAR A-to-I RNA editing (>20,000 sites, >13,000 codons)",
        "editor_present": True,
        "base_freeze_cost_established": True,
        "mapping_class": "SOURCE_DOMAIN",
        "topology_match": 1.0,
        "residuals": (),
    },
    RecodingSubstrate.AI: {
        "fixed_base": "Frozen base model weights",
        "runtime_layer": "LoRA adapters, system prompts, in-context learning",
        "editor_present": True,
        "base_freeze_cost_established": True,
        "mapping_class": "ISOMORPHIC_INVARIANT",
        "topology_match": 0.9,
        "residuals": (
            "ADAR is environment-driven automatically; adapters are chosen by an operator",
            "P3 (environment-exposed components get most tuning) untested in AI",
        ),
    },
    RecodingSubstrate.HUMAN: {
        "fixed_base": "Genome and baseline temperament",
        "runtime_layer": "Physiological acclimatization and state-dependent behaviour",
        "editor_present": True,
        "base_freeze_cost_established": False,
        "mapping_class": "STRUCTURAL_ANALOGY",
        "topology_match": 0.8,
        "residuals": ("base-freezing cost loop not shown",),
    },
    RecodingSubstrate.SOCIETAL: {
        "fixed_base": "Constitution / entrenched clauses",
        "runtime_layer": "Regulations, executive orders, sunset clauses",
        "editor_present": True,
        "base_freeze_cost_established": False,
        "mapping_class": "STRUCTURAL_ANALOGY",
        "topology_match": 0.7,
        "residuals": (
            "regulation is deliberate and contested rather than automatic",
            "laws can outlive authors whereas RNA edits are non-inherited",
        ),
    },
    RecodingSubstrate.PHYSICAL: {
        "fixed_base": "Fundamental physical constants",
        "runtime_layer": "Temperature-dependent material phase transitions",
        "editor_present": False,
        "base_freeze_cost_established": False,
        "mapping_class": "STRUCTURAL_ANALOGY",
        "topology_match": 0.3,
        "residuals": ("no adaptive editor, no acclimation goal",),
    },
}


def evaluate_flrw_hubble_schwarzschild(
    hubble_rate_s_inv: float = DEFAULT_HUBBLE_RATE_S_INV,
    sphere_radius_m: float | None = None,
    *,
    expanding: bool = True,
    pure_de_sitter: bool = False,
) -> dict[str, Any]:
    """Evaluate the SC-HS-001 v1.1.0 flat FLRW Hubble–Schwarzschild correspondence.

    Parameters
    ----------
    hubble_rate_s_inv:
        Magnitude of the Hubble parameter ``|H|`` in ``s^-1`` (must be strictly positive
        and finite).
    sphere_radius_m:
        Optional areal radius ``R`` (in meters) for Misner–Sharp mass and null-expansion
        classification. Defaults to the Hubble radius ``R_H = c / |H|``.
    expanding:
        ``True`` for an expanding flat FLRW epoch (``H > 0``); ``False`` for a
        contracting FLRW phase (``H < 0``), where super-Hubble spheres become
        future-trapped rather than anti-trapped (CLM-HS-003).
    pure_de_sitter:
        ``True`` only in pure cosmological-constant de Sitter spacetime, where the
        apparent horizon ``R_H = sqrt(3 / Lambda)`` coincides with the cosmological
        event horizon (CLM-HS-004).
    """
    if not isinstance(hubble_rate_s_inv, (int, float)) or isinstance(hubble_rate_s_inv, bool):
        raise TypeError("hubble_rate_s_inv must be a finite positive float")
    h_abs = float(hubble_rate_s_inv)
    if not math.isfinite(h_abs) or h_abs <= 0.0:
        raise ValueError("hubble_rate_s_inv must be strictly positive and finite")

    c = SPEED_OF_LIGHT_M_S
    g = GRAVITATIONAL_CONSTANT_SI

    rho_c = (3.0 * h_abs * h_abs) / (8.0 * math.pi * g)
    r_h = c / h_abs
    m_h = (c**3) / (2.0 * g * h_abs)
    r_s_hubble = (2.0 * g * m_h) / (c * c)
    rel_err = abs(r_s_hubble - r_h) / r_h

    if sphere_radius_m is None:
        r_eval = r_h
    else:
        if not isinstance(sphere_radius_m, (int, float)) or isinstance(sphere_radius_m, bool):
            raise TypeError("sphere_radius_m must be a finite positive float or None")
        r_eval = float(sphere_radius_m)
        if not math.isfinite(r_eval) or r_eval <= 0.0:
            raise ValueError("sphere_radius_m must be strictly positive and finite")

    misner_sharp_mass_kg = (h_abs * h_abs * (r_eval**3)) / (2.0 * g)
    r_s_sphere = (2.0 * g * misner_sharp_mass_kg) / (c * c)
    ratio_rs_over_r = r_s_sphere / r_eval
    ratio_r_over_rh_sq = (r_eval / r_h) ** 2

    # CLM-HS-003 null-expansion signs:
    # In expanding flat FLRW: theta_out = 2(1/R + H/c) > 0 everywhere;
    # theta_in = 2(-1/R + H/c) is <0 inside R_H, 0 at R_H, >0 outside R_H (anti-trapped).
    # In contracting flat FLRW (H -> -|H|): signs reverse; super-Hubble spheres have
    # theta_out < 0 and theta_in < 0 (future-trapped).
    signed_h = h_abs if expanding else -h_abs
    theta_out_sign = 1 if (1.0 / r_eval + signed_h / c) > 1e-12 / r_h else (
        -1 if (1.0 / r_eval + signed_h / c) < -1e-12 / r_h else 0
    )
    theta_in_sign = 1 if (-1.0 / r_eval + signed_h / c) > 1e-12 / r_h else (
        -1 if (-1.0 / r_eval + signed_h / c) < -1e-12 / r_h else 0
    )

    if abs(r_eval - r_h) / r_h <= 1e-12:
        regime = NullExpansionRegime.HUBBLE_APPARENT_HORIZON
    elif r_eval < r_h:
        regime = NullExpansionRegime.SUB_HUBBLE_NORMAL
    elif expanding:
        regime = NullExpansionRegime.SUPER_HUBBLE_ANTI_TRAPPED
    else:
        regime = NullExpansionRegime.SUPER_HUBBLE_FUTURE_TRAPPED

    horizon_area_m2 = 4.0 * math.pi * r_h * r_h
    dimensionless_entropy = horizon_area_m2 / (4.0 * PLANCK_LENGTH_SQ_M2)
    entropy_j_per_k = BOLTZMANN_J_K * dimensionless_entropy
    implied_lambda_m_inv2 = (3.0 / (r_h * r_h)) if pure_de_sitter else None

    return {
        "entry_id": "SC-HS-001",
        "entry_revision": "1.1.0",
        "hubble_rate_s_inv": signed_h,
        "expanding": expanding,
        "critical_density_kg_m3": rho_c,
        "hubble_radius_m": r_h,
        "enclosed_hubble_mass_kg": m_h,
        "schwarzschild_radius_of_hubble_mass_m": r_s_hubble,
        "hubble_schwarzschild_equality_holds": rel_err <= 1e-12,
        "equality_relative_error": rel_err,
        "sphere_radius_m": r_eval,
        "misner_sharp_mass_kg": misner_sharp_mass_kg,
        "sphere_schwarzschild_radius_m": r_s_sphere,
        "rs_over_r": ratio_rs_over_r,
        "r_over_rh_squared": ratio_r_over_rh_sq,
        "null_expansion_regime": regime.value,
        "theta_out_sign": theta_out_sign,
        "theta_in_sign": theta_in_sign,
        "is_apparent_horizon": True,
        "coincides_with_event_horizon": bool(pure_de_sitter),
        "de_sitter_lambda_m_inv2": implied_lambda_m_inv2,
        "horizon_area_m2": horizon_area_m2,
        "dimensionless_entropy_s_over_kb": dimensionless_entropy,
        "horizon_entropy_j_per_k": entropy_j_per_k,
        "mapping_id": "MAP:HS-001",
        "mapping_class": "STRUCTURAL_ANALOGY",
        "substrate_confusion_check": True,
        "positional_claims_permitted": True,
        "tig_claim_status": {
            "CLM-HS-001": "ANCHORED",
            "CLM-HS-002A": "ANCHORED",
            "CLM-HS-002B": "OPEN_HYPOTHESIS",
            "CLM-HS-003": "ANCHORED",
            "CLM-HS-004": "ANCHORED",
            "CLM-HS-005": "ANCHORED",
            "CLM-HS-006": "ANALOGOUS",
        },
        "residual_mismatches": list(HS_RESIDUAL_MISMATCHES),
    }


def evaluate_runtime_recoding_layer(
    substrate: RecodingSubstrate | str,
    *,
    writes_back_to_base: bool = False,
    environment_driven: bool = True,
    conserved_attachment_sites: bool = True,
    recoding_timescale_hours: float = 24.0,
    base_evolution_timescale_hours: float = 87_600.0,
    exceeds_editable_ceiling: bool = False,
) -> dict[str, Any]:
    """Evaluate a system against Catalog Class #24 (Claude #19) RUNTIME_RECODING_OVER_FIXED_BASE.

    Formalizes ``SC-IT-OCTO-RNA-EDIT-001`` (Birk et al., Cell 2023; Liscovitch-Brauer et al.,
    Cell 2017): a fast, reversible runtime recoding layer sitting between fixed base code
    and live output, plus the confirmed frozen-base attachment cost (P1), timescale
    separation (P2), and untested editable ceiling (P4).
    """
    if isinstance(substrate, str):
        try:
            sub_enum = RecodingSubstrate(substrate.strip().upper())
        except ValueError as exc:
            valid = ", ".join(s.value for s in RecodingSubstrate)
            raise ValueError(f"Unknown substrate {substrate!r}; expected one of: {valid}") from exc
    elif isinstance(substrate, RecodingSubstrate):
        sub_enum = substrate
    else:
        raise TypeError("substrate must be a RecodingSubstrate or string")

    if recoding_timescale_hours <= 0 or base_evolution_timescale_hours <= 0:
        raise ValueError("timescales must be strictly positive")

    spec = RUNTIME_RECODING_SUBSTRATE_SPECS[sub_enum]
    speedup_ratio = base_evolution_timescale_hours / recoding_timescale_hours
    substrate_sovereignty_preserved = not writes_back_to_base
    timescale_separation_holds = speedup_ratio >= 100.0
    editor_present = bool(spec["editor_present"])

    invariants_satisfied = (
        editor_present
        and substrate_sovereignty_preserved
        and timescale_separation_holds
        and not exceeds_editable_ceiling
    )

    residuals = list(spec["residuals"])
    if not environment_driven and editor_present and sub_enum == RecodingSubstrate.BIOLOGY:
        residuals.append("biological RNA editing in this model is triggered externally rather than by environment")
    if writes_back_to_base:
        residuals.append("VIOLATION: writes_back_to_base breaks DNA/base-weight substrate sovereignty")
    if exceeds_editable_ceiling:
        residuals.append("P4 ceiling exceeded: runtime recoding exhausted; base modification required")

    return {
        "entry_id": "SC-IT-OCTO-RNA-EDIT-001",
        "catalog_class": "RUNTIME_RECODING_OVER_FIXED_BASE",
        "catalog_class_number": 24,
        "claude_catalog_alias": "#19",
        "substrate": sub_enum.value,
        "fixed_base": spec["fixed_base"],
        "runtime_layer": spec["runtime_layer"],
        "editor_present": editor_present,
        "environment_driven": bool(environment_driven),
        "substrate_sovereignty_preserved": substrate_sovereignty_preserved,
        "base_freeze_cost_active": bool(conserved_attachment_sites and editor_present),
        "base_freeze_cost_established_in_substrate": bool(spec["base_freeze_cost_established"]),
        "timescale_speedup_ratio": speedup_ratio,
        "timescale_separation_holds": timescale_separation_holds,
        "exceeds_editable_ceiling": bool(exceeds_editable_ceiling),
        "invariants_satisfied": invariants_satisfied,
        "mapping_class": spec["mapping_class"],
        "topology_match": spec["topology_match"],
        "substrate_confusion_check": True,
        "positional_claims_permitted": True,
        "prediction_status": {
            "P1_frozen_base_attachment_cost": "CONFIRMED",
            "P2_orders_of_magnitude_faster": "CONFIRMED",
            "P3_environment_exposed_most_tuned": (
                "CONFIRMED" if sub_enum == RecodingSubstrate.BIOLOGY else "UNTESTED"
            ),
            "P4_editable_ceiling": "UNTESTED",
        },
        "residual_mismatches": residuals,
    }


__all__ = [
    "BOLTZMANN_J_K",
    "DEFAULT_HUBBLE_RATE_S_INV",
    "GRAVITATIONAL_CONSTANT_SI",
    "HS_RESIDUAL_MISMATCHES",
    "PLANCK_LENGTH_SQ_M2",
    "REDUCED_PLANCK_J_S",
    "RUNTIME_RECODING_SUBSTRATE_SPECS",
    "SPEED_OF_LIGHT_M_S",
    "NullExpansionRegime",
    "RecodingSubstrate",
    "evaluate_flrw_hubble_schwarzschild",
    "evaluate_runtime_recoding_layer",
]
