import math

from hourglass_stealth.constants import SOLAR_FLUX_1_AU_W_M2
from hourglass_stealth.optics import absorbed_solar_power, total_absorption_fraction


def test_total_absorption_fraction_matches_expected_example() -> None:
    assert math.isclose(total_absorption_fraction(0.01, 2), 0.0199)


def test_total_absorption_fraction_zero_absorption_is_zero() -> None:
    assert total_absorption_fraction(0.0, 2) == 0.0


def test_absorbed_solar_power_increases_with_aperture_area() -> None:
    small = absorbed_solar_power(SOLAR_FLUX_1_AU_W_M2, 1.0, 1e-4, 2)
    large = absorbed_solar_power(SOLAR_FLUX_1_AU_W_M2, 10.0, 1e-4, 2)
    assert large > small
