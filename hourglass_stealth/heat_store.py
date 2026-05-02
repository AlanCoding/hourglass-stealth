"""Sealed heat-store and dwell-time calculations."""


SECONDS_PER_YEAR = 365.25 * 24.0 * 3600.0


def heat_store_mass_kg(
    tank_volume_m3: float,
    rho_initial_kg_m3: float,
) -> float:
    if tank_volume_m3 < 0.0 or rho_initial_kg_m3 < 0.0:
        raise ValueError("tank_volume_m3 and rho_initial_kg_m3 must be non-negative.")
    return tank_volume_m3 * rho_initial_kg_m3


def heat_store_energy_j(
    tank_volume_m3: float,
    rho_initial_kg_m3: float,
    usable_energy_j_kg: float,
) -> float:
    if usable_energy_j_kg < 0.0:
        raise ValueError("usable_energy_j_kg must be non-negative.")
    return heat_store_mass_kg(tank_volume_m3, rho_initial_kg_m3) * usable_energy_j_kg


def usable_energy_density_j_m3(
    rho_initial_kg_m3: float,
    usable_energy_j_kg: float,
) -> float:
    if rho_initial_kg_m3 < 0.0 or usable_energy_j_kg < 0.0:
        raise ValueError("rho_initial_kg_m3 and usable_energy_j_kg must be non-negative.")
    return rho_initial_kg_m3 * usable_energy_j_kg


def final_volume_single_phase_m3(
    mass_kg: float,
    rho_final_kg_m3: float,
) -> float:
    if mass_kg < 0.0:
        raise ValueError("mass_kg must be non-negative.")
    if rho_final_kg_m3 <= 0.0:
        raise ValueError("rho_final_kg_m3 must be positive.")
    return mass_kg / rho_final_kg_m3


def final_state_fits(
    mass_kg: float,
    rho_final_kg_m3: float,
    tank_volume_m3: float,
    margin_fraction: float = 0.0,
) -> bool:
    if tank_volume_m3 < 0.0:
        raise ValueError("tank_volume_m3 must be non-negative.")
    if not 0.0 <= margin_fraction < 1.0:
        raise ValueError("margin_fraction must be between 0 and 1.")

    effective_capacity_m3 = tank_volume_m3 * (1.0 - margin_fraction)
    return final_volume_single_phase_m3(mass_kg, rho_final_kg_m3) <= effective_capacity_m3


def final_volume_two_phase_m3(
    mass_kg: float,
    vapor_fraction: float,
    rho_liquid_kg_m3: float,
    rho_vapor_kg_m3: float,
) -> float:
    if mass_kg < 0.0:
        raise ValueError("mass_kg must be non-negative.")
    if not 0.0 <= vapor_fraction <= 1.0:
        raise ValueError("vapor_fraction must be between 0 and 1.")
    if rho_liquid_kg_m3 <= 0.0 or rho_vapor_kg_m3 <= 0.0:
        raise ValueError("rho_liquid_kg_m3 and rho_vapor_kg_m3 must be positive.")

    liquid_mass_kg = (1.0 - vapor_fraction) * mass_kg
    vapor_mass_kg = vapor_fraction * mass_kg
    return (liquid_mass_kg / rho_liquid_kg_m3) + (vapor_mass_kg / rho_vapor_kg_m3)


def dwell_time_seconds(
    usable_energy_j: float,
    heat_load_w: float,
) -> float:
    if usable_energy_j < 0.0:
        raise ValueError("usable_energy_j must be non-negative.")
    if heat_load_w <= 0.0:
        raise ValueError("heat_load_w must be positive.")
    return usable_energy_j / heat_load_w


def seconds_to_years(seconds: float) -> float:
    if seconds < 0.0:
        raise ValueError("seconds must be non-negative.")
    return seconds / SECONDS_PER_YEAR
