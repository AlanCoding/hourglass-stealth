from hourglass_stealth.environment import (
    body_albedo_flux_w_m2,
    body_ir_flux_w_m2,
    dwell_multiplier_from_extra_heat,
    environmental_heat_load_w,
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
