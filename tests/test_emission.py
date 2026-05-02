import math

from hourglass_stealth.emission import band_power_w, graybody_luminosity_w, wien_peak_um


def test_graybody_luminosity_scales_with_emissivity() -> None:
    low = graybody_luminosity_w(0.001, 10.0, 20.0)
    high = graybody_luminosity_w(0.01, 10.0, 20.0)
    assert math.isclose(high, low * 10.0)


def test_graybody_luminosity_scales_with_area() -> None:
    small = graybody_luminosity_w(0.01, 10.0, 20.0)
    large = graybody_luminosity_w(0.01, 20.0, 20.0)
    assert large == small * 2.0


def test_graybody_luminosity_scales_as_t_fourth() -> None:
    cold = graybody_luminosity_w(0.01, 10.0, 10.0)
    warm = graybody_luminosity_w(0.01, 10.0, 20.0)
    assert warm == cold * 16.0


def test_wien_peak_matches_anchor_value() -> None:
    assert round(wien_peak_um(20.0), 1) == 144.9


def test_band_power_is_positive_over_valid_band() -> None:
    assert band_power_w(0.01, 10.0, 20.0, 100e-6, 200e-6, n=200) > 0.0
