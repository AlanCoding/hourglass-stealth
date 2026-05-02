from hourglass_stealth.heat_store import (
    dwell_time_seconds,
    final_state_fits,
    heat_store_energy_j,
    heat_store_mass_kg,
    seconds_to_years,
    usable_energy_density_j_m3,
)


def test_heat_store_mass_tracks_density_times_volume() -> None:
    assert heat_store_mass_kg(10.0, 1000.0) == 10_000.0


def test_heat_store_energy_tracks_volume_density_and_specific_energy() -> None:
    assert heat_store_energy_j(10.0, 1000.0, 100_000.0) == 1_000_000_000.0


def test_usable_energy_density_is_density_times_specific_energy() -> None:
    assert usable_energy_density_j_m3(1000.0, 100_000.0) == 100_000_000.0


def test_dwell_time_and_year_conversion_are_consistent() -> None:
    dwell_seconds = dwell_time_seconds(1_000_000.0, 10.0)
    assert dwell_seconds == 100_000.0
    assert seconds_to_years(dwell_seconds) > 0.0


def test_final_state_fits_when_final_volume_is_within_tank() -> None:
    assert final_state_fits(mass_kg=100.0, rho_final_kg_m3=200.0, tank_volume_m3=1.0)
