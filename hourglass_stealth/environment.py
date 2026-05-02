"""Planetary heating approximations for cislunar environments."""

import math

from hourglass_stealth.constants import SIGMA_SB


def body_solid_angle_sr(
    body_radius_m: float,
    distance_from_body_center_m: float,
) -> float:
    """Return the apparent solid angle of a sphere from an external point."""
    if body_radius_m <= 0.0 or distance_from_body_center_m <= 0.0:
        raise ValueError("body_radius_m and distance_from_body_center_m must be positive.")
    if distance_from_body_center_m < body_radius_m:
        raise ValueError("distance_from_body_center_m must be outside the body radius.")

    ratio = body_radius_m / distance_from_body_center_m
    return 2.0 * math.pi * (1.0 - math.sqrt(1.0 - ratio**2))


def blackbody_irradiance_from_solid_angle_w_m2(
    temperature_k: float,
    solid_angle_sr: float,
) -> float:
    """Return irradiance from a diffuse blackbody source over a given solid angle."""
    if temperature_k < 0.0:
        raise ValueError("temperature_k must be non-negative.")
    if not 0.0 <= solid_angle_sr <= 2.0 * math.pi:
        raise ValueError("solid_angle_sr must be between 0 and 2*pi.")
    return SIGMA_SB * temperature_k**4 * (solid_angle_sr / (2.0 * math.pi))


def radiative_equilibrium_temperature_from_body_k(
    body_temperature_k: float,
    body_solid_angle_sr: float,
    absorptivity_to_emissivity_ratio: float = 1.0,
    absorption_to_emission_area_ratio: float = 1.0,
    background_temperature_k: float = 0.0,
) -> float:
    """
    Return equilibrium temperature for a diffuse graybody viewing a warm body plus cold space.

    This is an envelope model. The key dimensionless factor is:

        (absorptivity / emissivity) * (absorbing area / emitting area) * (Omega / 2pi)

    where `Omega / 2pi` is the fraction of the visible hemisphere occupied by the warm body.
    """
    if body_temperature_k < 0.0 or background_temperature_k < 0.0:
        raise ValueError("Temperatures must be non-negative.")
    if not 0.0 <= body_solid_angle_sr <= 2.0 * math.pi:
        raise ValueError("body_solid_angle_sr must be between 0 and 2*pi.")
    if absorptivity_to_emissivity_ratio < 0.0:
        raise ValueError("absorptivity_to_emissivity_ratio must be non-negative.")
    if absorption_to_emission_area_ratio < 0.0:
        raise ValueError("absorption_to_emission_area_ratio must be non-negative.")

    hemisphere_fraction = body_solid_angle_sr / (2.0 * math.pi)
    source_term = (
        absorptivity_to_emissivity_ratio
        * absorption_to_emission_area_ratio
        * hemisphere_fraction
        * body_temperature_k**4
    )
    return (background_temperature_k**4 + source_term) ** 0.25


def body_ir_flux_w_m2(
    body_emit_flux_w_m2: float,
    body_radius_m: float,
    distance_from_body_center_m: float,
) -> float:
    if body_emit_flux_w_m2 < 0.0:
        raise ValueError("body_emit_flux_w_m2 must be non-negative.")
    if body_radius_m <= 0.0 or distance_from_body_center_m <= 0.0:
        raise ValueError("body_radius_m and distance_from_body_center_m must be positive.")
    return body_emit_flux_w_m2 * (body_radius_m / distance_from_body_center_m) ** 2


def body_albedo_flux_w_m2(
    solar_flux_w_m2: float,
    bond_albedo: float,
    phase_factor: float,
    body_radius_m: float,
    distance_from_body_center_m: float,
) -> float:
    if solar_flux_w_m2 < 0.0:
        raise ValueError("solar_flux_w_m2 must be non-negative.")
    if not 0.0 <= bond_albedo <= 1.0:
        raise ValueError("bond_albedo must be between 0 and 1.")
    if phase_factor < 0.0:
        raise ValueError("phase_factor must be non-negative.")
    if body_radius_m <= 0.0 or distance_from_body_center_m <= 0.0:
        raise ValueError("body_radius_m and distance_from_body_center_m must be positive.")
    return (
        solar_flux_w_m2
        * bond_albedo
        * phase_factor
        * (body_radius_m / distance_from_body_center_m) ** 2
    )


def environmental_heat_load_w(
    projected_area_m2: float,
    alpha_visible: float,
    alpha_ir: float,
    albedo_flux_w_m2: float,
    ir_flux_w_m2: float,
) -> float:
    if projected_area_m2 < 0.0:
        raise ValueError("projected_area_m2 must be non-negative.")
    if not 0.0 <= alpha_visible <= 1.0 or not 0.0 <= alpha_ir <= 1.0:
        raise ValueError("alpha_visible and alpha_ir must be between 0 and 1.")
    if albedo_flux_w_m2 < 0.0 or ir_flux_w_m2 < 0.0:
        raise ValueError("albedo_flux_w_m2 and ir_flux_w_m2 must be non-negative.")
    return projected_area_m2 * ((alpha_visible * albedo_flux_w_m2) + (alpha_ir * ir_flux_w_m2))


def dwell_multiplier_from_extra_heat(
    baseline_heat_w: float,
    extra_heat_w: float,
) -> float:
    if baseline_heat_w <= 0.0:
        raise ValueError("baseline_heat_w must be positive.")
    if extra_heat_w < 0.0:
        raise ValueError("extra_heat_w must be non-negative.")
    return baseline_heat_w / (baseline_heat_w + extra_heat_w)
