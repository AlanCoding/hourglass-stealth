from hourglass_stealth.scenarios import default_heat_store_for_temperature, evaluate_scenario


def test_default_heat_store_mapping_uses_hydrogen_for_20k() -> None:
    candidate = default_heat_store_for_temperature(20.0)
    assert candidate["material_class"] == "liquid hydrogen"


def test_evaluate_scenario_returns_expected_shape() -> None:
    result = evaluate_scenario(
        architecture="mirror",
        optical_grade="B",
        emissivity_grade="B",
        aperture_area_m2=10.0,
        emitting_area_m2=10.0,
        heat_store_volume_m3=10.0,
        spacecraft_temperature_k=20.0,
        detector_diameter_m=6.5,
        detector_throughput=0.3,
        integration_time_s=1000.0,
        required_signal_photons=25.0,
        survey_penalty_factor=1000.0,
    )
    assert result["heat_store_material_class"] == "liquid hydrogen"
    assert result["absorbed_solar_power_W"] > 0.0
    assert result["dwell_time_years"] > 0.0
    assert result["pointed_detection_distance_m"] > result["survey_detection_distance_m"]
