"""Planetary heating approximations for cislunar environments."""


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
