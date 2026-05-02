from hourglass_stealth.detector import (
    detector_collecting_area_m2,
    photon_energy_j,
    photon_limited_detection_distance_m,
    survey_detection_distance_m,
)


def test_collecting_area_scales_as_diameter_squared() -> None:
    area_1 = detector_collecting_area_m2(1.0)
    area_2 = detector_collecting_area_m2(2.0)
    assert area_2 == area_1 * 4.0


def test_photon_energy_decreases_with_longer_wavelength() -> None:
    short = photon_energy_j(10e-6)
    long = photon_energy_j(100e-6)
    assert short > long


def test_detection_distance_scales_linearly_with_diameter() -> None:
    d1 = photon_limited_detection_distance_m(1.0, 1.0, 100e-6, 1000.0, 0.3, 25.0)
    d2 = photon_limited_detection_distance_m(1.0, 2.0, 100e-6, 1000.0, 0.3, 25.0)
    assert round(d2 / d1, 6) == 2.0


def test_survey_distance_applies_square_root_penalty() -> None:
    assert survey_detection_distance_m(1000.0, 100.0) == 100.0
