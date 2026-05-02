"""Scenario evaluation entry points built from the lower-level modules."""

from hourglass_stealth.constants import EMISSIVITY_GRADES, HEAT_STORE_DEFAULTS, OPTICAL_ABSORPTION_GRADES, SOLAR_FLUX_1_AU_W_M2
from hourglass_stealth.detector import meters_to_earth_moon_distances, photon_limited_detection_distance_m, survey_detection_distance_m
from hourglass_stealth.emission import band_power_w, graybody_luminosity_w, wien_peak_um
from hourglass_stealth.heat_store import dwell_time_seconds, heat_store_energy_j, seconds_to_years
from hourglass_stealth.optics import absorbed_solar_power, total_absorption_fraction


def default_heat_store_for_temperature(temperature_k: float) -> dict:
    if temperature_k <= 0.0:
        raise ValueError("temperature_k must be positive.")

    for candidate in HEAT_STORE_DEFAULTS:
        if candidate["temperature_min_k"] <= temperature_k <= candidate["temperature_max_k"]:
            return dict(candidate)
    return dict(HEAT_STORE_DEFAULTS[-1])


def evaluate_scenario(
    architecture: str,
    optical_grade: str,
    emissivity_grade: str,
    aperture_area_m2: float,
    emitting_area_m2: float,
    heat_store_volume_m3: float,
    spacecraft_temperature_k: float,
    detector_diameter_m: float,
    detector_throughput: float,
    integration_time_s: float,
    required_signal_photons: float,
    survey_penalty_factor: float,
    heat_store_density_kg_m3: float | None = None,
    heat_store_usable_energy_j_kg: float | None = None,
    solar_flux_w_m2: float = SOLAR_FLUX_1_AU_W_M2,
    n_passes: int = 2,
    internal_heat_w: float = 0.0,
    earth_heat_w: float = 0.0,
    moon_heat_w: float = 0.0,
) -> dict:
    architecture_key = architecture.lower()
    if architecture_key not in {"mirror", "lens"}:
        raise ValueError("architecture must be 'mirror' or 'lens'.")
    if optical_grade not in OPTICAL_ABSORPTION_GRADES:
        raise ValueError(f"Unknown optical grade: {optical_grade}")
    if emissivity_grade not in EMISSIVITY_GRADES:
        raise ValueError(f"Unknown emissivity grade: {emissivity_grade}")

    optical_row = OPTICAL_ABSORPTION_GRADES[optical_grade]
    emissivity_row = EMISSIVITY_GRADES[emissivity_grade]
    heat_store_defaults = default_heat_store_for_temperature(spacecraft_temperature_k)

    abs_per_pass = optical_row[f"{architecture_key}_absorption_per_pass"]
    total_absorption = total_absorption_fraction(abs_per_pass, n_passes=n_passes)
    absorbed_power_w = absorbed_solar_power(
        solar_flux_w_m2=solar_flux_w_m2,
        aperture_area_m2=aperture_area_m2,
        abs_per_pass=abs_per_pass,
        n_passes=n_passes,
    )

    rho_initial_kg_m3 = (
        heat_store_defaults["rho_initial_kg_m3"]
        if heat_store_density_kg_m3 is None
        else heat_store_density_kg_m3
    )
    usable_energy_j_kg = (
        heat_store_defaults["usable_energy_j_kg"]
        if heat_store_usable_energy_j_kg is None
        else heat_store_usable_energy_j_kg
    )
    heat_store_energy_total_j = heat_store_energy_j(
        tank_volume_m3=heat_store_volume_m3,
        rho_initial_kg_m3=rho_initial_kg_m3,
        usable_energy_j_kg=usable_energy_j_kg,
    )

    total_heat_load_w = absorbed_power_w + internal_heat_w + earth_heat_w + moon_heat_w
    dwell_time_years_value = seconds_to_years(
        dwell_time_seconds(
            usable_energy_j=heat_store_energy_total_j,
            heat_load_w=total_heat_load_w,
        )
    )

    emissivity = emissivity_row["emissivity"]
    thermal_luminosity_w = graybody_luminosity_w(
        emissivity=emissivity,
        emitting_area_m2=emitting_area_m2,
        temperature_k=spacecraft_temperature_k,
    )
    peak_wavelength_um = wien_peak_um(spacecraft_temperature_k)
    peak_wavelength_m = peak_wavelength_um * 1e-6
    peak_band_power_w = band_power_w(
        emissivity=emissivity,
        area_m2=emitting_area_m2,
        temperature_k=spacecraft_temperature_k,
        lambda_min_m=0.5 * peak_wavelength_m,
        lambda_max_m=1.5 * peak_wavelength_m,
        n=400,
    )

    pointed_detection_distance_m = photon_limited_detection_distance_m(
        band_power_w=peak_band_power_w,
        detector_diameter_m=detector_diameter_m,
        wavelength_m=peak_wavelength_m,
        integration_time_s=integration_time_s,
        throughput=detector_throughput,
        required_signal_photons=required_signal_photons,
    )
    survey_distance_m = survey_detection_distance_m(
        pointed_distance_m=pointed_detection_distance_m,
        survey_penalty_factor=survey_penalty_factor,
    )

    return {
        "architecture": architecture_key,
        "optical_grade": optical_grade,
        "emissivity_grade": emissivity_grade,
        "abs_per_pass": abs_per_pass,
        "total_absorption_fraction": total_absorption,
        "absorbed_solar_power_W": absorbed_power_w,
        "total_heat_load_W": total_heat_load_w,
        "heat_store_energy_J": heat_store_energy_total_j,
        "heat_store_energy_MJ": heat_store_energy_total_j / 1_000_000.0,
        "dwell_time_years": dwell_time_years_value,
        "emissivity": emissivity,
        "thermal_luminosity_W": thermal_luminosity_w,
        "wien_peak_um": peak_wavelength_um,
        "detector_diameter_m": detector_diameter_m,
        "pointed_detection_distance_m": pointed_detection_distance_m,
        "pointed_detection_distance_EM": meters_to_earth_moon_distances(pointed_detection_distance_m),
        "survey_detection_distance_m": survey_distance_m,
        "survey_detection_distance_EM": meters_to_earth_moon_distances(survey_distance_m),
        "heat_store_material_class": heat_store_defaults["material_class"],
        "heat_store_density_kg_m3": rho_initial_kg_m3,
        "heat_store_usable_energy_j_kg": usable_energy_j_kg,
    }
