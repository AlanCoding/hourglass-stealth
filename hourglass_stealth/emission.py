"""Thermal emission and spectral power helpers."""

import math
from collections.abc import Sequence

from hourglass_stealth.constants import C, H, K_B, SIGMA_SB


def graybody_luminosity_w(
    emissivity: float,
    emitting_area_m2: float,
    temperature_k: float,
) -> float:
    if not 0.0 <= emissivity <= 1.0:
        raise ValueError("emissivity must be between 0 and 1.")
    if emitting_area_m2 < 0.0 or temperature_k < 0.0:
        raise ValueError("emitting_area_m2 and temperature_k must be non-negative.")
    return emissivity * SIGMA_SB * emitting_area_m2 * temperature_k**4


def equilibrium_temperature_k(
    absorbed_power_w: float,
    emissivity: float,
    emitting_area_m2: float,
) -> float:
    """Return the graybody equilibrium temperature for a steady absorbed power."""
    if absorbed_power_w < 0.0:
        raise ValueError("absorbed_power_w must be non-negative.")
    if not 0.0 < emissivity <= 1.0:
        raise ValueError("emissivity must be between 0 and 1, exclusive of 0.")
    if emitting_area_m2 <= 0.0:
        raise ValueError("emitting_area_m2 must be positive.")
    return (absorbed_power_w / (emissivity * SIGMA_SB * emitting_area_m2)) ** 0.25


def temperature_with_extra_heat_k(
    baseline_temperature_k: float,
    extra_heat_w: float,
    emissivity: float,
    emitting_area_m2: float,
) -> float:
    """Return the new equilibrium temperature after adding a steady extra heat load."""
    if baseline_temperature_k < 0.0:
        raise ValueError("baseline_temperature_k must be non-negative.")
    if extra_heat_w < 0.0:
        raise ValueError("extra_heat_w must be non-negative.")
    if not 0.0 < emissivity <= 1.0:
        raise ValueError("emissivity must be between 0 and 1, exclusive of 0.")
    if emitting_area_m2 <= 0.0:
        raise ValueError("emitting_area_m2 must be positive.")

    baseline_power_w = graybody_luminosity_w(
        emissivity=emissivity,
        emitting_area_m2=emitting_area_m2,
        temperature_k=baseline_temperature_k,
    )
    return equilibrium_temperature_k(
        absorbed_power_w=baseline_power_w + extra_heat_w,
        emissivity=emissivity,
        emitting_area_m2=emitting_area_m2,
    )


def wien_peak_um(temperature_k: float) -> float:
    if temperature_k <= 0.0:
        raise ValueError("temperature_k must be positive.")
    return 2898.0 / temperature_k


def _planck_scalar(wavelength_m: float, temperature_k: float) -> float:
    if wavelength_m <= 0.0:
        raise ValueError("wavelength_m must be positive.")
    if temperature_k <= 0.0:
        raise ValueError("temperature_k must be positive.")

    exponent = H * C / (wavelength_m * K_B * temperature_k)
    if exponent > 700.0:
        return 0.0

    numerator = 2.0 * H * C**2
    denominator = wavelength_m**5 * math.expm1(exponent)
    return numerator / denominator


def planck_b_lambda_w_m3_sr(
    wavelength_m: float | Sequence[float],
    temperature_k: float,
) -> float | list[float]:
    if isinstance(wavelength_m, Sequence) and not isinstance(wavelength_m, (str, bytes)):
        return [_planck_scalar(value, temperature_k) for value in wavelength_m]
    return _planck_scalar(float(wavelength_m), temperature_k)


def band_power_w(
    emissivity: float,
    area_m2: float,
    temperature_k: float,
    lambda_min_m: float,
    lambda_max_m: float,
    n: int = 2000,
) -> float:
    if lambda_min_m <= 0.0 or lambda_max_m <= 0.0:
        raise ValueError("Band bounds must be positive.")
    if lambda_max_m <= lambda_min_m:
        raise ValueError("lambda_max_m must be greater than lambda_min_m.")
    if n < 2:
        raise ValueError("n must be at least 2.")

    wavelengths = [
        lambda_min_m + (lambda_max_m - lambda_min_m) * i / (n - 1)
        for i in range(n)
    ]
    spectral_radiance = planck_b_lambda_w_m3_sr(wavelengths, temperature_k)

    integral = 0.0
    for left_w, right_w, left_b, right_b in zip(
        wavelengths[:-1],
        wavelengths[1:],
        spectral_radiance[:-1],
        spectral_radiance[1:],
    ):
        integral += 0.5 * (left_b + right_b) * (right_w - left_w)

    return emissivity * area_m2 * math.pi * integral
