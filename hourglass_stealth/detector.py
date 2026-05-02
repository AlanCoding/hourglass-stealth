"""Detector aperture, photon, flux, and range calculations."""

import math

from hourglass_stealth.constants import C, EARTH_MOON_DISTANCE_M, H


def detector_collecting_area_m2(
    diameter_m: float,
    obscuration_fraction: float = 0.0,
) -> float:
    if diameter_m < 0.0:
        raise ValueError("diameter_m must be non-negative.")
    if not 0.0 <= obscuration_fraction < 1.0:
        raise ValueError("obscuration_fraction must be between 0 and 1.")

    gross_area = math.pi * diameter_m**2 / 4.0
    return gross_area * (1.0 - obscuration_fraction)


def photon_energy_j(wavelength_m: float) -> float:
    if wavelength_m <= 0.0:
        raise ValueError("wavelength_m must be positive.")
    return H * C / wavelength_m


def bolometric_flux_at_range_w_m2(
    luminosity_w: float,
    distance_m: float,
) -> float:
    if luminosity_w < 0.0:
        raise ValueError("luminosity_w must be non-negative.")
    if distance_m <= 0.0:
        raise ValueError("distance_m must be positive.")
    return luminosity_w / (4.0 * math.pi * distance_m**2)


def bolometric_detection_distance_m(
    luminosity_w: float,
    limiting_flux_w_m2: float,
) -> float:
    if luminosity_w < 0.0:
        raise ValueError("luminosity_w must be non-negative.")
    if limiting_flux_w_m2 <= 0.0:
        raise ValueError("limiting_flux_w_m2 must be positive.")
    return math.sqrt(luminosity_w / (4.0 * math.pi * limiting_flux_w_m2))


def photon_limited_detection_distance_m(
    band_power_w: float,
    detector_diameter_m: float,
    wavelength_m: float,
    integration_time_s: float,
    throughput: float,
    required_signal_photons: float,
    obscuration_fraction: float = 0.0,
) -> float:
    if band_power_w < 0.0:
        raise ValueError("band_power_w must be non-negative.")
    if integration_time_s <= 0.0:
        raise ValueError("integration_time_s must be positive.")
    if not 0.0 <= throughput <= 1.0:
        raise ValueError("throughput must be between 0 and 1.")
    if required_signal_photons <= 0.0:
        raise ValueError("required_signal_photons must be positive.")

    collecting_area_m2 = detector_collecting_area_m2(
        diameter_m=detector_diameter_m,
        obscuration_fraction=obscuration_fraction,
    )
    numerator = band_power_w * collecting_area_m2 * throughput * integration_time_s * wavelength_m
    denominator = 4.0 * math.pi * H * C * required_signal_photons
    return math.sqrt(numerator / denominator)


def survey_detection_distance_m(
    pointed_distance_m: float,
    survey_penalty_factor: float,
) -> float:
    if pointed_distance_m < 0.0:
        raise ValueError("pointed_distance_m must be non-negative.")
    if survey_penalty_factor <= 0.0:
        raise ValueError("survey_penalty_factor must be positive.")
    return pointed_distance_m / math.sqrt(survey_penalty_factor)


def meters_to_earth_moon_distances(distance_m: float) -> float:
    if distance_m < 0.0:
        raise ValueError("distance_m must be non-negative.")
    return distance_m / EARTH_MOON_DISTANCE_M
