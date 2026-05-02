from hourglass_stealth.environment import (
    blackbody_irradiance_from_solid_angle_w_m2,
    body_albedo_flux_w_m2,
    body_ir_flux_w_m2,
    body_solid_angle_sr,
    dwell_multiplier_from_extra_heat,
    environmental_heat_load_w,
    radiative_equilibrium_temperature_from_body_k,
)


def test_body_fluxes_fall_with_distance() -> None:
    near_ir = body_ir_flux_w_m2(239.0, 6_371_000.0, 2 * 6_371_000.0)
    far_ir = body_ir_flux_w_m2(239.0, 6_371_000.0, 10 * 6_371_000.0)
    near_albedo = body_albedo_flux_w_m2(1361.0, 0.3, 0.5, 6_371_000.0, 2 * 6_371_000.0)
    far_albedo = body_albedo_flux_w_m2(1361.0, 0.3, 0.5, 6_371_000.0, 10 * 6_371_000.0)
    assert near_ir > far_ir
    assert near_albedo > far_albedo


def test_environmental_heat_load_combines_ir_and_albedo_terms() -> None:
    load = environmental_heat_load_w(10.0, 1e-3, 1e-2, 100.0, 200.0)
    assert load == 21.0


def test_dwell_multiplier_drops_with_extra_heat() -> None:
    assert dwell_multiplier_from_extra_heat(10.0, 10.0) == 0.5


def test_body_solid_angle_shrinks_with_distance() -> None:
    near = body_solid_angle_sr(6_371_000.0, 2 * 6_371_000.0)
    far = body_solid_angle_sr(6_371_000.0, 10 * 6_371_000.0)
    assert near > far


def test_blackbody_irradiance_matches_hemisphere_limit() -> None:
    full_hemisphere = blackbody_irradiance_from_solid_angle_w_m2(255.0, 2.0 * 3.141592653589793)
    assert full_hemisphere > 200.0


def test_radiative_equilibrium_temperature_is_below_body_temperature_for_partial_sky() -> None:
    temperature_k = radiative_equilibrium_temperature_from_body_k(
        body_temperature_k=255.0,
        body_solid_angle_sr=3.141592653589793,
        absorptivity_to_emissivity_ratio=1.0,
        absorption_to_emission_area_ratio=1.0,
    )
    assert temperature_k < 255.0


def test_radiative_equilibrium_temperature_hits_body_temperature_at_hemisphere_limit() -> None:
    temperature_k = radiative_equilibrium_temperature_from_body_k(
        body_temperature_k=255.0,
        body_solid_angle_sr=2.0 * 3.141592653589793,
        absorptivity_to_emissivity_ratio=1.0,
        absorption_to_emission_area_ratio=1.0,
    )
    assert round(temperature_k, 6) == 255.0
