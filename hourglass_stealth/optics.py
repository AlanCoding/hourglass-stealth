"""Optical absorption helpers for mirror and lens architectures."""


def total_absorption_fraction(abs_per_pass: float, n_passes: int = 2) -> float:
    """Return total absorbed fraction across multiple optical interactions."""
    if not 0.0 <= abs_per_pass <= 1.0:
        raise ValueError("abs_per_pass must be between 0 and 1.")
    if n_passes < 0:
        raise ValueError("n_passes must be non-negative.")

    return 1.0 - (1.0 - abs_per_pass) ** n_passes


def absorbed_solar_power(
    solar_flux_w_m2: float,
    aperture_area_m2: float,
    abs_per_pass: float,
    n_passes: int = 2,
) -> float:
    """Return absorbed solar power at the aperture."""
    if solar_flux_w_m2 < 0.0:
        raise ValueError("solar_flux_w_m2 must be non-negative.")
    if aperture_area_m2 < 0.0:
        raise ValueError("aperture_area_m2 must be non-negative.")

    return (
        solar_flux_w_m2
        * aperture_area_m2
        * total_absorption_fraction(abs_per_pass=abs_per_pass, n_passes=n_passes)
    )
